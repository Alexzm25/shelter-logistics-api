from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class TransferParticipant(Base):
    __tablename__ = "transfer_participants"

    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("person.id"), primary_key=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transfer_request.id"), primary_key=True
    )
    is_transfer_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
