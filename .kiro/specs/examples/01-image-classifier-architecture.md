# Spec 01: 系统架构设计 — MNIST 图像分类器

**状态**：`已完成`
**创建日期**：`2025-07-01`
**最后更新**：`2025-07-15`
**负责人**：`@alice`

---

## 概述

> 这是一个**示例 spec**，展示如何将空白模板填写为真实可用的架构文档。
> 你可以复制此文件到 `.kiro/specs/` 目录下作为新模块 spec 的起点。

本 spec 定义 MNIST 手写数字分类器的整体架构，包括数据加载、模型结构、
训练流程和评估组件的划分。实现细节由 `02-image-classifier-implementation.md` 覆盖。

---

## 背景与动机

- **问题陈述**：需要一个端到端的图像分类 pipeline，用于验证项目脚手架的完整性，
  同时作为团队新成员的入门参考项目。
- **关键约束**：单卡 GPU（RTX 3060, 12 GB）可训练；推理延迟 < 10 ms/张。
- **参考资料**：[LeCun et al. 1998](http://yann.lecun.com/exdb/mnist/)

---

## 需求列表

### 功能需求

- **REQ-F-01**：系统应能对 28x28 灰度图像进行 0-9 数字分类
  - 验收条件：在 MNIST 测试集上输出 10 类概率分布，argmax 与标签一致

- **REQ-F-02**：系统应支持模型的保存与加载
  - 验收条件：保存后重新加载的模型在相同输入上产生相同输出（bit-exact）

- **REQ-F-03**：系统应提供命令行推理接口
  - 验收条件：`python -m src.inference.predict --image path/to/img.png` 输出分类结果

### 性能需求

- **REQ-P-01**：测试集准确率 >= 99.0%
  - 验收条件：在完整 MNIST 测试集（10,000 张）上评估

- **REQ-P-02**：训练峰值显存 < 2 GB
  - 验收条件：`nvidia-smi` 监控确认

### 可靠性需求

- **REQ-R-01**：输入尺寸不为 28x28 时应抛出明确的 ValueError
  - 验收条件：传入 32x32 图像时，错误信息包含期望尺寸

---

## 架构设计

### 组件划分

```
mnist-classifier/
├── src/data/           # 数据加载与预处理
│   └── mnist_loader.py
├── src/models/         # CNN 模型定义
│   └── classifier.py
├── src/training/       # 训练循环与优化器配置
│   └── trainer.py
├── src/inference/      # 推理入口
│   └── predict.py
└── src/utils/          # 通用工具（日志、checkpoint 管理）
    └── checkpoint.py
```

### 数据流

```
MNIST 数据集 → [DataLoader] → 归一化 Tensor (B, 1, 28, 28)
    → [CNN Model] → logits (B, 10)
    → [CrossEntropyLoss] → 反向传播 → [Optimizer.step()]
                                          ↓
                                   [Checkpoint 保存]
```

### 关键接口定义

```python
class MNISTClassifier(nn.Module):
    def forward(self, x: Tensor) -> Tensor:
        """
        Args:
            x: 灰度图像 Tensor, shape (B, 1, 28, 28), 像素值 [0, 1]
        Returns:
            logits: 未归一化概率, shape (B, 10)
        Raises:
            ValueError: 输入 shape 不符合要求时抛出
        """
        ...

class Trainer:
    def train(self, epochs: int) -> dict[str, float]:
        """执行训练循环，返回 {"loss": ..., "accuracy": ...}"""
        ...

    def evaluate(self) -> float:
        """在测试集上评估，返回准确率 (0.0 ~ 1.0)"""
        ...
```

---

## 任务分解

### 阶段一：基础框架

- [x] **TASK-01**：搭建项目目录结构，配置 pyproject.toml
  - 关联需求：全局
  - 预估工作量：`S`

- [x] **TASK-02**：实现 `MNISTClassifier` 骨架代码与 forward 接口
  - 关联需求：REQ-F-01
  - 预估工作量：`M`

- [x] **TASK-03**：编写 `MNISTClassifier` 的单元测试框架
  - 关联需求：REQ-F-01
  - 预估工作量：`S`

### 阶段二：核心实现

- [x] **TASK-04**：实现 MNIST 数据加载管线（下载 + 归一化 + DataLoader）
  - 关联需求：REQ-F-01
  - 依赖：TASK-01
  - 预估工作量：`M`

- [x] **TASK-05**：实现训练循环（loss 计算 + 反向传播 + 日志记录）
  - 关联需求：REQ-F-01, REQ-P-01
  - 依赖：TASK-02, TASK-04
  - 预估工作量：`L`

- [x] **TASK-06**：实现 checkpoint 保存/加载
  - 关联需求：REQ-F-02
  - 预估工作量：`S`

### 阶段三：推理与优化

- [x] **TASK-07**：实现命令行推理入口
  - 关联需求：REQ-F-03
  - 依赖：TASK-06
  - 预估工作量：`S`

- [x] **TASK-08**：性能调优（batch size、learning rate），达到 99% 准确率目标
  - 关联需求：REQ-P-01, REQ-P-02
  - 依赖：TASK-05
  - 预估工作量：`M`

---

## 风险与未决问题

| ID | 风险描述 | 影响 | 缓解措施 | 状态 |
|----|---------|------|---------|------|
| RISK-01 | 99% 准确率目标在简单 CNN 上可能需要多轮调参 | 中 | 备选方案：引入 BatchNorm 或切换到 ResNet-18 | 已解决 |
| RISK-02 | MNIST 下载源可能被墙或限速 | 低 | 配置镜像 URL 或本地缓存 | 已解决 |

---

## 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| 2025-07-01 | v0.1 | 初稿 | @alice |
| 2025-07-08 | v0.2 | 补充性能需求与风险评估 | @alice |
| 2025-07-15 | v1.0 | 标记已完成，所有任务通过验收 | @alice |
