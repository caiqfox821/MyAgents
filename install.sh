#!/usr/bin/env bash
# 将 MyAgents 中的专家 agent 与技能同步/安装到 opencode。
# 用法:
#   ./install.sh           # 软链接到全局 ~/.config/opencode（默认，推荐）
#   ./install.sh --copy    # 复制而非软链接（不随源文件更新）
#   ./install.sh --project # 仅刷新项目内 .opencode 链接
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="link"
TARGET="global"

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --link) MODE="link" ;;
    --project) TARGET="project" ;;
    --global) TARGET="global" ;;
    *) echo "unknown arg: $arg" >&2; exit 1 ;;
  esac
done

# 专家名 -> 目录
AGENTS=(
  "orchestrator:协调专家"
  "planting-expert:种植专家"
  "breeding-expert:育种专家"
  "nursery-expert:育苗专家"
  "fermentation-expert:发酵专家"
  "document-expert:文档专家"
  "food-processing-expert:食品加工专家"
  "food-safety-expert:食品安全专家"
  "nutrition-expert:营养专家"
  "detection-expert:检测专家"
  "mass-spec-expert:质谱专家"
  "toxicology-expert:毒理专家"
  "submission-expert:投稿专家"
)
SKILLS=(
  "orchestration:协调专家"
  "planting-knowledge:种植专家"
  "plant-lstm:种植专家"
  "breeding-knowledge:育种专家"
  "nursery-knowledge:育苗专家"
  "fermentation-knowledge:发酵专家"
  "microbial-growth:发酵专家"
  "document-format:文档专家"
  "food-processing:食品加工专家"
  "food-safety:食品安全专家"
  "nutrition:营养专家"
  "nutritionist:营养专家"
  "detection-analysis:检测专家"
  "mass-spectrometry:质谱专家"
  "toxicology:毒理专家"
  "journal-submission:投稿专家"
  "togomcp-sparql:公共技能"
  "risk-assessment:公共技能"
)

place() {
  local src="$1" dst="$2"
  rm -rf "$dst"
  if [ "$MODE" = "copy" ]; then
    cp -R "$src" "$dst"
  else
    ln -s "$src" "$dst"
  fi
}

if [ "$TARGET" = "project" ]; then
  AGENT_DIR="$ROOT/.opencode/agent"
  SKILL_DIR="$ROOT/.opencode/skills"
else
  AGENT_DIR="$HOME/.config/opencode/agents"
  SKILL_DIR="$HOME/.config/opencode/skills"
fi
mkdir -p "$AGENT_DIR" "$SKILL_DIR"

for entry in "${AGENTS[@]}"; do
  name="${entry%%:*}"; dir="${entry#*:}"
  place "$ROOT/$dir/agent.md" "$AGENT_DIR/$name.md"
  echo "agent  -> $AGENT_DIR/$name.md"
done

for entry in "${SKILLS[@]}"; do
  name="${entry%%:*}"; dir="${entry#*:}"
  place "$ROOT/$dir/skills/$name" "$SKILL_DIR/$name"
  echo "skill  -> $SKILL_DIR/$name"
done

echo "完成 ($MODE -> $TARGET)。重启 opencode 生效。"
