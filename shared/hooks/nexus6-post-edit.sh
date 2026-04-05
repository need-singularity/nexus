#!/usr/bin/env bash
# mk2 hexa-only hook (Rust/Python 의존 0)
set +e
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$HOOK_DIR/bootstrap.sh" || exit 0

INPUT=$(cat)
bash "$HOOK_DIR/growth-tick.sh" post-edit </dev/null >/dev/null 2>&1 &

HEXA="$HOME/Dev/hexa-lang/target/release/hexa"
HEXA_HOOK="$HOME/Dev/nexus6/mk2_hexa/native/hook.hexa"
MK1_HOOK="$HOME/Dev/nexus6/target/release/nexus6_hook"

# mk2 (hexa) 우선
RESULT=$(echo "$INPUT" | "$HEXA" "$HEXA_HOOK" post-edit 2>/dev/null) || true

# mk1 (Rust) 병렬 — detect 파이프라인
if [ -x "$MK1_HOOK" ]; then
  echo "$INPUT" | "$MK1_HOOK" --mode post-edit 2>/dev/null &
elif [ -x "$HOME/Dev/nexus6/target/release/nexus6" ]; then
  echo "$INPUT" | "$HOME/Dev/nexus6/target/release/nexus6" detect --min-matches 2 --adaptive 2>/dev/null &
fi

[ -n "$RESULT" ] && echo "$RESULT" || bash "$HOOK_DIR/nexus6-banner.sh"
exit 0
