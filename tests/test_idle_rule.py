from types import SimpleNamespace

from backend.app.services.metrics import is_idle

# 5 KB/s over one hourly sample. Hardcoded on purpose: the test documents the rule.
NETWORK_LIMIT = 5 * 1024 * 3600


def sample(cpu=1.0, net_in=100, net_out=100):
    return SimpleNamespace(
        cpu_percent=cpu, network_in_bytes=net_in, network_out_bytes=net_out
    )


def test_idle_when_all_samples_below_thresholds():
    assert is_idle([sample(), sample(cpu=0.5)])


def test_not_idle_with_no_samples():
    assert not is_idle([])


def test_not_idle_with_a_single_sample():
    assert not is_idle([sample()])


def test_not_idle_if_any_sample_has_high_cpu():
    assert not is_idle([sample(), sample(cpu=40.0)])


def test_cpu_threshold_is_exclusive():
    assert not is_idle([sample(cpu=5.0), sample(cpu=5.0)])


def test_not_idle_if_network_exceeds_limit():
    assert not is_idle([sample(), sample(net_in=NETWORK_LIMIT, net_out=0)])


def test_network_in_and_out_are_added_together():
    half = NETWORK_LIMIT // 2
    # total exactly at the limit is not idle (strictly below is required)
    assert not is_idle([sample(), sample(net_in=half, net_out=half)])


def test_just_below_network_limit_is_idle():
    half = NETWORK_LIMIT // 2
    assert is_idle([sample(), sample(net_in=half - 1, net_out=half)])


def test_missing_cpu_reading_is_not_idle():
    assert not is_idle([sample(), sample(cpu=None)])


def test_missing_network_values_count_as_zero():
    assert is_idle([sample(net_in=None, net_out=None), sample()])