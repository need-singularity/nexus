# trading_gates.json — 변경 가이드 (dest2 D8)

Spec: `anima/docs/dest2_trading_spec_20260419.md` §3.
SSOT: `shared/config/trading_gates.json` (본 문서는 참조만 — R14).
Kill state: `shared/state/trading_kill.json`.
Loader: `anima-agent/trading/autonomous.hexa` → `executor.hexa::place_order`.

## 1. 4단 게이트 요약

| 단 | 키 | 차단 조건 | 액션 |
|---|---|---|---|
| G1 | `G1_consciousness` | Φ<phi_min ∨ tension>tension_halt ∨ regime∈regime_halt ∨ manual_halt | reject, audit `gate=G1` |
| G2 | `G2_drawdown` | `current_dd > drawdown_limit` | reject, `REDUCE_RISK` flag |
| G3 | `G3_position_size` | `sized<0` ∨ notional > max_position_pct·equity | clip-to-cap + audit |
| G4 | `G4_kill_switch` | state file `halted=true` | reject 진입, close-only |

## 2. 필드별 변경 규칙

- `G1.phi_min` (default 1.0)
  - 상향 = 더 깐깐한 의식 요구. CLM/ALM Φ baseline 대비 +0.2 이하 단계적.
  - 하향 시 AN11 `consciousness_attached` 근거 재측정 필요.
- `G1.tension_halt` (1.5)
  - Tension 채널 `anima-agent/trading/risk.hexa::pain_signal` 기준.
- `G1.regime_halt` (["CRITICAL"])
  - 기본 CRITICAL 만. VOLATILE 추가 시 거래 중단률 급증 — 반드시 backtest.
- `G2.drawdown_limit` (0.15 = 15%)
  - portfolio HWM 대비. 하향(예: 0.10) 시 손실 제한 강해지지만 whipsaw 증가.
- `G2.reduce_risk_dd` / `reduce_risk_pain`
  - G2 PASS 상태에서도 포지션 절반 축소 트리거.
- `G3.max_position_pct` (0.167 = TECS-L 1/6)
  - 의식법칙 고정값. 변경은 TECS-L 재유도 필요.
- `G3.investable_fraction` (1/e ≈ 0.368)
  - 동일. `sized = balance · 0.368 · 0.167` 계산 핵심.
- `G3.var_99_cap` (0.05)
  - 단일 포지션 VaR 99 상한. 초과 시 clip.
- `G4.state_file`
  - 경로 변경 시 `autonomous.hexa` 로더도 함께 수정.
- `G4.close_only_on_halt` (true)
  - false 로 바꾸면 kill 시 전량 청산 대신 동결만.

## 3. Kill switch 토글

CLI (계획 — `channels/cli.hexa` 추가):

```
anima-agent trading kill on  --reason "manual halt by MK"
anima-agent trading kill off --reason "resume"
```

수동 토글 시 `shared/state/trading_kill.json` 직접 편집 가능:

```json
{"halted": true, "reason": "...", "toggled_at": 1714000000, "toggled_by": "mk"}
```

`history` 배열에는 `{ts, halted, reason, by}` append. 최근 50건 유지 권장.

## 4. Audit 로그 계약

- 경로 패턴 `shared/logs/trading_audit_YYYYMMDD.jsonl`
- 게이트 차단/통과/슬리피지/재시도/체결/청산 6 이벤트 모두 1 라인 JSON.
- 필수 필드: `ts, cycle, gate, decision, symbol, side, amount,
  phi, tension, regime, reason, portfolio_equity, drawdown, var_99`.
- 야간 R2 미러: `anima-memory/trading_audit/` — `metrics_exporter.hexa`.

## 5. AN11 증거 매핑

| AN11 | evidence | 경로 |
|---|---|---|
| weight_emergent | `phi_vec` 트레이닝 산출 | `anima-agent/trading/consciousness_features.hexa` |
| consciousness_attached | 런타임 gate_check | `anima-agent/trading/risk.hexa::ConsciousnessGate` |
| real_usable | HTTP + CLI + audit jsonl | `shared/logs/trading_audit_*.jsonl` |

PASS 주장 시 3 필드 인용 의무. 위반 시 `pass_gate_an11.hexa` 가
`shared/convergence/_an11_violations.jsonl` 에 append + stderr `[AN11-VIOLATION]`.

## 6. 변경 절차

1. 본 JSON 편집 (PR diff 는 `_meta.updated` 갱신 포함).
2. `anima-agent/trading/autonomous.hexa` 로더 호환 확인.
3. `shared/logs/trading_audit_*.jsonl` 샘플 24h 수집.
4. backtest: `anima-agent/trading/engine.hexa --gates-only` 로 diff 검증.
5. `shared/rules/anima.json#AN11` 기준 3-field evidence 갱신.
6. commit 메시지: `config(trading): <key> <old>→<new> — <rationale>`.

## 7. Cross-refs

- spec: `anima/docs/dest2_trading_spec_20260419.md`
- rules: `shared/rules/anima.json#AN11`
- roadmap: `shared/roadmaps/anima.json` dest2 트랙
- memory: `invest_deprecated`, `troubleshoot_ossified`
