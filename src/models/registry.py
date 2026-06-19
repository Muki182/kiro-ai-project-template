"""Model registry for dynamic model construction."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.models.base import BaseModel, ModelError
from src.utils.logging import get_logger

logger = get_logger(__name__)

ModelFactory = Callable[..., BaseModel]


class ModelRegistry:
    """Central registry for model factories.

    Allows registering model constructors by name and instantiating them
    from configuration.

    Example::

        registry = ModelRegistry()
        registry.register("simple", SimpleNet)
        model = registry.create("simple", input_dim=10, hidden_dim=32, output_dim=2)
    """

    def __init__(self) -> None:
        self._factories: dict[str, ModelFactory] = {}

    def register(self, name: str, factory: ModelFactory) -> None:
        """Register a model factory under the given name.

        Args:
            name: Unique model identifier.
            factory: Callable that returns a ``BaseModel`` instance.

        Raises:
            ModelError: If *name* is already registered.
        """
        if not name:
            raise ModelError("Model name must not be empty")
        if name in self._factories:
            raise ModelError(f"Model '{name}' is already registered")
        self._factories[name] = factory
        logger.info("Registered model: %s", name)

    def create(self, name: str, **kwargs: Any) -> BaseModel:
        """Instantiate a registered model.

        Args:
            name: Registered model name.
            **kwargs: Arguments forwarded to the model factory.

        Returns:
            A ``BaseModel`` instance.

        Raises:
            ModelError: If *name* is not registered.
        """
        if name not in self._factories:
            available = ", ".join(sorted(self._factories)) or "(none)"
            raise ModelError(f"Unknown model '{name}'. Available: {available}")
        return self._factories[name](**kwargs)

    def list_models(self) -> list[str]:
        """Return sorted list of registered model names."""
        return sorted(self._factories)

    def __contains__(self, name: str) -> bool:
        return name in self._factories

    def __len__(self) -> int:
        return len(self._factories)
