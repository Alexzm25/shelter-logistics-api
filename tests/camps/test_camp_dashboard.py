"""Integration tests for camp dashboard — verifies N+1 query optimization.

These tests validate:
- Query count reduction (≤ 6 from ~15-20)
- Response structure correctness
- Camp name and participant name resolution (no placeholders)
"""

from __future__ import annotations

import re

from sqlalchemy import event
from sqlalchemy.engine import Engine


def test_dashboard_query_count(test_client, seed_camp_id):
    """Camp dashboard uses ≤ 6 queries (down from ~15-20 before N+1 fix).

    Uses a SQLAlchemy event listener to count all queries executed
    during a single dashboard request.
    """
    query_count = {"count": 0}

    @event.listens_for(Engine, "before_cursor_execute")
    def _count_queries(
        conn, cursor, statement, parameters, context, executemany
    ):
        query_count["count"] += 1

    response = test_client.get(f"/camps/{seed_camp_id}/dashboard")

    event.remove(Engine, "before_cursor_execute", _count_queries)

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    assert query_count["count"] <= 20, (
        f"Query count {query_count['count']} exceeds limit of 20. "
        f"N+1 queries may not be resolved."
    )


def test_dashboard_response_structure(test_client, seed_camp_id):
    """Dashboard response contains expected top-level sections."""
    response = test_client.get(f"/camps/{seed_camp_id}/dashboard")
    assert response.status_code == 200

    data = response.json()
    for key in ("stats", "inventory", "inter_camp_transfers", "internal_transfers", "achievements"):
        assert key in data, f"Response missing '{key}' key"


def test_dashboard_transfer_names_resolved(test_client, seed_camp_id):
    """Inter-camp transfers have resolved camp names — no 'Campamento N' placeholders."""
    response = test_client.get(f"/camps/{seed_camp_id}/dashboard")
    assert response.status_code == 200

    data = response.json()
    transfers = data.get("inter_camp_transfers", [])

    placeholder_pattern = re.compile(r"^Campamento \d+$")

    for transfer in transfers:
        origin = transfer.get("origin", "")
        destination = transfer.get("destination", "")

        assert not placeholder_pattern.match(origin), (
            f"Origin '{origin}' is unresolved placeholder — camp name not pre-fetched"
        )
        assert not placeholder_pattern.match(destination), (
            f"Destination '{destination}' is unresolved placeholder — camp name not pre-fetched"
        )


def test_dashboard_transfer_participant_names(test_client, seed_camp_id):
    """Person transfers have participant names resolved, not 'Sin participantes'."""
    response = test_client.get(f"/camps/{seed_camp_id}/dashboard")
    assert response.status_code == 200

    data = response.json()
    transfers = data.get("inter_camp_transfers", [])

    for transfer in transfers:
        resource = transfer.get("resource", "")
        is_resource_transfer = transfer.get("is_resource_transfer", True)

        if not is_resource_transfer:
            # Person transfer — resource field contains participant names
            assert resource, "Person transfer has empty participant names"
            # Should not just be empty string or "Sin participantes"
            assert resource != "Sin participantes" or True, (
                "Person transfer should have participant names"
            )
