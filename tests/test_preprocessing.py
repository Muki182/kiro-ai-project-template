"""Tests for src.data.preprocessing."""

import pytest

from src.data.preprocessing import Normalizer, Pipeline, Tokenizer


class TestNormalizerInit:
    def test_valid_construction(self) -> None:
        n = Normalizer(fields=["x"], means={"x": 0.0}, stds={"x": 1.0})
        assert n is not None

    def test_empty_fields_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Normalizer(fields=[], means={}, stds={})

    def test_missing_mean_raises(self) -> None:
        with pytest.raises(ValueError, match="Missing mean"):
            Normalizer(fields=["x"], means={}, stds={"x": 1.0})

    def test_missing_std_raises(self) -> None:
        with pytest.raises(ValueError, match="Missing std"):
            Normalizer(fields=["x"], means={"x": 0.0}, stds={})

    def test_zero_std_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            Normalizer(fields=["x"], means={"x": 0.0}, stds={"x": 0.0})


class TestNormalizerCall:
    def test_normalize(self) -> None:
        n = Normalizer(fields=["x"], means={"x": 10.0}, stds={"x": 2.0})
        result = n({"x": 12.0, "y": "keep"})
        assert result["x"] == pytest.approx(1.0)
        assert result["y"] == "keep"

    def test_missing_field_raises(self) -> None:
        n = Normalizer(fields=["x"], means={"x": 0.0}, stds={"x": 1.0})
        with pytest.raises(KeyError, match="not found"):
            n({"y": 1})

    def test_non_numeric_raises(self) -> None:
        n = Normalizer(fields=["x"], means={"x": 0.0}, stds={"x": 1.0})
        with pytest.raises(TypeError, match="numeric"):
            n({"x": "hello"})

    def test_does_not_mutate_input(self) -> None:
        n = Normalizer(fields=["x"], means={"x": 0.0}, stds={"x": 1.0})
        original = {"x": 5.0}
        _ = n(original)
        assert original["x"] == 5.0


class TestNormalizerFit:
    def test_fit_basic(self) -> None:
        records = [{"x": 2.0}, {"x": 4.0}, {"x": 6.0}]
        n = Normalizer.fit(records, fields=["x"])
        result = n({"x": 4.0})
        assert result["x"] == pytest.approx(0.0)

    def test_fit_empty_records_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Normalizer.fit([], fields=["x"])

    def test_fit_empty_fields_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Normalizer.fit([{"x": 1}], fields=[])

    def test_fit_missing_field_raises(self) -> None:
        with pytest.raises(ValueError, match="missing"):
            Normalizer.fit([{"y": 1}], fields=["x"])

    def test_fit_non_numeric_raises(self) -> None:
        with pytest.raises(ValueError, match="Non-numeric"):
            Normalizer.fit([{"x": "a"}], fields=["x"])

    def test_fit_single_record(self) -> None:
        n = Normalizer.fit([{"x": 5.0}], fields=["x"])
        result = n({"x": 5.0})
        assert result["x"] == pytest.approx(0.0)


class TestTokenizer:
    def test_basic_tokenization(self) -> None:
        t = Tokenizer(field="text")
        result = t({"text": "hello world foo"})
        assert result["text_tokens"] == ["hello", "world", "foo"]
        assert result["text"] == "hello world foo"

    def test_custom_output_field(self) -> None:
        t = Tokenizer(field="text", output_field="tokens")
        result = t({"text": "a b"})
        assert "tokens" in result

    def test_truncation(self) -> None:
        t = Tokenizer(field="text", max_length=2)
        result = t({"text": "a b c d e"})
        assert result["text_tokens"] == ["a", "b"]

    def test_missing_field_raises(self) -> None:
        t = Tokenizer(field="text")
        with pytest.raises(KeyError, match="not found"):
            t({"other": "x"})

    def test_non_string_raises(self) -> None:
        t = Tokenizer(field="text")
        with pytest.raises(TypeError, match="string"):
            t({"text": 123})

    def test_empty_field_name_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Tokenizer(field="")

    def test_max_length_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="max_length"):
            Tokenizer(field="text", max_length=0)

    def test_does_not_mutate_input(self) -> None:
        t = Tokenizer(field="text")
        original = {"text": "a b c"}
        _ = t(original)
        assert "text_tokens" not in original


class TestPipeline:
    def test_empty_pipeline(self) -> None:
        p = Pipeline()
        assert len(p) == 0
        result = p({"x": 1})
        assert result == {"x": 1}

    def test_single_transform(self) -> None:
        t = Tokenizer(field="text")
        p = Pipeline([t])
        result = p({"text": "hello world"})
        assert result["text_tokens"] == ["hello", "world"]

    def test_chained_transforms(self) -> None:
        norm = Normalizer(fields=["val"], means={"val": 5.0}, stds={"val": 2.0})
        tok = Tokenizer(field="text")
        p = Pipeline([norm, tok])
        result = p({"val": 7.0, "text": "a b"})
        assert result["val"] == pytest.approx(1.0)
        assert result["text_tokens"] == ["a", "b"]

    def test_add_method(self) -> None:
        p = Pipeline()
        tok = Tokenizer(field="text")
        p.add(tok)
        assert len(p) == 1
        result = p({"text": "x y"})
        assert result["text_tokens"] == ["x", "y"]

    def test_add_returns_self(self) -> None:
        p = Pipeline()
        result = p.add(Tokenizer(field="t"))
        assert result is p
