from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.camps.models.camp import Camp
from src.core.realtime_events import inventory_events
from src.inventory.enums import MovementTypeEnum
from src.inventory.models.inventory import Inventory
from src.inventory.models.inventory_movement import InventoryMovement
from src.inventory.models.inventory_resource import InventoryResource
from src.inventory.models.resource import Resource
from src.persons.enums import CurrentStatusEnum
from src.persons.models.person import Person
from src.persons.models.profession import Profession
from src.persons.models.profession_assignment import ProfessionAssignment
from src.transfers.enums import RequestStatusEnum, TransferStatusEnum
from src.transfers.models.transfer_participants import TransferParticipant
from src.transfers.models.transfer_request import TransferRequest
from src.transfers.models.transfer_resource import TransferResource
from src.transfers.schemas.camp_option_response import CampOptionResponse
from src.transfers.schemas.explorer_option_response import ExplorerOptionResponse
from src.transfers.schemas.resource_availability_response import (
    ResourceAvailabilityResponse,
)
from src.transfers.schemas.transfer_request_create import TransferRequestCreate
from src.transfers.schemas.transfer_request_response import TransferRequestResponse
from src.transfers.schemas.transfer_resource_response import TransferResourceResponse


class TransferService:
    @staticmethod
    def list_camps(db: Session, current_camp_id: int) -> list[CampOptionResponse]:
        camps = (
            db.query(Camp)
            .filter(Camp.id != current_camp_id)
            .order_by(Camp.name.asc())
            .all()
        )
        return [
            CampOptionResponse(id=camp.id, name=camp.name, location=camp.location)
            for camp in camps
        ]

    @staticmethod
    def list_resources(
        db: Session,
        current_camp_id: int,
        camp_id: int,
    ) -> list[ResourceAvailabilityResponse]:
        if camp_id == current_camp_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El campamento consultado debe ser externo.",
            )

        camp = db.query(Camp).filter(Camp.id == camp_id).first()
        if not camp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campamento proveedor no encontrado.",
            )

        inventory = db.query(Inventory).filter(Inventory.camp_id == camp_id).first()
        if not inventory:
            return []

        rows = (
            db.query(InventoryResource, Resource)
            .join(Resource, Resource.id == InventoryResource.resource_id)
            .filter(InventoryResource.inventory_id == inventory.id)
            .order_by(Resource.name.asc())
            .all()
        )

        return [
            ResourceAvailabilityResponse(
                resource_id=resource.id,
                resource_name=resource.name,
                category=resource.category,
                available=inventory_resource.quantity,
            )
            for inventory_resource, resource in rows
        ]

    @staticmethod
    def list_pending_requests(
        db: Session, current_camp_id: int
    ) -> list[TransferRequestResponse]:
        requests = (
            db.query(TransferRequest)
            .filter(
                TransferRequest.from_camp_id == current_camp_id,
                TransferRequest.request_status == RequestStatusEnum.PENDIENTE,
            )
            .order_by(TransferRequest.created_at.desc())
            .all()
        )
        return TransferService._build_transfer_responses(db, requests)

    @staticmethod
    def list_history_requests(
        db: Session, current_camp_id: int
    ) -> list[TransferRequestResponse]:
        requests = (
            db.query(TransferRequest)
            .filter(
                or_(
                    TransferRequest.from_camp_id == current_camp_id,
                    TransferRequest.to_camp_id == current_camp_id,
                )
            )
            .order_by(TransferRequest.created_at.desc())
            .all()
        )
        return TransferService._build_transfer_responses(db, requests)

    @staticmethod
    def list_history_requests_paginated(
        db: Session, current_camp_id: int, page: int, size: int
    ) -> tuple[int, list[TransferRequestResponse]]:
        base_query = db.query(TransferRequest).filter(
            or_(
                TransferRequest.from_camp_id == current_camp_id,
                TransferRequest.to_camp_id == current_camp_id,
            )
        )
        total = base_query.count()
        offset = (page - 1) * size
        requests = (
            base_query.order_by(TransferRequest.created_at.desc())
            .offset(offset)
            .limit(size)
            .all()
        )
        return total, TransferService._build_transfer_responses(db, requests)

    @staticmethod
    def list_explorers(
        db: Session, current_camp_id: int
    ) -> list[ExplorerOptionResponse]:
        explorer_profession = (
            db.query(Profession)
            .filter(Profession.name == "EXPLORADOR")
            .first()
        )
        if not explorer_profession:
            return []

        assignments = (
            db.query(ProfessionAssignment)
            .filter(
                ProfessionAssignment.profession_id == explorer_profession.id,
                ProfessionAssignment.is_active == True,
                ProfessionAssignment.is_main_profession == True,
            )
            .all()
        )

        if not assignments:
            return []

        person_ids = [assignment.person_id for assignment in assignments]
        people = (
            db.query(Person)
            .filter(Person.id.in_(person_ids), Person.camp_id == current_camp_id)
            .order_by(Person.name.asc(), Person.last_name.asc())
            .all()
        )

        return [
            ExplorerOptionResponse(
                id=person.id,
                full_name=f"{person.name} {person.last_name}",
            )
            for person in people
        ]

    @staticmethod
    def create_request(
        db: Session,
        current_user: UserProfileResponse,
        payload: TransferRequestCreate,
    ) -> TransferRequestResponse:
        provider_camp_id = payload.to_camp_id
        if provider_camp_id == current_user.camp_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El campamento proveedor no puede ser el mismo.",
            )

        provider = db.query(Camp).filter(Camp.id == provider_camp_id).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campamento proveedor no encontrado.",
            )

        if payload.is_resource_transfer and not payload.resources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud de recursos debe incluir items.",
            )

        transfer_request = TransferRequest(
            from_camp_id=provider_camp_id,
            to_camp_id=current_user.camp_id,
            request_status=RequestStatusEnum.PENDIENTE,
            transfer_status=None,
            arrival_date=None,
            departure_date=date.today(),
            authorized_by=current_user.username,
            is_resource_transfer=payload.is_resource_transfer,
        )
        db.add(transfer_request)
        db.flush()

        if payload.is_resource_transfer:
            for resource_item in payload.resources:
                transfer_resource = TransferResource(
                    transfer_amount=resource_item.transfer_amount,
                    resource_id=resource_item.resource_id,
                    request_id=transfer_request.id,
                )
                db.add(transfer_resource)

        db.commit()
        db.refresh(transfer_request)
        return TransferService._build_transfer_responses(db, [transfer_request])[0]

    @staticmethod
    def approve_request(
        db: Session,
        current_camp_id: int,
        request_id: int,
        participant_ids: list[int] | None,
    ) -> None:
        request = (
            db.query(TransferRequest)
            .filter(
                TransferRequest.id == request_id,
                TransferRequest.from_camp_id == current_camp_id,
            )
            .first()
        )
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada.",
            )

        if request.request_status != RequestStatusEnum.PENDIENTE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud ya fue procesada.",
            )

        requested_participant_ids = set(participant_ids or [])
        if not request.is_resource_transfer and not requested_participant_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes seleccionar al menos un explorador.",
            )

        valid_ids: set[int] = set()
        if requested_participant_ids:
            camp_person_ids = {
                person_id
                for (person_id,) in (
                    db.query(Person.id)
                    .filter(
                        Person.id.in_(requested_participant_ids),
                        Person.camp_id == current_camp_id,
                    )
                    .all()
                )
            }
            if camp_person_ids != requested_participant_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Persona no encontrada.",
                )

            explorer_profession = (
                db.query(Profession)
                .filter(Profession.name == "EXPLORADOR")
                .first()
            )
            if not explorer_profession:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No existe la profesion EXPLORADOR.",
                )

            assignments = (
                db.query(ProfessionAssignment)
                .join(Person, Person.id == ProfessionAssignment.person_id)
                .filter(
                    ProfessionAssignment.profession_id == explorer_profession.id,
                    ProfessionAssignment.is_active == True,
                    ProfessionAssignment.is_main_profession == True,
                    Person.camp_id == current_camp_id,
                    Person.id.in_(requested_participant_ids),
                )
                .all()
            )

            valid_ids = {assignment.person_id for assignment in assignments}
            if valid_ids != requested_participant_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Exploradores invalidos.",
                )

        try:
            for person_id in valid_ids:
                db.add(
                    TransferParticipant(
                        person_id=person_id,
                        request_id=request.id,
                        is_transfer_active=True,
                    )
                )

            request.request_status = RequestStatusEnum.APROBADO
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def confirm_request(db: Session, current_camp_id: int, request_id: int) -> None:
        request = (
            db.query(TransferRequest)
            .filter(
                TransferRequest.id == request_id,
                TransferRequest.to_camp_id == current_camp_id,
            )
            .first()
        )
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada.",
            )

        if request.request_status != RequestStatusEnum.APROBADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud debe estar aprobada por el campamento proveedor.",
            )

        if request.transfer_status is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El prestamo ya fue confirmado.",
            )

        try:
            request.transfer_status = TransferStatusEnum.EN_PREPARACION
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def confirm_departure(db: Session, current_camp_id: int, request_id: int) -> None:
        request = TransferService._get_transfer_for_departure(
            db, current_camp_id, request_id
        )
        try:
            if request.request_status != RequestStatusEnum.APROBADO:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La solicitud debe estar aprobada.",
                )
            if request.transfer_status != TransferStatusEnum.EN_PREPARACION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El traslado no esta en preparacion.",
                )

            transfer_resources = TransferService._get_transfer_resources(db, request.id)
            if request.is_resource_transfer:
                TransferService._subtract_origin_resources(
                    db, current_camp_id, request.id, transfer_resources
                )

            participants = TransferService._get_transfer_participants(db, request.id)
            for participant in participants:
                participant.is_transfer_active = True
                person = db.query(Person).filter(Person.id == participant.person_id).first()
                if person:
                    person.current_status = CurrentStatusEnum.TRASLADANDO_RECURSOS

            request.transfer_status = TransferStatusEnum.DE_CAMINO
            db.commit()
        except Exception:
            db.rollback()
            raise

        if request.is_resource_transfer:
            inventory_events.publish(
                camp_id=current_camp_id,
                source="transfer_request.departed",
                metadata={"request_id": request.id},
            )

    @staticmethod
    def confirm_arrival(db: Session, current_camp_id: int, request_id: int) -> None:
        request = TransferService._get_transfer_for_arrival(
            db, current_camp_id, request_id
        )
        try:
            if request.transfer_status != TransferStatusEnum.DE_CAMINO:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El traslado no esta de camino.",
                )

            transfer_resources = TransferService._get_transfer_resources(db, request.id)
            if request.is_resource_transfer:
                TransferService._add_destination_resources(
                    db, current_camp_id, request.id, transfer_resources
                )

            participants = TransferService._get_transfer_participants(db, request.id)
            for participant in participants:
                participant.is_transfer_active = False
                person = db.query(Person).filter(Person.id == participant.person_id).first()
                if not person:
                    continue
                if request.is_resource_transfer:
                    person.current_status = CurrentStatusEnum.LIBRE
                else:
                    person.camp_id = current_camp_id
                    person.current_status = CurrentStatusEnum.LIBRE

            request.transfer_status = TransferStatusEnum.LLEGO
            request.arrival_date = date.today()
            db.commit()
        except Exception:
            db.rollback()
            raise

        if request.is_resource_transfer:
            inventory_events.publish(
                camp_id=current_camp_id,
                source="transfer_request.arrived",
                metadata={"request_id": request.id},
            )

    @staticmethod
    def reject_request(db: Session, current_camp_id: int, request_id: int) -> None:
        request = (
            db.query(TransferRequest)
            .filter(
                TransferRequest.id == request_id,
                TransferRequest.from_camp_id == current_camp_id,
            )
            .first()
        )
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada.",
            )

        if request.request_status != RequestStatusEnum.PENDIENTE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud ya fue procesada.",
            )

        request.request_status = RequestStatusEnum.RECHAZADO
        request.transfer_status = None
        db.commit()

    @staticmethod
    def _get_transfer_inventory_resources(
        db: Session,
        camp_id: int,
        transfer_resources: list[TransferResource],
    ) -> dict[int, InventoryResource]:
        resource_ids = {transfer_resource.resource_id for transfer_resource in transfer_resources}
        rows = (
            db.query(InventoryResource)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .filter(
                Inventory.camp_id == camp_id,
                InventoryResource.resource_id.in_(resource_ids),
            )
            .all()
        )
        return {inventory_resource.resource_id: inventory_resource for inventory_resource in rows}

    @staticmethod
    def _get_transfer_for_departure(
        db: Session, current_camp_id: int, request_id: int
    ) -> TransferRequest:
        request = (
            db.query(TransferRequest)
            .filter(
                TransferRequest.id == request_id,
                TransferRequest.from_camp_id == current_camp_id,
            )
            .with_for_update()
            .first()
        )
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada.",
            )
        return request

    @staticmethod
    def _get_transfer_for_arrival(
        db: Session, current_camp_id: int, request_id: int
    ) -> TransferRequest:
        request = (
            db.query(TransferRequest)
            .filter(
                TransferRequest.id == request_id,
                TransferRequest.to_camp_id == current_camp_id,
            )
            .with_for_update()
            .first()
        )
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada.",
            )
        return request

    @staticmethod
    def _get_transfer_resources(db: Session, request_id: int) -> list[TransferResource]:
        return (
            db.query(TransferResource)
            .filter(TransferResource.request_id == request_id)
            .all()
        )

    @staticmethod
    def _get_transfer_participants(
        db: Session, request_id: int
    ) -> list[TransferParticipant]:
        return (
            db.query(TransferParticipant)
            .filter(TransferParticipant.request_id == request_id)
            .all()
        )

    @staticmethod
    def _subtract_origin_resources(
        db: Session,
        origin_camp_id: int,
        request_id: int,
        transfer_resources: list[TransferResource],
    ) -> None:
        if not transfer_resources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud no tiene recursos asociados.",
            )

        inventory_resources_by_resource_id = TransferService._get_transfer_inventory_resources(
            db, origin_camp_id, transfer_resources
        )
        for transfer_resource in transfer_resources:
            inventory_resource = inventory_resources_by_resource_id.get(
                transfer_resource.resource_id
            )
            if inventory_resource is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recurso no encontrado en el inventario del campamento.",
                )
            if inventory_resource.quantity < transfer_resource.transfer_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Stock insuficiente para confirmar salida.",
                )

        for transfer_resource in transfer_resources:
            inventory_resource = inventory_resources_by_resource_id[
                transfer_resource.resource_id
            ]
            inventory_resource.quantity -= transfer_resource.transfer_amount
            db.add(
                InventoryMovement(
                    quantity=transfer_resource.transfer_amount,
                    inventory_resource_id=inventory_resource.id,
                    movement_type=MovementTypeEnum.TRANSFERENCIA,
                    transfer_request_id=request_id,
                )
            )

    @staticmethod
    def _add_destination_resources(
        db: Session,
        destination_camp_id: int,
        request_id: int,
        transfer_resources: list[TransferResource],
    ) -> None:
        if not transfer_resources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La solicitud no tiene recursos asociados.",
            )

        inventory = (
            db.query(Inventory)
            .filter(Inventory.camp_id == destination_camp_id)
            .first()
        )
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventario destino no encontrado.",
            )

        inventory_resources_by_resource_id = TransferService._get_transfer_inventory_resources(
            db, destination_camp_id, transfer_resources
        )
        for transfer_resource in transfer_resources:
            inventory_resource = inventory_resources_by_resource_id.get(
                transfer_resource.resource_id
            )
            if inventory_resource is None:
                inventory_resource = InventoryResource(
                    quantity=0,
                    minimum_stock_level=0,
                    inventory_id=inventory.id,
                    resource_id=transfer_resource.resource_id,
                )
                db.add(inventory_resource)
                db.flush()
                inventory_resources_by_resource_id[
                    transfer_resource.resource_id
                ] = inventory_resource

            inventory_resource.quantity += transfer_resource.transfer_amount
            db.add(
                InventoryMovement(
                    quantity=transfer_resource.transfer_amount,
                    inventory_resource_id=inventory_resource.id,
                    movement_type=MovementTypeEnum.TRANSFERENCIA,
                    transfer_request_id=request_id,
                )
            )

    @staticmethod
    def _build_transfer_responses(
        db: Session, requests: list[TransferRequest]
    ) -> list[TransferRequestResponse]:
        if not requests:
            return []

        camp_ids = {request.from_camp_id for request in requests} | {
            request.to_camp_id for request in requests
        }
        camps = db.query(Camp).filter(Camp.id.in_(camp_ids)).all()
        camp_map = {camp.id: camp for camp in camps}

        request_ids = [request.id for request in requests]
        transfer_resources = (
            db.query(TransferResource, Resource)
            .join(Resource, Resource.id == TransferResource.resource_id)
            .filter(TransferResource.request_id.in_(request_ids))
            .all()
        )

        resources_by_request: dict[int, list[TransferResourceResponse]] = {}
        for transfer_resource, resource in transfer_resources:
            resources_by_request.setdefault(transfer_resource.request_id, []).append(
                TransferResourceResponse(
                    resource_id=resource.id,
                    resource_name=resource.name,
                    transfer_amount=transfer_resource.transfer_amount,
                )
            )

        responses: list[TransferRequestResponse] = []
        for request in requests:
            from_camp = camp_map.get(request.from_camp_id)
            to_camp = camp_map.get(request.to_camp_id)
            responses.append(
                TransferRequestResponse(
                    id=request.id,
                    from_camp_id=request.from_camp_id,
                    from_camp_name=from_camp.name if from_camp else "",
                    to_camp_id=request.to_camp_id,
                    to_camp_name=to_camp.name if to_camp else "",
                    request_status=request.request_status,
                    transfer_status=request.transfer_status,
                    created_at=request.created_at,
                    departure_date=request.departure_date,
                    arrival_date=request.arrival_date,
                    authorized_by=request.authorized_by,
                    is_resource_transfer=request.is_resource_transfer,
                    resources=resources_by_request.get(request.id, []),
                )
            )

        return responses
