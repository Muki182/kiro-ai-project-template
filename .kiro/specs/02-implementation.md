# Spec 02: 模块实现

**状态**：`[ 草稿 / 评审中 / 已确认 / 实现中 / 已完成 ]`
**父级 Spec**：`01-architecture.md`
**创建日期**：`YYYY-MM-DD`
**最后更新**：`YYYY-MM-DD`

---

## 概述

本 spec 覆盖 `[模块名称]` 的具体实现细节，包括算法选择、数据结构、边界处理和测试策略。
架构层面的设计决策参见 `01-architecture.md`。

---

## 实现范围

本 spec 负责以下任务（来自 `01-architecture.md`）：

- TASK-04：`[任务描述]`
- TASK-05：`[任务描述]`

---

## 实现细节

### `[子模块名称]`

**对应需求**：REQ-F-01, REQ-F-02

**算法/方法选择**：

> 描述选择当前实现方案的原因，以及放弃了哪些替代方案。

选用 `[方案名称]`，原因：`[简述]`。
备选方案 `[替代方案]` 因 `[原因]` 被放弃。

**实现要点**：

```python
# 关键逻辑的伪代码或实际代码片段
def key_function(param: Type) -> ReturnType:
    # Step 1: [描述]
    ...
    # Step 2: [描述]
    ...
    # Edge case: [描述需要特殊处理的情况]
    ...
```

**边界情况处理**：

| 边界情况 | 处理方式 |
|---------|---------|
| 输入为空 | 抛出 `ValueError`，日志记录 |
| 超出内存限制 | 触发分块处理，降低并行度 |
| `[其他边界情况]` | `[处理方式]` |

### 错误处理实现

> 对照 `01-architecture.md` 中的错误处理策略，实现本模块的具体错误处理逻辑。

**异常转换规则**：

| 原始异常 | 转换为 | 触发条件 | 日志级别 |
|---------|-------|---------|---------|
| `FileNotFoundError` | `DataError` | 数据文件缺失 | `ERROR` |
| `ConnectionError` / `TimeoutError` | `ExternalServiceError` | 外部服务不可达 | `ERROR` |
| `json.JSONDecodeError` | `ConfigError` | 配置文件格式非法 | `ERROR` |
| `[其他原始异常]` | `[对应项目异常]` | `[条件]` | `[级别]` |

**错误传播实现**：

```python
# ✅ 异常转换 + 上下文保留
def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        raise ConfigError(f"配置文件不存在: {path}") from e
    except yaml.YAMLError as e:
        raise ConfigError(f"配置文件格式错误: {path}") from e

# ✅ 可恢复错误 → 降级 + 日志
def fetch_with_fallback(primary_url: str, fallback_url: str) -> Response:
    try:
        return http_client.get(primary_url, timeout=5)
    except (ConnectionError, TimeoutError) as e:
        logger.warning("主服务不可达，切换到备用: %s", e)
        return http_client.get(fallback_url, timeout=10)
```

**需要避免的反模式**：

```python
# ❌ 反模式 1：静默吞没 — 调用方无法感知失败
def get_data(key):
    try:
        return cache.get(key)
    except Exception:
        return None  # 调用方不知道这是"未找到"还是"服务挂了"

# ❌ 反模式 2：丢弃原始异常链
def process(data):
    try:
        return transform(data)
    except ValueError:
        raise DataError("转换失败")  # 缺少 `from e`，丢失原始 traceback

# ❌ 反模式 3：过宽捕获 — 掩盖了编程错误
def save(data):
    try:
        db.insert(data)
    except Exception as e:  # TypeError/AttributeError 也被吞掉了
        logger.error("保存失败: %s", e)
```

---

## 测试策略

### 单元测试

```python
# tests/test_[module_name].py

class Test[ClassName]:
    def test_[功能描述]_正常输入(self):
        """验收条件：REQ-F-01 - [具体验收标准]"""
        ...
    
    def test_[功能描述]_空输入(self):
        """边界用例：空输入应抛出 ValueError"""
        ...
    
    def test_[功能描述]_性能(self):
        """验收条件：REQ-P-01 - 吞吐量 >= X samples/sec"""
        ...
```

### 错误路径测试

```python
# tests/test_[module_name]_errors.py

class Test[ClassName]ErrorHandling:
    def test_[功能]_外部服务不可达时抛出ExternalServiceError(self):
        """错误传播：外部依赖失败时不应被静默吞没"""
        with pytest.raises(ExternalServiceError) as exc_info:
            ...
        assert exc_info.value.__cause__ is not None  # 验证异常链保留

    def test_[功能]_无效输入时抛出具体异常而非通用Exception(self):
        """异常精确性：捕获的异常类型应足够具体"""
        with pytest.raises(DataError):  # 不应是 Exception 或 ValueError
            ...

    def test_[功能]_降级路径返回有效结果(self):
        """降级行为：主路径失败时，降级路径应返回可用结果"""
        ...

    def test_[功能]_错误日志包含排障上下文(self, caplog):
        """日志质量：错误日志应包含足够的上下文信息"""
        with caplog.at_level(logging.ERROR):
            ...
        assert "[关键参数值]" in caplog.text
```

### 集成测试

- [ ] 与 `[上游模块]` 的接口联调
- [ ] 端到端 pipeline 跑通验证
- [ ] 显存占用监控测试
- [ ] 错误传播链路验证：模拟底层异常，确认顶层收到正确的项目自定义异常

---

## 任务分解（细化）

- [ ] **TASK-04.1**：实现 `[具体函数/类]`
  - 关联需求：REQ-F-01
  - 测试用例：`test_[描述]`

- [ ] **TASK-04.2**：实现边界处理逻辑
  - 关联需求：REQ-R-01
  - 测试用例：`test_[描述]_空输入`

- [ ] **TASK-04.3**：性能优化（向量化 / 算子融合）
  - 关联需求：REQ-P-01
  - 依赖：TASK-04.1 完成并通过基础测试

- [ ] **TASK-04.4**：补全类型标注与文档字符串
  - 关联需求：架构约束 §5

---

## 完成标准

以下条件全部满足时，本 spec 标记为**已完成**：

- [ ] 所有任务 checkbox 勾选
- [ ] 单元测试覆盖率 >= 80%
- [ ] 错误路径测试覆盖所有异常转换规则和降级行为
- [ ] 无裸 `except:` 块，无静默吞没（`ruff` 规则 `E722` / `B001` 通过）
- [ ] 所有 `raise ... from` 链保留完整（grep 验证无孤立 `raise CustomError(...)` 缺少 `from`）
- [ ] 性能测试满足 REQ-P-01、REQ-P-02
- [ ] mypy 类型检查通过（zero errors）
- [ ] ruff 代码风格检查通过
- [ ] `01-architecture.md` 中对应任务更新为已完成
