import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.camps.models.camp import Camp
from src.inventory.enums import MovementTypeEnum
from src.inventory.models.inventory import Inventory
from src.inventory.models.inventory_movement import InventoryMovement
from src.inventory.models.inventory_resource import InventoryResource
from src.inventory.models.resource import Resource
from src.persons.enums import CurrentStatusEnum
from src.persons.models.person import Person
from src.production.models.daily_ration_log import DailyRationLog

SERVER_TIMEZONE = "America/Costa_Rica"
RATION_RUN_TIME = time(hour=20, minute=30)

logger = logging.getLogger(__name__)

CATEGORIES = {"ALIMENTO", "BEBIDAS", "MEDICINAS"}


class RationService:
    @staticmethod
    def server_now() -> datetime:
        return datetime.now(ZoneInfo(SERVER_TIMEZONE))

    @staticmethod
    def get_next_ration_run(now: datetime | None = None) -> datetime:
        current = now or RationService.server_now()
        today_run = datetime.combine(
            current.date(),
            RATION_RUN_TIME,
            tzinfo=ZoneInfo(SERVER_TIMEZONE),
        )
        if current < today_run:
            return today_run
        return today_run + timedelta(days=1)

    @staticmethod
    def distribute_daily_rations(
        db: Session, executed_at: datetime
    ) -> list[DailyRationLog]:
        logs: list[DailyRationLog] = []
        camps = db.query(Camp).all()

        for camp in camps:
            camp_id = camp.id

            eligible_count = (
                db.query(Person)
                .filter(
                    Person.camp_id == camp_id,
                    Person.is_active.is_(True),
                    Person.current_status.notin_(
                        [
                            CurrentStatusEnum.EN_EXPLORACION,
                            CurrentStatusEnum.TRASLADANDO_RECURSOS,
                        ]
                    ),
                )
                .count()
            )

            if eligible_count == 0:
                logger.info(
                    "Camp %s (%s): 0 eligible persons, skipping",
                    camp.name,
                    camp_id,
                )
                continue

            inventory_id = (
                db.query(Inventory.id)
                .filter(Inventory.camp_id == camp_id)
                .scalar()
            )

            if not inventory_id:
                logger.info(
                    "Camp %s (%s): no inventory found, skipping",
                    camp.name,
                    camp_id,
                )
                continue

            category_totals: dict[str, int] = {}
            for category in CATEGORIES:
                total = (
                    db.query(InventoryResource)
                    .join(Resource, Resource.id == InventoryResource.resource_id)
                    .filter(
                        InventoryResource.inventory_id == inventory_id,
                        Resource.category == category,
                    )
                    .with_entities(InventoryResource.quantity)
                    .all()
                )
                category_totals[category] = sum(row[0] for row in total)

            max_fed = eligible_count
            for category in CATEGORIES:
                max_fed = min(max_fed, category_totals[category])

            if max_fed == 0:
                logger.info(
                    "Camp %s (%s): 0 rations available, skipping (%s persons)",
                    camp.name,
                    camp_id,
                    eligible_count,
                )
                continue

            for category in CATEGORIES:
                RationService._deduct_category(db, inventory_id, category, max_fed)

            log_entry = DailyRationLog(
                persons_fed=max_fed,
                camp_id=camp_id,
                executed_at=executed_at,
            )
            db.add(log_entry)
            logs.append(log_entry)

            logger.info(
                "Camp %s (%s): %s/%s persons fed",
                camp.name,
                camp_id,
                max_fed,
                eligible_count,
            )

        db.commit()
        return logs

    @staticmethod
    def _deduct_category(
        db: Session,
        inventory_id: int,
        category: str,
        max_fed: int,
    ) -> None:
        resources = (
            db.query(InventoryResource)
            .join(Resource, Resource.id == InventoryResource.resource_id)
            .filter(
                InventoryResource.inventory_id == inventory_id,
                Resource.category == category,
                InventoryResource.quantity > 0,
            )
            .order_by(InventoryResource.id)
            .all()
        )

        remaining = max_fed
        for inv_resource in resources:
            if remaining <= 0:
                break

            deduct = min(inv_resource.quantity, remaining)

            inv_resource.quantity -= deduct

            movement = InventoryMovement(
                quantity=deduct,
                inventory_resource_id=inv_resource.id,
                movement_type=MovementTypeEnum.SALIDA,
            )
            db.add(movement)

            remaining -= deduct
