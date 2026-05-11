from typing import Literal
from pydantic import BaseModel
from .score_breakdown_response import ScoreBreakdownResponse


class EvaluationResponse(BaseModel):
    decision: Literal["APROBADO", "RECHAZADO"]
    score: int
    explanation: str
    suggested_profession: str
    score_breakdown: ScoreBreakdownResponse
    applied_rules: list[str]
