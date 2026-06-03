from pydantic import BaseModel

from src.worker_requests.schemas.worker_request_item_create import WorkerRequestItemCreate


class WorkerRequestCreate(BaseModel):
    items: list[WorkerRequestItemCreate]
    reason: str | None = None
