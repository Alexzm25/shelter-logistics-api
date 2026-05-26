from src.core.database import engine

# Import models so they are registered on the metadata
from src.worker_requests.models.worker_request import WorkerRequest  # noqa: F401
from src.worker_requests.models.worker_request_item import WorkerRequestItem  # noqa: F401
from src.core.base import Base


def main() -> None:
    print("Creating worker_requests tables (if missing)...")
    Base.metadata.create_all(bind=engine)
    print("Done")


if __name__ == "__main__":
    main()
