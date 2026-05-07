from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.auth.models import AppUser
from src.auth.schemas.login_request import LoginRequest
from src.auth.schemas.login_response import LoginResponse
from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.security import create_access_token, decode_access_token, verify_password
from src.persons.models.person import Person
from src.camps.models.camp import Camp


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

        person = db.query(Person).filter(Person.id == user.person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona no encontrada",
            )

        camp = db.query(Camp).filter(Camp.id == person.camp_id).first()
        if not camp:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campamento no encontrado",
        )

        access_token, expires_at = create_access_token(subject=user.username)
        return LoginResponse(access_token=access_token, expires_at=expires_at, camp_id=camp.id, camp_name=camp.name)

    @staticmethod
    def get_current_user_profile(db: Session, token: str) -> UserProfileResponse:
        try:
            payload = decode_access_token(token)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            ) from exc
        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        user = (
            db.query(AppUser)
            .filter(AppUser.username == username)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        person = db.query(Person).filter(Person.id == user.person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona no encontrada",
            )

        return UserProfileResponse(
            username=user.username,
            user_id=user.id,
            person_id=user.person_id,
            camp_id=person.camp_id,
        )
