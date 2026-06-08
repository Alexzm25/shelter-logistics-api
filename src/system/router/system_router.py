from collections.abc import Iterator
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.core.realtime_events import system_events


router = APIRouter(prefix="/system", tags=["System"])


def _notification_stream() -> Iterator[str]:
    for message in system_events.subscribe():
        if message.startswith(":"):
            yield message
            continue
        yield f"data: {message}\n\n"


@router.get("/notifications")
def stream_notifications() -> StreamingResponse:
    return StreamingResponse(
        _notification_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/clock")
def system_clock() -> dict[str, str | int]:
    tz_name = "America/Costa_Rica"
    now_cr = datetime.now(ZoneInfo(tz_name))
    return {
        "timezone": tz_name,
        "server_time_iso": now_cr.isoformat(),
        "server_unix_ms": int(now_cr.timestamp() * 1000),
    }
