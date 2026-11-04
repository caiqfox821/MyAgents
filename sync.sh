#!/usr/bin/env bash
# MyAgents 一键同步：拉取 -> 提交 -> 推送
#
# 用法:
#   ./sync.sh                  自动生成提交信息（时间 + 文件数 + 文件清单）
#   ./sync.sh -m "说明"         指定提交信息
#   ./sync.sh --no-pull        跳过拉取（离线，或远端有冲突时）
#   ./sync.sh --dry-run        只展示将要执行的操作，不实际改动
#   ./sync.sh -h               显示本帮助
#
# 说明:
#   - 只处理当前分支；自动 --autostash，工作区有改动也能安全 rebase。
#   - 推送走 SSH，非交互（BatchMode），不会卡在输入。
#   - 首次无上游时会自动 push -u origin <当前分支>。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MSG=""
DO_PULL=1
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    -m|--message) MSG="${2:-}"; shift 2 ;;
    --no-pull)    DO_PULL=0; shift ;;
    --dry-run)    DRY=1; shift ;;
    -h|--help)    sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "未知参数: $1（用 -h 看帮助）" >&2; exit 2 ;;
  esac
done

export GIT_SSH_COMMAND="ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "✗ 不是 git 仓库: $ROOT"; exit 1; }

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
has_upstream() { git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; }
run() { if [ "$DRY" = 1 ]; then echo "    [dry-run] $*"; else "$@"; fi; }

echo "▸ 仓库: $ROOT"
echo "▸ 分支: $BRANCH"

# ── 1) 拉取 ──────────────────────────────────────────────
if [ "$DO_PULL" = 1 ] && has_upstream; then
  echo "▸ 拉取远端（rebase + autostash）…"
  run git pull --rebase --autostash --quiet
elif [ "$DO_PULL" = 1 ]; then
  echo "▸ 无上游分支，跳过拉取"
else
  echo "▸ 已跳过拉取（--no-pull）"
fi

# ── 2) 提交 ──────────────────────────────────────────────
if [ -z "$(git status --porcelain)" ]; then
  echo "▸ 工作区干净，无需提交"
else
  count="$(git status --porcelain | wc -l | tr -d ' ')"
  sample="$(git status --porcelain | cut -c4- | head -6 | sed 's/^/  - /')"
  [ -n "$MSG" ] || MSG="sync: $(date '+%Y-%m-%d %H:%M')（${count} 个文件）"
  echo "▸ 提交 ${count} 处改动：$MSG"
  run git add -A
  run git commit -q -m "$MSG" -m "$sample"
fi

# ── 3) 推送 ──────────────────────────────────────────────
if has_upstream; then
  ahead="$(git rev-list --count '@{u}'..HEAD)"
  if [ "$ahead" = 0 ]; then
    echo "▸ 本地与远端一致，无需推送"
  else
    echo "▸ 推送 $ahead 个提交…"
    run git push --quiet
  fi
elif git remote get-url origin >/dev/null 2>&1; then
  echo "▸ 首次推送并设置上游…"
  run git push -u origin "$BRANCH"
else
  echo "✗ 未配置 origin 远端，无法推送" >&2
  exit 1
fi

echo "✓ 同步完成"
