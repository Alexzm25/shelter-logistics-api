from typing import Literal
from pydantic import BaseModel
from .score_breakdown_response import ScoreBreakdownResponse


class AILogSummaryResponse(BaseModel):
    id: int
    full_name: str
    ai_decision: Literal["APROBADO", "RECHAZADO"]
    human_decision: Literal["INGRESO_PERMITIDO", "INGRESO_RECHAZADO"]
    human_override: bool
    score: int
    explanation: str
    suggested_profession: str
    score_breakdown: ScoreBreakdownResponse
    applied_rules: list[str]
