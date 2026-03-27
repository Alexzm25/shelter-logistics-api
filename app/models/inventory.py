from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maximum_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
