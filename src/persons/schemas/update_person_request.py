from pydantic import BaseModel, Field


class UpdatePersonRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=30)
    last_name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=120)
    background_info: str = Field(min_length=1)
    weight: float = Field(ge=0)
    height: float = Field(ge=0)
    id_card: str | None = None
    photo_url: str | None = None
