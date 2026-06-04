from typing import Literal

from pydantic import BaseModel


class WorkerRequestResponse(BaseModel):
    id: int
    worker_name: str | None = None
    worker_role: str | None = None
    request_type: Literal["RESOURCE_REQUEST", "QUOTA_SHORTFALL"] = "RESOURCE_REQUEST"
    resource_name: str | None = None
    quantity: int
    request_status: str
    created_at: str
    reason: str | None = None
    rejection_reason: str | None = None
    camp_name: str | None = None
