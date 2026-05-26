from pydantic import BaseModel


class WorkerRequestItemResponse(BaseModel):
    id: int
    worker_request_id: int
    inventory_resource_id: int
    resource_name: str | None = None
    quantity: int


class WorkerRequestResponse(BaseModel):
    id: int
    worker_name: str | None = None
    worker_role: str | None = None
    resource_name: str | None = None
    quantity: int
    request_status: str
    created_at: str
    reason: str | None = None
    camp_name: str | None = None
