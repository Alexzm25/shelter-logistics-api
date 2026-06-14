from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import settings
from src.auth.router.auth_router import router as auth_router
from src.camps.router.camp_dashboard_router import router as camp_dashboard_router
from src.persons.router.human_intake_router import router as human_intake_router
from src.achievement.router.achievement_router import router as achievement_router
from src.inventory.router.inventory_router import router as inventory_router
from src.explorations.router.exploration_router import router as exploration_router
from src.production.router.production_router import router as production_router
from src.transfers.router.transfer_router import router as transfer_router
from src.system.router.system_router import router as system_router
from src.ai.router.ai_configuration_router import router as ai_configuration_router
from src.core.cloudinary import configure_cloudinary
from src.production.service.production_scheduler import (
    start_production_scheduler,
    stop_production_scheduler,
)
from src.production.service.ration_scheduler import (
    start_ration_scheduler,
    stop_ration_scheduler,
)
from src.worker_requests import router as worker_request_router

app = FastAPI(title="shelter-logistics-api")


@app.on_event("startup")
def setup_cloudinary() -> None:
    configure_cloudinary()
    start_production_scheduler()
    start_ration_scheduler()


@app.on_event("shutdown")
async def shutdown_httpx() -> None:
    from src.ai.service.groq_evaluation_service import GroqEvaluationService

    await stop_production_scheduler()
    await stop_ration_scheduler()
    await GroqEvaluationService.close_client()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Total-Count-Internal"],
)

app.include_router(ai_configuration_router)
app.include_router(auth_router)
app.include_router(camp_dashboard_router)
app.include_router(human_intake_router)
app.include_router(achievement_router)
app.include_router(inventory_router)
app.include_router(exploration_router)
app.include_router(production_router)
app.include_router(transfer_router)
app.include_router(worker_request_router)
app.include_router(system_router)

@app.get("/")
def root() -> dict[str, str]:
	return {"message": "shelter-logistics-api is running"}


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}
