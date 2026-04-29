from pydantic import BaseModel


class AchievementResponse(BaseModel):
    id: int
    title: str
    description: str
    unlocked_at: str
    icon: str
