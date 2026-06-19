"""Tests for src.models."""

import pytest

from src.models.base import LinearLayer, ModelError, SimpleNet
from src.models.registry import ModelRegistry


class TestLinearLayer:
    def test_construction(self) -> None:
        layer = LinearLayer(3, 2)
        assert layer.input_dim == 3
        assert layer.output_dim == 2

    def test_invalid_dims(self) -> None:
        with pytest.raises(ModelError):
            LinearLayer(0, 2)
        with pytest.raises(ModelError):
            LinearLayer(2, 0)

    def test_forward_shape(self) -> None:
        layer = LinearLayer(3, 2)
        out = layer.forward([[1.0, 2.0, 3.0]])
        assert len(out) == 1
        assert len(out[0]) == 2

    def test_forward_batch(self) -> None:
        layer = LinearLayer(2, 3)
        inputs = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
        out = layer.forward(inputs)
        assert len(out) == 3
        for row in out:
            assert len(row) == 3

    def test_forward_dim_mismatch(self) -> None:
        layer = LinearLayer(3, 2)
        with pytest.raises(ModelError, match="Expected input dim"):
            layer.forward([[1.0, 2.0]])

    def test_deterministic_with_seed(self) -> None:
        l1 = LinearLayer(2, 2, seed=99)
        l2 = LinearLayer(2, 2, seed=99)
        assert l1.weights == l2.weights


class TestSimpleNet:
    def test_construction(self) -> None:
        net = SimpleNet(input_dim=4, hidden_dim=8, output_dim=2)
        assert net.name == "SimpleNet"
        assert net.num_parameters() > 0

    def test_forward_shape(self) -> None:
        net = SimpleNet(input_dim=3, hidden_dim=5, output_dim=2)
        out = net.forward([[1.0, 2.0, 3.0]])
        assert len(out) == 1
        assert len(out[0]) == 2

    def test_forward_batch(self) -> None:
        net = SimpleNet(input_dim=2, hidden_dim=4, output_dim=1)
        inputs = [[1.0, 0.0], [0.0, 1.0]]
        out = net.forward(inputs)
        assert len(out) == 2

    def test_train_eval_modes(self) -> None:
        net = SimpleNet(2, 4, 1)
        assert net.training is True
        net.eval()
        assert net.training is False
        net.train()
        assert net.training is True

    def test_parameters_returns_matrices(self) -> None:
        net = SimpleNet(2, 3, 1)
        params = net.parameters()
        assert len(params) == 4

    def test_repr(self) -> None:
        net = SimpleNet(2, 3, 1)
        r = repr(net)
        assert "SimpleNet" in r
        assert "params=" in r


class TestModelRegistry:
    def test_register_and_create(self) -> None:
        reg = ModelRegistry()
        reg.register("simple", lambda **kw: SimpleNet(**kw))
        model = reg.create("simple", input_dim=2, hidden_dim=4, output_dim=1)
        assert isinstance(model, SimpleNet)

    def test_register_duplicate_raises(self) -> None:
        reg = ModelRegistry()
        reg.register("a", lambda: SimpleNet(1, 1, 1))
        with pytest.raises(ModelError, match="already registered"):
            reg.register("a", lambda: SimpleNet(1, 1, 1))

    def test_register_empty_name_raises(self) -> None:
        reg = ModelRegistry()
        with pytest.raises(ModelError, match="empty"):
            reg.register("", lambda: SimpleNet(1, 1, 1))

    def test_create_unknown_raises(self) -> None:
        reg = ModelRegistry()
        with pytest.raises(ModelError, match="Unknown model"):
            reg.create("nonexistent")

    def test_list_models(self) -> None:
        reg = ModelRegistry()
        reg.register("b", lambda: SimpleNet(1, 1, 1))
        reg.register("a", lambda: SimpleNet(1, 1, 1))
        assert reg.list_models() == ["a", "b"]

    def test_contains(self) -> None:
        reg = ModelRegistry()
        reg.register("x", lambda: SimpleNet(1, 1, 1))
        assert "x" in reg
        assert "y" not in reg

    def test_len(self) -> None:
        reg = ModelRegistry()
        assert len(reg) == 0
        reg.register("x", lambda: SimpleNet(1, 1, 1))
        assert len(reg) == 1
