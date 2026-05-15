from pydantic import BaseModel


class CancelExplorationResponse(BaseModel):
    message: str
    exploration_id: int