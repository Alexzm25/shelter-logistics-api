from pydantic import BaseModel


class WorkerRequestItemCreate(BaseModel):
    inventory_resource_id: int
    quantity: int


class WorkerRequestCreate(BaseModel):
    items: list[WorkerRequestItemCreate]
    reason: str | None = None
