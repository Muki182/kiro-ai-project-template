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
4. **错误处理**：所有外部调用必须有显式异常捕获，禁止裸 `except:` 块（详见下方「错误处理策略」）
5. **类型标注**：所有公开函数必须有完整的类型标注（参数 + 返回值）
6. `[添加项目特定约束]`

---

## 错误处理策略

> 错误处理是系统可靠性的基石。以下规则确保错误被显式捕获、正确传播、完整记录。

### 基本原则

1. **禁止静默吞没**：任何 `try/except` 块必须至少执行以下之一：重新抛出、抛出新异常、记录日志并返回显式错误值。空 `except: pass` 严禁出现
2. **禁止裸 `except:`**：必须捕获具体异常类型（如 `except ValueError`），不得使用 `except:` 或 `except Exception:`（除非在最外层入口处做兜底，且必须记录完整 traceback）
3. **错误必须传播**：底层模块不应自行决定"忽略"错误，应将异常向上抛出，由调用方决定降级策略
4. **上下文保留**：使用 `raise NewError(...) from original_error` 保留原始异常链，禁止 `raise NewError(...)` 丢弃原始上下文

### 自定义异常体系

```python
# src/utils/exceptions.py
class ProjectBaseError(Exception):
    """项目所有自定义异常的基类"""

class ConfigError(ProjectBaseError):
    """配置加载或校验失败"""

class DataError(ProjectBaseError):
    """数据加载、预处理或校验失败"""

class ModelError(ProjectBaseError):
    """模型加载、推理或训练过程中的错误"""

class ExternalServiceError(ProjectBaseError):
    """外部服务调用失败（API、存储、消息队列等）"""
```

### 错误处理模式

```python
# ✅ 正确：捕获具体异常，保留上下文，记录日志
try:
    result = external_api.call(params)
except ConnectionError as e:
    logger.error("外部服务调用失败: %s", e)
    raise ExternalServiceError(f"API 调用失败: {params}") from e

# ❌ 错误：裸 except + 静默吞没
try:
    result = external_api.call(params)
except:
    pass

# ❌ 错误：捕获后仅记录日志，不传播也不返回错误值
try:
    result = load_data(path)
except FileNotFoundError as e:
    logger.warning("文件不存在: %s", path)
    # 调用方不知道 result 未被赋值，后续会产生 NameError
```

### 日志与错误级别对照

| 错误类型 | 日志级别 | 处理方式 |
|---------|---------|---------|
| 可恢复的预期错误（如缓存未命中） | `WARNING` | 记录 + 走降级路径 |
| 不可恢复的业务错误（如数据格式非法） | `ERROR` | 记录 + 向上抛出 |
| 系统级故障（如 OOM、磁盘写满） | `CRITICAL` | 记录完整 traceback + 向上抛出 |
| 编程错误（如参数类型不匹配） | 不捕获 | 让异常直接抛出，暴露 bug |

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
