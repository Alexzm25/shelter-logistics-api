from pydantic import BaseModel


class ProfessionOptionResponse(BaseModel):
    name: str
    is_critical: bool
