from sqlalchemy import DateTime, Enum, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base
from src.explorations.enums import ExplorationStatusEnum


class Exploration(Base):
    __tablename__ = "exploration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    return_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exploration_status: Mapped[ExplorationStatusEnum] = mapped_column(
        Enum(ExplorationStatusEnum, name="exploration_status_enum"), nullable=False
    )
    camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
    extra_days: Mapped[int] = mapped_column(Integer, nullable=False)
    ration_per_person: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    max_extra_days: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    estimated_days: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
