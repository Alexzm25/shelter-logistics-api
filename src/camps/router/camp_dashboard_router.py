from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import PERM_VIEW_DASHBOARD, ROLE_ADMIN, require_role_permissions
from src.camps.schemas.camp_dashboard_response import CampDashboardResponse
from src.camps.service.camp_dashboard_service import CampDashboardService
from src.core.database import get_db


router = APIRouter(prefix="/camps", tags=["Camps"])


@router.get("/{camp_id}/dashboard", response_model=CampDashboardResponse)
def get_camp_dashboard(
    camp_id: int = Path(..., ge=1),
    current_user: UserProfileResponse = Depends(
        require_role_permissions({ROLE_ADMIN}, {PERM_VIEW_DASHBOARD})
    ),
    db: Session = Depends(get_db),
) -> CampDashboardResponse:
    _ = current_user
    return CampDashboardService.get_dashboard(db, camp_id)
