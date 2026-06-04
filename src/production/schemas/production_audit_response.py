from datetime import datetime

from pydantic import BaseModel


class ProducedResourceResponse(BaseModel):
    resource_id: int
    resource_name: str
    quantity: int


class ProductionAuditResponse(BaseModel):
    id: int
    executed_at: datetime
    camp_id: int
    camp_name: str
    resources_produced: list[ProducedResourceResponse]
    total_quantity: int


class ProductionAutomationStatusResponse(BaseModel):
    timezone: str
    next_run_at: datetime
    already_ran_today: bool
    last_run: ProductionAuditResponse | None
