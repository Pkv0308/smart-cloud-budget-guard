import pytest

from backend.app.services.cost_estimator import get_budget_state


def budget(limit=100.0, warning=75.0, critical=90.0):
    return {
        "monthly_limit": limit,
        "warning_threshold_percent": warning,
        "critical_threshold_percent": critical,
    }


@pytest.mark.parametrize(
    "spend, expected",
    [
        (0, "normal"),
        (74, "normal"),
        (75, "warning"),  # exactly at the warning threshold
        (89, "warning"),
        (90, "critical"),  # exactly at the critical threshold
        (100, "critical"),
        (250, "critical"),  # over budget
    ],
)
def test_state_thresholds(spend, expected):
    assert get_budget_state(budget(), spend) == expected


def test_zero_limit_is_normal():
    assert get_budget_state(budget(limit=0), 50) == "normal"


def test_custom_thresholds():
    b = budget(limit=200, warning=50, critical=80)
    assert get_budget_state(b, 99) == "normal"
    assert get_budget_state(b, 100) == "warning"
    assert get_budget_state(b, 160) == "critical"