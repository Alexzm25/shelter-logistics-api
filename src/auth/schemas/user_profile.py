from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    username: str
    user_id: int
    person_id: int
    camp_id: int
