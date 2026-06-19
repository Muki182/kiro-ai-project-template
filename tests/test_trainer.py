"""Tests for src.training.trainer."""

import pytest

from src.models.base import SimpleNet
from src.training.trainer import Trainer, TrainerConfig, _compute_mse_loss, _create_batches


class TestTrainerConfig:
    def test_defaults(self) -> None:
        cfg = TrainerConfig()
        assert cfg.learning_rate == 1e-3
        assert cfg.max_epochs == 10
        assert cfg.batch_size == 32

    def test_custom_values(self) -> None:
        cfg = TrainerConfig(learning_rate=0.01, max_epochs=5, batch_size=16)
        assert cfg.learning_rate == 0.01
        assert cfg.max_epochs == 5

    def test_invalid_lr(self) -> None:
        with pytest.raises(ValueError, match="learning_rate"):
            TrainerConfig(learning_rate=0.0)
        with pytest.raises(ValueError, match="learning_rate"):
            TrainerConfig(learning_rate=-1.0)

    def test_invalid_epochs(self) -> None:
        with pytest.raises(ValueError, match="max_epochs"):
            TrainerConfig(max_epochs=0)

    def test_invalid_batch_size(self) -> None:
        with pytest.raises(ValueError, match="batch_size"):
            TrainerConfig(batch_size=0)

    def test_invalid_patience(self) -> None:
        with pytest.raises(ValueError, match="early_stop_patience"):
            TrainerConfig(early_stop_patience=0)

    def test_from_dict(self) -> None:
        cfg = TrainerConfig.from_dict({"learning_rate": 0.05, "max_epochs": 3})
        assert cfg.learning_rate == 0.05
        assert cfg.max_epochs == 3

    def test_from_dict_defaults(self) -> None:
        cfg = TrainerConfig.from_dict({})
        assert cfg.learning_rate == 1e-3


class TestComputeMseLoss:
    def test_zero_loss(self) -> None:
        preds = [[1.0, 2.0]]
        targets = [[1.0, 2.0]]
        assert _compute_mse_loss(preds, targets) == pytest.approx(0.0)

    def test_nonzero_loss(self) -> None:
        preds = [[1.0]]
        targets = [[3.0]]
        assert _compute_mse_loss(preds, targets) == pytest.approx(4.0)

    def test_batch_loss(self) -> None:
        preds = [[1.0], [2.0]]
        targets = [[0.0], [0.0]]
        loss = _compute_mse_loss(preds, targets)
        assert loss == pytest.approx(2.5)

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            _compute_mse_loss([], [])

    def test_batch_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="Batch size"):
            _compute_mse_loss([[1.0]], [[1.0], [2.0]])

    def test_dim_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="Dimension"):
            _compute_mse_loss([[1.0, 2.0]], [[1.0]])


class TestCreateBatches:
    def test_exact_split(self) -> None:
        data = [[float(i)] for i in range(6)]
        batches = _create_batches(data, batch_size=3)
        assert len(batches) == 2
        assert len(batches[0]) == 3

    def test_remainder(self) -> None:
        data = [[float(i)] for i in range(5)]
        batches = _create_batches(data, batch_size=3)
        assert len(batches) == 2
        assert len(batches[1]) == 2

    def test_single_batch(self) -> None:
        data = [[1.0, 2.0]]
        batches = _create_batches(data, batch_size=10)
        assert len(batches) == 1


class TestTrainer:
    def _make_data(self) -> tuple[list[list[float]], list[list[float]]]:
        inputs = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.5, 0.5]]
        targets = [[0.0], [0.0], [0.0], [0.0]]
        return inputs, targets

    def test_train_epoch(self) -> None:
        model = SimpleNet(2, 4, 1)
        cfg = TrainerConfig(learning_rate=0.01, max_epochs=5, batch_size=4)
        trainer = Trainer(model, cfg)
        inputs, targets = self._make_data()
        loss = trainer.train_epoch(inputs, targets)
        assert isinstance(loss, float)
        assert trainer.epoch == 1

    def test_multiple_epochs(self) -> None:
        model = SimpleNet(2, 4, 1)
        cfg = TrainerConfig(max_epochs=3, batch_size=4)
        trainer = Trainer(model, cfg)
        inputs, targets = self._make_data()
        for _ in range(3):
            trainer.train_epoch(inputs, targets)
        assert trainer.epoch == 3
        assert trainer.loss_tracker.count == 3

    def test_empty_inputs_raises(self) -> None:
        model = SimpleNet(2, 4, 1)
        trainer = Trainer(model, TrainerConfig())
        with pytest.raises(ValueError, match="empty"):
            trainer.train_epoch([], [])

    def test_mismatched_lengths_raises(self) -> None:
        model = SimpleNet(2, 4, 1)
        trainer = Trainer(model, TrainerConfig())
        with pytest.raises(ValueError, match="same length"):
            trainer.train_epoch(
                [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
                [[0.0], [0.0]],
            )

    def test_fit_returns_summary(self) -> None:
        model = SimpleNet(2, 4, 1)
        cfg = TrainerConfig(max_epochs=3, batch_size=4)
        trainer = Trainer(model, cfg)
        inputs, targets = self._make_data()
        summary = trainer.fit(inputs, targets)
        assert "final_loss" in summary
        assert "epochs_run" in summary
        assert "stopped_early" in summary
        assert summary["epochs_run"] == 3

    def test_early_stopping(self) -> None:
        model = SimpleNet(2, 4, 1)
        cfg = TrainerConfig(max_epochs=100, early_stop_patience=1, batch_size=4)
        trainer = Trainer(model, cfg)
        assert trainer.should_stop(1.0) is False
        assert trainer.should_stop(2.0) is True

    def test_early_stop_resets_on_improvement(self) -> None:
        model = SimpleNet(2, 4, 1)
        cfg = TrainerConfig(max_epochs=100, early_stop_patience=2, batch_size=4)
        trainer = Trainer(model, cfg)
        assert trainer.should_stop(5.0) is False
        assert trainer.should_stop(6.0) is False
        assert trainer.should_stop(4.0) is False
        assert trainer.should_stop(5.0) is False
        assert trainer.should_stop(5.0) is True
