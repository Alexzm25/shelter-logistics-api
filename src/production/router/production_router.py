from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.auth_service import AuthService
from src.core.database import get_db
from src.production.schemas.production_request import RegisterProductionRequest
from src.production.schemas.production_response import RegisterProductionResponse
from src.production.service.production_service import ProductionService


router = APIRouter(prefix="/production", tags=["Production"])


def get_current_user_from_token(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> UserProfileResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Falta el token de autorización",
        )

    token = authorization.replace("Bearer ", "", 1).strip()
    return AuthService.get_current_user_profile(db, token)


@router.post("/register", response_model=RegisterProductionResponse)
def register_production(
    payload: RegisterProductionRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> RegisterProductionResponse:
    return ProductionService.register_production(
        db=db,
        person_id=current_user.person_id,
        payload=payload,
    )