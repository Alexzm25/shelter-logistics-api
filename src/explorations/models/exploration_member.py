from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base import Base


class ExplorationMember(Base):
    __tablename__ = "exploration_member"

    person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person.id"), primary_key=True
    )
    exploration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exploration.id"), primary_key=True
    )
