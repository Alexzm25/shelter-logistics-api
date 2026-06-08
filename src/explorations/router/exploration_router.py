import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
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
from src.explorations.schemas.exploration_loot import (
    RegisterExplorationLootRequest,
    RegisterExplorationLootResponse,
    ReturnExplorationRequest,
)
from src.explorations.service.exploration_service import ExplorationService
from src.explorations.schemas.available_explorer import AvailableExplorerResponse
from src.explorations.schemas.create_exploration import (
    CreateExplorationRequest,
    CreateExplorationResponse,
    MaxExtraDaysResponse,
)
from src.explorations.schemas.cancel_exploration import CancelExplorationResponse
from src.explorations.schemas.exploration_list import ExplorationListResponse
router = APIRouter(prefix="/explorations", tags=["Explorations"])
logger = logging.getLogger(__name__)


def validate_exploration_access(
    db: Session,
    current_user: UserProfileResponse,
) -> None:
    if current_user.role_name == ROLE_WORKER:
        enforce_role_permissions(
            db,
            current_user,
            {ROLE_WORKER},
            {PERM_VIEW_WORKER_PAGE},
        )

        profession_name = (current_user.profession_name or "").upper()

        if profession_name != "EXPLORADOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profesión no autorizada",
            )

        return

    if current_user.role_name in {ROLE_TRAVEL, ROLE_ADMIN}:
        enforce_role_permissions(
            db,
            current_user,
            {ROLE_TRAVEL, ROLE_ADMIN},
            {PERM_VIEW_EXPEDITIONS},
        )

        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Rol no autorizado",
    )

@router.get(
    "",
    response_model=list[ExplorationListResponse],
)
def get_explorations(
    response: Response,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ExplorationListResponse]:
    validate_exploration_access(db, current_user)

    camp_id = getattr(current_user, "camp_id", None)

    if not camp_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene campamento asociado",
        )

    total, items = ExplorationService.get_all_by_camp_paginated(
        db, camp_id, page=page, size=size
    )
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get(
    "/history/{person_id}",
    response_model=list[ExplorationHistoryResponse],
)
def get_exploration_history(
    person_id: int = Path(..., ge=1),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ExplorationHistoryResponse]:
    validate_exploration_access(db, current_user)

    history = ExplorationService.get_history_by_person(db, person_id, current_user.camp_id)

    if current_user.role_name == ROLE_WORKER and current_user.person_id != person_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes ver expediciones de otra persona",
        )

    return history

@router.post(
    "",
    response_model=CreateExplorationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exploration(
    payload: CreateExplorationRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> CreateExplorationResponse:
    validate_exploration_access(db, current_user)

    if not current_user.camp_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene campamento asociado",
        )

    return ExplorationService.create_exploration(
        db=db,
        payload=payload,
        camp_id=current_user.camp_id,
    )

@router.get(
    "/max-extra-days",
    response_model=MaxExtraDaysResponse,
)
def get_max_extra_days() -> MaxExtraDaysResponse:
    return MaxExtraDaysResponse(max_extra_days=20)

@router.get(
    "/available-explorers",
    response_model=list[AvailableExplorerResponse],
)
def get_available_explorers(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[AvailableExplorerResponse]:
    validate_exploration_access(db, current_user)

    if not current_user.camp_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene campamento asociado",
        )

    return ExplorationService.get_available_explorers(
        db=db,
        camp_id=current_user.camp_id,
    )

@router.post(
    "/loot",
    response_model=RegisterExplorationLootResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_exploration_loot(
    payload: RegisterExplorationLootRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> RegisterExplorationLootResponse:
    validate_exploration_access(db, current_user)

    return ExplorationService.register_loot(db, payload, current_user.camp_id)


@router.post(
    "/return",
    response_model=RegisterExplorationLootResponse,
    status_code=status.HTTP_200_OK,
)
def return_exploration(
    payload: ReturnExplorationRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> RegisterExplorationLootResponse:
    validate_exploration_access(db, current_user)
    logger.info(
        "POST /explorations/return payload=%s exploration_id=%s",
        payload.model_dump(),
        payload.exploration_id,
    )

    return ExplorationService.return_exploration(db, payload, current_user.camp_id)


@router.post(
    "/cancel",
    response_model=CancelExplorationResponse,
    status_code=status.HTTP_200_OK,
)
def cancel_exploration(
    exploration_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> CancelExplorationResponse:
    validate_exploration_access(db, current_user)

    return ExplorationService.cancel_exploration(db, exploration_id, current_user.camp_id)
