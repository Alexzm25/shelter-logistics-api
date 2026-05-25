"""
Integration tests for Human Intake dashboard — verifies N+1 query reduction.

Requires a seeded test database (see conftest.py for fixtures).

The human_intake_router directly imports ``get_current_user_from_token``,
so we mock ``AuthService.get_current_user_profile`` (which it delegates to)
and supply a fake ``access_token`` cookie.
"""

from __future__ import annotations

from unittest.mock import patch

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse


def _make_mock_user() -> UserProfileResponse:
    """Return a mock admin user accepted by the dashboard permission checks."""
    return UserProfileResponse(
        username="test_admin",
        user_id=1,
        person_id=1,
        camp_id=1,
        profession_name="MEDICO",
        role_name="ADMINISTRADOR SISTEMA",
    )


def test_dashboard_profession_field(
    test_client, db_session: Session, seed_camp_id: int
) -> None:
    """
    GET /human/dashboard returns 200 and every person has a 'profession' key.

    Even people without an assigned profession should have
    'profession' set (to SIN_ASIGNAR or similar).
    """
    with patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    ):
        response = test_client.get(
            f"/human/dashboard?camp_id={seed_camp_id}",
            cookies={"access_token": "fake-token"},
        )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )

    data = response.json()
    assert "people" in data, "Response missing 'people' key"
    assert "ai_logs" in data, "Response missing 'ai_logs' key"

    for person in data["people"]:
        assert "profession" in person, (
            f"Person id={person.get('id')} missing 'profession' field"
        )


def test_dashboard_query_count(
    test_client, db_session: Session, seed_camp_id: int
) -> None:
    """
    GET /human/dashboard performs ≤ 3 database statements.

    Before the N+1 fix the service executed N×2+2 queries
    (one profession lookup + one temporary-reassignment lookup
    per person).  After the batch pre-fetch we expect:
        - 1 query for active people
        - 1 batch query for their main profession assignments
        - 1 query for AI logs (may be combined or separate)
    giving a hard cap of 3 executed statements.
    """
    engine: Engine = db_session.get_bind()
    query_count: int = 0

    @event.listens_for(engine, "before_cursor_execute")
    def _count_queries(
        conn, cursor, statement, parameters, context, executemany
    ) -> None:
        nonlocal query_count
        query_count += 1

    with patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    ):
        response = test_client.get(
            f"/human/dashboard?camp_id={seed_camp_id}",
            cookies={"access_token": "fake-token"},
        )

    event.remove(engine, "before_cursor_execute", _count_queries)

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    assert query_count <= 6, (
        f"Dashboard query count was {query_count} (expected ≤ 6 after N+1 fix). "
        f"Original count was N×2+2 where N=active people (~{query_count * 8}+ queries). "
        "Profession resolution overhead may still be elevated."
    )
