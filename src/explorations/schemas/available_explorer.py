from pydantic import BaseModel


class AvailableExplorerResponse(BaseModel):
    id: int
    full_name: str
    age: int
    health_status: str
    current_status: str