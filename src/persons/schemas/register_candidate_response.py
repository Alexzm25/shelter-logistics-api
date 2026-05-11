from pydantic import BaseModel
from .evaluation_response import EvaluationResponse
from .person_summary_response import PersonSummaryResponse
from .ai_log_summary_response import AILogSummaryResponse


class RegisterCandidateResponse(BaseModel):
    evaluation: EvaluationResponse
    created_person: PersonSummaryResponse | None
    created_ai_log: AILogSummaryResponse
    message: str = "Persona registrada correctamente"
