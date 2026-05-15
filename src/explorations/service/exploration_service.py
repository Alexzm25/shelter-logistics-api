from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.explorations.enums import ExplorationStatusEnum
from src.explorations.models.exploration import Exploration
from src.explorations.models.exploration_loot import ExplorationLoot
from src.explorations.models.exploration_member import ExplorationMember
from src.explorations.schemas.available_explorer import AvailableExplorerResponse
from src.explorations.schemas.create_exploration import (
    CreateExplorationRequest,
    CreateExplorationResponse,
)
from src.explorations.schemas.cancel_exploration import CancelExplorationResponse
from src.explorations.schemas.exploration_history import ExplorationHistoryResponse
from src.explorations.schemas.exploration_list import ExplorationListResponse
from src.explorations.schemas.exploration_loot import (
    ExplorationLootItemRequest,
    RegisterExplorationLootRequest,
    RegisterExplorationLootResponse,
    ReturnExplorationRequest,
)
from src.inventory.enums import MovementTypeEnum
from src.inventory.models import Inventory, InventoryMovement, InventoryResource, Resource
from src.persons.enums import CurrentStatusEnum, HealthStatusEnum
from src.persons.models.person import Person
from src.persons.models.profession import Profession
from src.persons.models.profession_assignment import ProfessionAssignment


class ExplorationService:
    @staticmethod
    def get_all_by_camp(
        db: Session,
        camp_id: int,
    ) -> list[ExplorationListResponse]:
        rows = (
            db.query(Exploration)
            .filter(Exploration.camp_id == camp_id)
            .order_by(Exploration.start_date.desc())
            .all()
        )

        result: list[ExplorationListResponse] = []

        for exploration in rows:
            team_count = (
                db.query(ExplorationMember)
                .filter(ExplorationMember.exploration_id == exploration.id)
                .count()
            )

            result.append(
                ExplorationListResponse(
                    id=exploration.id,
                    start_date=exploration.start_date,
                    return_date=exploration.return_date,
                    exploration_status=exploration.exploration_status.value,
                    estimated_days=exploration.estimated_days,
                    extra_days=exploration.extra_days,
                    team_count=team_count,
                )
            )

        return result

    @staticmethod
    def get_history_by_person(
        db: Session,
        person_id: int,
    ) -> list[ExplorationHistoryResponse]:
        rows = (
            db.query(Exploration)
            .join(
                ExplorationMember,
                ExplorationMember.exploration_id == Exploration.id,
            )
            .filter(ExplorationMember.person_id == person_id)
            .order_by(Exploration.start_date.desc())
            .all()
        )

        return [
            ExplorationHistoryResponse(
                id=exploration.id,
                start_date=exploration.start_date,
                return_date=exploration.return_date,
                exploration_status=exploration.exploration_status.value,
                estimated_days=exploration.estimated_days,
                extra_days=exploration.extra_days,
            )
            for exploration in rows
        ]

    @staticmethod
    def get_available_explorers(
        db: Session,
        camp_id: int,
    ) -> list[AvailableExplorerResponse]:
        rows = (
            db.query(Person)
            .join(
                ProfessionAssignment,
                ProfessionAssignment.person_id == Person.id,
            )
            .join(
                Profession,
                Profession.id == ProfessionAssignment.profession_id,
            )
            .filter(Person.camp_id == camp_id)
            .filter(Person.is_active.is_(True))
            .filter(Person.health_status == HealthStatusEnum.SANO)
            .filter(Person.current_status == CurrentStatusEnum.LIBRE)
            .filter(ProfessionAssignment.is_active.is_(True))
            .filter(Profession.name == "EXPLORADOR")
            .order_by(Person.name.asc(), Person.last_name.asc())
            .all()
        )

        return [
            AvailableExplorerResponse(
                id=person.id,
                full_name=f"{person.name} {person.last_name}",
                age=person.age,
                health_status=person.health_status.value,
                current_status=person.current_status.value,
            )
            for person in rows
        ]

    @staticmethod
    def create_exploration(
        db: Session,
        payload: CreateExplorationRequest,
        camp_id: int,
    ) -> CreateExplorationResponse:
        explorers = (
            db.query(Person)
            .join(
                ProfessionAssignment,
                ProfessionAssignment.person_id == Person.id,
            )
            .join(
                Profession,
                Profession.id == ProfessionAssignment.profession_id,
            )
            .filter(Person.id.in_(payload.member_ids))
            .filter(Person.camp_id == camp_id)
            .filter(Person.is_active.is_(True))
            .filter(Person.health_status == HealthStatusEnum.SANO)
            .filter(Person.current_status == CurrentStatusEnum.LIBRE)
            .filter(ProfessionAssignment.is_active.is_(True))
            .filter(Profession.name == "EXPLORADOR")
            .all()
        )

        if len(explorers) != len(set(payload.member_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más exploradores no están disponibles",
            )

        exploration = Exploration(
            start_date=payload.start_date,
            return_date=None,
            exploration_status=ExplorationStatusEnum.EN_PROCESO,
            camp_id=camp_id,
            extra_days=payload.extra_days,
            ration_per_person=payload.ration_per_person,
            max_extra_days=payload.max_extra_days,
            estimated_days=payload.estimated_days,
        )

        db.add(exploration)
        db.flush()

        for explorer in explorers:
            member = ExplorationMember(
                person_id=explorer.id,
                exploration_id=exploration.id,
            )

            explorer.current_status = CurrentStatusEnum.EN_EXPLORACION
            db.add(member)

        db.commit()
        db.refresh(exploration)

        return CreateExplorationResponse(
            message="Expedición creada correctamente",
            exploration_id=exploration.id,
        )

    @staticmethod
    def register_loot(
        db: Session,
        payload: RegisterExplorationLootRequest,
    ) -> RegisterExplorationLootResponse:
        exploration = ExplorationService._get_exploration_in_process(
            db,
            payload.exploration_id,
        )

        ExplorationService._get_resource(db, payload.resource_id)

        loot = ExplorationLoot(
            exploration_id=exploration.id,
            resource_id=payload.resource_id,
            quantity=payload.quantity,
            is_added_to_inventory=False,
        )

        db.add(loot)
        db.commit()
        db.refresh(loot)

        return RegisterExplorationLootResponse(
            message="Recolección registrada correctamente",
            loot_id=loot.id,
        )

    @staticmethod
    def return_exploration(
        db: Session,
        payload: ReturnExplorationRequest,
    ) -> RegisterExplorationLootResponse:
        exploration = ExplorationService._get_exploration_in_process(
            db,
            payload.exploration_id,
        )

        loot_records: list[ExplorationLoot] = []
        movement_records: list[InventoryMovement] = []

        for item in payload.items:
            ExplorationService._get_resource(db, item.resource_id)

            inventory_resource = ExplorationService._get_or_create_inventory_resource(
                db=db,
                camp_id=exploration.camp_id,
                resource_id=item.resource_id,
            )

            loot_records.append(
                ExplorationLoot(
                    exploration_id=exploration.id,
                    resource_id=item.resource_id,
                    quantity=item.quantity,
                    is_added_to_inventory=True,
                )
            )

            inventory_resource.quantity += item.quantity

            movement_records.append(
                InventoryMovement(
                    inventory_resource_id=inventory_resource.id,
                    quantity=item.quantity,
                    movement_type=MovementTypeEnum.INGRESO,
                )
            )

        exploration.exploration_status = ExplorationStatusEnum.COMPLETADA
        exploration.return_date = datetime.now(timezone.utc)

        members = (
            db.query(ExplorationMember)
            .filter(ExplorationMember.exploration_id == exploration.id)
            .all()
        )

        member_ids = [member.person_id for member in members]

        if member_ids:
            (
                db.query(Person)
                .filter(Person.id.in_(member_ids))
                .update(
                    {Person.current_status: CurrentStatusEnum.LIBRE},
                    synchronize_session=False,
                )
            )

        db.add_all(loot_records)
        db.add_all(movement_records)
        db.commit()
        for loot in loot_records:
            db.refresh(loot)

        return RegisterExplorationLootResponse(
            message="Expedición retornada y recursos agregados al inventario",
            loot_id=loot_records[0].id,
        )

    @staticmethod
    def cancel_exploration(
        db: Session,
        exploration_id: int,
    ) -> CancelExplorationResponse:
        exploration = ExplorationService._get_exploration_in_process(
            db,
            exploration_id,
        )

        exploration.exploration_status = ExplorationStatusEnum.CANCELADA
        exploration.return_date = datetime.now(timezone.utc)

        members = (
            db.query(ExplorationMember)
            .filter(ExplorationMember.exploration_id == exploration.id)
            .all()
        )

        member_ids = [member.person_id for member in members]

        if member_ids:
            (
                db.query(Person)
                .filter(Person.id.in_(member_ids))
                .update(
                    {Person.current_status: CurrentStatusEnum.LIBRE},
                    synchronize_session=False,
                )
            )

        db.commit()

        return CancelExplorationResponse(
            message="Expedición cancelada correctamente",
            exploration_id=exploration.id,
        )

    @staticmethod
    def _get_exploration_in_process(
        db: Session,
        exploration_id: int,
    ) -> Exploration:
        exploration = (
            db.query(Exploration)
            .filter(Exploration.id == exploration_id)
            .first()
        )

        if not exploration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expedición no encontrada",
            )

        if exploration.exploration_status != ExplorationStatusEnum.EN_PROCESO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede modificar una expedición en proceso",
            )

        return exploration

    @staticmethod
    def _get_resource(
        db: Session,
        resource_id: int,
    ) -> Resource:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()

        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurso no encontrado",
            )

        return resource

    @staticmethod
    def _get_or_create_inventory_resource(
        db: Session,
        camp_id: int,
        resource_id: int,
    ) -> InventoryResource:
        inventory = db.query(Inventory).filter(Inventory.camp_id == camp_id).first()

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventario del campamento no encontrado",
            )

        inventory_resource = (
            db.query(InventoryResource)
            .filter(
                InventoryResource.inventory_id == inventory.id,
                InventoryResource.resource_id == resource_id,
            )
            .first()
        )

        if inventory_resource:
            return inventory_resource

        inventory_resource = InventoryResource(
            inventory_id=inventory.id,
            resource_id=resource_id,
            quantity=0,
            minimum_stock_level=1,
        )

        db.add(inventory_resource)
        db.flush()

        return inventory_resource