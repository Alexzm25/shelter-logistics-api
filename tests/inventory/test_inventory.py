"""Integration tests for inventory endpoint with pagination.

Validates:
- Pagination with page/size params and X-Total-Count header
- Category filtering with pagination
"""

from __future__ import annotations

from unittest.mock import patch

from src.auth.schemas.user_profile import UserProfileResponse


def _make_mock_user() -> UserProfileResponse:
    return UserProfileResponse(
        username="test_admin",
        user_id=1,
        person_id=1,
        camp_id=1,
        profession_name="MEDICO",
        role_name="ADMINISTRADOR SISTEMA",
    )


def _auth_patch():
    return patch(
        "src.auth.service.auth_service.AuthService.get_current_user_profile",
        return_value=_make_mock_user(),
    )


def test_inventory_pagination_default(test_client, seed_camp_id):
    with _auth_patch():
        response = test_client.get(
            f"/inventory/camp/{seed_camp_id}",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    items = response.json()
    assert isinstance(items, list), f"Expected list, got {type(items)}"
    assert len(items) <= 10, f"Expected ≤ 10 default items, got {len(items)}"
    assert "x-total-count" in response.headers, (
        "Response missing X-Total-Count header"
    )
    total = int(response.headers["x-total-count"])
    assert total >= 0, f"X-Total-Count should be ≥ 0, got {total}"


def test_inventory_pagination_custom_size(test_client, seed_camp_id):
    with _auth_patch():
        response = test_client.get(
            f"/inventory/camp/{seed_camp_id}?page=1&size=5",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    items = response.json()
    assert len(items) <= 5, f"Expected ≤ 5 items, got {len(items)}"
    assert "x-total-count" in response.headers


def test_inventory_pagination_empty_page(test_client, seed_camp_id):
    with _auth_patch():
        response = test_client.get(
            f"/inventory/camp/{seed_camp_id}?page=999&size=10",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 0, f"Empty page should return [], got {len(items)} items"
    assert "x-total-count" in response.headers
    total = int(response.headers["x-total-count"])
    assert total >= 0


def test_inventory_pagination_category_filter(test_client, seed_camp_id):
    with _auth_patch():
        response = test_client.get(
            f"/inventory/camp/{seed_camp_id}?page=1&size=10&category=MEDICINAS",
            cookies={"access_token": "fake-token"},
        )
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert "x-total-count" in response.headers
    for item in items:
        assert item["category"] == "MEDICINAS", (
            f"Expected MEDICINAS, got {item['category']}"
        )
