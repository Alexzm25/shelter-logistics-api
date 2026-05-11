from pydantic import BaseModel, Field


class TemporaryReassignmentRequest(BaseModel):
    profession_name: str = Field(min_length=1, max_length=50)
    reason: str = Field(min_length=1, max_length=100)
