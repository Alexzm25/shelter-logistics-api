from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.auth_service import AuthService
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


def get_current_user_from_token(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> UserProfileResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta el token de autorización")

    token = authorization.replace("Bearer ", "", 1).strip()
    return AuthService.get_current_user_profile(db, token)


@router.get("/camps", response_model=list[CampOptionResponse])
def list_camps(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[CampOptionResponse]:
    return TransferService.list_camps(db, current_user.camp_id)


@router.get("/resources", response_model=list[ResourceAvailabilityResponse])
def list_resources(
    camp_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ResourceAvailabilityResponse]:
    _ = current_user
    return TransferService.list_resources(db, camp_id)


@router.get("/pending", response_model=list[TransferRequestResponse])
def list_pending_requests(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[TransferRequestResponse]:
    return TransferService.list_pending_requests(db, current_user.camp_id)


@router.get("/history", response_model=list[TransferRequestResponse])
def list_history_requests(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[TransferRequestResponse]:
    return TransferService.list_history_requests(db, current_user.camp_id)


@router.get("/explorers", response_model=list[ExplorerOptionResponse])
def list_explorers(
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[ExplorerOptionResponse]:
    return TransferService.list_explorers(db, current_user.camp_id)


@router.post("/requests", response_model=TransferRequestResponse)
def create_request(
    payload: TransferRequestCreate,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TransferRequestResponse:
    return TransferService.create_request(db, current_user, payload)


@router.post("/requests/{request_id}/approve", response_model=TransferActionResponse)
def approve_request(
    request_id: int,
    payload: TransferRequestApproval,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TransferActionResponse:
    TransferService.approve_request(db, current_user.camp_id, request_id, payload.participant_ids)
    return TransferActionResponse(message="Solicitud aprobada")


@router.post("/requests/{request_id}/reject", response_model=TransferActionResponse)
def reject_request(
    request_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> TransferActionResponse:
    TransferService.reject_request(db, current_user.camp_id, request_id)
    return TransferActionResponse(message="Solicitud rechazada")
