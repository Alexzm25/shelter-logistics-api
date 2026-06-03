from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.ai.models.ai_configuration import AIConfiguration
from src.ai.schemas.ai_configuration_schema import (
    AIConfigurationCreate,
    AIConfigurationUpdate,
)


class AIConfigurationService:
    @staticmethod
    def create(db: Session, payload: AIConfigurationCreate) -> AIConfiguration:
        existing = db.query(AIConfiguration).filter(
            AIConfiguration.name == payload.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A configuration with this name already exists.",
            )
        config = AIConfiguration(
            name=payload.name,
            description=payload.description,
            prompt=payload.prompt,
            rules=payload.rules,
            is_active=payload.is_active,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def get_all(db: Session) -> list[AIConfiguration]:
        return db.query(AIConfiguration).order_by(AIConfiguration.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, config_id: int) -> AIConfiguration:
        config = db.query(AIConfiguration).filter(
            AIConfiguration.id == config_id
        ).first()
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI Configuration not found.",
            )
        return config

    @staticmethod
    def update(
        db: Session, config_id: int, payload: AIConfigurationUpdate
    ) -> AIConfiguration:
        config = AIConfigurationService.get_by_id(db, config_id)
        if payload.name is not None:
            existing = db.query(AIConfiguration).filter(
                AIConfiguration.name == payload.name,
                AIConfiguration.id != config_id,
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A configuration with this name already exists.",
                )
            config.name = payload.name
        if payload.description is not None:
            config.description = payload.description
        if payload.prompt is not None:
            config.prompt = payload.prompt
        if payload.rules is not None:
            config.rules = payload.rules
        if payload.is_active is not None:
            config.is_active = payload.is_active
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def delete(db: Session, config_id: int) -> None:
        config = AIConfigurationService.get_by_id(db, config_id)
        db.delete(config)
        db.commit()
