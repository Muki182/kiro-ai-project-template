"""Dataset loading and management."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

from src.utils.logging import get_logger

logger = get_logger(__name__)


class DatasetError(Exception):
    """Raised when dataset loading or access fails."""


class Dataset:
    """In-memory dataset backed by a list of record dicts.

    Supports loading from JSON-lines and CSV files, slicing, iteration,
    and train/validation splitting.

    Example::

        ds = Dataset.from_jsonl("data/train.jsonl")
        for record in ds:
            process(record)
    """

    def __init__(self, records: Sequence[dict[str, Any]]) -> None:
        if not isinstance(records, (list, tuple)):
            raise DatasetError("records must be a list or tuple of dicts")
        self._records: list[dict[str, Any]] = list(records)

    @classmethod
    def from_jsonl(cls, path: str | Path) -> Dataset:
        """Load a dataset from a JSON-lines file.

        Args:
            path: Path to a ``.jsonl`` file (one JSON object per line).

        Returns:
            A ``Dataset`` instance.

        Raises:
            DatasetError: If the file does not exist or contains invalid JSON.
        """
        filepath = Path(path)
        if not filepath.exists():
            raise DatasetError(f"File not found: {filepath}")

        records: list[dict[str, Any]] = []
        try:
            with open(filepath) as f:
                for lineno, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        raise DatasetError(
                            f"Expected JSON object at line {lineno}, got {type(obj).__name__}"
                        )
                    records.append(obj)
        except json.JSONDecodeError as exc:
            raise DatasetError(f"Invalid JSON in {filepath}: {exc}") from exc

        logger.info("Loaded %d records from %s", len(records), filepath)
        return cls(records)

    @classmethod
    def from_csv(cls, path: str | Path) -> Dataset:
        """Load a dataset from a CSV file with a header row.

        Args:
            path: Path to a ``.csv`` file.

        Returns:
            A ``Dataset`` instance.

        Raises:
            DatasetError: If the file does not exist or is empty.
        """
        filepath = Path(path)
        if not filepath.exists():
            raise DatasetError(f"File not found: {filepath}")

        records: list[dict[str, Any]] = []
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))

        if not records:
            raise DatasetError(f"CSV file is empty: {filepath}")

        logger.info("Loaded %d records from %s", len(records), filepath)
        return cls(records)

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int) -> dict[str, Any]:
        if not isinstance(index, int):
            raise TypeError(f"Index must be an integer, got {type(index).__name__}")
        if index < 0 or index >= len(self._records):
            raise IndexError(f"Index {index} out of range for dataset of size {len(self)}")
        return self._records[index]

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self._records)

    def split(
        self, ratio: float = 0.8, seed: int | None = None
    ) -> tuple[Dataset, Dataset]:
        """Split into train and validation datasets.

        Args:
            ratio: Fraction of data for the first (train) split. Must be in (0, 1).
            seed: Optional random seed for reproducibility.

        Returns:
            A tuple ``(train_dataset, val_dataset)``.

        Raises:
            ValueError: If *ratio* is not in (0, 1) or dataset is too small.
        """
        if not 0 < ratio < 1:
            raise ValueError(f"ratio must be in (0, 1), got {ratio}")
        if len(self._records) < 2:
            raise ValueError("Dataset must have at least 2 records to split")

        import random

        rng = random.Random(seed)
        shuffled = list(self._records)
        rng.shuffle(shuffled)

        split_idx = max(1, int(len(shuffled) * ratio))
        return Dataset(shuffled[:split_idx]), Dataset(shuffled[split_idx:])

    def select_columns(self, columns: list[str]) -> Dataset:
        """Return a new dataset with only the specified columns.

        Args:
            columns: List of column names to keep.

        Returns:
            A new ``Dataset`` with filtered columns.

        Raises:
            DatasetError: If any column is not found in the records.
        """
        if not columns:
            raise DatasetError("columns list must not be empty")

        filtered: list[dict[str, Any]] = []
        for i, record in enumerate(self._records):
            row: dict[str, Any] = {}
            for col in columns:
                if col not in record:
                    raise DatasetError(f"Column '{col}' not found in record {i}")
                row[col] = record[col]
            filtered.append(row)
        return Dataset(filtered)
