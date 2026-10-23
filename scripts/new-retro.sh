#!/usr/bin/env bash
# 新增复盘记录
# 用法: scripts/new-retro.sh <专家> <主题>
#   例: scripts/new-retro.sh 种植专家 番茄施肥方案返工
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$ROOT/retrospectives"
TPL="$DIR/_template.md"

if [ "$#" -lt 2 ]; then
  echo "用法: $0 <专家> <主题>" >&2
  exit 1
fi

expert="$1"
shift
topic="$*"
date="$(date +%F)"
out="$DIR/$date-$expert-$topic.md"

if [ ! -f "$TPL" ]; then
  echo "模板不存在: $TPL" >&2
  exit 1
fi

content="$(<"$TPL")"
content="${content//<DATE>/$date}"
content="${content//<EXPERT>/$expert}"
content="${content//<TOPIC>/$topic}"
printf '%s\n' "$content" > "$out"

echo "已创建: $out"
echo "下一步: 填写问题根因与固化动作，并更新 EVOLUTION.md。"
