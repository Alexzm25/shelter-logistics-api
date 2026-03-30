from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class TransferResource(Base):
    __tablename__ = "transfer_resource"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transfer_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), nullable=False)
    request_id: Mapped[int] = mapped_column(ForeignKey("transfer_request.id"), nullable=False)
