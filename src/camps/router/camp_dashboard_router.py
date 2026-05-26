from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_REQUEST_PERSONS,
    PERM_REQUEST_RESOURCES,
    PERM_VIEW_DASHBOARD,
    PERM_VIEW_TRANSFERS,
    ROLE_ADMIN,
    ROLE_RESOURCES,
    ROLE_TRAVEL,
    enforce_role_permissions,
    get_current_user_from_token,
)
from src.camps.schemas.camp_dashboard_response import CampDashboardResponse
from src.camps.service.camp_dashboard_service import CampDashboardService
from src.core.database import get_db


router = APIRouter(prefix="/camps", tags=["Camps"])


@router.get("/{camp_id}/dashboard", response_model=CampDashboardResponse)
def get_camp_dashboard(
    response: Response,
    camp_id: int = Path(..., ge=1),
    page: int = Query(default=1, ge=1),
    person_page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    internal_page: int = Query(default=1, ge=1),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> CampDashboardResponse:
    if current_user.role_name == ROLE_ADMIN:
        enforce_role_permissions(db, current_user, {ROLE_ADMIN}, {PERM_VIEW_DASHBOARD})
    elif current_user.role_name == ROLE_RESOURCES:
        enforce_role_permissions(db, current_user, {ROLE_RESOURCES}, {PERM_VIEW_TRANSFERS})
    elif current_user.role_name == ROLE_TRAVEL:
        enforce_role_permissions(
            db,
            current_user,
            {ROLE_TRAVEL},
            {PERM_REQUEST_RESOURCES, PERM_REQUEST_PERSONS},
        )
    else:
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    dashboard = CampDashboardService.get_dashboard(db, camp_id, page, person_page, size, internal_page)
    response.headers["X-Total-Count"] = str(dashboard.inter_camp_resource_total)
    response.headers["X-Total-Count-Internal"] = str(dashboard.internal_total)
    return dashboard
