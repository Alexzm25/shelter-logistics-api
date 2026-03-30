from enum import Enum


class CurrentStatusEnum(str, Enum):
    TRABAJANDO = "TRABAJANDO"
    EN_EXPLORACION = "EN EXPLORACIÓN"
    TRASLADANDO_RECURSOS = "TRASLADANDO RECURSOS"
    LIBRE = "LIBRE"
