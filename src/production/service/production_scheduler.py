import asyncio
import logging
from contextlib import suppress

from src.core.database import SessionLocal
from src.production.service.production_service import ProductionService


logger = logging.getLogger(__name__)
_scheduler_task: asyncio.Task | None = None


async def _production_scheduler_loop() -> None:
    while True:
        next_run = ProductionService.get_next_automatic_run()
        wait_seconds = max(
            0,
            (next_run - ProductionService.server_now()).total_seconds(),
        )
        await asyncio.sleep(wait_seconds)

        db = SessionLocal()
        try:
            audits = ProductionService.register_daily_automatic_production(
                db,
                executed_at=ProductionService.server_now(),
            )
            logger.info(
                "Automatic production finished for %s camps at %s",
                len(audits),
                ProductionService.server_now().isoformat(),
            )
        except Exception:
            db.rollback()
            logger.exception("Automatic production failed")
        finally:
            db.close()


def start_production_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        return
    _scheduler_task = asyncio.create_task(_production_scheduler_loop())


async def stop_production_scheduler() -> None:
    global _scheduler_task
    if not _scheduler_task:
        return
    _scheduler_task.cancel()
    with suppress(asyncio.CancelledError):
        await _scheduler_task
    _scheduler_task = None
