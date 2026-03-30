from enum import Enum


class TransferStatusEnum(str, Enum):
    EN_PREPARACION = "EN PREPARACIÓN"
    DE_CAMINO = "DE CAMINO"
    LLEGO = "LLEGÓ"
