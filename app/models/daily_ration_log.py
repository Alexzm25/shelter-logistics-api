from sqlalchemy import DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DailyRationLog(Base):
    __tablename__ = "daily_ration_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persons_fed: Mapped[int] = mapped_column(Integer, nullable=False)
    executed_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    camp_id: Mapped[int | None] = mapped_column(ForeignKey("camp.id"), nullable=True)
