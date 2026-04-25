#!/usr/bin/env bash
# Self-test for lint_nested_if_continue.sh
# Verifies: BAD fixture → exit 1, GOOD fixture → exit 0
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
LINT="$HERE/../lint_nested_if_continue.sh"
[ -x "$LINT" ] || { echo "FAIL: lint not executable: $LINT"; exit 2; }

fail=0

"$LINT" "$HERE/nested_if_continue_BAD.hexa" >/dev/null 2>&1
rc=$?
if [ "$rc" = "1" ]; then echo "OK   BAD  → exit 1"
else                     echo "FAIL BAD  → exit $rc (expected 1)"; fail=1; fi

"$LINT" "$HERE/nested_if_continue_GOOD.hexa" >/dev/null 2>&1
rc=$?
if [ "$rc" = "0" ]; then echo "OK   GOOD → exit 0"
else                     echo "FAIL GOOD → exit $rc (expected 0)"; fail=1; fi

# Also re-verify post-sweep tool/ is clean (regression guard)
"$LINT" "$(cd "$HERE/../.." && pwd)" >/dev/null 2>&1
rc=$?
if [ "$rc" = "0" ]; then echo "OK   tool/ clean → exit 0"
else                     echo "FAIL tool/ → exit $rc (expected 0)"; fail=1; fi

if [ "$fail" = "0" ]; then echo "ALL PASS"; exit 0
else echo "SELFTEST FAILED"; exit 1; fi
