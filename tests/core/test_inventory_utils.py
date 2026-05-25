from src.core.inventory_utils import resolve_alert_level


def test_alert_critical_when_below_minimum():
    assert resolve_alert_level(5, 10) == "critical"


def test_alert_critical_when_equal_to_minimum():
    assert resolve_alert_level(10, 10) == "critical"


def test_alert_warning_when_above_minimum_but_below_threshold():
    assert resolve_alert_level(12, 10) == "warning"


def test_alert_normal_when_above_threshold():
    assert resolve_alert_level(20, 10) == "normal"


def test_alert_warning_at_threshold_boundary():
    assert resolve_alert_level(15, 10) == "warning"


def test_alert_normal_at_threshold_plus_one():
    assert resolve_alert_level(16, 10) == "normal"
