from pydantic import BaseModel


class ScoreBreakdownResponse(BaseModel):
    resilience: int
    medical_experience: int
    defense_experience: int
    context: int
