from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.inventory.schemas import InventoryItemResponse
from src.inventory.service.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get(
    "/camp/{camp_id}",
    response_model=list[InventoryItemResponse],
)
def get_inventory_by_camp(
    camp_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> list[InventoryItemResponse]:
    return InventoryService.get_inventory_by_camp(db, camp_id)