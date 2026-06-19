"""Inference predictor for serving model predictions."""

from __future__ import annotations

import time
from typing import Any

from src.models.base import BaseModel
from src.utils.logging import get_logger
from src.utils.metrics import MetricTracker

logger = get_logger(__name__)


class PredictorError(Exception):
    """Raised on prediction errors."""


class Predictor:
    """Wraps a trained model for inference with batching and timing.

    Args:
        model: A trained ``BaseModel`` instance.
        max_batch_size: Maximum number of inputs per batch.
    """

    def __init__(self, model: BaseModel, max_batch_size: int = 64) -> None:
        if max_batch_size < 1:
            raise PredictorError(f"max_batch_size must be >= 1, got {max_batch_size}")
        self._model = model
        self._model.eval()
        self._max_batch_size = max_batch_size
        self._latency_tracker = MetricTracker(name="inference_latency_ms")
        self._call_count = 0

    @property
    def model_name(self) -> str:
        """Name of the underlying model."""
        return self._model.name

    @property
    def call_count(self) -> int:
        """Total number of predict calls made."""
        return self._call_count

    @property
    def latency_tracker(self) -> MetricTracker:
        """Access inference latency metrics."""
        return self._latency_tracker

    def predict(self, inputs: list[list[float]]) -> list[list[float]]:
        """Run inference on a batch of inputs.

        Args:
            inputs: Batch of input vectors.

        Returns:
            Batch of prediction vectors.

        Raises:
            PredictorError: If inputs are empty or model forward pass fails.
        """
        if not inputs:
            raise PredictorError("inputs must not be empty")

        self._call_count += 1
        all_outputs: list[list[float]] = []

        start = time.monotonic()

        for i in range(0, len(inputs), self._max_batch_size):
            batch = inputs[i : i + self._max_batch_size]
            try:
                outputs = self._model.forward(batch)
            except Exception as exc:
                raise PredictorError(f"Model forward pass failed: {exc}") from exc
            all_outputs.extend(outputs)

        elapsed_ms = (time.monotonic() - start) * 1000
        self._latency_tracker.update(elapsed_ms)

        logger.info(
            "Prediction #%d: %d samples in %.2f ms",
            self._call_count,
            len(inputs),
            elapsed_ms,
        )

        return all_outputs

    def predict_single(self, input_vec: list[float]) -> list[float]:
        """Run inference on a single input vector.

        Args:
            input_vec: A single input vector.

        Returns:
            The prediction vector.

        Raises:
            PredictorError: If the input is invalid.
        """
        if not input_vec:
            raise PredictorError("input vector must not be empty")
        results = self.predict([input_vec])
        return results[0]

    def stats(self) -> dict[str, Any]:
        """Return inference statistics.

        Returns:
            Dict with ``call_count``, ``total_latency_ms``, and
            ``avg_latency_ms`` (if calls have been made).
        """
        result: dict[str, Any] = {"call_count": self._call_count}
        if self._call_count > 0:
            result["avg_latency_ms"] = self._latency_tracker.mean
            result["min_latency_ms"] = self._latency_tracker.min
            result["max_latency_ms"] = self._latency_tracker.max
        return result
