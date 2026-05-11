"""Re-export de esquemas de `persons` para compatibilidad.

Cada clase ahora vive en su propio módulo dentro de
`src/persons/schemas/`. Este archivo mantiene las importaciones
anteriores funcionando mediante reexportación.
"""

from .candidate_input import CandidateInput
from .score_breakdown_response import ScoreBreakdownResponse
from .evaluation_response import EvaluationResponse
from .evaluate_candidate_request import EvaluateCandidateRequest
from .register_candidate_request import RegisterCandidateRequest
from .profession_option_response import ProfessionOptionResponse
from .person_summary_response import PersonSummaryResponse
from .ai_log_summary_response import AILogSummaryResponse
from .dashboard_response import DashboardResponse
from .register_candidate_response import RegisterCandidateResponse
from .update_person_request import UpdatePersonRequest
from .update_person_response import UpdatePersonResponse
from .update_person_status_request import UpdatePersonStatusRequest
from .update_person_status_response import UpdatePersonStatusResponse
from .temporary_reassignment_request import TemporaryReassignmentRequest
from .temporary_reassignment_response import TemporaryReassignmentResponse

__all__ = [
    "CandidateInput",
    "ScoreBreakdownResponse",
    "EvaluationResponse",
    "EvaluateCandidateRequest",
    "RegisterCandidateRequest",
    "ProfessionOptionResponse",
    "PersonSummaryResponse",
    "AILogSummaryResponse",
    "DashboardResponse",
    "RegisterCandidateResponse",
    "UpdatePersonRequest",
    "UpdatePersonResponse",
    "UpdatePersonStatusRequest",
    "UpdatePersonStatusResponse",
    "TemporaryReassignmentRequest",
    "TemporaryReassignmentResponse",
]
