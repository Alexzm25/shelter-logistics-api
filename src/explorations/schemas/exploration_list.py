from datetime import datetime
from pydantic import BaseModel


class ExplorationListResponse(BaseModel):
    id: int
    start_date: datetime
    return_date: datetime | None
    exploration_status: str
    estimated_days: int
    extra_days: int
    team_count: int