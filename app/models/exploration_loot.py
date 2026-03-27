from sqlalchemy import Boolean, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ExplorationLoot(Base):
    __tablename__ = "exploration_loot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), nullable=False)
    exploration_id: Mapped[int] = mapped_column(ForeignKey("exploration.id"), nullable=False)
    is_added_to_inventory: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
