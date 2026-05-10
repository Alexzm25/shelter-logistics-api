from pydantic import BaseModel


class CampOptionResponse(BaseModel):
    id: int
    name: str
    location: str
