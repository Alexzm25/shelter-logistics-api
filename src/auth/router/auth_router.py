import os

from fastapi import APIRouter, BackgroundTasks, Depends, Response
from sqlalchemy.orm import Session

from src.auth.schemas.login_request import LoginRequest
from src.auth.schemas.login_response import LoginResponse
from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.auth_service import AuthService
from src.auth.service.authorization import ALL_ROLES, PERM_VIEW_ACHIEVEMENTS, require_role_permissions
from src.achievement.service.achievement_service import AchievementService
from src.auth.models import AppUser
from src.core.database import get_db


router = APIRouter(prefix="/auth", tags=["Auth"])


def get_cookie_settings() -> dict[str, object]:
    is_production = os.getenv("ENVIRONMENT") == "production"
    return {
        "httponly": True,
        "secure": is_production,
        "samesite": "none" if is_production else "lax",
        "max_age": 1800,
    }


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    login_response = AuthService.login(db, credentials)
    access_token = login_response.access_token
    response.set_cookie(
        key="access_token",
        value=access_token,
        **get_cookie_settings(),
    )

    # schedule achievements evaluation in background using a fresh session
    try:
        user = db.query(AppUser).filter(AppUser.username == credentials.username).first()
        if user:
            background_tasks.add_task(AchievementService.evaluate_achievements_background, user.id)
    except Exception:
        # do not block login on background scheduling failures
        pass

    return login_response.copy(update={"access_token": ""})


@router.get("/me", response_model=UserProfileResponse)
def get_current_user(
    current_user: UserProfileResponse = Depends(
        require_role_permissions(ALL_ROLES, {PERM_VIEW_ACHIEVEMENTS})
    ),
) -> UserProfileResponse:
    return current_user


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="access_token",
        secure=os.getenv("ENVIRONMENT") == "production",
        samesite="none" if os.getenv("ENVIRONMENT") == "production" else "lax",
    )
    return {"message": "Logout exitoso"}
