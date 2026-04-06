from pydantic import BaseModel
from datetime import datetime

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
