# Project Steering

> 本文件是项目的全局上下文，Kiro Agent 在执行所有任务时均会参考此文件。
> 请在开始项目前完整填写，后续架构调整时同步更新。

---

## 项目概述

**项目名称**：`[填写项目名称]`
**项目类型**：`[AI训练系统 / 推理服务 / Pipeline / 应用]`
**当前阶段**：`[设计 / 原型 / 开发 / 优化]`

**一句话描述**：
> [用一句话描述系统要解决的核心问题]

---

## 技术栈

```yaml
language: Python 3.10+
framework:
  - [e.g. PyTorch 2.x / JAX / vLLM]
  - [e.g. FastAPI / gRPC]
infrastructure:
  - [e.g. CUDA 12.x, NCCL]
  - [e.g. Docker, Kubernetes]
testing: pytest
linting: ruff, mypy
```

---

## 架构约束

> 列出所有**不允许违反**的设计约束，Agent 在生成代码时必须遵守。

1. **模块边界**：各模块通过显式接口通信，禁止跨模块直接访问内部状态
2. **配置管理**：所有超参数和路径通过 `config/` 下的 YAML 文件管理，禁止硬编码
3. **日志规范**：使用统一的 `logger = get_logger(__name__)` 模式，禁止 `print()` 调试输出
4. **错误处理**：所有外部调用必须有显式异常捕获，禁止裸 `except:` 块
5. **类型标注**：所有公开函数必须有完整的类型标注（参数 + 返回值）
6. **安全约束**：
   - 禁止在代码中硬编码密钥、令牌、密码等敏感信息，必须通过环境变量或密钥管理服务获取
   - 禁止使用 `pickle.load()` 反序列化不可信数据，使用 `safetensors` 或 `json`
   - 禁止使用 `yaml.load()` 不带 `Loader=SafeLoader`，统一使用 `yaml.safe_load()`
   - 禁止使用 `eval()` / `exec()` 处理用户输入或外部数据
   - 所有 SQL 查询必须使用参数化查询，禁止字符串拼接
   - 所有 API 端点默认要求认证，公开端点需显式标记
   - 生产环境禁止开启 debug 模式，CORS 禁止使用通配符 `*`
7. `[添加项目特定约束]`

---

## 命名规范

| 类别 | 规范 | 示例 |
|------|------|------|
| 模块文件 | `snake_case.py` | `data_loader.py` |
| 类名 | `PascalCase` | `VideoEncoder` |
| 函数/方法 | `snake_case` | `load_checkpoint()` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_SEQ_LEN` |
| 配置键 | `snake_case` | `learning_rate` |
| 实验分支 | `exp/[描述]-[日期]` | `exp/lr-warmup-20250501` |

---

## 目录结构规范

```
project/
├── config/          # 所有配置文件（YAML）
├── src/
│   ├── data/        # 数据加载与预处理
│   ├── models/      # 模型定义
│   ├── training/    # 训练逻辑
│   ├── inference/   # 推理逻辑
│   └── utils/       # 工具函数
├── tests/           # 测试文件，镜像 src/ 结构
├── scripts/         # 一次性脚本，不纳入模块
└── docs/            # 文档
```

---

## 当前已知限制

> 列出系统目前存在的、Agent 需要知道的约束或临时妥协方案。

- `[示例：当前 batch size 受 GPU 显存限制，暂时 hardcode 为 4，待优化]`
- `[示例：分布式训练尚未实现，所有代码假设单机单卡]`
- `[添加更多]`

---

## 关键设计决策记录

| 决策 | 选择 | 放弃的替代方案 | 原因 |
|------|------|--------------|------|
| `[示例：序列化格式]` | `safetensors` | `pickle` | 安全性与跨框架兼容性 |
| `[添加更多]` | | | |

---

## 外部依赖与接口

> 列出系统依赖的外部服务或数据源，Agent 在涉及这些接口时需特别注意。

- **数据源**：`[描述数据格式、位置、访问方式]`
- **模型权重**：`[描述权重来源、加载方式]`
- **外部服务**：`[描述依赖的 API 或服务]`
