from sqlalchemy import DateTime, Enum, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base
from src.inventory.enums import MovementTypeEnum


class InventoryMovement(Base):
    __tablename__ = "inventory_movement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    inventory_resource_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_resource.id"), nullable=False
    )
    movement_type: Mapped[MovementTypeEnum] = mapped_column(
        Enum(MovementTypeEnum, name="movement_type_enum"), nullable=False
    )
    transfer_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("transfer_request.id"), nullable=True
    )
