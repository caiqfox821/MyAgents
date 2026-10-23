#!/usr/bin/env bash
# 新增评估用例
# 用法: scripts/new-eval.sh <专家> <slug>
#   专家：中文目录名（如 种植专家）或 agent id（如 planting-expert）
#   slug：简短英文/拼音主题（如 soil-fertigation），不要含空格
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVALS="$ROOT/evals"
TPL="$EVALS/_template.md"

if [ "$#" -lt 2 ]; then
  echo "用法: $0 <专家> <slug>" >&2
  exit 1
fi

expert="$1"
slug="$2"

case "$expert" in
  协调专家|orchestrator)       expert="协调专家";     code="ORCH";     aid="orchestrator" ;;
  种植专家|planting-expert)    expert="种植专家";     code="PLANT";    aid="planting-expert" ;;
  育种专家|breeding-expert)    expert="育种专家";     code="BREED";    aid="breeding-expert" ;;
  育苗专家|nursery-expert)     expert="育苗专家";     code="NURSERY";  aid="nursery-expert" ;;
  发酵专家|fermentation-expert) expert="发酵专家";    code="FERM";     aid="fermentation-expert" ;;
  食品加工专家|food-processing-expert) expert="食品加工专家"; code="FOODPROC"; aid="food-processing-expert" ;;
  食品安全专家|food-safety-expert) expert="食品安全专家"; code="FOODSAFE"; aid="food-safety-expert" ;;
  营养专家|nutrition-expert)   expert="营养专家";     code="NUTRI";    aid="nutrition-expert" ;;
  检测专家|detection-expert) expert="检测专家"; code="DETECT"; aid="detection-expert" ;;
  文档专家|document-expert)    expert="文档专家";     code="DOC";      aid="document-expert" ;;
  *) echo "未知专家: $expert" >&2; exit 1 ;;
esac

if [ ! -f "$TPL" ]; then
  echo "模板不存在: $TPL" >&2
  exit 1
fi

dir="$EVALS/$expert"
mkdir -p "$dir"
n="$(find "$dir" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
id="$(printf '%s-%03d' "$code" $((n + 1)))"
out="$dir/$id-$slug.md"

content="$(<"$TPL")"
content="${content//<ID>/$id}"
content="${content//<TITLE>/$slug}"
content="${content//<EXPERT>/$expert}"
content="${content//<AGENT_ID>/$aid}"
content="${content//<DATE>/$(date +%F)}"
printf '%s\n' "$content" > "$out"

echo "已创建: $out"
echo "下一步: 到 evals/registry.md 登记该用例，并填写 Rubric。"
