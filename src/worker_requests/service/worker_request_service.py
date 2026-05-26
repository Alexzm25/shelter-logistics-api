from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.inventory.models import InventoryResource, InventoryMovement
from src.inventory.enums import MovementTypeEnum
from src.worker_requests.models.worker_request import WorkerRequest
from src.worker_requests.models.worker_request_item import WorkerRequestItem


class WorkerRequestService:
    @staticmethod
    def create_request(db: Session, current_user, payload) -> list[dict]:
        if not payload.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud de recursos debe incluir items.",
            )

        request = WorkerRequest(camp_id=current_user.camp_id, worker_person_id=current_user.person_id, request_status_id=0)
        db.add(request)
        db.flush()

        created_items = []
        for item in payload.items:
            inv_res = db.query(InventoryResource).filter(InventoryResource.id == item.inventory_resource_id).first()
            if not inv_res:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso de inventario no encontrado.")

            wr_item = WorkerRequestItem(
                worker_request_id=request.id,
                inventory_resource_id=inv_res.id,
                quantity=item.quantity,
                resource_name=None,
            )
            db.add(wr_item)
            created_items.append({
                "id": wr_item.id,
                "worker_request_id": request.id,
                "inventory_resource_id": inv_res.id,
                "quantity": item.quantity,
            })

        db.commit()
        return created_items

    @staticmethod
    def list_requests(db: Session, camp_id: int) -> list[dict]:
        # return flattened items for client
        rows = (
            db.query(WorkerRequestItem, WorkerRequest)
            .join(WorkerRequest, WorkerRequest.id == WorkerRequestItem.worker_request_id)
            .filter(WorkerRequest.camp_id == camp_id)
            .order_by(WorkerRequest.created_at.desc())
            .all()
        )

        result = []
        for item, request in rows:
            result.append(
                {
                    "id": item.id,
                    "request_id": request.id,
                    "worker_person_id": request.worker_person_id,
                    "inventory_resource_id": item.inventory_resource_id,
                    "quantity": item.quantity,
                    "request_status": "PENDIENTE",
                    "created_at": request.created_at.isoformat(),
                }
            )

        return result

    @staticmethod
    def approve_request(db: Session, camp_id: int, request_item_id: int):
        # Approve a single item request: subtract stock and record movement
        item = db.query(WorkerRequestItem).filter(WorkerRequestItem.id == request_item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada.")

        inv_res = db.query(InventoryResource).filter(InventoryResource.id == item.inventory_resource_id).first()
        if not inv_res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso de inventario no encontrado.")

        if inv_res.quantity < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente.")

        inv_res.quantity = inv_res.quantity - item.quantity
        movement = InventoryMovement(quantity=item.quantity, inventory_resource_id=inv_res.id, movement_type=MovementTypeEnum.SALIDA)
        db.add(movement)
        db.commit()

    @staticmethod
    def reject_request(db: Session, request_item_id: int):
        item = db.query(WorkerRequestItem).filter(WorkerRequestItem.id == request_item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada.")
        # nothing to do for rejection except maybe mark status; simplified for now
        return
