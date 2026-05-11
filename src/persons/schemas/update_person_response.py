from pydantic import BaseModel
from .person_summary_response import PersonSummaryResponse


class UpdatePersonResponse(BaseModel):
    person: PersonSummaryResponse
    message: str = "Persona editada correctamente"
