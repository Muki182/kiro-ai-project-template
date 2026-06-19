"""Training loop and optimizer logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.models.base import BaseModel
from src.utils.logging import get_logger
from src.utils.metrics import MetricTracker

logger = get_logger(__name__)


@dataclass
class TrainerConfig:
    """Configuration for the training loop.

    Attributes:
        learning_rate: Step size for gradient updates.
        max_epochs: Maximum number of training epochs.
        batch_size: Number of samples per training step.
        early_stop_patience: Stop after this many epochs without improvement.
        log_interval: Log metrics every N steps.
    """

    learning_rate: float = 1e-3
    max_epochs: int = 10
    batch_size: int = 32
    early_stop_patience: int = 3
    log_interval: int = 1

    def __post_init__(self) -> None:
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be positive, got {self.learning_rate}")
        if self.max_epochs < 1:
            raise ValueError(f"max_epochs must be >= 1, got {self.max_epochs}")
        if self.batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {self.batch_size}")
        if self.early_stop_patience < 1:
            raise ValueError(
                f"early_stop_patience must be >= 1, got {self.early_stop_patience}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrainerConfig:
        """Build a TrainerConfig from a dictionary.

        Args:
            data: Dict with config keys matching field names.

        Returns:
            A ``TrainerConfig`` instance.
        """
        return cls(
            learning_rate=data.get("learning_rate", 1e-3),
            max_epochs=data.get("max_epochs", 10),
            batch_size=data.get("batch_size", 32),
            early_stop_patience=data.get("early_stop_patience", 3),
            log_interval=data.get("log_interval", 1),
        )


def _compute_mse_loss(predictions: list[list[float]], targets: list[list[float]]) -> float:
    """Compute mean squared error between predictions and targets.

    Args:
        predictions: Predicted values, shape ``(batch, dim)``.
        targets: Target values, shape ``(batch, dim)``.

    Returns:
        Scalar MSE loss value.

    Raises:
        ValueError: If shapes don't match or inputs are empty.
    """
    if not predictions or not targets:
        raise ValueError("predictions and targets must not be empty")
    if len(predictions) != len(targets):
        raise ValueError(
            f"Batch size mismatch: {len(predictions)} vs {len(targets)}"
        )

    total = 0.0
    count = 0
    for pred, tgt in zip(predictions, targets):
        if len(pred) != len(tgt):
            raise ValueError(f"Dimension mismatch: {len(pred)} vs {len(tgt)}")
        for p, t in zip(pred, tgt):
            total += (p - t) ** 2
            count += 1

    return total / count if count > 0 else 0.0


def _create_batches(
    data: list[list[float]], batch_size: int
) -> list[list[list[float]]]:
    """Split data into batches.

    Args:
        data: Full dataset as list of vectors.
        batch_size: Maximum batch size.

    Returns:
        List of batches.
    """
    batches: list[list[list[float]]] = []
    for i in range(0, len(data), batch_size):
        batches.append(data[i : i + batch_size])
    return batches


class Trainer:
    """Orchestrates model training with early stopping and metric tracking.

    Args:
        model: The model to train.
        config: Training configuration.
    """

    def __init__(self, model: BaseModel, config: TrainerConfig) -> None:
        self._model = model
        self._config = config
        self._loss_tracker = MetricTracker(name="train_loss")
        self._epoch = 0
        self._best_loss: float | None = None
        self._patience_counter = 0

    @property
    def epoch(self) -> int:
        """Current epoch number."""
        return self._epoch

    @property
    def loss_tracker(self) -> MetricTracker:
        """Access the training loss tracker."""
        return self._loss_tracker

    def should_stop(self, current_loss: float) -> bool:
        """Check early stopping condition.

        Args:
            current_loss: Loss value for the current epoch.

        Returns:
            True if training should stop.
        """
        if self._best_loss is None or current_loss < self._best_loss:
            self._best_loss = current_loss
            self._patience_counter = 0
            return False

        self._patience_counter += 1
        if self._patience_counter >= self._config.early_stop_patience:
            logger.info(
                "Early stopping at epoch %d (patience %d exhausted)",
                self._epoch,
                self._config.early_stop_patience,
            )
            return True
        return False

    def train_epoch(
        self,
        inputs: list[list[float]],
        targets: list[list[float]],
    ) -> float:
        """Run one epoch of training.

        Args:
            inputs: Training input vectors.
            targets: Training target vectors.

        Returns:
            Average loss for this epoch.

        Raises:
            ValueError: If inputs or targets are empty.
        """
        if not inputs or not targets:
            raise ValueError("inputs and targets must not be empty")

        self._model.train()
        self._epoch += 1

        batches_in = _create_batches(inputs, self._config.batch_size)
        batches_tgt = _create_batches(targets, self._config.batch_size)

        epoch_loss = 0.0
        num_batches = 0

        for batch_inputs, batch_targets in zip(batches_in, batches_tgt):
            predictions = self._model.forward(batch_inputs)
            loss = _compute_mse_loss(predictions, batch_targets)
            epoch_loss += loss
            num_batches += 1

        avg_loss = epoch_loss / num_batches if num_batches > 0 else 0.0
        self._loss_tracker.update(avg_loss)

        if self._epoch % self._config.log_interval == 0:
            logger.info("Epoch %d — loss: %.6f", self._epoch, avg_loss)

        return avg_loss

    def fit(
        self,
        inputs: list[list[float]],
        targets: list[list[float]],
    ) -> dict[str, Any]:
        """Run the full training loop.

        Args:
            inputs: Training input vectors.
            targets: Training target vectors.

        Returns:
            Dict with ``final_loss``, ``epochs_run``, ``stopped_early``.
        """
        stopped_early = False

        for _ in range(self._config.max_epochs):
            loss = self.train_epoch(inputs, targets)
            if self.should_stop(loss):
                stopped_early = True
                break

        return {
            "final_loss": self._loss_tracker.last,
            "epochs_run": self._epoch,
            "stopped_early": stopped_early,
        }
