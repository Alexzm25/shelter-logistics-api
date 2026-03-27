from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Profession(Base):
    __tablename__ = "profession"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_critical: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
