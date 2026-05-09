from sqlalchemy.orm import Session
from src.explorations.models.exploration import Exploration
from src.explorations.models.exploration_member import ExplorationMember
from src.explorations.schemas.exploration_history import ExplorationHistoryResponse


class ExplorationService:
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