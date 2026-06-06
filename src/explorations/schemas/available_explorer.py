from datetime import date

from pydantic import BaseModel


class AvailableExplorerResponse(BaseModel):
    id: int
    full_name: str
    birth_date: date
    health_status: str
    current_status: str