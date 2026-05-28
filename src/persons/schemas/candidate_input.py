from datetime import date

from pydantic import BaseModel, Field, validator


class CandidateInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=30)
    last_name: str = Field(min_length=1, max_length=50)
    birth_date: date
    background_info: str = Field(min_length=1)
    weight: float = Field(ge=0)
    height: float = Field(ge=0)
    id_card: str | None = None
    photo_url: str | None = None
    camp_id: int = Field(ge=1)

    @validator("birth_date")
    def birth_date_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("birth_date cannot be in the future")
        return v
