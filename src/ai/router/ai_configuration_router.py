from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.ai.schemas.ai_configuration_schema import (
    AIConfigurationCreate,
    AIConfigurationResponse,
    AIConfigurationUpdate,
)
from src.ai.service.ai_configuration_service import AIConfigurationService
from src.core.database import get_db

router = APIRouter(prefix="/ai/configurations", tags=["AI Configuration"])


@router.post("", response_model=AIConfigurationResponse, status_code=201)
def create_configuration(
    payload: AIConfigurationCreate,
    db: Session = Depends(get_db),
) -> AIConfigurationResponse:
    return AIConfigurationService.create(db, payload)


@router.get("", response_model=list[AIConfigurationResponse])
def list_configurations(
    db: Session = Depends(get_db),
) -> list[AIConfigurationResponse]:
    return AIConfigurationService.get_all(db)


@router.get("/{config_id}", response_model=AIConfigurationResponse)
def get_configuration(
    config_id: int,
    db: Session = Depends(get_db),
) -> AIConfigurationResponse:
    return AIConfigurationService.get_by_id(db, config_id)


@router.put("/{config_id}", response_model=AIConfigurationResponse)
def update_configuration(
    config_id: int,
    payload: AIConfigurationUpdate,
    db: Session = Depends(get_db),
) -> AIConfigurationResponse:
    return AIConfigurationService.update(db, config_id, payload)


@router.delete("/{config_id}", status_code=204)
def delete_configuration(
    config_id: int,
    db: Session = Depends(get_db),
) -> None:
    AIConfigurationService.delete(db, config_id)
