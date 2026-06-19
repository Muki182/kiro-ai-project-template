"""Data preprocessing pipeline with composable transforms."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from src.utils.logging import get_logger

logger = get_logger(__name__)


class Transform(Protocol):
    """Protocol for composable data transforms."""

    def __call__(self, record: dict[str, Any]) -> dict[str, Any]: ...


class Normalizer:
    """Normalize numeric fields to zero mean and unit variance.

    Args:
        fields: List of field names to normalize.
        means: Pre-computed means per field.
        stds: Pre-computed standard deviations per field.
    """

    def __init__(
        self,
        fields: list[str],
        means: dict[str, float],
        stds: dict[str, float],
    ) -> None:
        if not fields:
            raise ValueError("fields must not be empty")
        for f in fields:
            if f not in means:
                raise ValueError(f"Missing mean for field '{f}'")
            if f not in stds:
                raise ValueError(f"Missing std for field '{f}'")
            if stds[f] <= 0:
                raise ValueError(f"Standard deviation for '{f}' must be positive, got {stds[f]}")
        self._fields = list(fields)
        self._means = dict(means)
        self._stds = dict(stds)

    def __call__(self, record: dict[str, Any]) -> dict[str, Any]:
        """Apply normalization to the record's numeric fields.

        Args:
            record: Input data record.

        Returns:
            A new record with normalized fields.

        Raises:
            KeyError: If a required field is missing from the record.
            TypeError: If a field value is not numeric.
        """
        result = dict(record)
        for f in self._fields:
            if f not in result:
                raise KeyError(f"Field '{f}' not found in record")
            val = result[f]
            if not isinstance(val, (int, float)):
                raise TypeError(
                    f"Expected numeric value for field '{f}', got {type(val).__name__}"
                )
            result[f] = (float(val) - self._means[f]) / self._stds[f]
        return result

    @classmethod
    def fit(cls, records: Sequence[dict[str, Any]], fields: list[str]) -> Normalizer:
        """Compute means and stds from a sequence of records.

        Args:
            records: Training records to compute statistics from.
            fields: List of field names to normalize.

        Returns:
            A fitted ``Normalizer`` instance.

        Raises:
            ValueError: If records is empty or fields contain non-numeric values.
        """
        if not records:
            raise ValueError("Cannot fit on empty records")
        if not fields:
            raise ValueError("fields must not be empty")

        import statistics

        means: dict[str, float] = {}
        stds: dict[str, float] = {}

        for f in fields:
            values = []
            for r in records:
                if f not in r:
                    raise ValueError(f"Field '{f}' missing from record")
                v = r[f]
                if not isinstance(v, (int, float)):
                    raise ValueError(f"Non-numeric value for field '{f}': {v!r}")
                values.append(float(v))

            means[f] = statistics.mean(values)
            if len(values) > 1:
                stds[f] = statistics.stdev(values)
            else:
                stds[f] = 1.0

        return cls(fields=fields, means=means, stds=stds)


class Tokenizer:
    """Simple whitespace tokenizer that converts text fields into token lists.

    Args:
        field: Name of the text field to tokenize.
        output_field: Name of the output field for tokens (defaults to ``{field}_tokens``).
        max_length: Maximum number of tokens to keep (truncation).
    """

    def __init__(
        self,
        field: str,
        output_field: str | None = None,
        max_length: int = 512,
    ) -> None:
        if not field:
            raise ValueError("field must not be empty")
        if max_length < 1:
            raise ValueError(f"max_length must be >= 1, got {max_length}")
        self._field = field
        self._output_field = output_field or f"{field}_tokens"
        self._max_length = max_length

    def __call__(self, record: dict[str, Any]) -> dict[str, Any]:
        """Tokenize the text field in the record.

        Args:
            record: Input data record.

        Returns:
            A new record with the tokenized field added.

        Raises:
            KeyError: If the text field is missing.
            TypeError: If the text field is not a string.
        """
        if self._field not in record:
            raise KeyError(f"Field '{self._field}' not found in record")

        text = record[self._field]
        if not isinstance(text, str):
            raise TypeError(
                f"Expected string for field '{self._field}', got {type(text).__name__}"
            )

        tokens = text.split()[: self._max_length]
        result = dict(record)
        result[self._output_field] = tokens
        return result


class Pipeline:
    """Compose multiple transforms into a sequential pipeline.

    Example::

        pipe = Pipeline([normalizer, tokenizer])
        processed = pipe(record)
    """

    def __init__(self, transforms: list[Transform] | None = None) -> None:
        self._transforms: list[Transform] = list(transforms or [])

    def add(self, transform: Transform) -> Pipeline:
        """Append a transform and return self for chaining.

        Args:
            transform: A callable transform.

        Returns:
            This pipeline instance.
        """
        self._transforms.append(transform)
        return self

    def __call__(self, record: dict[str, Any]) -> dict[str, Any]:
        """Apply all transforms in sequence.

        Args:
            record: Input data record.

        Returns:
            The transformed record.
        """
        result = dict(record)
        for transform in self._transforms:
            result = transform(result)
        return result

    def __len__(self) -> int:
        return len(self._transforms)
