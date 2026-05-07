from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.auth.service.auth_service import AuthService
from src.achievement.service.achievement_service import AchievementService


router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("/me")
def get_my_achievements(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta el token de autorización")

    token = authorization.replace("Bearer ", "", 1).strip()
    profile = AuthService.get_current_user_profile(db, token)

    return AchievementService.get_user_achievements(db, profile.user_id)
