from datetime import datetime

from pydantic import BaseModel, Field


class CreateExplorationRequest(BaseModel):
    start_date: datetime
    estimated_days: int = Field(..., ge=1)
    extra_days: int = Field(..., ge=0)
    ration_per_person: int = Field(..., ge=1)
    max_extra_days: int = Field(..., ge=0)
    member_ids: list[int] = Field(..., min_length=1)


class CreateExplorationResponse(BaseModel):
    message: str
    exploration_id: int