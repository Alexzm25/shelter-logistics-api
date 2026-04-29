from pydantic import BaseModel

from src.camps.schemas.achievement_response import AchievementResponse
from src.camps.schemas.camp_stats_response import CampStatsResponse
from src.camps.schemas.inter_camp_transfer_response import InterCampTransferResponse
from src.camps.schemas.internal_transfer_response import InternalTransferResponse
from src.camps.schemas.inventory_item_response import InventoryItemResponse


class CampDashboardResponse(BaseModel):
    stats: CampStatsResponse
    inventory: list[InventoryItemResponse]
    inter_camp_transfers: list[InterCampTransferResponse]
    internal_transfers: list[InternalTransferResponse]
    achievements: list[AchievementResponse]
