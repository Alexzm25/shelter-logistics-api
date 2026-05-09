from pydantic import BaseModel

class RegisterProductionResponse(BaseModel):
    message: str