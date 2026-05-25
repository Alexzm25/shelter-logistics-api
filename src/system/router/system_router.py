from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter


router = APIRouter(prefix="/system", tags=["System"])


@router.get("/clock")
def system_clock() -> dict[str, str | int]:
    tz_name = "America/Costa_Rica"
    now_cr = datetime.now(ZoneInfo(tz_name))
    return {
        "timezone": tz_name,
        "server_time_iso": now_cr.isoformat(),
        "server_unix_ms": int(now_cr.timestamp() * 1000),
    }
