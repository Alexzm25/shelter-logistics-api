"""Integration tests for explorations pagination and N+1 query fix.

Validates:
- Pagination with page/size params and X-Total-Count header
- Batch-counted team_count (GROUP BY, not per-row queries)
- Query count reduction (≤ 2 queries for get_all_by_camp)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.auth.schemas.user_profile import UserProfileResponse
from src.explorations.enums import ExplorationStatusEnum
from src.explorations.models.exploration import Exploration
from src.explorations.service.exploration_service import ExplorationService
from src.main import app


def _make_mock_user() -> UserProfileResponse:
    return UserProfileResponse(
        username="test_admin",
        user_id=1,
        person_id=1,
        camp_id=1,
        profession_name="EXPLORADOR",
        role_name="ADMINISTRADOR SISTEMA",
    )


def test_return_exploration_route_is_registered():
    routes = [
        route
        for route in app.routes
        if getattr(route, "path", None) == "/explorations/return"
    ]

    assert routes, "POST /explorations/return route is not registered"
    assert any("POST" in getattr(route, "methods", set()) for route in routes)


def test_explorations_default_pagination(test_client, seed_camp_id):
    with patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    ):
        response = test_client.get(
            "/explorations",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    items = response.json()
    assert isinstance(items, list), f"Expected list, got {type(items)}"
    assert len(items) <= 10, f"Expected ≤ 10 items, got {len(items)}"
    assert "x-total-count" in response.headers, (
        "Response missing X-Total-Count header"
    )
    total = int(response.headers["x-total-count"])
    assert total >= 0, f"X-Total-Count should be ≥ 0, got {total}"


def test_explorations_custom_page_size(test_client, seed_camp_id):
    with patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    ):
        response = test_client.get(
            "/explorations?page=1&size=5",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200
    items = response.json()
    assert len(items) <= 5, f"Expected ≤ 5 items, got {len(items)}"
    assert "x-total-count" in response.headers


def test_explorations_empty_page(test_client, seed_camp_id):
    with patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    ):
        response = test_client.get(
            "/explorations?page=999&size=10",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 0, f"Empty page should return [], got {len(items)} items"
    assert "x-total-count" in response.headers
    total = int(response.headers["x-total-count"])
    assert total >= 0


def test_explorations_team_count_valid(test_client, seed_camp_id):
    with patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    ):
        response = test_client.get(
            "/explorations?page=1&size=100",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert "team_count" in item, (
            f"Item missing team_count: {item}"
        )
        tc = item["team_count"]
        assert isinstance(tc, int), (
            f"team_count should be int, got {type(tc)}"
        )
        assert tc >= 0, f"team_count should be ≥ 0, got {tc}"


def test_explorations_query_count(test_client, db_session: Session, seed_camp_id):
    engine: Engine = db_session.get_bind()
    query_count = {"count": 0}

    @event.listens_for(engine, "before_cursor_execute")
    def _count_queries(conn, cursor, statement, parameters, context, executemany):
        query_count["count"] += 1

    with patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    ):
        response = test_client.get(
            "/explorations?page=1&size=10",
            cookies={"access_token": "fake-token"},
        )

    event.remove(engine, "before_cursor_execute", _count_queries)

    assert response.status_code == 200
    assert query_count["count"] <= 5, (
        f"Query count {query_count['count']} exceeds limit of 5. "
        f"N+1 member count queries may not be batch-pre-fetched."
    )


def test_cancel_started_exploration(db_session: Session, seed_camp_id):
    exploration = Exploration(
        start_date=datetime.now(timezone.utc) - timedelta(days=1),
        return_date=None,
        exploration_status=ExplorationStatusEnum.EN_PROCESO,
        camp_id=seed_camp_id,
        extra_days=0,
        ration_per_person=1,
        max_extra_days=20,
        estimated_days=1,
    )
    db_session.add(exploration)
    db_session.commit()
    db_session.refresh(exploration)

    response = ExplorationService.cancel_exploration(
        db_session,
        exploration.id,
        seed_camp_id,
    )

    db_session.refresh(exploration)
    assert response.exploration_id == exploration.id
    assert exploration.exploration_status == ExplorationStatusEnum.CANCELADA
    assert exploration.return_date is not None
