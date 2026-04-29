from typing import Literal

from pydantic import BaseModel


class InventoryItemResponse(BaseModel):
    id: int
    code: str
    name: str
    stock: int
    minimum_stock_level: int
    category: Literal["ALIMENTO", "BEBIDAS", "SEMILLAS", "MEDICINAS"]
    alert_level: Literal["critical", "warning", "normal"]
