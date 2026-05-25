"""
Shared pytest fixtures for shelter-logistics-api tests.

Provides:
  - db_session: SQLAlchemy Session against a seeded test database
  - test_client: FastAPI TestClient wired to the test database
  - seed_camp_id: a valid camp ID from the seed data
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.core.database import get_db
from src.main import app

# ── helpers ────────────────────────────────────────────────────────────────


def _maintenance_conn(
    host: str, port: str, user: str, password: str
) -> psycopg2.extensions.connection:
    """Return a psycopg2 connection to the 'postgres' maintenance database."""
    return psycopg2.connect(
        dbname="postgres", host=host, port=port, user=user, password=password
    )


def _init_sql_paths() -> list[Path]:
    """Return sorted list of init SQL files from database/init/."""
    init_dir = Path(__file__).resolve().parent.parent / "database" / "init"
    files = sorted(init_dir.glob("*.sql"))
    if not files:
        raise FileNotFoundError(f"No .sql files found in {init_dir}")
    return files


# ── fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def test_db_url() -> Generator[str, None, None]:
    """
    Create a test database, seed it from init SQL, and tear it down after tests.

    Uses the production DATABASE_URL with '_test' appended to the db name.
    """
    from src.core.settings import settings

    parsed = urlparse(settings.database_url)
    dbname = parsed.path.lstrip("/") or "shelter_logistics"
    test_dbname = f"{dbname}_test"

    # Use localhost instead of Docker container hostname for local test access
    host = "localhost" if parsed.hostname == "db" else (parsed.hostname or "localhost")
    port = str(parsed.port or 5432)
    user = parsed.username or ""
    password = parsed.password or ""

    # Create the test database
    conn = _maintenance_conn(host, port, user, password)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (test_dbname,)
        )
        if cur.fetchone() is None:
            cur.execute(
                f'CREATE DATABASE "{test_dbname}" '
                f"OWNER = {user} ENCODING = 'UTF8'"
            )
    conn.close()

    # Build test URL
    test_url = f"postgresql://{user}:{password}@{host}:{port}/{test_dbname}"

    # Seed the test database
    sql_files = _init_sql_paths()
    seed_test_db(test_url, sql_files)

    yield test_url

    # Teardown: drop the test database
    conn = _maintenance_conn(host, port, user, password)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid()",
            (test_dbname,),
        )
        cur.execute(f'DROP DATABASE IF EXISTS "{test_dbname}"')
    conn.close()


def _split_sql_statements(raw_sql: str) -> list[str]:
    """Split SQL on ``;`` while respecting dollar-quoted strings (``$$...$$``).

    Semicolons inside ``DO $$ ... END; $$`` blocks are NOT treated as
    statement separators.
    """
    statements: list[str] = []
    current: list[str] = []
    in_dollar = False

    for ch in raw_sql:
        current.append(ch)
        # Detect $$ open/close (two consecutive dollar signs)
        if len(current) >= 2 and "".join(current[-2:]) == "$$":
            in_dollar = not in_dollar
        # Only split on ; when outside dollar-quoted blocks
        if ch == ";" and not in_dollar:
            stmt = "".join(current).strip()
            current.clear()
            # Filter out blank/comment-only statements
            lines = [l for l in stmt.splitlines() if l.strip()]
            if lines and not all(
                ln.lstrip().startswith("--") for ln in lines
            ):
                statements.append("\n".join(lines).strip())
    # Catch any trailing content (should be empty after last ``;``)
    tail = "".join(current).strip()
    if tail:
        lines = [l for l in tail.splitlines() if l.strip()]
        if lines and not all(ln.lstrip().startswith("--") for ln in lines):
            statements.append("\n".join(lines).strip())

    return statements


def seed_test_db(database_url: str, sql_files: list[Path]) -> None:
    """Execute all init SQL scripts against the given database."""
    engine = create_engine(database_url)
    with engine.connect() as conn:
        for sql_file in sql_files:
            raw_sql = sql_file.read_text(encoding="utf-8-sig")
            statements = _split_sql_statements(raw_sql)
            for stmt in statements:
                if stmt:
                    conn.execute(text(stmt))
        conn.commit()
    engine.dispose()


@pytest.fixture(scope="session")
def test_engine(test_db_url: str):
    """SQLAlchemy engine bound to the seeded test database."""
    engine = create_engine(
        test_db_url,
        pool_size=5,
        max_overflow=5,
        pool_recycle=1800,
        pool_pre_ping=True,
    )
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """Transaction-scoped session — rolled back after each test."""
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def test_client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with get_db overridden to use the test session.

    Also bypasses authentication by patching ``get_current_user_from_token``
    to return a mock admin profile (per threat model T-01-01).
    """
    from unittest.mock import patch

    from src.auth.schemas.user_profile import UserProfileResponse
    from src.auth.service.authorization import get_current_user_from_token

    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def _mock_current_user(
        _db: Session, _access_token: str | None = None
    ) -> UserProfileResponse:
        return UserProfileResponse(
            username="test_admin",
            user_id=1,
            person_id=1,
            camp_id=1,
            profession_name="MEDICO",
            role_name="ADMINISTRADOR SISTEMA",
        )

    app.dependency_overrides[get_db] = _override_get_db
    with patch(
        "src.auth.service.authorization.get_current_user_from_token",
        side_effect=_mock_current_user,
    ):
        client = TestClient(app)
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_camp_id(db_session: Session) -> int:
    """Return an existing camp_id from the seed data."""
    from src.camps.models.camp import Camp

    camp = db_session.query(Camp).first()
    if camp is None:
        raise RuntimeError("No camps found in seed data — check init SQL")
    return int(camp.id)
