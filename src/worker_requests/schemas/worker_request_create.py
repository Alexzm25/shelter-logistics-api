from typing import Literal

from pydantic import BaseModel

from src.worker_requests.schemas.worker_request_item_create import WorkerRequestItemCreate


class WorkerRequestCreate(BaseModel):
    request_type: Literal["RESOURCE_REQUEST", "QUOTA_SHORTFALL"] = "RESOURCE_REQUEST"
    items: list[WorkerRequestItemCreate] = []
    inventory_resource_id: int | None = None
    quantity: int | None = None
    reason: str | None = None
