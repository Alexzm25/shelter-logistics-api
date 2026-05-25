import os
import pytest as pt


def _load_test_env():
    for line in open(".env.test"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ[key] = value


def test_allowed_origins_missing_env_var():
    _load_test_env()
    os.environ.pop("ALLOWED_ORIGINS", None)
    from src.core.settings import Settings
    with pt.raises(ValueError, match="ALLOWED_ORIGINS"):
        Settings()


def test_allowed_origins_empty_string():
    _load_test_env()
    os.environ["ALLOWED_ORIGINS"] = "   "
    from src.core.settings import Settings
    with pt.raises(ValueError, match="ALLOWED_ORIGINS"):
        Settings()


def test_allowed_origins_comma_separated():
    _load_test_env()
    os.environ["ALLOWED_ORIGINS"] = "http://a.com,http://b.com"
    from src.core.settings import Settings
    s = Settings()
    assert s.allowed_origins == ["http://a.com", "http://b.com"]


def test_allowed_origins_strips_whitespace():
    _load_test_env()
    os.environ["ALLOWED_ORIGINS"] = " http://a.com , http://b.com "
    from src.core.settings import Settings
    s = Settings()
    assert s.allowed_origins == ["http://a.com", "http://b.com"]


def test_jwt_placeholder_rejected():
    _load_test_env()
    os.environ["JWT_SECRET_KEY"] = "change_this_secret_key"
    from src.core.settings import Settings
    with pt.raises(ValueError, match="placeholder"):
        Settings()
