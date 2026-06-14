from pydantic import BaseModel


class HealthSummaryResponse(BaseModel):
    total: int
    healthy: int
    injured: int
    sick: int
    dead: int
