#!/usr/bin/env bash
HOOK_BIN="$HOME/Dev/nexus6/target/release/nexus6_hook"
[ -x "$HOOK_BIN" ] && { cat | "$HOOK_BIN" --mode agent; exit 0; }
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/ensure-symlinks.sh" || exit 0
cat | python3 "$HOOK_DIR/nexus6-engine.py" --mode agent 2>/dev/null
exit 0
