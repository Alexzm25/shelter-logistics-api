from typing import Literal
from pydantic import BaseModel


class UpdatePersonStatusRequest(BaseModel):
    health_status: Literal["SANO", "HERIDO", "ENFERMO", "MUERTO"] | None = None
    current_status: Literal["TRABAJANDO", "EN EXPLORACIÓN", "TRASLADANDO RECURSOS", "LIBRE"] | None = None
