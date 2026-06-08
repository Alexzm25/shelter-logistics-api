import asyncio
import logging
from contextlib import suppress

from src.core.database import SessionLocal
from src.core.realtime_events import system_events
from src.production.service.ration_service import RationService


logger = logging.getLogger(__name__)
_scheduler_task: asyncio.Task | None = None


async def _ration_scheduler_loop() -> None:
    while True:
        next_run = RationService.get_next_ration_run()
        wait_seconds = max(
            0,
            (next_run - RationService.server_now()).total_seconds(),
        )
        await asyncio.sleep(wait_seconds)

        db = SessionLocal()
        try:
            logs = RationService.distribute_daily_rations(
                db,
                executed_at=RationService.server_now(),
            )
            logger.info(
                "Daily rations distributed: %s camps fed at %s",
                len(logs),
                RationService.server_now().isoformat(),
            )
            if logs:
                total_fed = sum(log.persons_fed for log in logs)
                system_events.publish("ration", {
                    "camps_fed": len(logs),
                    "persons_fed": total_fed,
                    "executed_at": RationService.server_now().isoformat(),
                })
        except Exception:
            db.rollback()
            logger.exception("Daily ration distribution failed")
        finally:
            db.close()


def start_ration_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        return
    _scheduler_task = asyncio.create_task(_ration_scheduler_loop())


async def stop_ration_scheduler() -> None:
    global _scheduler_task
    if not _scheduler_task:
        return
    _scheduler_task.cancel()
    with suppress(asyncio.CancelledError):
        await _scheduler_task
    _scheduler_task = None
