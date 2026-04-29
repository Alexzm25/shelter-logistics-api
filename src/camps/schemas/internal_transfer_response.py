from typing import Literal

from pydantic import BaseModel


class InternalTransferResponse(BaseModel):
    id: int
    timestamp: str
    resource: str
    category: Literal["ALIMENTO", "BEBIDAS", "SEMILLAS", "MEDICINAS"]
    direction: Literal["move", "out", "in"]
    quantity: int
    from_zone: str
    to_zone: str
    authorized_by: str
