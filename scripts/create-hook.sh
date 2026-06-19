#!/usr/bin/env bash
# create-hook.sh — 从共享模板生成新的 hook 文件
# 用法: ./scripts/create-hook.sh <hook名称> <触发模式> <描述>
# 示例: ./scripts/create-hook.sh "lint-check" "src/**/*.py" "代码风格检查"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$PROJECT_ROOT/.kiro/templates/hook-template.yml"
HOOKS_DIR="$PROJECT_ROOT/.kiro/hooks"
SHARED_EXCLUDES="$PROJECT_ROOT/.kiro/shared/python-excludes.yml"

# 参数校验
if [ $# -lt 3 ]; then
    echo "用法: $0 <hook名称> <触发模式> <描述>"
    echo "示例: $0 'lint-check' 'src/**/*.py' '代码风格检查'"
    echo ""
    echo "共享排除模式（自动包含）："
    grep -A2 "^python_compiled:" "$SHARED_EXCLUDES" | grep "^  -" || true
    exit 1
fi

HOOK_NAME="$1"
TRIGGER_PATTERN="$2"
DESCRIPTION="$3"

OUTPUT_FILE="$HOOKS_DIR/${HOOK_NAME}.yml"

if [ -f "$OUTPUT_FILE" ]; then
    echo "错误：文件已存在: $OUTPUT_FILE"
    exit 1
fi

# 从模板生成
sed -e "s/{{HOOK_NAME}}/$HOOK_NAME/g" \
    -e "s|{{TRIGGER_PATTERN}}|$TRIGGER_PATTERN|g" \
    -e "s/{{DESCRIPTION}}/$DESCRIPTION/g" \
    -e "s/{{STEP_1_TITLE}}/[步骤1标题]/g" \
    -e "s/{{STEP_1_CONTENT}}/[步骤1具体内容]/g" \
    -e "s/{{STEP_2_TITLE}}/[步骤2标题]/g" \
    -e "s/{{STEP_2_CONTENT}}/[步骤2具体内容]/g" \
    -e "s/{{STEP_3_TITLE}}/[步骤3标题]/g" \
    -e "s/{{STEP_3_CONTENT}}/[步骤3具体内容]/g" \
    -e "s/{{OUTPUT_FORMAT}}/如无需处理，输出确认信息。/g" \
    "$TEMPLATE" > "$OUTPUT_FILE"

echo "已创建 hook 文件: $OUTPUT_FILE"
echo "下一步: 编辑文件填写具体的检查步骤和输出格式"
echo ""
echo "提示: 排除模式已从共享配置自动填入。"
echo "      如需额外排除模式，请同步更新 .kiro/shared/python-excludes.yml"
