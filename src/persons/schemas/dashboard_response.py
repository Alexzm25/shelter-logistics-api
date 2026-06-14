from pydantic import BaseModel
from .person_summary_response import PersonSummaryResponse
from .ai_log_summary_response import AILogSummaryResponse
from .health_summary_response import HealthSummaryResponse


class DashboardResponse(BaseModel):
    people: list[PersonSummaryResponse]
    ai_logs: list[AILogSummaryResponse]
    total_people: int
    health_summary: HealthSummaryResponse
