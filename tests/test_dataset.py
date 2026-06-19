"""Tests for src.data.dataset."""

import json

import pytest

from src.data.dataset import Dataset, DatasetError


class TestDatasetInit:
    def test_from_list(self) -> None:
        ds = Dataset([{"a": 1}, {"a": 2}])
        assert len(ds) == 2

    def test_empty_dataset(self) -> None:
        ds = Dataset([])
        assert len(ds) == 0

    def test_non_list_raises(self) -> None:
        with pytest.raises(DatasetError, match="list or tuple"):
            Dataset("not a list")  # type: ignore[arg-type]


class TestDatasetGetItem:
    def test_valid_index(self) -> None:
        ds = Dataset([{"x": 10}, {"x": 20}])
        assert ds[0] == {"x": 10}
        assert ds[1] == {"x": 20}

    def test_out_of_range(self) -> None:
        ds = Dataset([{"x": 1}])
        with pytest.raises(IndexError):
            _ = ds[5]

    def test_negative_index_raises(self) -> None:
        ds = Dataset([{"x": 1}])
        with pytest.raises(IndexError):
            _ = ds[-1]

    def test_non_int_index_raises(self) -> None:
        ds = Dataset([{"x": 1}])
        with pytest.raises(TypeError):
            _ = ds["0"]  # type: ignore[index]


class TestDatasetIteration:
    def test_iteration(self) -> None:
        records = [{"a": i} for i in range(5)]
        ds = Dataset(records)
        collected = list(ds)
        assert collected == records


class TestDatasetFromJsonl:
    def test_load_valid(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "data.jsonl"
        lines = [json.dumps({"x": i}) for i in range(3)]
        f.write_text("\n".join(lines))
        ds = Dataset.from_jsonl(f)
        assert len(ds) == 3
        assert ds[0] == {"x": 0}

    def test_file_not_found(self) -> None:
        with pytest.raises(DatasetError, match="not found"):
            Dataset.from_jsonl("/nonexistent.jsonl")

    def test_invalid_json(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "bad.jsonl"
        f.write_text("not json\n")
        with pytest.raises(DatasetError, match="Invalid JSON"):
            Dataset.from_jsonl(f)

    def test_non_dict_json(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "arr.jsonl"
        f.write_text("[1, 2, 3]\n")
        with pytest.raises(DatasetError, match="Expected JSON object"):
            Dataset.from_jsonl(f)

    def test_skips_blank_lines(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "blank.jsonl"
        f.write_text('{"a": 1}\n\n{"a": 2}\n')
        ds = Dataset.from_jsonl(f)
        assert len(ds) == 2


class TestDatasetFromCsv:
    def test_load_valid(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "data.csv"
        f.write_text("name,value\nalice,10\nbob,20\n")
        ds = Dataset.from_csv(f)
        assert len(ds) == 2
        assert ds[0]["name"] == "alice"

    def test_file_not_found(self) -> None:
        with pytest.raises(DatasetError, match="not found"):
            Dataset.from_csv("/nonexistent.csv")

    def test_empty_csv(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "empty.csv"
        f.write_text("col1,col2\n")
        with pytest.raises(DatasetError, match="empty"):
            Dataset.from_csv(f)


class TestDatasetSplit:
    def test_split_basic(self) -> None:
        ds = Dataset([{"x": i} for i in range(10)])
        train, val = ds.split(ratio=0.8, seed=42)
        assert len(train) + len(val) == 10
        assert len(train) == 8
        assert len(val) == 2

    def test_split_reproducible(self) -> None:
        ds = Dataset([{"x": i} for i in range(10)])
        t1, v1 = ds.split(ratio=0.7, seed=123)
        t2, v2 = ds.split(ratio=0.7, seed=123)
        assert list(t1) == list(t2)
        assert list(v1) == list(v2)

    def test_split_invalid_ratio(self) -> None:
        ds = Dataset([{"x": 1}, {"x": 2}])
        with pytest.raises(ValueError, match="ratio"):
            ds.split(ratio=0.0)
        with pytest.raises(ValueError, match="ratio"):
            ds.split(ratio=1.0)

    def test_split_too_small(self) -> None:
        ds = Dataset([{"x": 1}])
        with pytest.raises(ValueError, match="at least 2"):
            ds.split(ratio=0.5)


class TestDatasetSelectColumns:
    def test_select_valid(self) -> None:
        ds = Dataset([{"a": 1, "b": 2, "c": 3}])
        filtered = ds.select_columns(["a", "c"])
        assert filtered[0] == {"a": 1, "c": 3}

    def test_select_missing_column(self) -> None:
        ds = Dataset([{"a": 1}])
        with pytest.raises(DatasetError, match="not found"):
            ds.select_columns(["b"])

    def test_select_empty_columns(self) -> None:
        ds = Dataset([{"a": 1}])
        with pytest.raises(DatasetError, match="empty"):
            ds.select_columns([])
