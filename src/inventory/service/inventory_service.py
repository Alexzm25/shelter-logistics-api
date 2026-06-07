from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.camps.models.camp import Camp
from src.core.inventory_utils import resolve_alert_level
from src.inventory.enums.resource_category_enum import ResourceCategoryEnum
from src.inventory.schemas.inventory_item_response import InventoryItemResponse
from src.inventory.schemas.internal_movement_response import InternalMovementResponse
from src.inventory.models import Inventory, InventoryResource, Resource
from src.inventory.models.inventory_movement import InventoryMovement
from src.inventory.enums.movement_type_enum import MovementTypeEnum

class InventoryService:

    @staticmethod
    def get_inventory_by_camp(
        db: Session,
        camp_id: int,
        category: ResourceCategoryEnum | None = None,
    ) -> list[InventoryItemResponse]:
        _, items = InventoryService.get_inventory_by_camp_paginated(
            db, camp_id, page=1, size=None, category=category
        )
        return items

    @staticmethod
    def get_inventory_by_camp_paginated(
        db: Session,
        camp_id: int,
        page: int = 1,
        size: int | None = 10,
        category: ResourceCategoryEnum | None = None,
    ) -> tuple[int, list[InventoryItemResponse]]:
        camp = db.query(Camp).filter(Camp.id == camp_id).first()

        if not camp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camp {camp_id} not found",
            )

        base_query = (
            db.query(InventoryResource, Resource)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .join(Resource, Resource.id == InventoryResource.resource_id)
            .filter(Inventory.camp_id == camp_id)
        )

        if category is not None:
            base_query = base_query.filter(Resource.category == category)

        total = base_query.count()

        query = base_query.order_by(Resource.name.asc())

        if size is not None:
            query = query.offset((page - 1) * size).limit(size)

        rows = query.all()

        items: list[InventoryItemResponse] = []

        for inventory_resource, resource in rows:
            alert_level = resolve_alert_level(
                inventory_resource.quantity,
                inventory_resource.minimum_stock_level,
            )

            items.append(
                InventoryItemResponse(
                    id=inventory_resource.id,
                    code=f"RES-{resource.id:03d}",
                    name=resource.name,
                    stock=inventory_resource.quantity,
                    minimum_stock_level=inventory_resource.minimum_stock_level,
                    category=resource.category.value,
                    alert_level=alert_level,
                )
            )

        return total, items

    @staticmethod
    def get_internal_movements_paginated(
        db: Session,
        camp_id: int,
        page: int = 1,
        size: int = 10,
    ) -> tuple[int, list[InternalMovementResponse]]:
        base_query = (
            db.query(InventoryMovement, Resource)
            .join(InventoryResource, InventoryResource.id == InventoryMovement.inventory_resource_id)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .join(Resource, Resource.id == InventoryResource.resource_id)
            .filter(
                Inventory.camp_id == camp_id,
                InventoryMovement.movement_type == MovementTypeEnum.SALIDA,
            )
        )

        total = base_query.count()

        rows = (
            base_query
            .order_by(InventoryMovement.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        items: list[InternalMovementResponse] = []
        for movement, resource in rows:
            items.append(
                InternalMovementResponse(
                    id=movement.id,
                    created_at=movement.created_at,
                    quantity=movement.quantity,
                    resource_name=resource.name,
                    resource_category=resource.category.value if hasattr(resource.category, 'value') else resource.category,
                )
            )

        return total, items
