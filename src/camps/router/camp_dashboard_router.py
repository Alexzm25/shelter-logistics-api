from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from src.camps.schemas.camp_dashboard_response import CampDashboardResponse
from src.camps.service.camp_dashboard_service import CampDashboardService
from src.core.database import get_db


router = APIRouter(prefix="/camps", tags=["Camps"])


@router.get("/{camp_id}/dashboard", response_model=CampDashboardResponse)
def get_camp_dashboard(
    camp_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> CampDashboardResponse:
    return CampDashboardService.get_dashboard(db, camp_id)
