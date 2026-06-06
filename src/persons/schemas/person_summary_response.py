from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict


class PersonSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    birth_date: date
    current_status: Literal["TRABAJANDO", "EN EXPLORACIÓN", "TRASLADANDO RECURSOS", "LIBRE"]
    health_status: Literal["SANO", "HERIDO", "ENFERMO", "MUERTO"]
    profession: str
    temporary_reassignment: str | None = None
    weight: float
    height: float
    camp_id: int
    id_card: str | None
    photo_url: str | None
    background_info: str
    is_active: bool
