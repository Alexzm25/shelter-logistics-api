from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from src.inventory.enums import MovementTypeEnum
from src.inventory.models import Inventory, InventoryMovement, InventoryResource
from src.persons.enums import CurrentStatusEnum, HealthStatusEnum
from src.persons.models.person import Person
from src.worker_requests.models.worker_request import WorkerRequest
from src.worker_requests.schemas.worker_request_create import WorkerRequestCreate
from src.worker_requests.service.worker_request_service import (
    REQUEST_TYPE_QUOTA_SHORTFALL,
    STATUS_APPROVED,
    WorkerRequestService,
)


def test_approving_quota_shortfall_compensates_inventory(db_session, seed_camp_id):
    inventory_resource = (
        db_session.query(InventoryResource)
        .join(Inventory, Inventory.id == InventoryResource.inventory_id)
        .filter(Inventory.camp_id == seed_camp_id)
        .first()
    )
    assert inventory_resource is not None

    inventory_resource.quantity = 10
    db_session.commit()

    worker = Person(
        name="Test",
        last_name="Worker",
        age=30,
        background_info="Test worker",
        weight=Decimal("70.00"),
        height=Decimal("1.75"),
        camp_id=seed_camp_id,
        current_status=CurrentStatusEnum.TRABAJANDO,
        health_status=HealthStatusEnum.SANO,
        camp_entry_date=datetime.now(timezone.utc),
        photo_url="https://example.test/worker.png",
        is_active=True,
        id_card="worker-quota-shortfall-test",
    )
    db_session.add(worker)
    db_session.flush()

    current_user = SimpleNamespace(camp_id=seed_camp_id, person_id=worker.id)
    created_items = WorkerRequestService.create_request(
        db_session,
        current_user,
        WorkerRequestCreate(
            request_type=REQUEST_TYPE_QUOTA_SHORTFALL,
            inventory_resource_id=inventory_resource.id,
            quantity=3,
            reason="No se cumplio la cuota diaria",
        ),
    )

    WorkerRequestService.approve_request(
        db_session,
        seed_camp_id,
        created_items[0]["id"],
    )

    db_session.refresh(inventory_resource)
    request = (
        db_session.query(WorkerRequest)
        .filter(WorkerRequest.id == created_items[0]["worker_request_id"])
        .one()
    )
    movement = (
        db_session.query(InventoryMovement)
        .filter(
            InventoryMovement.inventory_resource_id == inventory_resource.id,
            InventoryMovement.quantity == 3,
            InventoryMovement.movement_type == MovementTypeEnum.SALIDA,
        )
        .order_by(InventoryMovement.id.desc())
        .first()
    )

    assert inventory_resource.quantity == 7
    assert request.request_status_id == STATUS_APPROVED
    assert movement is not None
