from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProductionLog(Base):
    __tablename__ = "production_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actual_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("person.id"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), nullable=False)
    profession_id: Mapped[int] = mapped_column(ForeignKey("profession.id"), nullable=False)
