from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_APPROVE_REJECT,
    PERM_REQUEST_RESOURCES,
    PERM_VIEW_WORKER_PAGE,
    ROLE_ADMIN,
    ROLE_RESOURCES,
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
    worker_person_id: int | None = None
    if camp_id is None:
        camp_id = current_user.camp_id

    if camp_id != current_user.camp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes consultar otro campamento",
        )

    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_VIEW_WORKER_PAGE})
    elif current_user.role_name == ROLE_RESOURCES:
        enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_APPROVE_REJECT})
    else:
        enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_REQUEST_RESOURCES})
        worker_person_id = current_user.person_id

    rows = WorkerRequestService.list_requests(db, camp_id, worker_person_id)
    return [
        WorkerRequestResponse(
            id=row["id"],
            worker_name=row["worker_name"],
            worker_role=row["worker_role"],
            request_type=row["request_type"],
            resource_name=row["resource_name"],
            quantity=row["quantity"],
            request_status=row["request_status"],
            created_at=row["created_at"],
            reason=row["reason"],
            rejection_reason=row["rejection_reason"],
            camp_name=row["camp_name"],
        )
        for row in rows
    ]


@router.post("/{request_id}/aprobar")
def approve_worker_request(
    request_id: int,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
):
    enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_APPROVE_REJECT})
    WorkerRequestService.approve_request(db, current_user.camp_id, request_id)
    return {"message": "Solicitud aprobada"}


@router.post("/{request_id}/rechazar")
def reject_worker_request(
    request_id: int,
    payload: dict | None = Body(default=None),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
):
    enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_APPROVE_REJECT})
    reason = None
    if payload:
        reason = payload.get("reason") or payload.get("motivo") or payload.get("rejection_reason")
    WorkerRequestService.reject_request(db, current_user.camp_id, request_id, reason)
    return {"message": "Solicitud rechazada"}
