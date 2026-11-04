from types import SimpleNamespace

import pytest

from backend.app.services.automation import is_automation_eligible


def vm(tags):
    """Stand-in for a Resource row; the safety gate only reads .tags."""
    return SimpleNamespace(tags=tags)


def test_eligible_when_development_and_autoshutdown_true():
    assert is_automation_eligible(
        vm({"Environment": "Development", "AutoShutdown": "True"})
    )


@pytest.mark.parametrize(
    "tags",
    [
        {"Environment": "Production", "AutoShutdown": "True"},
        {"Environment": "Staging", "AutoShutdown": "True"},
        {"Environment": "Development", "AutoShutdown": "False"},
        {"Environment": "Development"},  # AutoShutdown missing
        {"AutoShutdown": "True"},  # Environment missing
        {},  # no tags at all
        None,  # empty tags column
        {"Environment": "", "AutoShutdown": ""},
        {"Environment": "Development", "AutoShutdown": "yes"},  # only "true" counts
        [],  # tags stored as the wrong type
        "Environment=Development",  # tags stored as a string
        ["Development"],
        
    ],
)
def test_excluded_unless_explicitly_safe(tags):
    assert not is_automation_eligible(vm(tags))


@pytest.mark.parametrize(
    "tags",
    [
        {"Environment": "development", "AutoShutdown": "true"},
        {"Environment": " Development ", "AutoShutdown": " TRUE "},
    ],
)
def test_case_and_whitespace_are_normalised(tags):
    assert is_automation_eligible(vm(tags))