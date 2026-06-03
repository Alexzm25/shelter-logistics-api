from datetime import datetime

from pydantic import BaseModel, Field


class AIConfigurationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    prompt: str = Field(min_length=1)
    rules: str | None = None
    is_active: bool = True


class AIConfigurationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    prompt: str | None = Field(default=None, min_length=1)
    rules: str | None = None
    is_active: bool | None = None


class AIConfigurationResponse(BaseModel):
    id: int
    name: str
    description: str | None
    prompt: str
    rules: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
