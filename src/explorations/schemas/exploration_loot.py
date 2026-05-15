from pydantic import BaseModel, Field


class ExplorationLootItemRequest(BaseModel):
    resource_id: int = Field(..., ge=1)
    quantity: int = Field(..., gt=0)


class RegisterExplorationLootRequest(BaseModel):
    exploration_id: int = Field(..., ge=1)
    resource_id: int = Field(..., ge=1)
    quantity: int = Field(..., gt=0)


class ReturnExplorationRequest(BaseModel):
    exploration_id: int = Field(..., ge=1)
    items: list[ExplorationLootItemRequest] = Field(..., min_length=1)


class RegisterExplorationLootResponse(BaseModel):
    message: str
    loot_id: int