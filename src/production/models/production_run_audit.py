from sqlalchemy import DateTime, ForeignKey, Integer, JSON, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class ProductionRunAudit(Base):
    __tablename__ = "production_run_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    executed_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    camp_id: Mapped[int] = mapped_column(ForeignKey("camp.id"), nullable=False)
    resources_produced: Mapped[list[dict[str, int | str]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
