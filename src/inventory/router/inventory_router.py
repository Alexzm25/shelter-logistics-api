from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.authorization import (
    PERM_VIEW_INVENTORY_FULL,
    PERM_VIEW_MEDICINES,
    PERM_VIEW_SEEDS,
    ROLE_ADMIN,
    ROLE_RESOURCES,
    ROLE_WORKER,
    enforce_role_permissions,
    get_current_user_from_token,
)
from src.core.database import get_db
from src.inventory.enums.resource_category_enum import ResourceCategoryEnum
from src.inventory.schemas import InventoryItemResponse
from src.inventory.service.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get(
    "/camp/{camp_id}",
    response_model=list[InventoryItemResponse],
)
def get_inventory_by_camp(
    camp_id: int = Path(..., ge=1),
    category: ResourceCategoryEnum | None = Query(default=None),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[InventoryItemResponse]:
    if current_user.role_name in {ROLE_ADMIN, ROLE_RESOURCES}:
        enforce_role_permissions(
            db,
            current_user,
            {ROLE_ADMIN, ROLE_RESOURCES},
            {PERM_VIEW_INVENTORY_FULL},
        )
        return InventoryService.get_inventory_by_camp(db, camp_id, category)

    if current_user.role_name == ROLE_WORKER:
        profession_name = (current_user.profession_name or "").upper()
        if profession_name == "AGRICULTOR":
            enforce_role_permissions(
                db,
                current_user,
                {ROLE_WORKER},
                {PERM_VIEW_SEEDS},
            )
            return InventoryService.get_inventory_by_camp(
                db,
                camp_id,
                ResourceCategoryEnum.SEMILLAS,
            )
        if profession_name == "MEDICO":
            enforce_role_permissions(
                db,
                current_user,
                {ROLE_WORKER},
                {PERM_VIEW_MEDICINES},
            )
            return InventoryService.get_inventory_by_camp(
                db,
                camp_id,
                ResourceCategoryEnum.MEDICINAS,
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profesion no autorizada",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Rol no autorizado",
    )