#!/usr/bin/env bash
# create-spec.sh — 从共享模板生成新的 spec 文件
# 用法: ./scripts/create-spec.sh <编号> <标题> [父级spec] [负责人]
# 示例: ./scripts/create-spec.sh 03 "数据处理模块" "01-architecture.md" "@zhangsan"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$PROJECT_ROOT/.kiro/templates/spec-template.md"
SPECS_DIR="$PROJECT_ROOT/.kiro/specs"

# 参数校验
if [ $# -lt 2 ]; then
    echo "用法: $0 <编号> <标题> [父级spec] [负责人]"
    echo "示例: $0 03 '数据处理模块' '01-architecture.md' '@zhangsan'"
    exit 1
fi

NUMBER="$1"
TITLE="$2"
PARENT_SPEC="${3:-无}"
AUTHOR="${4:-@username}"
DATE="$(date +%Y-%m-%d)"

OUTPUT_FILE="$SPECS_DIR/${NUMBER}-$(echo "$TITLE" | tr ' ' '-').md"

if [ -f "$OUTPUT_FILE" ]; then
    echo "错误：文件已存在: $OUTPUT_FILE"
    exit 1
fi

# 从模板生成
sed -e "s/{{NUMBER}}/$NUMBER/g" \
    -e "s/{{TITLE}}/$TITLE/g" \
    -e "s/{{PARENT_SPEC}}/$PARENT_SPEC/g" \
    -e "s/{{DATE}}/$DATE/g" \
    -e "s/{{AUTHOR}}/$AUTHOR/g" \
    "$TEMPLATE" > "$OUTPUT_FILE"

echo "已创建 spec 文件: $OUTPUT_FILE"
echo "下一步: 编辑文件填写具体需求和任务"
