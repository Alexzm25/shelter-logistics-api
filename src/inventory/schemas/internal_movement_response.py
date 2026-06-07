from datetime import datetime

from pydantic import BaseModel


class InternalMovementResponse(BaseModel):
    id: int
    created_at: datetime
    quantity: int
    resource_name: str
    resource_category: str
