from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permission.id"), primary_key=True
    )
