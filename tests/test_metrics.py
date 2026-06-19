"""Tests for src.utils.metrics."""


import pytest

from src.utils.metrics import MetricTracker


class TestMetricTrackerUpdate:
    def test_update_int(self) -> None:
        t = MetricTracker(name="x")
        t.update(1)
        assert t.count == 1

    def test_update_float(self) -> None:
        t = MetricTracker(name="x")
        t.update(3.14)
        assert t.count == 1

    def test_update_nan_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError, match="finite"):
            t.update(float("nan"))

    def test_update_inf_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError, match="finite"):
            t.update(float("inf"))

    def test_update_non_numeric_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError, match="numeric"):
            t.update("hello")  # type: ignore[arg-type]


class TestMetricTrackerProperties:
    def test_mean(self) -> None:
        t = MetricTracker(name="loss")
        t.update(2.0)
        t.update(4.0)
        assert t.mean == pytest.approx(3.0)

    def test_last(self) -> None:
        t = MetricTracker(name="x")
        t.update(1.0)
        t.update(5.0)
        assert t.last == 5.0

    def test_min_max(self) -> None:
        t = MetricTracker(name="x")
        for v in [3.0, 1.0, 4.0, 1.5]:
            t.update(v)
        assert t.min == 1.0
        assert t.max == 4.0

    def test_count(self) -> None:
        t = MetricTracker(name="x")
        assert t.count == 0
        t.update(1.0)
        t.update(2.0)
        assert t.count == 2


class TestMetricTrackerEmpty:
    def test_mean_empty_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError, match="No values"):
            _ = t.mean

    def test_last_empty_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError, match="No values"):
            _ = t.last

    def test_min_empty_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError, match="No values"):
            _ = t.min

    def test_max_empty_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError, match="No values"):
            _ = t.max


class TestMetricTrackerReset:
    def test_reset_clears_values(self) -> None:
        t = MetricTracker(name="x")
        t.update(1.0)
        t.update(2.0)
        t.reset()
        assert t.count == 0

    def test_reset_then_update(self) -> None:
        t = MetricTracker(name="x")
        t.update(10.0)
        t.reset()
        t.update(5.0)
        assert t.mean == 5.0


class TestMetricTrackerToDict:
    def test_to_dict(self) -> None:
        t = MetricTracker(name="loss")
        t.update(1.0)
        t.update(3.0)
        d = t.to_dict()
        assert d["count"] == 2.0
        assert d["mean"] == pytest.approx(2.0)
        assert d["min"] == 1.0
        assert d["max"] == 3.0
        assert d["last"] == 3.0

    def test_to_dict_empty_raises(self) -> None:
        t = MetricTracker(name="x")
        with pytest.raises(ValueError):
            t.to_dict()
