from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base
from src.ai.enums import AIDecisionEnum


class AILog(Base):
    __tablename__ = "ai_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    decision_reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    ai_decision: Mapped[AIDecisionEnum] = mapped_column(
        Enum(AIDecisionEnum, name="ai_decision_enum"), nullable=False
    )
    evaluation_context: Mapped[dict] = mapped_column(JSONB, nullable=False)
    camp_id: Mapped[int | None] = mapped_column(ForeignKey("camp.id"), nullable=True)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("person.id"), nullable=True)
    final_user_decision: Mapped[bool] = mapped_column(Boolean, nullable=False)
