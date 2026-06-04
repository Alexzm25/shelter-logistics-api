from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.camps.models.camp import Camp
from src.core.realtime_events import inventory_events
from src.inventory.enums import MovementTypeEnum
from src.inventory.models import Inventory, InventoryMovement, InventoryResource, Resource
from src.persons.models.person import Person
from src.persons.models.profession import Profession
from src.persons.models.profession_assignment import ProfessionAssignment
from src.worker_requests.models.worker_request import WorkerRequest
from src.worker_requests.models.worker_request_item import WorkerRequestItem
from src.worker_requests.schemas.worker_request_item_create import WorkerRequestItemCreate


STATUS_PENDING = 0
STATUS_APPROVED = 1
STATUS_REJECTED = 2

REQUEST_TYPE_RESOURCE = "RESOURCE_REQUEST"
REQUEST_TYPE_QUOTA_SHORTFALL = "QUOTA_SHORTFALL"

STATUS_LABELS = {
    STATUS_PENDING: "PENDIENTE",
    STATUS_APPROVED: "APROBADO",
    STATUS_REJECTED: "RECHAZADO",
}

REQUEST_TYPE_LABELS = {
    REQUEST_TYPE_RESOURCE: REQUEST_TYPE_RESOURCE,
    REQUEST_TYPE_QUOTA_SHORTFALL: REQUEST_TYPE_QUOTA_SHORTFALL,
}


class WorkerRequestService:
    @staticmethod
    def create_request(db: Session, current_user, payload) -> list[dict]:
        request_type = WorkerRequestService._normalize_request_type(payload.request_type)
        items = WorkerRequestService._normalize_items(payload, request_type)

        if request_type == REQUEST_TYPE_QUOTA_SHORTFALL and not (payload.reason or "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El incumplimiento de cuota debe incluir un motivo.",
            )

        request = WorkerRequest(
            camp_id=current_user.camp_id,
            worker_person_id=current_user.person_id,
            request_status_id=STATUS_PENDING,
            request_type=request_type,
            reason=(payload.reason or "").strip() or None,
        )
        db.add(request)
        db.flush()

        created_items = []
        for item in items:
            inv_res = WorkerRequestService._get_camp_inventory_resource(
                db,
                current_user.camp_id,
                item.inventory_resource_id,
            )

            wr_item = WorkerRequestItem(
                worker_request_id=request.id,
                inventory_resource_id=inv_res.id,
                quantity=item.quantity,
            )
            db.add(wr_item)
            db.flush()
            created_items.append(
                {
                    "id": wr_item.id,
                    "worker_request_id": request.id,
                    "inventory_resource_id": inv_res.id,
                    "quantity": item.quantity,
                    "request_type": request_type,
                }
            )

        db.commit()
        return created_items

    @staticmethod
    def list_requests(
        db: Session,
        camp_id: int,
        worker_person_id: int | None = None,
    ) -> list[dict]:
        rows = (
            db.query(
                WorkerRequestItem,
                WorkerRequest,
                InventoryResource,
                Resource,
                Person,
                Profession,
                Camp,
            )
            .join(WorkerRequest, WorkerRequest.id == WorkerRequestItem.worker_request_id)
            .join(InventoryResource, InventoryResource.id == WorkerRequestItem.inventory_resource_id)
            .join(Resource, Resource.id == InventoryResource.resource_id)
            .join(Person, Person.id == WorkerRequest.worker_person_id)
            .outerjoin(
                ProfessionAssignment,
                (ProfessionAssignment.person_id == Person.id)
                & (ProfessionAssignment.is_active.is_(True))
                & (ProfessionAssignment.is_main_profession.is_(True)),
            )
            .outerjoin(Profession, Profession.id == ProfessionAssignment.profession_id)
            .join(Camp, Camp.id == WorkerRequest.camp_id)
            .filter(WorkerRequest.camp_id == camp_id)
            .order_by(WorkerRequest.created_at.desc(), WorkerRequest.id.desc())
        )

        if worker_person_id is not None:
            rows = rows.filter(WorkerRequest.worker_person_id == worker_person_id)

        result = []
        for item, request, _inv_res, resource, person, profession, camp in rows.all():
            result.append(
                {
                    "id": item.id,
                    "request_id": request.id,
                    "worker_person_id": request.worker_person_id,
                    "worker_name": f"{person.name} {person.last_name}",
                    "worker_role": profession.name if profession else None,
                    "inventory_resource_id": item.inventory_resource_id,
                    "resource_name": resource.name,
                    "quantity": item.quantity,
                    "request_type": request.request_type,
                    "request_status": STATUS_LABELS.get(request.request_status_id, "PENDIENTE"),
                    "created_at": request.created_at.isoformat(),
                    "reason": request.reason,
                    "rejection_reason": request.rejection_reason,
                    "camp_name": camp.name,
                }
            )

        return result

    @staticmethod
    def approve_request(db: Session, camp_id: int, request_item_id: int) -> None:
        item, request = WorkerRequestService._get_request_item(db, camp_id, request_item_id)

        if request.request_status_id != STATUS_PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud ya fue procesada.",
            )

        inv_res = db.query(InventoryResource).filter(InventoryResource.id == item.inventory_resource_id).first()
        if not inv_res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso de inventario no encontrado.")

        if inv_res.quantity < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente.")

        inv_res.quantity -= item.quantity
        movement = InventoryMovement(
            quantity=item.quantity,
            inventory_resource_id=inv_res.id,
            movement_type=MovementTypeEnum.SALIDA,
        )
        request.request_status_id = STATUS_APPROVED
        request.rejection_reason = None
        db.add(movement)
        db.commit()
        inventory_events.publish(
            camp_id=camp_id,
            source="worker_request.approved",
            metadata={
                "request_item_id": request_item_id,
                "inventory_resource_id": inv_res.id,
                "quantity": item.quantity,
                "request_type": request.request_type,
            },
        )

    @staticmethod
    def reject_request(db: Session, camp_id: int, request_item_id: int, reason: str | None = None) -> None:
        _item, request = WorkerRequestService._get_request_item(db, camp_id, request_item_id)

        if request.request_status_id != STATUS_PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud ya fue procesada.",
            )

        request.request_status_id = STATUS_REJECTED
        request.rejection_reason = (reason or "").strip() or None
        db.commit()

    @staticmethod
    def _normalize_request_type(raw_type: str | None) -> str:
        normalized = (raw_type or REQUEST_TYPE_RESOURCE).strip()
        return REQUEST_TYPE_LABELS.get(normalized, REQUEST_TYPE_LABELS.get(normalized.upper(), normalized.upper()))

    @staticmethod
    def _normalize_items(payload, request_type: str) -> list[WorkerRequestItemCreate]:
        if request_type == REQUEST_TYPE_QUOTA_SHORTFALL:
            if not payload.inventory_resource_id or not payload.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El incumplimiento de cuota debe indicar recurso y cantidad no cumplida.",
                )
            if payload.quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La cantidad no cumplida debe ser mayor a cero.",
                )
            return [
                WorkerRequestItemCreate(
                    inventory_resource_id=payload.inventory_resource_id,
                    quantity=payload.quantity,
                )
            ]

        if request_type != REQUEST_TYPE_RESOURCE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de solicitud no soportado.",
            )

        if not payload.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud de recursos debe incluir items.",
            )
        return payload.items

    @staticmethod
    def _get_camp_inventory_resource(
        db: Session,
        camp_id: int,
        inventory_resource_id: int,
    ) -> InventoryResource:
        inv_res = (
            db.query(InventoryResource)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .filter(
                InventoryResource.id == inventory_resource_id,
                Inventory.camp_id == camp_id,
            )
            .first()
        )
        if not inv_res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurso de inventario no encontrado en el campamento.",
            )
        return inv_res

    @staticmethod
    def _get_request_item(
        db: Session,
        camp_id: int,
        request_item_id: int,
    ) -> tuple[WorkerRequestItem, WorkerRequest]:
        row = (
            db.query(WorkerRequestItem, WorkerRequest)
            .join(WorkerRequest, WorkerRequest.id == WorkerRequestItem.worker_request_id)
            .filter(
                WorkerRequestItem.id == request_item_id,
                WorkerRequest.camp_id == camp_id,
            )
            .first()
        )
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada.")
        return row
