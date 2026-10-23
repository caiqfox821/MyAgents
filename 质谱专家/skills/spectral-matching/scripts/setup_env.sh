#!/usr/bin/env bash
# 为 spectral-matching 技能建立「可选增强后端」的独立 Python 环境。
# 核心功能无需它（纯 Python + numpy 即可）；装了以后解锁：
#   matchms     完整导入/过滤/打分生态
#   ms_entropy  高速熵相似度（大库检索）
#   pyteomics   mzML / mzXML 读取
#   rdkit       由 SMILES 推导 InChIKey / 指纹
#
# 用法:  ./setup_env.sh [目标目录]      # 默认 ~/opt/specmatch-venv
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${1:-$HOME/opt/specmatch-venv}"
PY_BIN=""

for cand in python3.12 python3.11 python3.10 python3.9; do
  if command -v "$cand" >/dev/null 2>&1; then PY_BIN="$(command -v "$cand")"; break; fi
done
if [ -z "$PY_BIN" ]; then
  echo "未找到 python3.9+ 解释器；matchms 需要 3.9 以上。" >&2
  echo "可用 micromamba 建环境：micromamba create -n specmatch python=3.12" >&2
  exit 1
fi
echo "使用解释器：$PY_BIN"

# 本机 PyPI 需直连（代理不可用）
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY || true

if command -v uv >/dev/null 2>&1; then
  uv venv --python "$PY_BIN" "$VENV"
  uv pip install --python "$VENV/bin/python" matchms ms_entropy pyteomics rdkit
else
  "$PY_BIN" -m venv "$VENV"
  "$VENV/bin/pip" install -U pip
  "$VENV/bin/pip" install matchms ms_entropy pyteomics rdkit
fi

echo
echo "完成。校验："
"$VENV/bin/python" -c "import matchms; print('  matchms', matchms.__version__)"
"$VENV/bin/python" -c "import ms_entropy; print('  ms_entropy ok')"
"$VENV/bin/python" -c "import pyteomics; print('  pyteomics', pyteomics.__version__)"
echo
echo "用该环境跑技能："
echo "  $VENV/bin/python $ROOT/match.py --caps"
