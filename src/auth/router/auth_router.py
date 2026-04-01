from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.schemas.login_request import LoginRequest
from src.auth.schemas.login_response import LoginResponse
from src.auth.service.auth_service import AuthService
from src.core.database import get_db


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    return AuthService.login(db, credentials)
