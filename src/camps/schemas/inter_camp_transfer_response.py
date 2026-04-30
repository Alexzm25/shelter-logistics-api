from typing import Literal

from pydantic import BaseModel


class InterCampTransferResponse(BaseModel):
    id: int
    origin: str
    destination: str
    resource: str
    quantity: int
    status: Literal["pending", "approved", "rejected", "in-transit"]
    scheduled_date: str
    is_resource_transfer: bool
    approved_by: str
