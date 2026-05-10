from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import ALL_ROLES, PERM_VIEW_ACHIEVEMENTS, require_role_permissions
from src.achievement.service.achievement_service import AchievementService
from src.core.database import get_db


router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("/me")
def get_my_achievements(
    current_user: UserProfileResponse = Depends(
        require_role_permissions(ALL_ROLES, {PERM_VIEW_ACHIEVEMENTS})
    ),
    db: Session = Depends(get_db),
):
    return AchievementService.get_user_achievements(db, current_user.user_id)
