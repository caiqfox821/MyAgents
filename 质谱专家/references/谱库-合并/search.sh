#!/usr/bin/env bash
# 统一检索入口：把查询谱与合并谱库比对（转发到 spectral-matching 技能）
# 用法: ./search.sh <查询谱.msp|mgf|csv|json> [match.py 的其他参数...]
# 例:   ./search.sh unknown.msp
#       ./search.sh unknown.mgf --adduct '[M-H]-' --top 5 --method entropy,cosine_greedy
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="${SPECTRAL_MATCHING:-$HOME/MyAgents/质谱专家/skills/spectral-matching/scripts/match.py}"
if [ $# -lt 1 ]; then
  echo "用法: $0 <查询谱.msp|mgf|csv|json> [match.py 参数...]" >&2
  echo "     可选环境变量 SPECTRAL_MATCHING=/path/to/match.py" >&2
  exit 2
fi
Q="$1"; shift
exec env -u http_proxy -u https_proxy -u all_proxy python3 "$SKILL" \
  --query "$Q" --library "$HERE/library.msp" \
  --precursor-ppm "${PRECURSOR_PPM:-50}" --top "${TOP:-10}" --format md "$@"
