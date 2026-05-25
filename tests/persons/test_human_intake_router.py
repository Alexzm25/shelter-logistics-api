"""Verify camp_id is no longer hardcoded in human_intake_router endpoints."""

import ast
from pathlib import Path

import pytest


def _get_router_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "src" / "persons" / "router" / "human_intake_router.py"


def _get_router_source() -> str:
    return _get_router_path().read_text(encoding="utf-8")


def test_no_camp_id_query_default():
    source = _get_router_source()
    assert "Query(default=1" not in source


def test_get_dashboard_uses_current_user_camp_id():
    source = _get_router_source()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_dashboard":
            func_source = ast.get_source_segment(source, node) or ""
            assert "current_user.camp_id" in func_source
            return

    pytest.fail("get_dashboard function not found")


def test_get_available_people_uses_current_user_camp_id():
    source = _get_router_source()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_available_people_for_profession":
            func_source = ast.get_source_segment(source, node) or ""
            assert "current_user.camp_id" in func_source
            return

    pytest.fail("get_available_people_for_profession function not found")


def test_get_person_by_id_card_uses_current_user_camp_id():
    source = _get_router_source()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_person_by_id_card":
            func_source = ast.get_source_segment(source, node) or ""
            assert "current_user.camp_id" in func_source
            return

    pytest.fail("get_person_by_id_card function not found")
