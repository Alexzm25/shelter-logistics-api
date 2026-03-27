from fastapi import FastAPI


app = FastAPI(title="shelter-logistics-api")


@app.get("/")
def root() -> dict[str, str]:
	return {"message": "shelter-logistics-api is running"}


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}
