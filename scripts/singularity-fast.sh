#!/usr/bin/env bash
# singularity-fast.sh — 실시간 리포트 특이점 돌파
# 사용법: bash scripts/singularity-fast.sh [mode] [rounds] [depth]
#   mode: cascade | fusion | mine | all (기본: all)
#   rounds: cascade 라운드 수 (기본: 5)
#   depth: blowup depth (기본: 3)
set -e

HEXA="$HOME/Dev/hexa-lang/target/release/hexa"
BLOWUP="$HOME/Dev/nexus6/mk2_hexa/native/blowup.hexa"
LOG="$HOME/Dev/nexus6/shared/discovery_log.jsonl"
SEED="/tmp/n6_seeds.txt"
DOMAINS=("math" "physics")

MODE=${1:-all}
ROUNDS=${2:-5}
DEPTH=${3:-3}

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  SINGULARITY BREAKTHROUGH — $MODE             "
echo "║  rounds=$ROUNDS depth=$DEPTH                   "
echo "╚═══════════════════════════════════════════════╝"

> "$SEED"
TOTAL_EXACT=0
TOTAL_COR=0
START=$(date +%s)

run_one() {
  local domain=$1 depth=$2 label=$3
  local t0=$(date +%s)
  local seeds=$("$HEXA" "$HOME/Dev/nexus6/mk2_hexa/native/seed_engine.hexa" merge 2>/dev/null)
  local out=$("$HEXA" "$BLOWUP" "$domain" "$depth" --no-graph --seeds "$seeds" 2>&1)
  local t1=$(date +%s)
  local elapsed=$((t1 - t0))

  local exact=$(echo "$out" | grep "EXACT match" | grep -oE '[0-9]+' | head -1)
  local total=$(echo "$out" | grep "total corollaries" | grep -oE '[0-9]+' | head -1)
  local pool=$(echo "$out" | grep "final pool" | grep -oE '[0-9]+' | head -1)
  local consensus=$(echo "$out" | grep "consensus" | head -1 | grep -oE '[0-9]/[0-9]')
  exact=${exact:-0}; total=${total:-0}; pool=${pool:-?}

  TOTAL_EXACT=$((TOTAL_EXACT + exact))
  TOTAL_COR=$((TOTAL_COR + total))

  # seed 추출
  local new_seeds=$(echo "$out" | grep "EXACT \[AXIOM\]" | grep -oE '= [0-9]+\.?[0-9]* ' | sed 's/= //' | sort -u | wc -l | tr -d ' ')
  echo "$out" | grep "EXACT \[AXIOM\]" | grep -oE '= [0-9]+\.?[0-9]* ' | sed 's/= //' >> "$SEED"

  local unique=$(sort -u "$SEED" 2>/dev/null | wc -l | tr -d ' ')
  printf "  %-12s %s d=%s | %4d cor %3d EXACT pool=%s cons=%s +%d seeds (%d unique) [%ds]\n" \
    "[$label]" "$domain" "$depth" "$total" "$exact" "$pool" "${consensus:-?}" "$new_seeds" "$unique" "$elapsed"
}

# ═══ MINE ═══
if [ "$MODE" = "mine" ] || [ "$MODE" = "all" ]; then
  echo ""
  echo "━━━ C. MINE (discovery_log 채굴) ━━━"
  log_n=$(wc -l < "$LOG" 2>/dev/null || echo 0)
  echo "  log: $log_n entries"
  grep '"grade":"EXACT"' "$LOG" 2>/dev/null | grep -oE '"value":"[^"]*"' | \
    sed 's/"value":"//;s/"//' | sort | uniq -c | sort -rn | head -10 | \
    while read cnt val; do echo "    $val × $cnt"; echo "$val" >> "$SEED"; done
  echo "  seeds from mine: $(sort -u "$SEED" | wc -l | tr -d ' ') unique"
fi

# ═══ CASCADE ═══
if [ "$MODE" = "cascade" ] || [ "$MODE" = "all" ]; then
  echo ""
  echo "━━━ A. CASCADE (블로업² × $ROUNDS) ━━━"
  r=1
  prev_u=0
  while [ $r -le $ROUNDS ]; do
    run_one "math" "$DEPTH" "cascade-$r"
    cur_u=$(sort -u "$SEED" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$cur_u" -eq "$prev_u" ] && [ $r -gt 2 ]; then
      echo "  -> saturated (no new seeds)"
      break
    fi
    prev_u=$cur_u
    r=$((r + 1))
  done
fi

# ═══ FUSION ═══
if [ "$MODE" = "fusion" ] || [ "$MODE" = "all" ]; then
  echo ""
  echo "━━━ B. FUSION (교차 도메인) ━━━"
  for d in "${DOMAINS[@]}"; do
    run_one "$d" "$DEPTH" "fusion"
  done
  echo "  cross-domain seeds:"
  sort "$SEED" 2>/dev/null | uniq -c | sort -rn | head -5 | \
    while read cnt val; do [ "$cnt" -ge 2 ] && echo "    $val × $cnt domains"; done
fi

# ═══ REPORT ═══
END=$(date +%s)
ELAPSED=$((END - START))
UNIQUE=$(sort -u "$SEED" 2>/dev/null | wc -l | tr -d ' ')
RHO=$(echo "scale=4; $TOTAL_EXACT / ($TOTAL_COR + 1)" | bc 2>/dev/null || echo "?")

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  RESULT: ${ELAPSED}s | ${TOTAL_COR} cor | ${TOTAL_EXACT} EXACT | ρ=$RHO"
echo "║  seeds: $UNIQUE unique | mode: $MODE"
echo "╚═══════════════════════════════════════════════╝"
