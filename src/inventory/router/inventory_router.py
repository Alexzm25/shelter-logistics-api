from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from fastapi.responses import StreamingResponse
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
from src.core.realtime_events import inventory_events
from src.inventory.enums.resource_category_enum import ResourceCategoryEnum
from src.inventory.schemas import InventoryItemResponse
from src.inventory.service.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


def _inventory_event_stream(camp_ids: set[int]) -> Iterator[str]:
    for event in inventory_events.subscribe(camp_ids):
        if event.source == "heartbeat":
            yield ": heartbeat\n\n"
            continue
        yield event.to_sse()


@router.get("/events")
def stream_inventory_events(
    camp_id: int | None = Query(default=None, ge=1),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    selected_camp_id = camp_id or current_user.camp_id

    if selected_camp_id != current_user.camp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes consultar otro campamento",
        )

    if current_user.role_name in {ROLE_ADMIN, ROLE_RESOURCES}:
        enforce_role_permissions(
            db,
            current_user,
            {ROLE_ADMIN, ROLE_RESOURCES},
            {PERM_VIEW_INVENTORY_FULL},
        )
    elif current_user.role_name == ROLE_WORKER:
        if selected_camp_id != current_user.camp_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol no autorizado",
            )
        profession_name = (current_user.profession_name or "").upper()
        if profession_name == "AGRICULTOR":
            enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_VIEW_SEEDS})
        elif profession_name == "MEDICO":
            enforce_role_permissions(db, current_user, {ROLE_WORKER}, {PERM_VIEW_MEDICINES})
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profesion no autorizada",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )

    return StreamingResponse(
        _inventory_event_stream({selected_camp_id}),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/camp/{camp_id}",
    response_model=list[InventoryItemResponse],
)
def get_inventory_by_camp(
    response: Response,
    camp_id: int = Path(..., ge=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    category: ResourceCategoryEnum | None = Query(default=None),
    current_user: UserProfileResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
) -> list[InventoryItemResponse]:
    if camp_id != current_user.camp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes consultar otro campamento",
        )

    if current_user.role_name in {ROLE_ADMIN, ROLE_RESOURCES}:
        enforce_role_permissions(
            db,
            current_user,
            {ROLE_ADMIN, ROLE_RESOURCES},
            {PERM_VIEW_INVENTORY_FULL},
        )
        total, items = InventoryService.get_inventory_by_camp_paginated(
            db, camp_id, page, size, category
        )
        response.headers["X-Total-Count"] = str(total)
        return items

    if current_user.role_name == ROLE_WORKER:
        profession_name = (current_user.profession_name or "").upper()
        if profession_name == "AGRICULTOR":
            enforce_role_permissions(
                db,
                current_user,
                {ROLE_WORKER},
                {PERM_VIEW_SEEDS},
            )
            total, items = InventoryService.get_inventory_by_camp_paginated(
                db, camp_id, page, size, ResourceCategoryEnum.SEMILLAS
            )
            response.headers["X-Total-Count"] = str(total)
            return items
        if profession_name == "MEDICO":
            enforce_role_permissions(
                db,
                current_user,
                {ROLE_WORKER},
                {PERM_VIEW_MEDICINES},
            )
            total, items = InventoryService.get_inventory_by_camp_paginated(
                db, camp_id, page, size, ResourceCategoryEnum.MEDICINAS
            )
            response.headers["X-Total-Count"] = str(total)
            return items

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profesion no autorizada",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Rol no autorizado",
    )
