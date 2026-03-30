from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class UserAchievement(Base):
    __tablename__ = "user_achievement"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("app_user.id"), primary_key=True)
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievement.id"), primary_key=True
    )
    is_unlocked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    unlocked_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
