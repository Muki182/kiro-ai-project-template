"""Base model interface and linear layer implementations."""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod

from src.utils.logging import get_logger

logger = get_logger(__name__)


class ModelError(Exception):
    """Raised on model construction or forward-pass errors."""


class BaseModel(ABC):
    """Abstract base class for all models.

    Subclasses must implement ``forward`` and ``parameters``.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._training = True

    @property
    def name(self) -> str:
        """Model name identifier."""
        return self._name

    @property
    def training(self) -> bool:
        """Whether the model is in training mode."""
        return self._training

    def train(self) -> None:
        """Set the model to training mode."""
        self._training = True

    def eval(self) -> None:
        """Set the model to evaluation mode."""
        self._training = False

    @abstractmethod
    def forward(self, inputs: list[list[float]]) -> list[list[float]]:
        """Run a forward pass.

        Args:
            inputs: Batch of input vectors, shape ``(batch, input_dim)``.

        Returns:
            Batch of output vectors, shape ``(batch, output_dim)``.
        """
        ...

    @abstractmethod
    def parameters(self) -> list[list[list[float]]]:
        """Return all trainable parameter matrices."""
        ...

    def num_parameters(self) -> int:
        """Total number of scalar parameters."""
        total = 0
        for matrix in self.parameters():
            for row in matrix:
                total += len(row)
        return total

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self._name!r}, params={self.num_parameters()})"


class LinearLayer:
    """A single fully-connected (dense) layer: y = x @ W + b.

    Args:
        input_dim: Dimensionality of input vectors.
        output_dim: Dimensionality of output vectors.
        seed: Random seed for weight initialization.
    """

    def __init__(self, input_dim: int, output_dim: int, seed: int = 42) -> None:
        if input_dim < 1:
            raise ModelError(f"input_dim must be >= 1, got {input_dim}")
        if output_dim < 1:
            raise ModelError(f"output_dim must be >= 1, got {output_dim}")

        self.input_dim = input_dim
        self.output_dim = output_dim

        rng = random.Random(seed)
        scale = 1.0 / math.sqrt(input_dim)
        self.weights: list[list[float]] = [
            [rng.gauss(0, scale) for _ in range(output_dim)] for _ in range(input_dim)
        ]
        self.bias: list[float] = [0.0] * output_dim

    def forward(self, inputs: list[list[float]]) -> list[list[float]]:
        """Compute y = x @ W + b for a batch of inputs.

        Args:
            inputs: Batch of input vectors, shape ``(batch, input_dim)``.

        Returns:
            Batch of output vectors, shape ``(batch, output_dim)``.

        Raises:
            ModelError: If input dimensions don't match.
        """
        outputs: list[list[float]] = []
        for x in inputs:
            if len(x) != self.input_dim:
                raise ModelError(
                    f"Expected input dim {self.input_dim}, got {len(x)}"
                )
            y = list(self.bias)
            for j in range(self.output_dim):
                for i in range(self.input_dim):
                    y[j] += x[i] * self.weights[i][j]
            outputs.append(y)
        return outputs


class SimpleNet(BaseModel):
    """A simple two-layer feedforward network.

    Args:
        input_dim: Input feature dimension.
        hidden_dim: Hidden layer dimension.
        output_dim: Output dimension.
        seed: Random seed for initialization.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        seed: int = 42,
    ) -> None:
        super().__init__(name="SimpleNet")
        self._layer1 = LinearLayer(input_dim, hidden_dim, seed=seed)
        self._layer2 = LinearLayer(hidden_dim, output_dim, seed=seed + 1)

    def forward(self, inputs: list[list[float]]) -> list[list[float]]:
        """Forward pass through two layers with ReLU activation.

        Args:
            inputs: Batch of input vectors.

        Returns:
            Batch of output vectors.
        """
        hidden = self._layer1.forward(inputs)
        activated = [[max(0.0, v) for v in row] for row in hidden]
        return self._layer2.forward(activated)

    def parameters(self) -> list[list[list[float]]]:
        """Return weight matrices of both layers."""
        return [
            self._layer1.weights,
            [self._layer1.bias],
            self._layer2.weights,
            [self._layer2.bias],
        ]
