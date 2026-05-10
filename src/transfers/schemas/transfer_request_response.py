from datetime import date, datetime
from pydantic import BaseModel

from src.transfers.enums import RequestStatusEnum, TransferStatusEnum
from src.transfers.schemas.transfer_resource_response import TransferResourceResponse


class TransferRequestResponse(BaseModel):
    id: int
    from_camp_id: int
    from_camp_name: str
    to_camp_id: int
    to_camp_name: str
    request_status: RequestStatusEnum
    transfer_status: TransferStatusEnum | None = None
    created_at: datetime
    departure_date: date
    arrival_date: date | None = None
    authorized_by: str | None = None
    is_resource_transfer: bool
    resources: list[TransferResourceResponse] = []
