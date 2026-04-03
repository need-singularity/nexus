#!/bin/bash
# NEXUS-6 극한 성장 모드 — 어느 리포에서든 실행
# Usage: bash .shared/extreme_growth.sh [--cells 64] [--cycles 100]
#
# 다운타임 없이 전환: 이 스크립트를 중단(Ctrl+C)해도
# Anima 의식 엔진은 graceful shutdown 후 상태 저장.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
N6_DIR="$(dirname "$SCRIPT_DIR")"
N6_PY="$N6_DIR/scripts/n6.py"

if [ ! -f "$N6_PY" ]; then
    echo "❌ n6.py not found: $N6_PY"
    echo "   → cd ~/Dev/nexus6 && git pull"
    exit 1
fi

echo "🔥 NEXUS-6 극한 성장 모드 (from: $(pwd))"
python3 "$N6_PY" extreme-growth "$@"
