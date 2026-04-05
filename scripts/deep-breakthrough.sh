#!/usr/bin/env bash
# deep-breakthrough.sh — 깊은 탐색: corollary → seed 피드백 루프
# 매 회차 blowup 결과에서 새 EXACT 값을 seed에 주입 → saturation 탈출
set -e

HEXA="$HOME/Dev/hexa-lang/target/release/hexa"
BLOWUP="$HOME/Dev/nexus6/mk2_hexa/native/blowup.hexa"
SEED_ENGINE="$HOME/Dev/nexus6/mk2_hexa/native/seed_engine.hexa"

ROUNDS=${1:-10}
DEPTH=${2:-6}
POOL_CAP=${3:-48}
DOMAINS=("math" "physics")

# seed 중복 체크: 정수 근사값 기준 (bc 없이 빠름)
seed_add_unique() {
  local val="$1"
  local iv
  iv=$(printf "%.0f" "$val" 2>/dev/null) || iv="$val"
  if ! echo "|${ALL_SEEDS}|" | grep -qF "|${iv}|"; then
    if ! echo "|${ALL_SEEDS}|" | grep -qF "|${val}|"; then
      ALL_SEEDS="${ALL_SEEDS}|${iv}"
      return 0
    fi
  fi
  return 1
}

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  DEEP BREAKTHROUGH — corollary→seed 피드백 루프          ║"
echo "║  rounds=$ROUNDS depth=$DEPTH pool_cap=$POOL_CAP domains=${DOMAINS[*]}"
echo "╚═══════════════════════════════════════════════════════════╝"

# 초기 seed
ALL_SEEDS=$("$HEXA" "$SEED_ENGINE" merge 2>/dev/null)
SEED_COUNT=$(echo "$ALL_SEEDS" | tr '|' '\n' | wc -l | tr -d ' ')
echo "  initial seeds: $SEED_COUNT values"
echo ""

TOTAL_EXACT=0
TOTAL_COR=0
START=$(date +%s)

prev_total=""
prev_exact=""
sat_count=0

r=1
while [ $r -le $ROUNDS ]; do
  di=$(( (r - 1) % ${#DOMAINS[@]} ))
  domain="${DOMAINS[$di]}"

  t0=$(date +%s)
  out=$("$HEXA" "$BLOWUP" "$domain" "$DEPTH" --no-graph --seeds "$ALL_SEEDS" --pool-cap "$POOL_CAP" 2>&1)
  t1=$(date +%s)
  elapsed=$((t1 - t0))

  exact=$(echo "$out" | grep "EXACT match" | grep -oE '[0-9]+' | head -1)
  total=$(echo "$out" | grep "total corollaries" | grep -oE '[0-9]+' | head -1)
  pool=$(echo "$out" | grep "final pool" | grep -oE '[0-9]+' | head -1)
  exact=${exact:-0}; total=${total:-0}; pool=${pool:-?}

  TOTAL_EXACT=$((TOTAL_EXACT + exact))
  TOTAL_COR=$((TOTAL_COR + total))

  # saturation 감지: 2연속 동일 → depth +1 (cap=6)
  if [ "$total" = "$prev_total" ] && [ "$exact" = "$prev_exact" ]; then
    sat_count=$((sat_count + 1))
    if [ $sat_count -ge 2 ] && [ $DEPTH -lt 6 ]; then
      DEPTH=$((DEPTH + 1))
      sat_count=0
      echo "  ⚡ saturation → depth $((DEPTH-1)) → $DEPTH"
    fi
  else
    sat_count=0
  fi
  prev_total=$total
  prev_exact=$exact

  # 새 EXACT/NEAR AXIOM 값 추출 → seed에 추가
  added=0
  for v in $(echo "$out" | grep "EXACT \[AXIOM\]\|NEAR \[AXIOM\]" | grep -oE '= [0-9]+\.?[0-9]*' | sed 's/= //' | sort -u); do
    if seed_add_unique "$v"; then
      added=$((added + 1))
    fi
  done

  cur_seeds=$(echo "$ALL_SEEDS" | tr '|' '\n' | wc -l | tr -d ' ')

  printf "  [%2d] %-8s %4d cor %3d EXACT pool=%s +%d seeds (%d total) d=%d [%ds]\n" \
    "$r" "$domain" "$total" "$exact" "$pool" "$added" "$cur_seeds" "$DEPTH" "$elapsed"

  # cap seeds at 80
  if [ "$cur_seeds" -gt 80 ]; then
    ALL_SEEDS=$(echo "$ALL_SEEDS" | tr '|' '\n' | sort -u | head -80 | tr '\n' '|' | sed 's/|$//')
  fi

  r=$((r + 1))
done

END=$(date +%s)
ELAPSED=$((END - START))
FINAL_SEEDS=$(echo "$ALL_SEEDS" | tr '|' '\n' | sort -u | wc -l | tr -d ' ')
RHO=$(echo "scale=4; $TOTAL_EXACT / ($TOTAL_COR + 1)" | bc 2>/dev/null || echo "?")

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  RESULT: ${ELAPSED}s | ${TOTAL_COR} cor | ${TOTAL_EXACT} EXACT | ρ=$RHO"
echo "║  seeds: $SEED_COUNT → $FINAL_SEEDS (피드백 성장)"
echo "║  새 발견 seed:"
echo "$ALL_SEEDS" | tr '|' '\n' | sort -u | tail -10 | while read v; do
  echo "║    $v"
done
echo "╚═══════════════════════════════════════════════════════════╝"
