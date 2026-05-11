from pydantic import BaseModel
from .person_summary_response import PersonSummaryResponse


class TemporaryReassignmentResponse(BaseModel):
    person: PersonSummaryResponse
    message: str = "Reasignacion temporal actualizada correctamente"
