from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.enums import ResourceCategoryEnum


class Resource(Base):
    __tablename__ = "resource"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    category: Mapped[ResourceCategoryEnum] = mapped_column(
        Enum(ResourceCategoryEnum, name="resource_category_enum"), nullable=False
    )
