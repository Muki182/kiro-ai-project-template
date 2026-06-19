"""Lightweight metric tracking utilities."""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass
class MetricTracker:
    """Accumulates scalar values and computes summary statistics.

    Example::

        tracker = MetricTracker(name="loss")
        tracker.update(0.5)
        tracker.update(0.3)
        print(tracker.mean)  # 0.4
    """

    name: str
    _values: list[float] = field(default_factory=list, repr=False)

    def update(self, value: float) -> None:
        """Record a single scalar value.

        Args:
            value: The metric value to record.

        Raises:
            ValueError: If *value* is not finite.
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected a numeric value, got {type(value).__name__}")
        import math

        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"Metric value must be finite, got {value}")
        self._values.append(float(value))

    @property
    def count(self) -> int:
        """Number of recorded values."""
        return len(self._values)

    @property
    def mean(self) -> float:
        """Arithmetic mean of recorded values.

        Raises:
            ValueError: If no values have been recorded.
        """
        if not self._values:
            raise ValueError(f"No values recorded for metric '{self.name}'")
        return statistics.mean(self._values)

    @property
    def last(self) -> float:
        """Most recently recorded value.

        Raises:
            ValueError: If no values have been recorded.
        """
        if not self._values:
            raise ValueError(f"No values recorded for metric '{self.name}'")
        return self._values[-1]

    @property
    def min(self) -> float:
        """Minimum recorded value.

        Raises:
            ValueError: If no values have been recorded.
        """
        if not self._values:
            raise ValueError(f"No values recorded for metric '{self.name}'")
        return min(self._values)

    @property
    def max(self) -> float:
        """Maximum recorded value.

        Raises:
            ValueError: If no values have been recorded.
        """
        if not self._values:
            raise ValueError(f"No values recorded for metric '{self.name}'")
        return max(self._values)

    def reset(self) -> None:
        """Clear all recorded values."""
        self._values.clear()

    def to_dict(self) -> dict[str, float]:
        """Return summary statistics as a dictionary.

        Returns:
            Dict with keys ``count``, ``mean``, ``min``, ``max``, ``last``.

        Raises:
            ValueError: If no values have been recorded.
        """
        return {
            "count": float(self.count),
            "mean": self.mean,
            "min": self.min,
            "max": self.max,
            "last": self.last,
        }
