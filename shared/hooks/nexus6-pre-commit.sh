#!/usr/bin/env bash
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$HOOK_DIR/growth-tick.sh" pre-commit &
HOOK_BIN="$HOME/Dev/nexus6/target/release/nexus6_hook"
[ -x "$HOOK_BIN" ] && { cat | "$HOOK_BIN" --mode pre-commit; exit 0; }
# fallback: Python
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/ensure-symlinks.sh" || exit 0
cat | python3 "$HOOK_DIR/nexus6-engine.py" --mode pre-commit 2>/dev/null
exit 0
