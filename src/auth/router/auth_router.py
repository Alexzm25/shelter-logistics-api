from datetime import datetime
import os

from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.auth.schemas.login_request import LoginRequest
from src.auth.schemas.login_response import LoginResponse
from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.auth_service import AuthService
from src.auth.service.authorization import ALL_ROLES, PERM_VIEW_ACHIEVEMENTS, require_role_permissions
from src.auth.service.security import create_access_token, create_refresh_token, decode_refresh_token
from src.achievement.service.achievement_service import AchievementService
from src.auth.models import AppUser
from src.core.database import get_db
from src.core.settings import settings


router = APIRouter(prefix="/auth", tags=["Auth"])


def _cookie_base() -> dict[str, object]:
    is_production = os.getenv("ENVIRONMENT") == "production"
    return {
        "httponly": True,
        "secure": is_production,
        "samesite": "none" if is_production else "lax",
    }


def _set_auth_cookies(response: Response, username: str) -> datetime:
    access_token, expires_at = create_access_token(subject=username)
    refresh_token, _ = create_refresh_token(subject=username)

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        **_cookie_base(),
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.jwt_refresh_token_expire_days * 86400,
        **_cookie_base(),
    )

    return expires_at


def _delete_auth_cookies(response: Response) -> None:
    base = _cookie_base()
    response.delete_cookie(key="access_token", **base)
    response.delete_cookie(key="refresh_token", **base)


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    login_response = AuthService.login(db, credentials)

    expires_at = _set_auth_cookies(response, credentials.username)

    # schedule achievements evaluation in background using a fresh session
    try:
        user = db.query(AppUser).filter(AppUser.username == credentials.username).first()
        if user:
            background_tasks.add_task(AchievementService.evaluate_achievements_background, user.id)
    except Exception:
        # do not block login on background scheduling failures
        pass

    return login_response.copy(update={"access_token": "", "expires_at": expires_at})


@router.get("/me", response_model=UserProfileResponse)
def get_current_user(
    current_user: UserProfileResponse = Depends(
        require_role_permissions(ALL_ROLES, {PERM_VIEW_ACHIEVEMENTS})
    ),
) -> UserProfileResponse:
    return current_user


@router.post("/refresh")
def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
) -> dict[str, str]:
    if not refresh_token or not refresh_token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de actualización",
        )

    try:
        payload = decode_refresh_token(refresh_token.strip())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de actualización inválido o expirado",
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de actualización inválido",
        )

    _set_auth_cookies(response, username)
    return {"message": "Token actualizado"}


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    _delete_auth_cookies(response)
    return {"message": "Logout exitoso"}
