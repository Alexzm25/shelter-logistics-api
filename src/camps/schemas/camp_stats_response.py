from pydantic import BaseModel


class CampStatsResponse(BaseModel):
    id: int
    name: str
    total_population: int
    healthy_count: int
    unhealthy_count: int
    injured_count: int
    sick_count: int
    away_count: int
    critical_alerts: int
    low_stock_alerts: int
    active_explorations: int
    total_achievements: int
    aid_transfers: int
    survival_score: int
