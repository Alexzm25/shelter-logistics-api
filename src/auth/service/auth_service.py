from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.auth.models import AppUser
from src.auth.schemas.login_request import LoginRequest
from src.auth.schemas.login_response import LoginResponse
from src.auth.service.security import create_access_token, verify_password


class AuthService:
    @staticmethod
    def login(db: Session, credentials: LoginRequest) -> LoginResponse:
        user = (
            db.query(AppUser)
            .filter(AppUser.username == credentials.username)
            .first()
        )

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        access_token, expires_at = create_access_token(subject=user.username)
        return LoginResponse(access_token=access_token, expires_at=expires_at)
