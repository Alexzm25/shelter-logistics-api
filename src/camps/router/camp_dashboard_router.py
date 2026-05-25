from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import PERM_VIEW_DASHBOARD, ROLE_ADMIN, require_role_permissions
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
    current_user: UserProfileResponse = Depends(
        require_role_permissions({ROLE_ADMIN}, {PERM_VIEW_DASHBOARD})
    ),
    db: Session = Depends(get_db),
) -> CampDashboardResponse:
    _ = current_user
    dashboard = CampDashboardService.get_dashboard(db, camp_id, page, person_page, size, internal_page)
    response.headers["X-Total-Count"] = str(dashboard.inter_camp_resource_total)
    response.headers["X-Total-Count-Internal"] = str(dashboard.internal_total)
    return dashboard
