from pydantic import BaseModel
from .person_summary_response import PersonSummaryResponse


class UpdatePersonStatusResponse(BaseModel):
    person: PersonSummaryResponse
    message: str = "Estado de persona actualizado correctamente"
