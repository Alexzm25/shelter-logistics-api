from enum import Enum


class ExplorationStatusEnum(str, Enum):
    EN_PROCESO = "EN PROCESO"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
