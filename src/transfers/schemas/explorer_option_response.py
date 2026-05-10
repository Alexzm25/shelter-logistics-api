from pydantic import BaseModel


class ExplorerOptionResponse(BaseModel):
    id: int
    full_name: str
