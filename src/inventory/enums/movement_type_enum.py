from enum import Enum


class MovementTypeEnum(str, Enum):
    SALIDA = "SALIDA"
    INGRESO = "INGRESO"
    TRANSFERENCIA = "TRANSFERENCIA"
