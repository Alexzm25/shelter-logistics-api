from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class InventoryResource(Base):
    __tablename__ = "inventory_resource"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    minimum_stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), nullable=False)
