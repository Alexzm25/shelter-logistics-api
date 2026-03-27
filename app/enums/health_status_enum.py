from enum import Enum


class HealthStatusEnum(str, Enum):
    SANO = "SANO"
    HERIDO = "HERIDO"
    ENFERMO = "ENFERMO"
    MUERTO = "MUERTO"
