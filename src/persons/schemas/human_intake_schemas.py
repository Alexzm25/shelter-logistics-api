from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CandidateInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=30)
    last_name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=120)
    background_info: str = Field(min_length=1)
    weight: float = Field(ge=0)
    height: float = Field(ge=0)
    id_card: str | None = None
    photo_url: str | None = None
    camp_id: int = Field(ge=1)


class ScoreBreakdownResponse(BaseModel):
    resilience: int
    medical_experience: int
    defense_experience: int
    context: int


class EvaluationResponse(BaseModel):
    decision: Literal["APROBADO", "RECHAZADO"]
    score: int
    explanation: str
    suggested_profession: str
    score_breakdown: ScoreBreakdownResponse
    applied_rules: list[str]


class EvaluateCandidateRequest(BaseModel):
    candidate: CandidateInput


class RegisterCandidateRequest(BaseModel):
    candidate: CandidateInput
    human_decision: Literal["PERMITIR_INGRESO", "RECHAZAR_INGRESO"]
    selected_profession: str | None = None


class ProfessionOptionResponse(BaseModel):
    name: str


class PersonSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    age: int
    health_status: Literal["SANO", "HERIDO", "ENFERMO", "MUERTO"]
    profession: str
    temporary_reassignment: str | None = None
    weight: float
    height: float
    camp_id: int
    id_card: str | None
    photo_url: str | None
    background_info: str


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


class DashboardResponse(BaseModel):
    people: list[PersonSummaryResponse]
    ai_logs: list[AILogSummaryResponse]


class RegisterCandidateResponse(BaseModel):
    evaluation: EvaluationResponse
    created_person: PersonSummaryResponse | None
    created_ai_log: AILogSummaryResponse
