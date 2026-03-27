from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProfessionProduction(Base):
    __tablename__ = "profession_production"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    production_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), nullable=False)
    profession_id: Mapped[int] = mapped_column(ForeignKey("profession.id"), nullable=False)
