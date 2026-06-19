"""Configuration management via YAML files.

All hyperparameters and paths are managed through config/ YAML files.
No hard-coded values allowed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.utils.logging import get_logger

logger = get_logger(__name__)


class ConfigError(Exception):
    """Raised when a configuration file cannot be loaded or is invalid."""


class ConfigManager:
    """Load, merge and access YAML configuration files.

    Example::

        cfg = ConfigManager.from_file("config/train.yaml")
        lr = cfg.get("learning_rate", 1e-3)
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self._data: dict[str, Any] = data

    @classmethod
    def from_file(cls, path: str | Path) -> ConfigManager:
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            A ``ConfigManager`` populated with the file contents.

        Raises:
            ConfigError: If the file does not exist or contains invalid YAML.
        """
        filepath = Path(path)
        if not filepath.exists():
            raise ConfigError(f"Config file not found: {filepath}")

        try:
            with open(filepath) as f:
                raw = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid YAML in {filepath}: {exc}") from exc

        if not isinstance(raw, dict):
            raise ConfigError(
                f"Expected a YAML mapping at top level in {filepath}, got {type(raw).__name__}"
            )

        logger.info("Loaded config from %s", filepath)
        return cls(raw)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConfigManager:
        """Create a ConfigManager from an existing dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            A ``ConfigManager`` wrapping *data*.
        """
        return cls(dict(data))

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value by key, supporting dot-separated nested access.

        Args:
            key: Configuration key (e.g. ``"model.hidden_size"``).
            default: Fallback value when *key* is absent.

        Returns:
            The configuration value or *default*.
        """
        keys = key.split(".")
        node: Any = self._data
        for k in keys:
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                return default
        return node

    def set(self, key: str, value: Any) -> None:
        """Set a value by key, supporting dot-separated nested access.

        Intermediate dictionaries are created if they don't exist.

        Args:
            key: Configuration key (e.g. ``"model.hidden_size"``).
            value: Value to set.
        """
        keys = key.split(".")
        node = self._data
        for k in keys[:-1]:
            if k not in node or not isinstance(node[k], dict):
                node[k] = {}
            node = node[k]
        node[keys[-1]] = value

    def merge(self, other: ConfigManager) -> ConfigManager:
        """Return a new ConfigManager with *other*'s values merged on top.

        Args:
            other: Configuration whose values take precedence.

        Returns:
            A new ``ConfigManager`` with merged data.
        """
        merged = _deep_merge(dict(self._data), dict(other._data))
        return ConfigManager(merged)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the internal data dictionary."""
        return dict(self._data)

    def __contains__(self, key: str) -> bool:
        sentinel = object()
        return self.get(key, sentinel) is not sentinel

    def __repr__(self) -> str:
        return f"ConfigManager({self._data!r})"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *override* into *base*, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
