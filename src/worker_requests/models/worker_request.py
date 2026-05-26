from sqlalchemy import DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class WorkerRequest(Base):
    __tablename__ = "worker_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
    worker_person_id: Mapped[int] = mapped_column(ForeignKey("person.id"), nullable=False)
    request_status_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
