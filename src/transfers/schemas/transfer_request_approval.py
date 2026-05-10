from pydantic import BaseModel


class TransferRequestApproval(BaseModel):
    participant_ids: list[int] | None = None
