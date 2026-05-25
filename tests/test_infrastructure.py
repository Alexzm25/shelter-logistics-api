"""Minimal infrastructure verification — fails until pytest + conftest are set up."""
import importlib


def test_core_imports_work():
    """Verify core modules are importable."""
    from src.core.database import engine, SessionLocal, get_db

    assert engine is not None, "SQLAlchemy engine should be available"
    assert SessionLocal is not None, "SessionLocal sessionmaker should be available"
    assert get_db is not None, "get_db generator should be available"


def test_pytest_can_collect():
    """Placeholder — pytest --collect-only will discover this."""
    assert True
