from pydantic import BaseModel


class WorkerRequestItemResponse(BaseModel):
    id: int
    worker_request_id: int
    inventory_resource_id: int
    quantity: int
