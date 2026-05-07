from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.camps.models.camp import Camp
from src.inventory.schemas.inventory_item_response import InventoryItemResponse
from src.inventory.models import Inventory, InventoryResource, Resource

class InventoryService:
    LOW_STOCK_MULTIPLIER = 1.5

    @staticmethod
    def get_inventory_by_camp(
        db: Session,
        camp_id: int,
    ) -> list[InventoryItemResponse]:
        camp = db.query(Camp).filter(Camp.id == camp_id).first()

        if not camp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camp {camp_id} not found",
            )

        rows = (
            db.query(InventoryResource, Resource)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .join(Resource, Resource.id == InventoryResource.resource_id)
            .filter(Inventory.camp_id == camp_id)
            .order_by(Resource.name.asc())
            .all()
        )

        items: list[InventoryItemResponse] = []

        for inventory_resource, resource in rows:
            alert_level = InventoryService._resolve_alert_level(
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

        return items

    @staticmethod
    def _resolve_alert_level(
        quantity: int,
        minimum_stock_level: int,
    ) -> str:
        if quantity <= minimum_stock_level:
            return "critical"

        if (
            quantity
            <= minimum_stock_level * InventoryService.LOW_STOCK_MULTIPLIER
        ):
            return "warning"

        return "normal"