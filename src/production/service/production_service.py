from datetime import datetime, time, timedelta
import logging
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.camps.models.camp import Camp
from src.core.realtime_events import inventory_events
from src.inventory.enums import MovementTypeEnum
from src.inventory.models.inventory import Inventory
from src.inventory.models.inventory_movement import InventoryMovement
from src.inventory.models.inventory_resource import InventoryResource
from src.inventory.models.resource import Resource
from src.persons.enums import CurrentStatusEnum, HealthStatusEnum
from src.persons.models.person import Person
from src.persons.models.profession import Profession
from src.persons.models.profession_assignment import ProfessionAssignment
from src.persons.models.profession_production import ProfessionProduction
from src.production.models.production_log import ProductionLog
from src.production.models.production_run_audit import ProductionRunAudit
from src.production.schemas.production_audit_response import (
    ProducedResourceResponse,
    ProductionAuditResponse,
    ProductionAutomationStatusResponse,
)
from src.production.schemas.production_request import RegisterProductionRequest
from src.production.schemas.production_response import RegisterProductionResponse


SERVER_TIMEZONE = "America/Costa_Rica"
PRODUCTION_RUN_TIME = time(hour=12, minute=0)
logger = logging.getLogger(__name__)


class ProductionService:
    @staticmethod
    def server_now() -> datetime:
        return datetime.now(ZoneInfo(SERVER_TIMEZONE))

    @staticmethod
    def get_next_automatic_run(now: datetime | None = None) -> datetime:
        current = now or ProductionService.server_now()
        today_run = datetime.combine(
            current.date(),
            PRODUCTION_RUN_TIME,
            tzinfo=ZoneInfo(SERVER_TIMEZONE),
        )
        if current < today_run:
            return today_run
        return today_run + timedelta(days=1)

    @staticmethod
    def register_production(
        db: Session,
        person_id: int,
        payload: RegisterProductionRequest,
    ) -> RegisterProductionResponse:
        person = db.query(Person).filter(Person.id == person_id).first()

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona no encontrada",
            )

        profession_assignment = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.person_id == person.id,
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(True),
            )
            .first()
        )

        if not profession_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La persona no tiene una profesion activa",
            )

        profession = (
            db.query(Profession)
            .filter(Profession.id == profession_assignment.profession_id)
            .first()
        )

        if not profession:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profesion no encontrada",
            )

        inventory_resource = ProductionService._get_inventory_resource(
            db,
            person.camp_id,
            payload.resource_id,
        )

        profession_prod = (
            db.query(ProfessionProduction)
            .filter(
                ProfessionProduction.profession_id == profession.id,
                ProfessionProduction.resource_id == payload.resource_id,
            )
            .first()
        )

        if not profession_prod:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Limite de produccion no definido para esta profesion y recurso",
            )

        max_allowed = int(profession_prod.production_quantity)

        if payload.actual_quantity > max_allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La cantidad reportada no es posible. "
                    f"Maximo permitido: {max_allowed}."
                ),
            )

        ProductionService._add_production_to_inventory(
            db=db,
            camp_id=person.camp_id,
            person_id=person.id,
            profession_id=profession.id,
            resource_id=payload.resource_id,
            actual_quantity=payload.actual_quantity,
            expected_quantity=max_allowed,
            inventory_resource=inventory_resource,
        )
        db.commit()
        inventory_events.publish(
            camp_id=person.camp_id,
            source="production.registered",
            metadata={
                "resource_id": payload.resource_id,
                "quantity": payload.actual_quantity,
            },
        )

        return RegisterProductionResponse(
            message="Produccion registrada correctamente",
        )

    @staticmethod
    def register_daily_automatic_production(
        db: Session,
        executed_at: datetime | None = None,
    ) -> list[ProductionAuditResponse]:
        run_at = executed_at or ProductionService.server_now()
        camps = db.query(Camp).order_by(Camp.id.asc()).all()
        audit_responses: list[ProductionAuditResponse] = []

        for camp in camps:
            if ProductionService.has_automatic_run_for_day(db, camp.id, run_at):
                continue

            try:
                resources = ProductionService._produce_for_camp(db, camp.id)
                audit = ProductionRunAudit(
                    executed_at=run_at,
                    camp_id=camp.id,
                    resources_produced=resources,
                )
                db.add(audit)
                db.commit()
                db.refresh(audit)
                inventory_events.publish(
                    camp_id=camp.id,
                    source="production.automatic",
                    metadata={"audit_id": audit.id},
                )
                audit_responses.append(ProductionService._audit_to_response(db, audit))
            except Exception:
                db.rollback()
                logger.exception("Automatic production failed for camp %s", camp.id)

        return audit_responses

    @staticmethod
    def get_automation_status(
        db: Session,
        camp_id: int,
    ) -> ProductionAutomationStatusResponse:
        now = ProductionService.server_now()
        return ProductionAutomationStatusResponse(
            timezone=SERVER_TIMEZONE,
            next_run_at=ProductionService.get_next_automatic_run(now),
            already_ran_today=ProductionService.has_automatic_run_for_day(db, camp_id, now),
            last_run=ProductionService.get_latest_audit(db, camp_id),
        )

    @staticmethod
    def list_audits(
        db: Session,
        camp_id: int,
        limit: int = 10,
    ) -> list[ProductionAuditResponse]:
        rows = (
            db.query(ProductionRunAudit)
            .filter(ProductionRunAudit.camp_id == camp_id)
            .order_by(ProductionRunAudit.executed_at.desc(), ProductionRunAudit.id.desc())
            .limit(limit)
            .all()
        )
        return [ProductionService._audit_to_response(db, row) for row in rows]

    @staticmethod
    def get_latest_audit(
        db: Session,
        camp_id: int,
    ) -> ProductionAuditResponse | None:
        audit = (
            db.query(ProductionRunAudit)
            .filter(ProductionRunAudit.camp_id == camp_id)
            .order_by(ProductionRunAudit.executed_at.desc(), ProductionRunAudit.id.desc())
            .first()
        )
        if not audit:
            return None
        return ProductionService._audit_to_response(db, audit)

    @staticmethod
    def has_automatic_run_for_day(
        db: Session,
        camp_id: int,
        run_at: datetime,
    ) -> bool:
        local_run_at = run_at.astimezone(ZoneInfo(SERVER_TIMEZONE))
        day_start = datetime.combine(
            local_run_at.date(),
            time.min,
            tzinfo=ZoneInfo(SERVER_TIMEZONE),
        )
        next_day_start = day_start + timedelta(days=1)

        return (
            db.query(ProductionRunAudit.id)
            .filter(
                ProductionRunAudit.camp_id == camp_id,
                ProductionRunAudit.executed_at >= day_start,
                ProductionRunAudit.executed_at < next_day_start,
            )
            .first()
            is not None
        )

    @staticmethod
    def _produce_for_camp(
        db: Session,
        camp_id: int,
    ) -> list[dict[str, int | str]]:
        rows = (
            db.query(Person, Profession, ProfessionProduction, Resource)
            .join(ProfessionAssignment, ProfessionAssignment.person_id == Person.id)
            .join(Profession, Profession.id == ProfessionAssignment.profession_id)
            .join(ProfessionProduction, ProfessionProduction.profession_id == Profession.id)
            .join(Resource, Resource.id == ProfessionProduction.resource_id)
            .filter(
                Person.camp_id == camp_id,
                Person.is_active.is_(True),
                Person.health_status == HealthStatusEnum.SANO,
                Person.current_status.notin_(
                    [
                        CurrentStatusEnum.EN_EXPLORACION,
                        CurrentStatusEnum.TRASLADANDO_RECURSOS,
                    ]
                ),
                ProfessionAssignment.is_active.is_(True),
                ProfessionAssignment.is_main_profession.is_(True),
            )
            .all()
        )

        produced_by_resource: dict[int, dict[str, int | str]] = {}

        for person, profession, profession_prod, resource in rows:
            quantity = int(profession_prod.production_quantity)
            if quantity <= 0:
                continue

            inventory_resource = ProductionService._get_inventory_resource(
                db,
                camp_id,
                resource.id,
            )
            ProductionService._add_production_to_inventory(
                db=db,
                camp_id=camp_id,
                person_id=person.id,
                profession_id=profession.id,
                resource_id=resource.id,
                actual_quantity=quantity,
                expected_quantity=quantity,
                inventory_resource=inventory_resource,
            )

            if resource.id not in produced_by_resource:
                produced_by_resource[resource.id] = {
                    "resource_id": resource.id,
                    "resource_name": resource.name,
                    "quantity": 0,
                }
            produced_by_resource[resource.id]["quantity"] = (
                int(produced_by_resource[resource.id]["quantity"]) + quantity
            )

        return list(produced_by_resource.values())

    @staticmethod
    def _add_production_to_inventory(
        db: Session,
        camp_id: int,
        person_id: int,
        profession_id: int,
        resource_id: int,
        actual_quantity: int,
        expected_quantity: int,
        inventory_resource: InventoryResource,
    ) -> None:
        production_log = ProductionLog(
            actual_quantity=actual_quantity,
            expected_quantity=expected_quantity,
            camp_id=camp_id,
            person_id=person_id,
            resource_id=resource_id,
            profession_id=profession_id,
        )
        inventory_resource.quantity += actual_quantity
        inventory_movement = InventoryMovement(
            quantity=actual_quantity,
            inventory_resource_id=inventory_resource.id,
            movement_type=MovementTypeEnum.INGRESO,
            transfer_request_id=None,
        )
        db.add(production_log)
        db.add(inventory_movement)

    @staticmethod
    def _get_inventory_resource(
        db: Session,
        camp_id: int,
        resource_id: int,
    ) -> InventoryResource:
        inventory_resource = (
            db.query(InventoryResource)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .filter(
                Inventory.camp_id == camp_id,
                InventoryResource.resource_id == resource_id,
            )
            .first()
        )

        if not inventory_resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurso no encontrado en el inventario del campamento",
            )

        return inventory_resource

    @staticmethod
    def _audit_to_response(
        db: Session,
        audit: ProductionRunAudit,
    ) -> ProductionAuditResponse:
        camp_name = (
            db.query(Camp.name)
            .filter(Camp.id == audit.camp_id)
            .scalar()
            or f"Campamento {audit.camp_id}"
        )
        resources = [
            ProducedResourceResponse(
                resource_id=int(item["resource_id"]),
                resource_name=str(item["resource_name"]),
                quantity=int(item["quantity"]),
            )
            for item in (audit.resources_produced or [])
        ]

        return ProductionAuditResponse(
            id=audit.id,
            executed_at=audit.executed_at,
            camp_id=audit.camp_id,
            camp_name=camp_name,
            resources_produced=resources,
            total_quantity=sum(item.quantity for item in resources),
        )
