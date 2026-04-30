from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from src.achievement.models.achievement import Achievement
from src.achievement.models.user_achievement import UserAchievement
from src.camps.models.camp import Camp
from src.camps.schemas.achievement_response import AchievementResponse
from src.camps.schemas.camp_dashboard_response import CampDashboardResponse
from src.camps.schemas.camp_stats_response import CampStatsResponse
from src.camps.schemas.internal_transfer_response import InternalTransferResponse
from src.camps.schemas.inter_camp_transfer_response import InterCampTransferResponse
from src.camps.schemas.inventory_item_response import InventoryItemResponse
from src.explorations.enums import ExplorationStatusEnum
from src.explorations.models.exploration import Exploration
from src.inventory.enums import MovementTypeEnum
from src.inventory.models.inventory import Inventory
from src.inventory.models.inventory_movement import InventoryMovement
from src.inventory.models.inventory_resource import InventoryResource
from src.inventory.models.resource import Resource
from src.persons.enums import CurrentStatusEnum, HealthStatusEnum
from src.persons.models.person import Person
from src.auth.models.app_user import AppUser
from src.transfers.enums import RequestStatusEnum, TransferStatusEnum
from src.transfers.models.transfer_request import TransferRequest
from src.transfers.models.transfer_resource import TransferResource


class CampDashboardService:
    LOW_STOCK_MULTIPLIER = 1.5
    INTERNAL_TRANSFER_LIMIT = 25
    INTER_CAMP_TRANSFER_LIMIT = 50
    ACHIEVEMENT_LIMIT = 12

    @staticmethod
    def get_dashboard(db: Session, camp_id: int) -> CampDashboardResponse:
        camp = db.query(Camp).filter(Camp.id == camp_id).first()
        if not camp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camp {camp_id} not found",
            )

        stats = CampDashboardService._build_stats(db, camp)
        inventory = CampDashboardService._build_inventory(db, camp.id)
        inter_camp_transfers = CampDashboardService._build_inter_camp_transfers(db, camp.id)
        internal_transfers = CampDashboardService._build_internal_transfers(db, camp.id)
        achievements = CampDashboardService._build_achievements(db, camp.id)

        return CampDashboardResponse(
            stats=stats,
            inventory=inventory,
            inter_camp_transfers=inter_camp_transfers,
            internal_transfers=internal_transfers,
            achievements=achievements,
        )

    @staticmethod
    def _build_stats(db: Session, camp: Camp) -> CampStatsResponse:
        total_population = CampDashboardService._count_people(db, camp.id)
        healthy_count = CampDashboardService._count_people(
            db, camp.id, health_status=HealthStatusEnum.SANO
        )
        injured_count = CampDashboardService._count_people(
            db, camp.id, health_status=HealthStatusEnum.HERIDO
        )
        sick_count = CampDashboardService._count_people(
            db, camp.id, health_status=HealthStatusEnum.ENFERMO
        )
        dead_count = CampDashboardService._count_people(
            db, camp.id, health_status=HealthStatusEnum.MUERTO
        )
        away_count = CampDashboardService._count_people(
            db,
            camp.id,
            current_statuses=(
                CurrentStatusEnum.EN_EXPLORACION,
                CurrentStatusEnum.TRASLADANDO_RECURSOS,
            ),
        )

        unhealthy_count = injured_count + sick_count
        survival_score = CampDashboardService._calculate_survival_score(
            total_population,
            dead_count,
        )

        critical_alerts, low_stock_alerts = CampDashboardService._count_inventory_alerts(
            db, camp.id
        )
        active_explorations = CampDashboardService._count_active_explorations(db, camp.id)
        total_achievements = CampDashboardService._count_achievements(db, camp.id)
        aid_transfers = CampDashboardService._count_aid_transfers(db, camp.id)

        return CampStatsResponse(
            id=camp.id,
            name=camp.name,
            total_population=total_population,
            healthy_count=healthy_count,
            unhealthy_count=unhealthy_count,
            injured_count=injured_count,
            sick_count=sick_count,
            away_count=away_count,
            critical_alerts=critical_alerts,
            low_stock_alerts=low_stock_alerts,
            active_explorations=active_explorations,
            total_achievements=total_achievements,
            aid_transfers=aid_transfers,
            survival_score=survival_score,
        )

    @staticmethod
    def _count_people(
        db: Session,
        camp_id: int,
        health_status: HealthStatusEnum | None = None,
        current_statuses: tuple[CurrentStatusEnum, ...] | None = None,
    ) -> int:
        query = db.query(func.count(Person.id)).filter(Person.camp_id == camp_id)
        if health_status is not None:
            query = query.filter(Person.health_status == health_status)
        if current_statuses:
            query = query.filter(Person.current_status.in_(current_statuses))
        return int(query.scalar() or 0)

    @staticmethod
    def _calculate_survival_score(total_population: int, dead_count: int) -> int:
        if total_population <= 0:
            return 0
        living = max(total_population - dead_count, 0)
        return int(round((living / total_population) * 100))

    @staticmethod
    def _count_inventory_alerts(db: Session, camp_id: int) -> tuple[int, int]:
        threshold = CampDashboardService.LOW_STOCK_MULTIPLIER
        inventory_subquery = (
            db.query(InventoryResource)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .filter(Inventory.camp_id == camp_id)
            .subquery()
        )

        critical_count = (
            db.query(func.count(inventory_subquery.c.id))
            .filter(inventory_subquery.c.quantity <= inventory_subquery.c.minimum_stock_level)
            .scalar()
        )

        low_stock_count = (
            db.query(func.count(inventory_subquery.c.id))
            .filter(inventory_subquery.c.quantity > inventory_subquery.c.minimum_stock_level)
            .filter(
                inventory_subquery.c.quantity
                <= inventory_subquery.c.minimum_stock_level * threshold
            )
            .scalar()
        )

        return int(critical_count or 0), int(low_stock_count or 0)

    @staticmethod
    def _count_active_explorations(db: Session, camp_id: int) -> int:
        return int(
            db.query(func.count(Exploration.id))
            .filter(
                Exploration.camp_id == camp_id,
                Exploration.exploration_status == ExplorationStatusEnum.EN_PROCESO,
            )
            .scalar()
            or 0
        )

    @staticmethod
    def _count_achievements(db: Session, camp_id: int) -> int:
        return int(
            db.query(func.count(UserAchievement.achievement_id))
            .join(AppUser, AppUser.id == UserAchievement.user_id)
            .join(Person, Person.id == AppUser.person_id)
            .filter(Person.camp_id == camp_id, UserAchievement.is_unlocked.is_(True))
            .scalar()
            or 0
        )

    @staticmethod
    def _count_aid_transfers(db: Session, camp_id: int) -> int:
        return int(
            db.query(func.count(TransferRequest.id))
            .filter(
                (TransferRequest.from_camp_id == camp_id)
                | (TransferRequest.to_camp_id == camp_id)
            )
            .filter(TransferRequest.is_resource_transfer.is_(False))
            .filter(TransferRequest.request_status == RequestStatusEnum.APROBADO)
            .scalar()
            or 0
        )

    @staticmethod
    def _build_inventory(db: Session, camp_id: int) -> list[InventoryItemResponse]:
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
            alert_level = CampDashboardService._resolve_alert_level(
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
    def _resolve_alert_level(quantity: int, minimum_stock: int) -> str:
        if quantity <= minimum_stock:
            return "critical"
        if quantity <= minimum_stock * CampDashboardService.LOW_STOCK_MULTIPLIER:
            return "warning"
        return "normal"

    @staticmethod
    def _build_inter_camp_transfers(
        db: Session, camp_id: int
    ) -> list[InterCampTransferResponse]:
        from src.transfers.models.transfer_participants import TransferParticipant
        
        origin_camp = aliased(Camp)
        dest_camp = aliased(Camp)

        # Query for resource transfers
        resource_rows = (
            db.query(
                TransferRequest,
                TransferResource,
                Resource,
                origin_camp.name.label("origin_name"),
                dest_camp.name.label("destination_name"),
            )
            .join(TransferResource, TransferResource.request_id == TransferRequest.id)
            .join(Resource, Resource.id == TransferResource.resource_id)
            .join(origin_camp, origin_camp.id == TransferRequest.from_camp_id)
            .join(dest_camp, dest_camp.id == TransferRequest.to_camp_id)
            .filter(
                (TransferRequest.from_camp_id == camp_id)
                | (TransferRequest.to_camp_id == camp_id)
            )
            .filter(TransferRequest.is_resource_transfer.is_(True))
            .order_by(TransferRequest.created_at.desc())
            .limit(CampDashboardService.INTER_CAMP_TRANSFER_LIMIT)
            .all()
        )

        # Query for person transfers
        person_rows = (
            db.query(TransferRequest)
            .join(origin_camp, origin_camp.id == TransferRequest.from_camp_id)
            .join(dest_camp, dest_camp.id == TransferRequest.to_camp_id)
            .filter(
                (TransferRequest.from_camp_id == camp_id)
                | (TransferRequest.to_camp_id == camp_id)
            )
            .filter(TransferRequest.is_resource_transfer.is_(False))
            .order_by(TransferRequest.created_at.desc())
            .limit(CampDashboardService.INTER_CAMP_TRANSFER_LIMIT)
            .all()
        )

        transfers: list[InterCampTransferResponse] = []

        # Process resource transfers
        for request, transfer_resource, resource, origin_name, destination_name in resource_rows:
            transfers.append(
                InterCampTransferResponse(
                    id=request.id,
                    origin=origin_name,
                    destination=destination_name,
                    resource=resource.name,
                    quantity=transfer_resource.transfer_amount,
                    status=CampDashboardService._map_transfer_status(
                        request.request_status, request.transfer_status
                    ),
                    scheduled_date=CampDashboardService._format_date(request.departure_date),
                    is_resource_transfer=request.is_resource_transfer,
                    approved_by=request.authorized_by or "SISTEMA",
                )
            )

        # Process person transfers
        for request in person_rows:
            participants = (
                db.query(Person.name)
                .join(TransferParticipant, TransferParticipant.person_id == Person.id)
                .filter(TransferParticipant.request_id == request.id)
                .all()
            )
            participant_names = ", ".join([p[0] for p in participants]) or "Sin participantes"
            
            origin_name = (
                db.query(Camp.name)
                .filter(Camp.id == request.from_camp_id)
                .scalar() or f"Campamento {request.from_camp_id}"
            )
            destination_name = (
                db.query(Camp.name)
                .filter(Camp.id == request.to_camp_id)
                .scalar() or f"Campamento {request.to_camp_id}"
            )

            transfers.append(
                InterCampTransferResponse(
                    id=request.id,
                    origin=origin_name,
                    destination=destination_name,
                    resource=participant_names,
                    quantity=len(participants),
                    status=CampDashboardService._map_transfer_status(
                        request.request_status, request.transfer_status
                    ),
                    scheduled_date=CampDashboardService._format_date(request.departure_date),
                    is_resource_transfer=request.is_resource_transfer,
                    approved_by=request.authorized_by or "SISTEMA",
                )
            )

        # Sort by created_at descending and limit total
        transfers.sort(key=lambda x: x.id, reverse=True)
        return transfers[:CampDashboardService.INTER_CAMP_TRANSFER_LIMIT]

    @staticmethod
    def _map_transfer_status(
        request_status: RequestStatusEnum,
        transfer_status: TransferStatusEnum | None,
    ) -> str:
        if request_status == RequestStatusEnum.RECHAZADO:
            return "rejected"
        if request_status == RequestStatusEnum.PENDIENTE:
            return "pending"

        if transfer_status == TransferStatusEnum.DE_CAMINO:
            return "in-transit"
        return "approved"

    @staticmethod
    def _format_date(value: date | None) -> str:
        return value.isoformat() if value else ""

    @staticmethod
    def _build_internal_transfers(
        db: Session, camp_id: int
    ) -> list[InternalTransferResponse]:
        origin_camp = aliased(Camp)
        dest_camp = aliased(Camp)

        rows = (
            db.query(
                InventoryMovement,
                InventoryResource,
                Resource,
                TransferRequest,
                origin_camp.name.label("origin_name"),
                dest_camp.name.label("destination_name"),
            )
            .join(InventoryResource, InventoryResource.id == InventoryMovement.inventory_resource_id)
            .join(Inventory, Inventory.id == InventoryResource.inventory_id)
            .join(Resource, Resource.id == InventoryResource.resource_id)
            .outerjoin(TransferRequest, TransferRequest.id == InventoryMovement.transfer_request_id)
            .outerjoin(origin_camp, origin_camp.id == TransferRequest.from_camp_id)
            .outerjoin(dest_camp, dest_camp.id == TransferRequest.to_camp_id)
            .filter(Inventory.camp_id == camp_id)
            .order_by(InventoryMovement.created_at.desc())
            .limit(CampDashboardService.INTERNAL_TRANSFER_LIMIT)
            .all()
        )

        transfers: list[InternalTransferResponse] = []
        for movement, _, resource, request, origin_name, destination_name in rows:
            from_zone, to_zone = CampDashboardService._resolve_transfer_zones(
                movement.movement_type,
                request,
                origin_name,
                destination_name,
            )
            transfers.append(
                InternalTransferResponse(
                    id=movement.id,
                    timestamp=CampDashboardService._format_timestamp(movement.created_at),
                    resource=resource.name,
                    category=resource.category.value,
                    direction=CampDashboardService._map_movement_direction(movement.movement_type),
                    quantity=movement.quantity,
                    from_zone=from_zone,
                    to_zone=to_zone,
                    authorized_by=request.authorized_by if request else "SISTEMA",
                )
            )

        return transfers

    @staticmethod
    def _map_movement_direction(movement_type: MovementTypeEnum) -> str:
        if movement_type == MovementTypeEnum.INGRESO:
            return "in"
        if movement_type == MovementTypeEnum.SALIDA:
            return "out"
        return "move"

    @staticmethod
    def _resolve_transfer_zones(
        movement_type: MovementTypeEnum,
        request: TransferRequest | None,
        origin_name: str | None,
        destination_name: str | None,
    ) -> tuple[str, str]:
        if request:
            return (
                origin_name or f"Campamento {request.from_camp_id}",
                destination_name or f"Campamento {request.to_camp_id}",
            )

        if movement_type == MovementTypeEnum.INGRESO:
            return "EXTERIOR", "INVENTARIO"
        if movement_type == MovementTypeEnum.SALIDA:
            return "INVENTARIO", "CONSUMO"
        return "INVENTARIO", "INVENTARIO"

    @staticmethod
    def _format_timestamp(value) -> str:
        return value.strftime("%Y-%m-%d %H:%M") if value else ""

    @staticmethod
    def _build_achievements(db: Session, camp_id: int) -> list[AchievementResponse]:
        rows = (
            db.query(UserAchievement, Achievement)
            .join(AppUser, AppUser.id == UserAchievement.user_id)
            .join(Person, Person.id == AppUser.person_id)
            .join(Achievement, Achievement.id == UserAchievement.achievement_id)
            .filter(Person.camp_id == camp_id, UserAchievement.is_unlocked.is_(True))
            .order_by(UserAchievement.unlocked_at.desc())
            .limit(CampDashboardService.ACHIEVEMENT_LIMIT)
            .all()
        )

        achievements: list[AchievementResponse] = []
        for user_achievement, achievement in rows:
            achievements.append(
                AchievementResponse(
                    id=achievement.id,
                    title=achievement.name,
                    description=achievement.description,
                    unlocked_at=CampDashboardService._format_timestamp(
                        user_achievement.unlocked_at
                    ),
                    icon=achievement.icon_url,
                )
            )

        return achievements
