from fastapi import FastAPI

from src.auth.router.auth_router import router as auth_router


app = FastAPI(title="shelter-logistics-api")

app.include_router(auth_router)


@app.get("/")
def root() -> dict[str, str]:
	return {"message": "shelter-logistics-api is running"}


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}
