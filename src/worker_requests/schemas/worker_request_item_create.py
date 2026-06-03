from pydantic import BaseModel


class WorkerRequestItemCreate(BaseModel):
    inventory_resource_id: int
    quantity: int
