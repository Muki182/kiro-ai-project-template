"""Tests for src.utils.config."""

import pytest

from src.utils.config import ConfigError, ConfigManager


class TestConfigManagerFromDict:
    def test_basic_get(self) -> None:
        cfg = ConfigManager.from_dict({"learning_rate": 0.001, "epochs": 10})
        assert cfg.get("learning_rate") == 0.001
        assert cfg.get("epochs") == 10

    def test_get_missing_returns_default(self) -> None:
        cfg = ConfigManager.from_dict({"a": 1})
        assert cfg.get("b") is None
        assert cfg.get("b", 42) == 42

    def test_nested_dot_access(self) -> None:
        cfg = ConfigManager.from_dict({
            "model": {"hidden_size": 256, "layers": 4}
        })
        assert cfg.get("model.hidden_size") == 256
        assert cfg.get("model.layers") == 4

    def test_nested_dot_access_missing(self) -> None:
        cfg = ConfigManager.from_dict({"model": {"a": 1}})
        assert cfg.get("model.b") is None
        assert cfg.get("x.y.z", "fallback") == "fallback"

    def test_contains(self) -> None:
        cfg = ConfigManager.from_dict({"a": 1})
        assert "a" in cfg
        assert "b" not in cfg

    def test_contains_none_value(self) -> None:
        cfg = ConfigManager.from_dict({"optional_feature": None})
        assert "optional_feature" in cfg


class TestConfigManagerSet:
    def test_set_simple_key(self) -> None:
        cfg = ConfigManager.from_dict({})
        cfg.set("lr", 0.01)
        assert cfg.get("lr") == 0.01

    def test_set_nested_key(self) -> None:
        cfg = ConfigManager.from_dict({})
        cfg.set("model.hidden", 128)
        assert cfg.get("model.hidden") == 128

    def test_set_overwrites_existing(self) -> None:
        cfg = ConfigManager.from_dict({"lr": 0.1})
        cfg.set("lr", 0.01)
        assert cfg.get("lr") == 0.01


class TestConfigManagerMerge:
    def test_merge_adds_keys(self) -> None:
        a = ConfigManager.from_dict({"x": 1})
        b = ConfigManager.from_dict({"y": 2})
        merged = a.merge(b)
        assert merged.get("x") == 1
        assert merged.get("y") == 2

    def test_merge_override_takes_precedence(self) -> None:
        a = ConfigManager.from_dict({"x": 1})
        b = ConfigManager.from_dict({"x": 99})
        merged = a.merge(b)
        assert merged.get("x") == 99

    def test_merge_deep(self) -> None:
        a = ConfigManager.from_dict({"m": {"a": 1, "b": 2}})
        b = ConfigManager.from_dict({"m": {"b": 99, "c": 3}})
        merged = a.merge(b)
        assert merged.get("m.a") == 1
        assert merged.get("m.b") == 99
        assert merged.get("m.c") == 3


class TestConfigManagerFromFile:
    def test_file_not_found(self) -> None:
        with pytest.raises(ConfigError, match="not found"):
            ConfigManager.from_file("/nonexistent/path.yaml")

    def test_load_valid_yaml(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "cfg.yaml"
        f.write_text("lr: 0.01\nepochs: 5\n")
        cfg = ConfigManager.from_file(f)
        assert cfg.get("lr") == 0.01
        assert cfg.get("epochs") == 5

    def test_invalid_yaml(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "bad.yaml"
        f.write_text(":\n  :\n    : [")
        with pytest.raises(ConfigError, match="Invalid YAML"):
            ConfigManager.from_file(f)

    def test_non_dict_yaml(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        f = tmp_path / "list.yaml"
        f.write_text("- a\n- b\n")
        with pytest.raises(ConfigError, match="Expected a YAML mapping"):
            ConfigManager.from_file(f)


class TestToDict:
    def test_to_dict_returns_copy(self) -> None:
        cfg = ConfigManager.from_dict({"a": 1})
        d = cfg.to_dict()
        d["a"] = 999
        assert cfg.get("a") == 1


class TestRepr:
    def test_repr(self) -> None:
        cfg = ConfigManager.from_dict({"a": 1})
        assert "ConfigManager" in repr(cfg)
