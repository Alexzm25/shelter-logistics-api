from pydantic import BaseModel

from src.inventory.enums import ResourceCategoryEnum


class ResourceAvailabilityResponse(BaseModel):
    resource_id: int
    resource_name: str
    category: ResourceCategoryEnum
    available: int
