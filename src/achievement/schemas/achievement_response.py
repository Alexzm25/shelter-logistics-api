from typing import Optional

from pydantic import BaseModel


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_unlocked: bool
    unlocked_at: Optional[str] = None

    class Config:
        orm_mode = True
