"""Tests for src.inference.predictor."""

import pytest

from src.inference.predictor import Predictor, PredictorError
from src.models.base import SimpleNet


class TestPredictorInit:
    def test_valid_construction(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        assert pred.model_name == "SimpleNet"
        assert pred.call_count == 0

    def test_sets_model_to_eval(self) -> None:
        model = SimpleNet(2, 4, 1)
        model.train()
        _ = Predictor(model)
        assert model.training is False

    def test_invalid_batch_size(self) -> None:
        model = SimpleNet(2, 4, 1)
        with pytest.raises(PredictorError, match="max_batch_size"):
            Predictor(model, max_batch_size=0)


class TestPredictorPredict:
    def test_single_input(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        result = pred.predict([[1.0, 2.0]])
        assert len(result) == 1
        assert len(result[0]) == 1

    def test_batch_input(self) -> None:
        model = SimpleNet(3, 5, 2)
        pred = Predictor(model)
        inputs = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        result = pred.predict(inputs)
        assert len(result) == 3
        for row in result:
            assert len(row) == 2

    def test_empty_input_raises(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        with pytest.raises(PredictorError, match="empty"):
            pred.predict([])

    def test_call_count_increments(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        pred.predict([[1.0, 2.0]])
        pred.predict([[3.0, 4.0]])
        assert pred.call_count == 2

    def test_batching_with_small_max_batch(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model, max_batch_size=2)
        inputs = [[float(i), float(i)] for i in range(5)]
        result = pred.predict(inputs)
        assert len(result) == 5

    def test_latency_tracked(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        pred.predict([[1.0, 2.0]])
        assert pred.latency_tracker.count == 1
        assert pred.latency_tracker.last >= 0.0


class TestPredictorPredictSingle:
    def test_basic(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        result = pred.predict_single([1.0, 2.0])
        assert isinstance(result, list)
        assert len(result) == 1

    def test_empty_vector_raises(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        with pytest.raises(PredictorError, match="empty"):
            pred.predict_single([])


class TestPredictorStats:
    def test_stats_no_calls(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        stats = pred.stats()
        assert stats["call_count"] == 0
        assert "avg_latency_ms" not in stats

    def test_stats_after_calls(self) -> None:
        model = SimpleNet(2, 4, 1)
        pred = Predictor(model)
        pred.predict([[1.0, 2.0]])
        stats = pred.stats()
        assert stats["call_count"] == 1
        assert "avg_latency_ms" in stats
        assert stats["avg_latency_ms"] >= 0.0
