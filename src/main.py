from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router.auth_router import router as auth_router
from src.camps.router.camp_dashboard_router import router as camp_dashboard_router
from src.persons.router.human_intake_router import router as human_intake_router


app = FastAPI(title="shelter-logistics-api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(camp_dashboard_router)
app.include_router(human_intake_router)


@app.get("/")
def root() -> dict[str, str]:
	return {"message": "shelter-logistics-api is running"}


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}
