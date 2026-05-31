# kiro-ai-project-template

> 面向 AI 研究工程化场景的 Kiro 项目模板，提供完整的 spec 结构、分层 hook 配置与上下文管理策略。

[English](./README_EN.md) | 简体中文

---

## 背景

在 AI 系统开发中，工程迭代周期长、模块依赖复杂、需求频繁变更，传统的 AI 编码工具在这类场景下面临两个核心问题：

1. **上下文漂移**：多轮对话后，实现逐渐偏离原始设计意图
2. **验收缺失**：生成的代码缺乏与需求的显式绑定，无法自动验证一致性

Kiro 的 spec-driven 开发模式通过将需求、实现与验证三者结构化绑定，从根本上解决了上述问题。本模板将这套模式固化为可复用的项目脚手架。

---

## 适用场景

- AI 模型训练/推理系统设计与实现
- 多模块 AI Pipeline 工程化
- 需要长期迭代维护的研究工程项目
- 团队协作的 AI 应用开发

---

## 目录结构

```
.
├── .kiro/
│   ├── steering/
│   │   └── project.md          # 项目级全局上下文（架构约束、技术栈、命名规范）
│   ├── specs/
│   │   ├── 01-architecture.md  # 架构设计 spec（需求 + 任务分解）
│   │   └── 02-implementation.md # 实现阶段 spec
│   └── hooks/
│       ├── doc-sync.yml        # 代码变更后自动同步文档
│       ├── spec-validate.yml   # 实现变更后校验与 spec 的一致性
│       └── test-trigger.yml    # 关键文件变更后触发测试建议
├── docs/
│   └── workflow-guide.md       # 使用工作流说明
└── README.md
```

---

## 快速开始

### 1. 使用此模板创建项目

点击右上角 **Use this template** → **Create a new repository**

### 2. 用 Kiro 打开项目

```bash
git clone https://github.com/your-username/your-project
# 用 Kiro Desktop 或 VS Code + Kiro 插件打开项目根目录
```

### 3. 定制 steering 文件

编辑 `.kiro/steering/project.md`，填入你的项目架构约束、技术栈和命名规范。这是 Kiro Agent 在所有任务中都会参考的全局上下文。

### 4. 创建第一个 spec

参考 `.kiro/specs/01-architecture.md` 的格式，为你的第一个模块编写 spec。核心要素：
- **需求列表**：编号化、可验证的功能需求
- **任务分解**：对应需求的实现任务 checklist
- **验收条件**：每个需求的完成标准

### 5. 激活 hooks

Hooks 在项目打开后自动加载。可在 `.kiro/hooks/` 中按需启用或调整触发条件。

---

## Spec 设计原则

本模板的 spec 结构遵循以下原则：

| 原则 | 说明 |
|------|------|
| **原子性** | 每个需求独立可验证，不与其他需求产生隐式依赖 |
| **可追溯** | 每个实现任务必须对应至少一个需求编号 |
| **分层拆分** | 大型模块按功能边界拆分为多个 spec 文件，避免单文件上下文过载 |
| **状态显式** | 任务完成状态通过 checkbox 维护，不依赖对话历史 |

---

## Hook 策略说明

### `doc-sync.yml`
**触发条件**：`src/` 下任意 `.py` 文件变更
**行为**：提示 Agent 检查相关模块的文档字符串与 `docs/` 中对应文档是否需要同步更新

### `spec-validate.yml`
**触发条件**：核心模块文件变更
**行为**：对照对应 spec 文件中的需求列表，逐条确认实现是否满足验收条件，输出差异报告

### `test-trigger.yml`
**触发条件**：接口定义文件（`*_interface.py` / `*.proto`）变更
**行为**：提示 Agent 审查现有测试用例覆盖范围，建议补充缺失的边界测试

---

## 与其他工具的对比

| 维度 | 传统 AI 编码助手 | Kiro (本模板) |
|------|----------------|---------------|
| 需求持久化 | 依赖对话历史，会话结束即丢失 | spec 文件持久存储，跨会话有效 |
| 实现一致性 | 无显式校验机制 | hook 自动触发一致性检查 |
| 上下文管理 | 全局注入，大项目易超限 | steering + 分层 spec，按需加载 |
| 任务状态 | 无结构化跟踪 | checkbox 任务列表，状态可视 |
| 团队协作 | 个人对话，难以共享 | spec 文件纳入版本控制 |

---

## Contributing

欢迎提交 Issue 或 PR，特别是：
- 针对特定 AI 框架（PyTorch / JAX / vLLM 等）的专用 spec 模板
- 更细粒度的 hook 配置示例
- 实际项目的使用案例

---

## License

MIT
