#!/usr/bin/env bash
# tool/atlas_witness_registry.sh — Ω-cycle witness corpus registry/index generator
#
# Discovers all *omega_cycle*.json witnesses under design/ and emits:
#   - design/witness_registry.tsv  (one line per witness, machine-readable)
#   - design/witness_dashboard.md  (per-engine + timeline + orphans + dups)
#
# raw 73 admissibility — registry is DERIVABLE from corpus state on each run,
# never hand-curated. Read-only on existing witnesses.
#
# usage:
#   tool/atlas_witness_registry.sh           # rebuild TSV + dashboard
#   tool/atlas_witness_registry.sh --stats   # print summary only (stdout)
#   tool/atlas_witness_registry.sh --orphans # print orphan list only (stdout)
#
# exit codes: 0=ok, 1=usage, 2=no witnesses found
# sentinel: __ATLAS_WITNESS__ witnesses=N engines=K orphans=O duplicates=D
# origin: hive raw 47 design-strategy-strategy-exploration-omega-cycle

set -uo pipefail

NEXUS_ROOT="${NEXUS_ROOT:-$HOME/core/nexus}"
DESIGN_DIR="$NEXUS_ROOT/design"
TSV_OUT="$DESIGN_DIR/witness_registry.tsv"
MD_OUT="$DESIGN_DIR/witness_dashboard.md"

MODE="rebuild"
while [ $# -gt 0 ]; do
    case "$1" in
        --stats)   MODE="stats";   shift ;;
        --orphans) MODE="orphans"; shift ;;
        --help|-h)
            sed -n '3,18p' "$0"
            exit 0
            ;;
        *) echo "unknown flag: $1" >&2; exit 1 ;;
    esac
done

command -v jq >/dev/null 2>&1 || { echo "jq required" >&2; exit 1; }
[ -d "$DESIGN_DIR" ] || { echo "no design dir at $DESIGN_DIR" >&2; exit 1; }

# Collect witness paths (sorted, deterministic) — portable to bash 3.2 (no mapfile)
WITNESSES=()
while IFS= read -r line; do
    [ -n "$line" ] && WITNESSES[${#WITNESSES[@]}]="$line"
done < <(find "$DESIGN_DIR" -type f -name "*omega_cycle*.json" 2>/dev/null | sort)
N_WIT=${#WITNESSES[@]}
[ "$N_WIT" -eq 0 ] && { echo "__ATLAS_WITNESS__ FAIL no witnesses found" >&2; exit 2; }

# Per-witness extract → TSV rows in a temp buffer
TMP_TSV=$(mktemp)
trap 'rm -f "$TMP_TSV"' EXIT

for w in "${WITNESSES[@]}"; do
    rel="${w#$NEXUS_ROOT/}"
    engine=$(basename "$(dirname "$w")")
    # Extract date from filename prefix YYYY-MM-DD
    fn=$(basename "$w")
    date_field=$(echo "$fn" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}' || echo "unknown")

    # jq extracts — guard against missing fields with //
    cycle_id=$(jq -r '.trawl_id // .cycle_id // .name // "—"' "$w" 2>/dev/null)
    axes=$(jq -r '
        if (.axes_surfaced | type) == "array" then (.axes_surfaced | length)
        elif (.axes_surfaced | type) == "number" then .axes_surfaced
        elif (.axes | type) == "array" then (.axes | length)
        elif (.axes | type) == "number" then .axes
        else 0 end' "$w" 2>/dev/null)
    tier_count=$(jq -r '
        ((.tier_1_immediate_impl // .tier_1_immediate_impl_next_cycle // .tier_1_immediate_impl_this_cycle // []) | length)
        ' "$w" 2>/dev/null)
    has_fixpoint=$(jq -r '
        if (.omega_stop_witness // .omega_stop // .fixpoint_marker // null) == null then "N" else "Y" end
        ' "$w" 2>/dev/null)

    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$rel" "$engine" "$date_field" "$axes" "$tier_count" "$has_fixpoint" "$cycle_id" \
        >> "$TMP_TSV"
done

# ── Aggregations ────────────────────────────────────────────────────────────
N_ENGINES=$(awk -F'\t' '{print $2}' "$TMP_TSV" | sort -u | wc -l | tr -d ' ')
TOTAL_AXES=$(awk -F'\t' '{s+=$4} END{print s+0}' "$TMP_TSV")
TOTAL_TIER1=$(awk -F'\t' '{s+=$5} END{print s+0}' "$TMP_TSV")
DATE_MIN=$(awk -F'\t' '{print $3}' "$TMP_TSV" | grep -v unknown | sort | head -1)
DATE_MAX=$(awk -F'\t' '{print $3}' "$TMP_TSV" | grep -v unknown | sort | tail -1)

# Orphans: missing cycle_id ("—") OR axes=0 OR has_fixpoint=N
ORPHANS=$(awk -F'\t' '$4==0 || $7=="—" || $6=="N" {print $0}' "$TMP_TSV")
N_ORPH=$(echo -n "$ORPHANS" | grep -c . || true)

# Duplicates: same cycle_id appearing >1 (excluding "—")
DUPS=$(awk -F'\t' '$7!="—"{print $7}' "$TMP_TSV" | sort | uniq -d)
N_DUP=$(echo -n "$DUPS" | grep -c . || true)

# ── Mode dispatch ───────────────────────────────────────────────────────────
if [ "$MODE" = "stats" ]; then
    printf "Ω-cycle witness corpus stats:\n  witnesses : %d\n  engines   : %d\n  axes      : %d\n  tier-1    : %d\n  date span : %s .. %s\n  orphans   : %d\n  duplicates: %d\n\nPer-engine:\n" \
        "$N_WIT" "$N_ENGINES" "$TOTAL_AXES" "$TOTAL_TIER1" "$DATE_MIN" "$DATE_MAX" "$N_ORPH" "$N_DUP"
    awk -F'\t' '{print $2}' "$TMP_TSV" | sort | uniq -c | sort -rn | awk '{printf "  %4d  %s\n",$1,$2}'
    echo "__ATLAS_WITNESS__ witnesses=$N_WIT engines=$N_ENGINES orphans=$N_ORPH duplicates=$N_DUP"
    exit 0
fi

if [ "$MODE" = "orphans" ]; then
    echo "orphan witnesses ($N_ORPH):"
    if [ "$N_ORPH" -gt 0 ]; then
        echo "$ORPHANS" | awk -F'\t' '{printf "  axes=%s tier1=%s fix=%s  %s\n", $4,$5,$6,$1}'
    else
        echo "  (none)"
    fi
    echo "__ATLAS_WITNESS__ orphans=$N_ORPH"
    exit 0
fi

# ── Default: rebuild TSV + Markdown dashboard ───────────────────────────────
{
    printf "path\tengine\tdate\taxes\ttier_count\thas_fixpoint\tcycle_id\n"
    cat "$TMP_TSV"
} > "$TSV_OUT"

# Build dashboard
{
    cat <<EOF
# Ω-cycle Witness Dashboard

_Auto-generated by \`tool/atlas_witness_registry.sh\` — do not edit by hand._
_Source-of-truth: \`$TSV_OUT\` (regenerate via \`bash tool/atlas_witness_registry.sh\`)._

## Executive summary

| metric | value |
|---|---|
| total witnesses | $N_WIT |
| distinct engines | $N_ENGINES |
| total axes surfaced | $TOTAL_AXES |
| total Tier-1 promotions | $TOTAL_TIER1 |
| date span | $DATE_MIN .. $DATE_MAX |
| orphan witnesses | $N_ORPH |
| duplicate cycle_ids | $N_DUP |

## Per-engine breakdown

| engine | witnesses | axes | tier-1 | avg axes/witness |
|---|---:|---:|---:|---:|
EOF
    awk -F'\t' '{w[$2]++; ax[$2]+=$4; t1[$2]+=$5}
        END {for (e in w) printf "| %s | %d | %d | %d | %.1f |\n", e, w[e], ax[e], t1[e], ax[e]/w[e]}' \
        "$TMP_TSV" | sort
    printf "\n## Timeline (date histogram)\n\n| date | count | bar |\n|---|---:|---|\n"
    awk -F'\t' '{print $3}' "$TMP_TSV" | sort | uniq -c | awk '{
        bar=""; for (i=0;i<$1;i++) bar=bar"█"
        printf "| %s | %d | %s |\n", $2, $1, bar
    }'
    printf "\n## Top 5 most-axes witnesses\n\n| axes | tier-1 | engine | path |\n|---:|---:|---|---|\n"
    sort -t$'\t' -k4,4 -rn "$TMP_TSV" | head -5 \
        | awk -F'\t' '{printf "| %s | %s | %s | %s |\n", $4, $5, $2, $1}'
    printf "\n## Orphan witnesses (%d)\n\n_Definition: \`axes=0\` OR missing \`cycle_id\`/\`trawl_id\` OR no \`omega_stop\`/fixpoint marker._\n_May be stale, incomplete, or use a non-standard schema (e.g. \`title\`/\`axes\` instead of \`trawl_id\`/\`axes_surfaced\`)._\n\n" "$N_ORPH"
    if [ "$N_ORPH" -gt 0 ]; then
        printf "| axes | tier-1 | fixpoint | path |\n|---:|---:|:---:|---|\n"
        echo "$ORPHANS" | awk -F'\t' '{printf "| %s | %s | %s | %s |\n", $4,$5,$6,$1}'
    else
        echo "_(none — all witnesses well-formed)_"
    fi
    printf "\n## Duplicate cycle_ids (%d)\n\n" "$N_DUP"
    if [ "$N_DUP" -gt 0 ]; then
        printf "| cycle_id | paths |\n|---|---|\n"
        echo "$DUPS" | while IFS= read -r cid; do
            paths=$(awk -F'\t' -v c="$cid" '$7==c{print $1}' "$TMP_TSV" | tr '\n' ',' | sed 's/,$//')
            echo "| \`$cid\` | $paths |"
        done
    else
        echo "_(no duplicate cycle_ids — corpus is unique-keyed)_"
    fi
    echo ""
    cat <<EOF
## Recommended next actions

- **Aging policy**: witnesses older than 30 days with no \`tier_1_immediate_impl_this_cycle\` follow-up should move to \`design/_archive/<engine>/\`.
- **Consolidation**: if any engine has >15 witnesses on the same week, surface a meta-Ω-cycle to dedup overlapping axes.
- **Orphan cleanup**: $N_ORPH orphan(s) — backfill missing fields or move to \`_archive/\` to keep the registry signal-dense.
- **Duplicate keys**: $N_DUP duplicate cycle_id(s) — rename or merge (cycle_id should be a primary key).
- **Cross-engine audit**: run \`tool/atlas_witness_registry.sh --stats\` weekly; flag if a single engine produces <2/week (stalled) or >10/week (over-fragmentation).
- **Schema unification**: tier-1 field has 3 variants (\`tier_1_immediate_impl\`, \`..._next_cycle\`, \`..._this_cycle\`) — pick one canonical form per raw 8 retire-historical-tokens. Likewise for axis arrays (\`axes_surfaced\` vs \`axes\`).

---

_\`__ATLAS_WITNESS__ witnesses=$N_WIT engines=$N_ENGINES orphans=$N_ORPH duplicates=$N_DUP\`_
EOF
} > "$MD_OUT"

echo "wrote $TSV_OUT  ($N_WIT rows)"
echo "wrote $MD_OUT"
echo "__ATLAS_WITNESS__ witnesses=$N_WIT engines=$N_ENGINES orphans=$N_ORPH duplicates=$N_DUP"
exit 0
