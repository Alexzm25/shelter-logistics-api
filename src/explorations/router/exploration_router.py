from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_VIEW_EXPEDITIONS,
    PERM_VIEW_WORKER_PAGE,
    ROLE_ADMIN,
    ROLE_TRAVEL,
    ROLE_WORKER,
    enforce_role_permissions,
    get_current_user_from_token,
)
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
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ExplorationHistoryResponse]:
    if current_user.role_name == ROLE_WORKER:
        enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_VIEW_WORKER_PAGE})
        profession_name = (current_user.profession_name or "").upper()
        if profession_name != "EXPLORADOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profesion no autorizada",
            )
        if current_user.person_id != person_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes ver expediciones de otra persona",
            )
    elif current_user.role_name in {ROLE_TRAVEL, ROLE_ADMIN}:
        enforce_role_permissions(
            db,
            current_user,
            {ROLE_TRAVEL, ROLE_ADMIN},
            {PERM_VIEW_EXPEDITIONS},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )

    return ExplorationService.get_history_by_person(db, person_id)