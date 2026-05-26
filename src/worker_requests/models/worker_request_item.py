from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class WorkerRequestItem(Base):
    __tablename__ = "worker_request_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker_request_id: Mapped[int] = mapped_column(ForeignKey("worker_request.id"), nullable=False)
    inventory_resource_id: Mapped[int] = mapped_column(ForeignKey("inventory_resource.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
