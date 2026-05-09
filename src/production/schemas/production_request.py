from pydantic import BaseModel, Field

class RegisterProductionRequest(BaseModel):
    resource_id: int = Field(ge=1)
    actual_quantity: int = Field(gt=0)