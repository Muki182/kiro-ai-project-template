# Spec 02: 模块实现 — MNIST CNN 分类器

**状态**：`已完成`
**父级 Spec**：`01-image-classifier-architecture.md`
**创建日期**：`2025-07-08`
**最后更新**：`2025-07-15`

---

## 概述

> 这是一个**示例 spec**，展示如何将空白实现模板填写为具体的技术方案文档。

本 spec 覆盖 MNIST CNN 分类器的具体实现细节，包括网络结构选型、训练超参、
边界处理和测试策略。架构层面的设计决策参见 `01-image-classifier-architecture.md`。

---

## 实现范围

本 spec 负责以下任务（来自 `01-image-classifier-architecture.md`）：

- TASK-04：MNIST 数据加载管线
- TASK-05：训练循环实现
- TASK-06：Checkpoint 保存/加载
- TASK-07：命令行推理入口

---

## 实现细节

### `MNISTClassifier` (src/models/classifier.py)

**对应需求**：REQ-F-01, REQ-P-01, REQ-P-02

**算法/方法选择**：

选用两层卷积 + 两层全连接的轻量 CNN，原因：结构简单、显存占用低（< 500 MB），
在 MNIST 上可达 99%+ 准确率。
备选方案 ResNet-18 因参数量过大（11M vs 60K）且无必要被放弃。

**实现要点**：

```python
class MNISTClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),  # (B, 32, 28, 28)
            nn.ReLU(),
            nn.MaxPool2d(2),                              # (B, 32, 14, 14)
            nn.Conv2d(32, 64, kernel_size=3, padding=1), # (B, 64, 14, 14)
            nn.ReLU(),
            nn.MaxPool2d(2),                              # (B, 64, 7, 7)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10),
        )

    def forward(self, x: Tensor) -> Tensor:
        if x.shape[-2:] != (28, 28):
            raise ValueError(f"Expected 28x28 input, got {x.shape[-2:]}")
        return self.classifier(self.features(x))
```

**训练超参**：

| 参数 | 值 | 备注 |
|------|----|------|
| batch_size | 128 | 平衡吞吐与显存 |
| learning_rate | 1e-3 | Adam 默认值 |
| epochs | 10 | 通常第 5 轮即收敛 |
| optimizer | Adam | 相比 SGD 收敛更快 |
| loss | CrossEntropyLoss | 多分类标准选择 |

**边界情况处理**：

| 边界情况 | 处理方式 |
|---------|---------|
| 输入不是 28x28 | `forward()` 中检查 shape，抛出 `ValueError` |
| 输入像素值不在 [0, 1] | DataLoader 中统一归一化，不在模型内校验 |
| 空 batch (B=0) | PyTorch 原生支持，不需特殊处理 |
| GPU 不可用 | Trainer 自动 fallback 到 CPU，日志警告 |

---

### `Trainer` (src/training/trainer.py)

**对应需求**：REQ-F-01, REQ-P-01

**实现要点**：

```python
class Trainer:
    def train(self, epochs: int = 10) -> dict[str, float]:
        for epoch in range(epochs):
            running_loss = 0.0
            for batch_x, batch_y in self.train_loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                self.optimizer.zero_grad()
                logits = self.model(batch_x)
                loss = self.criterion(logits, batch_y)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()
            # 每轮结束打印 loss + 测试集准确率
            acc = self.evaluate()
            print(f"Epoch {epoch+1}: loss={running_loss:.4f}, acc={acc:.4f}")
        return {"loss": running_loss, "accuracy": acc}
```

---

### `checkpoint` (src/utils/checkpoint.py)

**对应需求**：REQ-F-02

```python
def save_checkpoint(model: nn.Module, path: str) -> None:
    torch.save(model.state_dict(), path)

def load_checkpoint(model: nn.Module, path: str) -> nn.Module:
    model.load_state_dict(torch.load(path, weights_only=True))
    return model
```

---

## 测试策略

### 单元测试

```python
# tests/test_classifier.py

class TestMNISTClassifier:
    def test_forward_output_shape(self):
        """验收条件：REQ-F-01 - 输出 shape 为 (B, 10)"""
        model = MNISTClassifier()
        x = torch.randn(4, 1, 28, 28)
        assert model(x).shape == (4, 10)

    def test_forward_invalid_shape_raises(self):
        """边界用例：REQ-R-01 - 非 28x28 输入应抛出 ValueError"""
        model = MNISTClassifier()
        with pytest.raises(ValueError, match="Expected 28x28"):
            model(torch.randn(1, 1, 32, 32))

    def test_checkpoint_roundtrip(self):
        """验收条件：REQ-F-02 - 保存后加载的模型输出一致"""
        model = MNISTClassifier()
        x = torch.randn(1, 1, 28, 28)
        original_output = model(x)
        save_checkpoint(model, "/tmp/test.pt")
        loaded = load_checkpoint(MNISTClassifier(), "/tmp/test.pt")
        assert torch.equal(loaded(x), original_output)

    def test_accuracy_above_threshold(self):
        """验收条件：REQ-P-01 - 测试集准确率 >= 99%"""
        trainer = Trainer(...)
        acc = trainer.evaluate()
        assert acc >= 0.99, f"Accuracy {acc:.4f} < 0.99"
```

### 集成测试

- [x] 与 DataLoader 的接口联调（Tensor 格式、dtype 一致性）
- [x] 端到端 pipeline 跑通：加载数据 → 训练 1 epoch → 保存 → 加载 → 推理
- [x] 显存占用监控测试（训练峰值 < 2 GB）

---

## 任务分解（细化）

- [x] **TASK-04.1**：实现 `get_mnist_loaders()` 返回 (train_loader, test_loader)
  - 关联需求：REQ-F-01
  - 测试用例：`test_loader_output_shape`

- [x] **TASK-05.1**：实现 `Trainer.__init__` 和 `train()` 主循环
  - 关联需求：REQ-F-01
  - 测试用例：`test_train_one_epoch`

- [x] **TASK-05.2**：实现 `Trainer.evaluate()` 准确率计算
  - 关联需求：REQ-P-01
  - 测试用例：`test_accuracy_above_threshold`

- [x] **TASK-06.1**：实现 `save_checkpoint` / `load_checkpoint`
  - 关联需求：REQ-F-02
  - 测试用例：`test_checkpoint_roundtrip`

- [x] **TASK-07.1**：实现 CLI 入口 `__main__` 解析参数并调用推理
  - 关联需求：REQ-F-03
  - 测试用例：手动验证 `python -m src.inference.predict --image test.png`

---

## 完成标准

以下条件全部满足时，本 spec 标记为**已完成**：

- [x] 所有任务 checkbox 勾选
- [x] 单元测试覆盖率 >= 80%（实际 92%）
- [x] 性能测试满足 REQ-P-01（实际 99.2%）、REQ-P-02（实际峰值 0.8 GB）
- [x] mypy 类型检查通过（zero errors）
- [x] ruff 代码风格检查通过
- [x] `01-image-classifier-architecture.md` 中对应任务更新为已完成
