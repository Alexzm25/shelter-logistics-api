"""
Unit tests for GroqEvaluationService — verifies httpx migration
and no lingering urllib imports.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_GROQ_SERVICE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "ai" / "service" / "groq_evaluation_service.py"
)


def _read_source() -> str:
    """Read the entire groq_evaluation_service.py as a string."""
    return _GROQ_SERVICE_PATH.read_text(encoding="utf-8")


def test_no_urllib_import() -> None:
    """groq_evaluation_service.py must NOT import urllib.request."""
    source = _read_source()
    assert "urllib.request" not in source, (
        "urllib.request is still referenced — httpx migration incomplete"
    )


def test_httpx_import_present() -> None:
    """groq_evaluation_service.py must import httpx."""
    source = _read_source()
    assert "import httpx" in source or "from httpx" in source, (
        "httpx import not found in groq_evaluation_service.py"
    )


@pytest.mark.asyncio
async def test_async_client_singleton() -> None:
    """Calling GroqEvaluationService.get_client() twice returns the same instance."""
    from src.ai.service.groq_evaluation_service import GroqEvaluationService

    # Ensure a clean state before the test
    if GroqEvaluationService._client is not None:
        await GroqEvaluationService.close_client()

    client_a = await GroqEvaluationService.get_client()
    client_b = await GroqEvaluationService.get_client()

    assert client_a is client_b, (
        "get_client() returned different instances — singleton contract broken"
    )


@pytest.mark.asyncio
async def test_close_client() -> None:
    """Calling close_client() sets _client to None."""
    from src.ai.service.groq_evaluation_service import GroqEvaluationService

    # Initialise the client
    _client = await GroqEvaluationService.get_client()
    assert GroqEvaluationService._client is not None, (
        "_client should be initialized before close_client test"
    )

    await GroqEvaluationService.close_client()
    assert GroqEvaluationService._client is None, (
        "close_client() did not set _client to None"
    )
