#!/usr/bin/env bash
# tool/atlas_falsifier_auto_spawn.sh — Tier-1 i11 from improvement_ideas_omega_cycle (2026-04-26)
#
# atlas high-grade entries ([10*+] / [11*+]) 에서 falsifier candidate 자동 spawn.
# 각 entry → F<NN> template (claim/cmd/pass/reason/fix/origin) emit.
# falsifiers.jsonl 직접 mutate 안 함 (suggest mode, raw 71 manual escalate).
# self-host 회피 (bash + grep + awk, no hexa dep).
#
# usage:
#   tool/atlas_falsifier_auto_spawn.sh                      # all candidates
#   tool/atlas_falsifier_auto_spawn.sh --type T             # filter by @type
#   tool/atlas_falsifier_auto_spawn.sh --grade G            # filter by grade
#   tool/atlas_falsifier_auto_spawn.sh --emit-jsonl         # emit JSONL to state/
#   tool/atlas_falsifier_auto_spawn.sh --limit N
#
# exit codes: 0=PASS, 1=usage, 2=no candidates
# sentinel: __ATLAS_FALSIFIER_SPAWN__ scanned=N candidates=C suggested=S existing=E
# origin: design/hexa_sim/2026-04-26_improvement_ideas_omega_cycle.json axis_i11

set -uo pipefail

NEXUS_ROOT="${NEXUS_ROOT:-$HOME/core/nexus}"
ATLAS_INDEX="$NEXUS_ROOT/state/atlas_index.tsv"
FALSIFIERS="$NEXUS_ROOT/design/hexa_sim/falsifiers.jsonl"
CANDIDATES_PATH="$NEXUS_ROOT/state/falsifier_candidates.jsonl"
mkdir -p "$NEXUS_ROOT/state" 2>/dev/null

TYPE_FILTER=""
GRADE_FILTER=""
LIMIT=20
EMIT_JSONL=0

while [ $# -gt 0 ]; do
    case "$1" in
        --type) TYPE_FILTER="$2"; shift 2 ;;
        --grade) GRADE_FILTER="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        --emit-jsonl) EMIT_JSONL=1; shift ;;
        --help|-h)
            echo "usage: $0 [--type T] [--grade G] [--emit-jsonl] [--limit N]"
            echo "  --type T:        filter by @type (P/C/F/L/R/S/X/M/T/E)"
            echo "  --grade G:       filter by grade (e.g. '11', '10*')"
            echo "  --emit-jsonl:    write candidates to state/falsifier_candidates.jsonl"
            echo "  --limit N:       cap output (default 20)"
            exit 0
            ;;
        *) echo "unknown: $1" >&2; exit 1 ;;
    esac
done

# Pre-flight: index must exist
if [ ! -f "$ATLAS_INDEX" ]; then
    echo "atlas index not found at $ATLAS_INDEX — run: bash tool/atlas_index.sh" >&2
    exit 1
fi

# Step 1: load existing falsifier ids (skip duplicates)
existing_ids=""
if [ -f "$FALSIFIERS" ]; then
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        local_id=$(echo "$line" | sed -nE 's/.*"id":"([^"]+)".*/\1/p')
        local_origin=$(echo "$line" | sed -nE 's/.*"origin":"([^"]+)".*/\1/p')
        # extract atlas id mentioned in origin
        atlas_id=$(echo "$local_origin" | grep -oE '\b[a-zA-Z][a-zA-Z0-9_]+\b' | head -1)
        [ -n "$atlas_id" ] && existing_ids="$existing_ids|$atlas_id|"
    done < "$FALSIFIERS"
fi
EXISTING_COUNT=$(grep -cE '^\{"id":"F' "$FALSIFIERS" 2>/dev/null || echo 0)

# Step 2: scan high-grade entries (use atlas_search shard reading)
SCANNED=0
CANDIDATES=0
SUGGESTED=0
NEXT_F=$((EXISTING_COUNT + 1))

# Truncate candidates jsonl if emit mode
[ "$EMIT_JSONL" = "1" ] && > "$CANDIDATES_PATH"

echo "atlas → falsifier auto-spawn candidates"
echo "─────────────────────────────────────────────────────────────"
echo "criteria: high-grade [10*+] or [11*+] entries with re-fetchable cmd"
echo "existing falsifiers: $EXISTING_COUNT (F1..F$EXISTING_COUNT)"
echo ""

# Read atlas index, filter high-grade by re-grepping the source line
while IFS=$'\t' read -r id type line shard; do
    [ "$id" = "id" ] && continue  # skip header
    SCANNED=$((SCANNED + 1))
    # Apply --type filter
    [ -n "$TYPE_FILTER" ] && [ "$type" != "$TYPE_FILTER" ] && continue
    # Read the actual line + extract grade
    full_path="$NEXUS_ROOT/$shard"
    [ ! -f "$full_path" ] && continue
    line_txt=$(sed -n "${line}p" "$full_path" 2>/dev/null)
    [ -z "$line_txt" ] && continue
    grade=$(echo "$line_txt" | sed -nE 's/.*\[([^]]+)\].*$/\1/p')
    # Apply --grade filter (must START with the filter, e.g. "11" matches "11*REPO_INVARIANT")
    if [ -n "$GRADE_FILTER" ]; then
        if ! echo "$grade" | grep -qE "^${GRADE_FILTER}"; then continue; fi
    fi
    # Default high-grade only: must contain '*' (10*+ / 11*+)
    if [ -z "$GRADE_FILTER" ]; then
        if ! echo "$grade" | grep -q '\*'; then continue; fi
    fi
    # Skip if id already mentioned in existing falsifier origin
    if echo "$existing_ids" | grep -q "|$id|"; then continue; fi
    CANDIDATES=$((CANDIDATES + 1))
    if [ "$SUGGESTED" -ge "$LIMIT" ]; then continue; fi

    # Build candidate falsifier template
    fid="F${NEXT_F}"
    NEXT_F=$((NEXT_F + 1))
    SUGGESTED=$((SUGGESTED + 1))
    slug=$(echo "$id" | tr '[:upper:]_' '[:lower:]-' | sed 's/[^a-z0-9-]//g')
    expr=$(echo "$line_txt" | sed -nE 's/^@[PCFLRSXMTE] [^ ]+ = (.+) :: .*$/\1/p')
    domain=$(echo "$line_txt" | sed -nE 's/.* :: ([^ ]+) \[.*$/\1/p')

    # Suggest cmd template: re-grep atlas for this id (simplest verification — entry still exists)
    cmd="grep -qE '^@${type} ${id} =' /Users/ghost/core/nexus/${shard} && echo PRESENT_$(echo "$id" | tr '[:lower:]' '[:upper:]')_${type}"
    pass="PRESENT_$(echo "$id" | tr '[:lower:]' '[:upper:]')_${type}"
    reason="atlas entry @${type} ${id} (current grade [${grade}]) was retired or modified — implies underlying claim '${expr}' no longer holds in domain ${domain}"
    fix="re-verify source (origin shard ${shard} line ${line}); if intentional retirement, update falsifier registry and atlas concurrently"
    origin="auto-spawn from atlas_index entry ${id} (@${type}, [${grade}], ${shard}:${line})"

    if [ "$EMIT_JSONL" = "1" ]; then
        # Escape JSON values (basic — assumes no quotes in expr/domain)
        printf '{"id":"%s","slug":"%s","claim":"atlas entry %s = %s remains @%s in %s","cmd":"%s","pass":"%s","reason":"%s","fix":"%s","origin":"%s"}\n' \
            "$fid" "$slug" "$id" "$expr" "$type" "$domain" "$cmd" "$pass" "$reason" "$fix" "$origin" >> "$CANDIDATES_PATH"
    else
        printf "  %s [%s]  @%s %s [%s]\n" "$fid" "$slug" "$type" "$id" "$grade"
        printf "      claim:  atlas entry @%s %s remains in %s\n" "$type" "$id" "$shard"
        printf "      origin: %s:%s\n" "$shard" "$line"
        echo ""
    fi
done < "$ATLAS_INDEX"

echo "─────────────────────────────────────────────────────────────"
if [ "$EMIT_JSONL" = "1" ]; then
    echo "JSONL emitted: $CANDIDATES_PATH"
    echo "  $(wc -l < "$CANDIDATES_PATH" | tr -d ' ') candidates written"
fi
echo "__ATLAS_FALSIFIER_SPAWN__ scanned=$SCANNED candidates=$CANDIDATES suggested=$SUGGESTED existing=$EXISTING_COUNT"
echo ""
if [ "$CANDIDATES" -gt "$SUGGESTED" ]; then
    echo "(showing first $SUGGESTED of $CANDIDATES candidates; use --limit N for more)"
fi
echo ""
echo "NOTE: SUGGEST mode 만 — falsifiers.jsonl 직접 mutate 안 함."
echo "  manual merge: review state/falsifier_candidates.jsonl + cat 추가:"
echo "    cat state/falsifier_candidates.jsonl >> design/hexa_sim/falsifiers.jsonl"
echo "  raw 71 정신 (manual escalate, no auto-promote)."
exit 0
