from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_APPROVE_REJECT,
    PERM_REQUEST_PERSONS,
    PERM_REQUEST_RESOURCES,
    PERM_VIEW_HISTORY,
    PERM_VIEW_TRANSFERS,
    ROLE_ADMIN,
    ROLE_RESOURCES,
    ROLE_TRAVEL,
    enforce_role_permissions,
    get_current_user_from_token,
)
from src.core.database import get_db
from src.transfers.schemas.camp_option_response import CampOptionResponse
from src.transfers.schemas.explorer_option_response import ExplorerOptionResponse
from src.transfers.schemas.resource_availability_response import (
    ResourceAvailabilityResponse,
)
from src.transfers.schemas.transfer_action_response import TransferActionResponse
from src.transfers.schemas.transfer_request_approval import TransferRequestApproval
from src.transfers.schemas.transfer_request_create import TransferRequestCreate
from src.transfers.schemas.transfer_request_response import TransferRequestResponse
from src.transfers.service.transfer_service import TransferService


router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.get("/camps", response_model=list[CampOptionResponse])
def list_camps(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[CampOptionResponse]:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_VIEW_TRANSFERS})
    elif current_user.role_name == ROLE_RESOURCES:
        enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_VIEW_TRANSFERS})
    elif current_user.role_name == ROLE_TRAVEL:
        enforce_role_permissions(db, current_user, {ROLE_TRAVEL}, {PERM_REQUEST_RESOURCES})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )
    return TransferService.list_camps(db, current_user.camp_id)


@router.get("/resources", response_model=list[ResourceAvailabilityResponse])
def list_resources(
    camp_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ResourceAvailabilityResponse]:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_VIEW_TRANSFERS})
    elif current_user.role_name == ROLE_RESOURCES:
        enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_VIEW_TRANSFERS})
    elif current_user.role_name == ROLE_TRAVEL:
        enforce_role_permissions(db, current_user, {ROLE_TRAVEL}, {PERM_REQUEST_RESOURCES})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )
    return TransferService.list_resources(db, camp_id)


@router.get("/pending", response_model=list[TransferRequestResponse])
def list_pending_requests(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[TransferRequestResponse]:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_VIEW_TRANSFERS})
    elif current_user.role_name == ROLE_RESOURCES:
        enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_VIEW_TRANSFERS})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )
    return TransferService.list_pending_requests(db, current_user.camp_id)


@router.get("/history", response_model=list[TransferRequestResponse])
def list_history_requests(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[TransferRequestResponse]:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_VIEW_HISTORY})
    elif current_user.role_name == ROLE_RESOURCES:
        enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_VIEW_HISTORY})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )
    return TransferService.list_history_requests(db, current_user.camp_id)


@router.get("/explorers", response_model=list[ExplorerOptionResponse])
def list_explorers(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ExplorerOptionResponse]:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_VIEW_TRANSFERS})
    elif current_user.role_name == ROLE_RESOURCES:
        enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_VIEW_TRANSFERS})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )
    return TransferService.list_explorers(db, current_user.camp_id)


@router.post("/requests", response_model=TransferRequestResponse)
def create_request(
    payload: TransferRequestCreate,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TransferRequestResponse:
    if current_user.role_name not in {ROLE_RESOURCES, ROLE_TRAVEL}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )

    required_permission = (
        PERM_REQUEST_RESOURCES if payload.is_resource_transfer else PERM_REQUEST_PERSONS
    )
    enforce_role_permissions(
        db,
        current_user,
        {ROLE_RESOURCES, ROLE_TRAVEL},
        {required_permission},
    )
    return TransferService.create_request(db, current_user, payload)


@router.post("/requests/{request_id}/approve", response_model=TransferActionResponse)
def approve_request(
    request_id: int,
    payload: TransferRequestApproval,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TransferActionResponse:
    enforce_role_permissions(
        db,
        current_user,
        {ROLE_RESOURCES},
        {PERM_APPROVE_REJECT},
    )
    TransferService.approve_request(db, current_user.camp_id, request_id, payload.participant_ids)
    return TransferActionResponse(message="Solicitud aprobada")


@router.post("/requests/{request_id}/reject", response_model=TransferActionResponse)
def reject_request(
    request_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TransferActionResponse:
    enforce_role_permissions(
        db,
        current_user,
        {ROLE_RESOURCES},
        {PERM_APPROVE_REJECT},
    )
    TransferService.reject_request(db, current_user.camp_id, request_id)
    return TransferActionResponse(message="Solicitud rechazada")
