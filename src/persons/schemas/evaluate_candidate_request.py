from pydantic import BaseModel
from .candidate_input import CandidateInput


class EvaluateCandidateRequest(BaseModel):
    candidate: CandidateInput
