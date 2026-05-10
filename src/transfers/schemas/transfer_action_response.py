from pydantic import BaseModel


class TransferActionResponse(BaseModel):
    message: str
