from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.explorations.schemas.exploration_history import ExplorationHistoryResponse
from src.explorations.service.exploration_service import ExplorationService


router = APIRouter(prefix="/explorations", tags=["Explorations"])


@router.get(
    "/history/{person_id}",
    response_model=list[ExplorationHistoryResponse],
)
def get_exploration_history(
    person_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> list[ExplorationHistoryResponse]:
    return ExplorationService.get_history_by_person(db, person_id)