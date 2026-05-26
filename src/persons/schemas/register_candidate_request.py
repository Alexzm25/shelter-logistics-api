from typing import Literal
from pydantic import BaseModel
from .candidate_input import CandidateInput


class RegisterCandidateRequest(BaseModel):
    candidate: CandidateInput
    human_decision: Literal["PERMITIR_INGRESO", "RECHAZAR_INGRESO"]
    password: str
    username: str | None = None
    selected_profession: str | None = None
