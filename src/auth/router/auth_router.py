from fastapi import APIRouter, Depends, Header, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from src.auth.schemas.login_request import LoginRequest
from src.auth.schemas.login_response import LoginResponse
from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.auth_service import AuthService
from src.achievement.service.achievement_service import AchievementService
from src.auth.models import AppUser
from src.core.database import get_db


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> LoginResponse:
    response = AuthService.login(db, credentials)

    # schedule achievements evaluation in background using a fresh session
    try:
        user = db.query(AppUser).filter(AppUser.username == credentials.username).first()
        if user:
            background_tasks.add_task(AchievementService.evaluate_achievements_background, user.id)
    except Exception:
        # do not block login on background scheduling failures
        pass

    return response


@router.get("/me", response_model=UserProfileResponse)
def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> UserProfileResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta el token de autorización")

    token = authorization.replace("Bearer ", "", 1).strip()
    return AuthService.get_current_user_profile(db, token)
