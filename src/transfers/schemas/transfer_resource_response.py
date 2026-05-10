from pydantic import BaseModel


class TransferResourceResponse(BaseModel):
    resource_id: int
    resource_name: str
    transfer_amount: int
