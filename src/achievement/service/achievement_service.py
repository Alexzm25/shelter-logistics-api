from typing import List

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from src.achievement.models.achievement import Achievement
from src.achievement.models.user_achievement import UserAchievement
from src.achievement.schemas.achievement_response import AchievementResponse
from src.auth.models import AppUser
from src.core.database import SessionLocal

from src.inventory.models.inventory_resource import InventoryResource
from src.inventory.models.inventory import Inventory
from src.explorations.models.exploration import Exploration
from src.explorations.models.exploration_loot import ExplorationLoot
from src.transfers.models.transfer_request import TransferRequest
from src.production.models.production_log import ProductionLog
from src.persons.models.person import Person
from src.production.models.daily_ration_log import DailyRationLog
from src.inventory.models.inventory_movement import InventoryMovement


class AchievementService:
    @staticmethod
    def evaluate_achievements(db: Session, user_id: int) -> None:
        user = db.query(AppUser).filter(AppUser.id == user_id).first()
        if not user:
            return

        person = db.query(Person).filter(Person.id == user.person_id).first()
        if not person:
            return

        camp_id = person.camp_id

        unlocked = (
            db.query(UserAchievement.achievement_id)
            .filter(UserAchievement.user_id == user_id, UserAchievement.is_unlocked == True)
            .all()
        )
        unlocked_ids = {u[0] for u in unlocked}

        achievements = db.query(Achievement).all()

        for ach in achievements:
            if ach.id in unlocked_ids:
                continue

            value = AchievementService._evaluate_metric(db, camp_id, ach.id)
            if value is None:
                continue

            if value >= ach.condition_value:
                ua = (
                    db.query(UserAchievement)
                    .filter(
                        UserAchievement.user_id == user_id,
                        UserAchievement.achievement_id == ach.id,
                    )
                    .first()
                )
                if not ua:
                    new = UserAchievement(
                        user_id=user_id,
                        achievement_id=ach.id,
                        is_unlocked=True,
                    )
                    db.add(new)
                else:
                    if not ua.is_unlocked:
                        ua.is_unlocked = True
                try:
                    db.commit()
                except Exception:
                    db.rollback()

    @staticmethod
    def evaluate_achievements_background(user_id: int) -> None:
        db = SessionLocal()
        try:
            AchievementService.evaluate_achievements(db, user_id)
        finally:
            db.close()

    @staticmethod
    def get_user_achievements(db: Session, user_id: int) -> List[AchievementResponse]:
        achievements = db.query(Achievement).order_by(Achievement.id).all()

        unlocked = (
            db.query(UserAchievement)
            .filter(UserAchievement.user_id == user_id, UserAchievement.is_unlocked == True)
            .all()
        )
        unlocked_map = {u.achievement_id: u for u in unlocked}

        result: List[AchievementResponse] = []
        for ach in achievements:
            ua = unlocked_map.get(ach.id)
            if ua:
                result.append(
                    AchievementResponse(
                        id=ach.id,
                        name=ach.name,
                        description=ach.description,
                        icon_url=ach.icon_url,
                        is_unlocked=True,
                        unlocked_at=ua.unlocked_at.isoformat() if ua.unlocked_at else None,
                    )
                )
            else:
                result.append(
                    AchievementResponse(
                        id=ach.id,
                        name=ach.name,
                        description=None,
                        icon_url=None,
                        is_unlocked=False,
                        unlocked_at=None,
                    )
                )

        return result

    @staticmethod
    def _evaluate_metric(db: Session, camp_id: int, achievement_id: int):
        # Map achievement id to metric queries
        if achievement_id == 1:
            # SUM inventory_resource.quantity where inventory.camp_id = camp_id
            q = (
                db.query(func.coalesce(func.sum(InventoryResource.quantity), 0))
                .join(Inventory, Inventory.id == InventoryResource.inventory_id)
                .filter(Inventory.camp_id == camp_id)
            )
            return q.scalar()
        if achievement_id == 2:
            q = (
                db.query(func.coalesce(func.sum(InventoryResource.quantity), 0))
                .join(Inventory, Inventory.id == InventoryResource.inventory_id)
                .filter(Inventory.camp_id == camp_id)
            )
            return q.scalar()
        if achievement_id == 3:
            q = (
                db.query(func.count(Exploration.id))
                .filter(Exploration.camp_id == camp_id, Exploration.exploration_status == "COMPLETADA")
            )
            return q.scalar()
        if achievement_id == 4:
            q = (
                db.query(func.count(Exploration.id))
                .filter(Exploration.camp_id == camp_id, Exploration.exploration_status == "COMPLETADA")
            )
            return q.scalar()
        if achievement_id == 5:
            q = (
                db.query(func.coalesce(func.sum(ExplorationLoot.quantity), 0))
                .join(Exploration, Exploration.id == ExplorationLoot.exploration_id)
                .filter(Exploration.camp_id == camp_id)
            )
            return q.scalar()
        if achievement_id in (6, 7):
            q = (
                db.query(func.count(TransferRequest.id))
                .filter(
                    or_(TransferRequest.from_camp_id == camp_id, TransferRequest.to_camp_id == camp_id),
                    TransferRequest.transfer_status == "LLEGÓ",
                )
            )
            return q.scalar()
        if achievement_id == 8:
            q = (
                db.query(func.coalesce(func.sum(ProductionLog.actual_quantity), 0))
                .filter(ProductionLog.camp_id == camp_id)
            )
            return q.scalar()
        if achievement_id == 9:
            q = (
                db.query(func.count(Person.id))
                .filter(Person.camp_id == camp_id, Person.is_active == True)
            )
            return q.scalar()
        if achievement_id == 10:
            q = (
                db.query(func.count(DailyRationLog.id))
                .filter(DailyRationLog.camp_id == camp_id)
            )
            return q.scalar()
        if achievement_id == 11:
            q = (
                db.query(func.count(Person.id))
                .filter(
                    Person.camp_id == camp_id,
                    Person.health_status == "SANO",
                    Person.is_active == True,
                )
            )
            return q.scalar()
        if achievement_id == 12:
            q = (
                db.query(func.count(InventoryMovement.id))
                .join(InventoryResource, InventoryResource.id == InventoryMovement.inventory_resource_id)
                .join(Inventory, Inventory.id == InventoryResource.inventory_id)
                .filter(Inventory.camp_id == camp_id)
            )
            return q.scalar()

        return None
