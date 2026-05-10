from pydantic import BaseModel

from src.transfers.schemas.transfer_request_create_resource import (
    TransferRequestCreateResource,
)


class TransferRequestCreate(BaseModel):
    to_camp_id: int
    is_resource_transfer: bool
    resources: list[TransferRequestCreateResource] = []
