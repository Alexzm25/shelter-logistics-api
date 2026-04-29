from datetime import date

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base
from src.transfers.enums import RequestStatusEnum, TransferStatusEnum


class TransferRequest(Base):
    __tablename__ = "transfer_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    from_camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
    to_camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
    request_status: Mapped[RequestStatusEnum] = mapped_column(
        Enum(RequestStatusEnum, name="request_status_enum"), nullable=False
    )
    transfer_status: Mapped[TransferStatusEnum | None] = mapped_column(
        Enum(
            TransferStatusEnum,
            name="transfer_status_enum",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=True,
    )
    arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    authorized_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_resource_transfer: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
