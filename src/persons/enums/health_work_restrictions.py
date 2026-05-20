from enum import Enum


class WorkAbilityEnum(str, Enum):
    CAN_WORK = "CAN_WORK"
    CANNOT_WORK = "CANNOT_WORK"


HEALTH_STATUS_WORK_RESTRICTIONS = {
    "SANO": WorkAbilityEnum.CAN_WORK,
    "HERIDO": WorkAbilityEnum.CANNOT_WORK,
    "ENFERMO": WorkAbilityEnum.CANNOT_WORK,
    "MUERTO": WorkAbilityEnum.CANNOT_WORK,
}


def can_work(health_status: str) -> bool:
    """
    Verifica si una persona con cierto estado de salud puede trabajar en una profesión.

    Args:
        health_status: Estado de salud (SANO, HERIDO, ENFERMO, MUERTO)

    Returns:
        True si puede trabajar, False si no puede
    """
    ability = HEALTH_STATUS_WORK_RESTRICTIONS.get(health_status)
    return ability == WorkAbilityEnum.CAN_WORK


def is_valid_health_transition(old_status: str, new_status: str) -> tuple[bool, str]:
    """
    Valida si la transición de estado de salud es permitida.

    Args:
        old_status: Estado actual
        new_status: Nuevo estado

    Returns:
        Tupla (es_válido, mensaje)
    """
    old = (old_status or "").upper()
    new = (new_status or "").upper()

    allowed_transitions = {
        "SANO": {"SANO", "HERIDO", "ENFERMO", "MUERTO"},
        "HERIDO": {"HERIDO", "ENFERMO", "SANO", "MUERTO"},
        "ENFERMO": {"ENFERMO", "HERIDO", "SANO", "MUERTO"},
        "MUERTO": {"MUERTO"},
    }

    if old not in allowed_transitions:
        return False, f"Estado anterior desconocido: '{old_status}'"
    if new not in {"SANO", "HERIDO", "ENFERMO", "MUERTO"}:
        return False, f"Nuevo estado desconocido: '{new_status}'"

    if new in allowed_transitions[old]:
        return True, ""

    return False, f"Transición inválida de '{old_status}' a '{new_status}'"
