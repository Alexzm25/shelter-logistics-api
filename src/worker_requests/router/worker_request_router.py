from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_REQUEST_RESOURCES,
    ROLE_WORKER,
    enforce_role_permissions,
    get_current_user_from_token,
)
from src.core.database import get_db
from src.worker_requests.schemas.worker_request_create import WorkerRequestCreate
from src.worker_requests.schemas.worker_request_response import WorkerRequestResponse
from src.worker_requests.service.worker_request_service import WorkerRequestService


router = APIRouter(prefix="/solicitudes-trabajadores", tags=["WorkerRequests"])


@router.post("", response_model=list[dict])
def create_worker_request(
    payload: WorkerRequestCreate,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[dict]:
    # allow workers to create requests
    enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_REQUEST_RESOURCES})
    return WorkerRequestService.create_request(db, current_user, payload)


@router.get("", response_model=list[WorkerRequestResponse])
def list_worker_requests(
    camp_id: int | None = Query(default=None),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[WorkerRequestResponse]:
    if camp_id is None:
        camp_id = current_user.camp_id
    rows = WorkerRequestService.list_requests(db, camp_id)
    # map rows to response model
    return [
        WorkerRequestResponse(
            id=row["id"],
            worker_name=None,
            worker_role=None,
            quantity=row["quantity"],
            request_status=row["request_status"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.post("/{request_id}/aprobar")
def approve_worker_request(
    request_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
):
    enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_REQUEST_RESOURCES})
    WorkerRequestService.approve_request(db, current_user.camp_id, request_id)
    return {"message": "Solicitud aprobada"}


@router.post("/{request_id}/rechazar")
def reject_worker_request(
    request_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
):
    enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_REQUEST_RESOURCES})
    WorkerRequestService.reject_request(db, request_id)
    return {"message": "Solicitud rechazada"}
