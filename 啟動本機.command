#!/bin/zsh
set -eu
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  print '找不到 Python 3，請先安裝 Python 3 再開啟。'
  read '?按 Enter 關閉。'
  exit 1
fi
python3 src/serve.py
