from collections.abc import Callable

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.models.permission import Permission
from src.auth.models.role import Role
from src.auth.models.role_permission import RolePermission
from src.auth.schemas.user_profile import UserProfileResponse
from src.auth.service.auth_service import AuthService
from src.core.database import get_db


ROLE_ADMIN = "ADMINISTRADOR SISTEMA"
ROLE_WORKER = "TRABAJADOR"
ROLE_RESOURCES = "GESTIÓN RECURSOS"
ROLE_TRAVEL = "ENCARGADO VIAJES Y COMUNICACIÓN"

ALL_ROLES = {ROLE_ADMIN, ROLE_WORKER, ROLE_RESOURCES, ROLE_TRAVEL}

PERM_VIEW_DASHBOARD = "VER_DASHBOARD"
PERM_VIEW_WORKER_PAGE = "VER_PAGINA_TRABAJADOR"
PERM_VIEW_TRANSFERS = "VER_PAGINA_TRANSFERENCIAS"
PERM_VIEW_EXPEDITIONS = "VER_PAGINA_EXPEDICIONES"
PERM_VIEW_INVENTORY_FULL = "VER_INVENTARIO_COMPLETO"
PERM_VIEW_ACHIEVEMENTS = "VER_LOGROS"
PERM_HUMAN_FULL = "GESTION_HUMANA_TOTAL"
PERM_REQUEST_RESOURCES = "SOLICITAR_RECURSOS"
PERM_REQUEST_PERSONS = "SOLICITAR_PERSONAS"
PERM_APPROVE_REJECT = "APROBAR_RECHAZAR_SOLICITUDES"
PERM_VIEW_HISTORY = "VER_HISTORIAL_SOLICITUDES"
PERM_CREATE_EXPEDITIONS = "CREAR_EXPEDICIONES"
PERM_REGISTER_PRODUCTION = "REGISTRAR_PRODUCCION"
PERM_VIEW_SEEDS = "VER_INVENTARIO_SEMILLAS"
PERM_VIEW_MEDICINES = "VER_INVENTARIO_MEDICINAS"
PERM_HEAL = "CURAR_PERSONAS"


def get_current_user_from_token(
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None),
) -> UserProfileResponse:
    if not access_token or not access_token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autorización",
        )

    token = access_token.strip()
    return AuthService.get_current_user_profile(db, token)


def get_permissions_for_role(db: Session, role_name: str | None) -> set[str]:
    if not role_name:
        return set()

    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        return set()

    rows = (
        db.query(Permission.name)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == role.id)
        .all()
    )
    return {row[0] for row in rows}


def enforce_role_permissions(
    db: Session,
    profile: UserProfileResponse,
    allowed_roles: set[str],
    required_permissions: set[str],
) -> set[str]:
    role_name = profile.role_name
    if not role_name or role_name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado",
        )

    permissions = get_permissions_for_role(db, role_name)
    missing = [permission for permission in required_permissions if permission not in permissions]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes",
        )

    return permissions


def require_role_permissions(
    allowed_roles: set[str],
    required_permissions: set[str],
) -> Callable[[Session, str | None], UserProfileResponse]:
    def _dependency(
        db: Session = Depends(get_db),
        access_token: str | None = Cookie(default=None),
    ) -> UserProfileResponse:
        profile = get_current_user_from_token(db, access_token)
        enforce_role_permissions(db, profile, allowed_roles, required_permissions)
        return profile

    return _dependency
