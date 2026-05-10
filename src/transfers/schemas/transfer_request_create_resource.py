from pydantic import BaseModel, Field


class TransferRequestCreateResource(BaseModel):
    resource_id: int
    transfer_amount: int = Field(gt=0)
