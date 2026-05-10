from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_REGISTER_PRODUCTION,
    ROLE_WORKER,
    enforce_role_permissions,
    get_current_user_from_token,
)
from src.core.database import get_db
from src.production.schemas.production_request import RegisterProductionRequest
from src.production.schemas.production_response import RegisterProductionResponse
from src.production.service.production_service import ProductionService


router = APIRouter(prefix="/production", tags=["Production"])


@router.post("/register", response_model=RegisterProductionResponse)
def register_production(
    payload: RegisterProductionRequest,
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> RegisterProductionResponse:
    enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_REGISTER_PRODUCTION})
    profession_name = (current_user.profession_name or "").upper()
    if profession_name != "AGRICULTOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profesion no autorizada",
        )
    return ProductionService.register_production(
        db=db,
        person_id=current_user.person_id,
        payload=payload,
    )