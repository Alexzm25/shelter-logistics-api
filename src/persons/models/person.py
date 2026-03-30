from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base
from src.persons.enums import CurrentStatusEnum, HealthStatusEnum


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    background_info: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    height: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
    current_status: Mapped[CurrentStatusEnum] = mapped_column(
        Enum(CurrentStatusEnum, name="current_status_enum"), nullable=False
    )
    health_status: Mapped[HealthStatusEnum] = mapped_column(
        Enum(HealthStatusEnum, name="health_status_enum"), nullable=False
    )
    camp_entry_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(250), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    id_card: Mapped[str] = mapped_column(String(250), nullable=False)
