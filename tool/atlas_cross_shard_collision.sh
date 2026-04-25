#!/usr/bin/env bash
# tool/atlas_cross_shard_collision.sh — cross-shard collision CI guard
#
# Watchdog for design/hexa_sim/2026-04-26_cross_shard_dedup_audit.md
# (56 byte-identical duplicates between atlas.append.chip-p5-2.n6 and atlas.n6,
# since retired). Pure bash 3.2 (macOS), no hexa dep, read-only.
#
# usage:
#   tool/atlas_cross_shard_collision.sh              # report + exit 0/76
#   tool/atlas_cross_shard_collision.sh --quiet      # silent, only sentinel
#   tool/atlas_cross_shard_collision.sh --tsv PATH   # write TSV report to PATH
#   tool/atlas_cross_shard_collision.sh --warn-dup   # exit 76 on HARMLESS_DUP too
#
# Behavior: glob atlas.append.*.n6 + atlas.n6 → extract (type, id, value)
# tuples → for any id in 2+ shards: same value → HARMLESS_DUP (warn); diff
# value → CONFLICT (urgent). TSV columns: type id shard_a shard_b value_eq status
#
# Exit: 0 ok / 76 conflict (raw 23) or --warn-dup with dups / 1 usage
# Sentinel (raw 80): __ATLAS_CROSS_SHARD_COLLISION__ <PASS|WARN|FAIL> shards=N total=T unique=U dup=D conflict=C
# Compliance: raw 23 + raw 66 (reason+fix) + raw 77 (read-only) + raw 80
# Origin: design/hexa_sim/2026-04-26_cross_shard_dedup_audit.md (Ω-cycle followup)

set -uo pipefail

NEXUS_ROOT="${NEXUS_ROOT:-$HOME/core/nexus}"
ATLAS_MAIN="$NEXUS_ROOT/n6/atlas.n6"
ATLAS_SHARDS_GLOB="$NEXUS_ROOT/n6/atlas.append.*.n6"

QUIET=0
WARN_DUP=0
TSV_OUT=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet)    QUIET=1; shift ;;
        --warn-dup) WARN_DUP=1; shift ;;
        --tsv)
            if [ $# -lt 2 ]; then
                echo "usage error: --tsv requires PATH" >&2
                echo "  reason: --tsv flag missing its PATH argument" >&2
                echo "  fix:    pass an output path, e.g. --tsv /tmp/collision.tsv" >&2
                exit 1
            fi
            TSV_OUT="$2"; shift 2 ;;
        --help|-h)
            sed -n '3,40p' "$0"
            exit 0
            ;;
        *)
            echo "usage error: unknown flag: $1" >&2
            echo "  reason: only --quiet|--tsv PATH|--warn-dup|--help recognized" >&2
            echo "  fix:    run \`$0 --help\` for the full flag list" >&2
            exit 1 ;;
    esac
done

# ─── Build shard list ─────────────────────────────────────────────────────────
SHARDS=""
N_SHARDS=0
if [ -f "$ATLAS_MAIN" ]; then
    SHARDS="$ATLAS_MAIN"
    N_SHARDS=$((N_SHARDS + 1))
fi
for f in $ATLAS_SHARDS_GLOB; do
    if [ -f "$f" ]; then
        if [ -z "$SHARDS" ]; then SHARDS="$f"; else SHARDS="$SHARDS
$f"; fi
        N_SHARDS=$((N_SHARDS + 1))
    fi
done

if [ "$N_SHARDS" -eq 0 ]; then
    echo "fatal: no atlas shards found" >&2
    echo "  reason: glob $ATLAS_SHARDS_GLOB and $ATLAS_MAIN both empty" >&2
    echo "  fix:    set NEXUS_ROOT=<path-to-nexus-checkout> or run from a nexus tree" >&2
    echo "__ATLAS_CROSS_SHARD_COLLISION__ FAIL shards=0 total=0 unique=0 dup=0 conflict=0"
    exit 1
fi

# Extract (type<TAB>id<TAB>value<TAB>shard) tuples. Format:
#   @<T> <id> = <value...> :: <domain> [<grade>]
# Combined value = "<value> :: <domain> [<grade>]" (so grade drift = CONFLICT).
TUPLES=$(mktemp)
trap 'rm -f "$TUPLES"' EXIT

echo "$SHARDS" | while IFS= read -r shard; do
    [ -z "$shard" ] && continue
    base=$(basename "$shard")
    awk -v shard="$base" '
        /^@[PCFLRSXMTE] [^ ]+ =/ {
            eq_pos = index($0, "=")
            if (eq_pos == 0) next
            tail = substr($0, eq_pos + 1); sub(/^ +/, "", tail); sub(/ +$/, "", tail)
            printf "%s\t%s\t%s\t%s\n", $1, $2, tail, shard
        }
    ' "$shard" >> "$TUPLES"
done

TOTAL=$(wc -l < "$TUPLES" | tr -d ' ')

# Sort by (type, id, shard) → cluster duplicates → fold across rows.
SORTED=$(mktemp)
trap 'rm -f "$TUPLES" "$SORTED"' EXIT
sort -t $'\t' -k1,1 -k2,2 -k4,4 "$TUPLES" > "$SORTED"
UNIQUE=$(awk -F'\t' '{print $1"\t"$2}' "$SORTED" | sort -u | wc -l | tr -d ' ')

# For each (type, id) in 2+ distinct shards, emit one row per (shard_a, shard_b)
# pair in canonical lex order with HARMLESS_DUP / CONFLICT verdict.
COLLISIONS=$(mktemp)
trap 'rm -f "$TUPLES" "$SORTED" "$COLLISIONS"' EXIT
awk -F'\t' '
    function flush(    i, j, sa, sb, va, vb, eq, status) {
        if (n < 2) return
        for (i = 1; i <= n; i++) for (j = i + 1; j <= n; j++) {
            if (shards[i] == shards[j]) continue
            va = vals[i]; vb = vals[j]
            if (va == vb) { eq = "Y"; status = "HARMLESS_DUP" }
            else          { eq = "N"; status = "CONFLICT" }
            if (shards[i] < shards[j]) { sa = shards[i]; sb = shards[j] }
            else                       { sa = shards[j]; sb = shards[i] }
            printf "%s\t%s\t%s\t%s\t%s\t%s\n", cur_type, cur_id, sa, sb, eq, status
        }
    }
    { key = $1 "\t" $2
      if (key != prev_key && NR > 1) { flush(); n = 0 }
      n++; vals[n] = $3; shards[n] = $4
      cur_type = $1; cur_id = $2; prev_key = key
    }
    END { flush() }
' "$SORTED" > "$COLLISIONS"

DUP=$(awk -F'\t' '$6 == "HARMLESS_DUP"' "$COLLISIONS" | wc -l | tr -d ' ')
CONF=$(awk -F'\t' '$6 == "CONFLICT"' "$COLLISIONS" | wc -l | tr -d ' ')

if [ -n "$TSV_OUT" ]; then
    { printf "type\tid\tshard_a\tshard_b\tvalue_eq\tstatus\n"; cat "$COLLISIONS"; } > "$TSV_OUT" || {
        echo "fatal: failed writing TSV to $TSV_OUT" >&2
        echo "  reason: filesystem or permissions error" >&2
        echo "  fix:    pick a writable path, e.g. --tsv /tmp/collision.tsv" >&2
        exit 1
    }
fi

VERDICT="PASS"; EXIT_CODE=0
if   [ "$CONF" -gt 0 ];                          then VERDICT="FAIL"; EXIT_CODE=76
elif [ "$DUP" -gt 0 ] && [ "$WARN_DUP" = "1" ];  then VERDICT="FAIL"; EXIT_CODE=76
elif [ "$DUP" -gt 0 ];                           then VERDICT="WARN"
fi

if [ "$QUIET" = "0" ]; then
    echo "atlas cross-shard collision report"
    echo "  shards scanned : $N_SHARDS"
    echo "  total tuples   : $TOTAL"
    echo "  unique (type,id): $UNIQUE"
    echo "  HARMLESS_DUP   : $DUP"
    echo "  CONFLICT       : $CONF"

    if [ "$CONF" -gt 0 ]; then
        echo ""
        echo "CONFLICT detail (urgent — different value at same (type,id)):"
        awk -F'\t' '$6 == "CONFLICT" { printf "  %s %s\n    %s\n    %s\n", $1, $2, $3, $4 }' "$COLLISIONS"
        echo ""
        echo "  reason: same (type,id) carries divergent values across shards" >&2
        echo "  fix:    reconcile values; pick canonical shard, then drop or namespace the other" >&2
    elif [ "$DUP" -gt 0 ]; then
        echo ""
        echo "HARMLESS_DUP families (first 10):"
        awk -F'\t' '$6 == "HARMLESS_DUP" { printf "  %s %-40s %s ↔ %s\n", $1, $2, $3, $4 }' "$COLLISIONS" | head -10
        if [ "$DUP" -gt 10 ]; then
            echo "  ... ($DUP total — see TSV for full list)"
        fi
        if [ "$WARN_DUP" = "1" ]; then
            echo ""
            echo "  reason: --warn-dup set and HARMLESS_DUP > 0 — strict mode failed" >&2
            echo "  fix:    retire the redundant shard (the one whose entries are already in atlas.n6)" >&2
        fi
    fi

    if [ -n "$TSV_OUT" ]; then
        echo ""
        echo "wrote TSV: $TSV_OUT"
    fi
    echo ""
fi

echo "__ATLAS_CROSS_SHARD_COLLISION__ $VERDICT shards=$N_SHARDS total=$TOTAL unique=$UNIQUE dup=$DUP conflict=$CONF"
exit $EXIT_CODE
