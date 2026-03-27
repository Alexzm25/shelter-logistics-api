from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProfessionAssignment(Base):
    __tablename__ = "profession_assignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    is_main_profession: Mapped[bool] = mapped_column(Boolean, nullable=False)
    profession_id: Mapped[int] = mapped_column(ForeignKey("profession.id"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("person.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
