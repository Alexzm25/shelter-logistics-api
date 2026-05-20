from src.persons.enums.health_work_restrictions import is_valid_health_transition


def test_allowed_transitions_from_sano():
    ok, msg = is_valid_health_transition("SANO", "HERIDO")
    assert ok, msg
    ok, msg = is_valid_health_transition("SANO", "ENFERMO")
    assert ok, msg
    ok, msg = is_valid_health_transition("SANO", "MUERTO")
    assert ok, msg
    ok, msg = is_valid_health_transition("SANO", "SANO")
    assert ok, msg


def test_allowed_transitions_from_herido():
    ok, msg = is_valid_health_transition("HERIDO", "ENFERMO")
    assert ok, msg
    ok, msg = is_valid_health_transition("HERIDO", "SANO")
    assert ok, msg
    ok, msg = is_valid_health_transition("HERIDO", "MUERTO")
    assert ok, msg
    ok, msg = is_valid_health_transition("HERIDO", "HERIDO")
    assert ok, msg


def test_allowed_transitions_from_enfermo():
    ok, msg = is_valid_health_transition("ENFERMO", "HERIDO")
    assert ok, msg
    ok, msg = is_valid_health_transition("ENFERMO", "SANO")
    assert ok, msg
    ok, msg = is_valid_health_transition("ENFERMO", "MUERTO")
    assert ok, msg
    ok, msg = is_valid_health_transition("ENFERMO", "ENFERMO")
    assert ok, msg


def test_disallowed_transitions_from_muerto():
    ok, msg = is_valid_health_transition("MUERTO", "SANO")
    assert not ok
    ok, msg = is_valid_health_transition("MUERTO", "HERIDO")
    assert not ok
    ok, msg = is_valid_health_transition("MUERTO", "ENFERMO")
    assert not ok


def test_invalid_states():
    ok, msg = is_valid_health_transition("DESCONOCIDO", "SANO")
    assert not ok
    ok, msg = is_valid_health_transition("SANO", "DESCONOCIDO")
    assert not ok
