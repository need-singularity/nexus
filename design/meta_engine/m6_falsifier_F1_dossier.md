# m6 — falsifier-integration-F1 Dossier

- ordinal_stamp: ω+1
- parent_omega_cycle: design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json
- subject: state/meta_engine_evolution_log.jsonl axis F1 (falsifier integration — currently incomplete)
- theorem_anchor: m14 Rice — semantic property of an axis is undecidable in general → SYNTACTIC falsifier proxies only
- handoff_to: m3 closed-loop-self-certificate (cert rows must reference falsifier ids)
- loc_estimate: 170 (axis budget 150; +20 over for Rice-gate verifier — see §8)

---

## 1. Problem

### 1.1 Reference schema (design/hexa_sim/falsifiers.jsonl)

The hexa_sim corpus already carries 12+ falsifier rows (F1..F12). Inspected schema (tail F12):

```
{
  "id":           "F12",
  "slug":         "triple-source-n6-anchor-corroboration",
  "claim":        "<assertion that an observable holds>",
  "cmd":          "<shell pipeline that exits PASS or fails>",
  "pass":         "<exact substring expected on stdout to mark PASS>",
  "reason":       "<what its failure would mean>",
  "fix":          "<remediation pointer if it flips>",
  "origin":       "<provenance: ω-cycle id / commit / theorem citation>"
}
```

Properties of the existing pattern:
- one row per claim, append-only (raw 77)
- `cmd` is a **syntactic** check (grep / diff / count), never a semantic judgement
- `pass` is a literal string match — verifier is a `[[ "$out" == *"$pass"* ]]` test, decidable

### 1.2 Gap

The meta engine (state/meta_engine_evolution_log.jsonl, state/meta_axis_dependency.jsonl) accumulates new axes per round (R4..R32+ added A1..A5, B1, C1, F1, γ, δ, …) but **no falsifier is auto-emitted** when a new axis row is appended. F1 is listed as `axes_blocked` in every round since R4. Result: axis pool grows monotonically without refutation channel — m17 Kleene fixpoint risk (see parent ω-cycle).

---

## 2. Auto-spawn protocol

Trigger: append to `state/meta_axis_dependency.jsonl` of any row whose `axis_id` is not yet present in `state/meta_falsifiers.jsonl`.

Protocol (scheduled scan, no daemon required — m19 OS-quantum bound respected):

1. Watcher (cron tick or m1 self-trigger) reads tail of `meta_axis_dependency.jsonl`.
2. For each new `axis_id`, generate a paired row in `state/meta_falsifiers.jsonl` with template:
   ```
   {
     "axis_id":       "<copied from new axis>",
     "falsifier_id":  "MF-<axis_id>-<seq>",
     "falsifier_kind":"<one of allowed enum, see §3>",
     "observable":    "<concrete syntactic command or path>",
     "threshold":     "<scalar / regex / file path>",
     "deadline_ts":   "<ISO8601 by which observable must hold>",
     "status":        "live"
   }
   ```
3. Append-only — row is never mutated; lifecycle transitions (§6) emit *new* rows.
4. Verifier (m3 cert prerequisite) walks live rows and runs `observable`; result feeds m3 cert chain.

---

## 3. Allowed `falsifier_kind` values (Rice gate)

Permitted (purely syntactic, decidable in P):

| kind                    | meaning                                                                    | example observable                                  |
|-------------------------|----------------------------------------------------------------------------|-----------------------------------------------------|
| `log_row_count`         | jsonl row count over a slice meets `>= / <= threshold`                     | `wc -l < state/meta_engine_evolution_log.jsonl`     |
| `file_exists`           | path is/isn't present at deadline                                          | `[[ -e tool/meta_self_state.json ]]`                |
| `value_threshold`       | numeric field extracted via fixed jq/grep crosses threshold                | `jq '.round' tail.json -> N >= 33`                  |
| `absence_within_window` | a row matching pattern does NOT appear within window                       | `! grep -q 'rollback_triggered' tail.jsonl`         |
| `schema_match`          | row matches a fixed JSON-schema (required keys / enum domains)             | `jq -e '.axis_id and .falsifier_kind'`              |

**Forbidden** (semantic — Rice 1953 forbids automatic decision):
- `axis_is_useful`
- `axis_is_correct`
- `system_is_consistent`
- `system_is_progressing`
- any predicate whose evaluation requires understanding *meaning* of the axis rather than counting/matching its syntactic shadow

Operational consequence: a falsifier may say "fewer than 5 cert rows reference this axis after deadline" (syntactic) but never "the axis is uninteresting" (semantic, undecidable).

---

## 4. Five worked examples

Selected from the parent ω-cycle's m1..m10 (final-form track) — these are the axes whose corresponding rows already exist in `state/meta_engine_evolution_log.jsonl` axis ledger. Falsifiers paired below:

```json
{"axis_id":"m5","falsifier_id":"MF-m5-1","falsifier_kind":"schema_match","observable":"jq -e 'select(.ordinal != null)' state/meta_engine_evolution_log.jsonl | wc -l","threshold":">=1 row with non-null .ordinal field after 2026-05-02T00:00:00Z","deadline_ts":"2026-05-02T00:00:00Z","status":"live"}
{"axis_id":"m3","falsifier_id":"MF-m3-1","falsifier_kind":"log_row_count","observable":"wc -l < state/meta_decision_cert.jsonl","threshold":">= prev_count + 1 within 7d after each round","deadline_ts":"2026-05-09T00:00:00Z","status":"live"}
{"axis_id":"m6","falsifier_id":"MF-m6-1","falsifier_kind":"file_exists","observable":"test -e state/meta_falsifiers.jsonl && test -s state/meta_falsifiers.jsonl","threshold":"file present and non-empty by deadline","deadline_ts":"2026-05-02T00:00:00Z","status":"live"}
{"axis_id":"m9","falsifier_id":"MF-m9-1","falsifier_kind":"absence_within_window","observable":"grep -c 'invariant_violation_unhandled' state/meta_rollback_snapshots.jsonl","threshold":"==0 within 30d window","deadline_ts":"2026-05-25T00:00:00Z","status":"live"}
{"axis_id":"m10","falsifier_id":"MF-m10-1","falsifier_kind":"value_threshold","observable":"jq -s 'map(select(.coupling==\"roadmap\")) | length' state/meta_engine_evolution_log.jsonl","threshold":">=2 cross-feed rows within 14d","deadline_ts":"2026-05-09T00:00:00Z","status":"live"}
```

Notes:
- Each `observable` is a literal shell pipeline — verifier is `bash -c "$observable"` plus a comparator.
- No row encodes "axis is good" / "axis works" — Rice gate respected by construction.
- `MF-m6-1` is **self-referential**: the falsifier system's own existence is its first falsifier (raw 71 self-application).

---

## 5. Rice gate (raw 71 sub-falsifier)

A meta-falsifier guarding the integrity of the falsifier system itself.

```python
ALLOWED_KINDS = {
    "log_row_count",
    "file_exists",
    "value_threshold",
    "absence_within_window",
    "schema_match",
}

def rice_gate_verify(row: dict) -> tuple[bool, str]:
    kind = row.get("falsifier_kind")
    if kind not in ALLOWED_KINDS:
        return (False, f"REFUTED: falsifier_kind={kind!r} not in allowed enum "
                       f"(Rice 1953 — semantic predicate forbidden)")
    # forbid implicit semantic phrasings even inside observable string
    obs = row.get("observable", "")
    forbidden_substrings = ("is_useful", "is_correct", "is_consistent",
                            "is_progressing", "is_meaningful")
    for fs in forbidden_substrings:
        if fs in obs:
            return (False, f"REFUTED: observable contains semantic predicate "
                           f"{fs!r} (syntactic only)")
    return (True, "PASS")
```

Verifier outcome:
- if any spawned row fails `rice_gate_verify`, the entire integration is marked REFUTED for that round, and m3 cert emission is blocked until the offending row is appended-with-correction (lifecycle §6).
- the gate itself is registered as `MF-rice-gate-0` with `falsifier_kind="schema_match"` against `ALLOWED_KINDS` enum — recursive but bounded (single fixed enum, no semantic open set).

---

## 6. Lifecycle

States and append-only transitions (raw 77 — never mutate):

```
live  ──(verifier runs observable)──▶  observed  ──(comparator)──▶  resolved
                                                            │
                                                            ├── PASS    (claim held; falsifier passes deadline)
                                                            └── REFUTED (claim violated; remediation row required)
```

Each transition emits a **new** row referencing the prior `falsifier_id`:
- `{"falsifier_id":"MF-m5-1","prev_status":"live","status":"observed","ts":"...","stdout_sha":"..."}`
- `{"falsifier_id":"MF-m5-1","prev_status":"observed","status":"resolved:PASS"|"resolved:REFUTED","ts":"...","comparator_result":"<bool>"}`

Old rows are never edited. Latest status = newest row by `(falsifier_id, ts)`. This preserves audit trail through time and lets m9 atomic rollback replay any historical decision.

---

## 7. Cross-cycle handoff to m3

Every `state/meta_decision_cert.jsonl` cert row emitted by m3 MUST carry a `depends_on_falsifiers` field listing the `falsifier_id`s whose latest status is `resolved:PASS` and which the cert relies upon:

```
{
  "cert_id":"MC-R33-1",
  "round":33,
  "ordinal":"omega+1",
  "axes_acted":["m5","m6"],
  "depends_on_falsifiers":["MF-m5-1","MF-m6-1"],
  "rice_gate":"PASS",
  "ts":"..."
}
```

Cert verifier (m3) refuses to emit a cert if any listed falsifier is in `live` (not yet observed) or `resolved:REFUTED` state. This pins m3's external trust anchor (parent ω-cycle's Löb / Tarski mitigation: trust comes from outside the cert, namely from the syntactic falsifier corpus).

---

## 8. Estimated LoC

| component                                                        | LoC |
|------------------------------------------------------------------|-----|
| watcher / scheduled-scan over meta_axis_dependency.jsonl         |  35 |
| auto-spawn template renderer (axis_id → MF row)                  |  25 |
| `rice_gate_verify` + ALLOWED_KINDS enum + forbidden-substring    |  20 |
| observable-runner (bash -c + sha256 stdout capture)              |  30 |
| comparator dispatch (one branch per allowed kind)                |  35 |
| lifecycle append-only transition writer                          |  15 |
| m3 cert-emission gate (depends_on_falsifiers check)              |  10 |
| **total**                                                        | **170** |

Axis budget was 150; estimate is +20 over. Overrun source: forbidden-substring scan in `rice_gate_verify` (defensive raw-71 reflection). Justification accepted in this dossier as cost-of-correctness; Tier-1 implementation may elide the substring scan (drop to ~155) if the enum check alone is judged sufficient.

---

## Provenance

- parent: design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json (m6 row)
- pattern lifted from: design/hexa_sim/falsifiers.jsonl (F1..F12)
- raw rules invoked: 71 (falsifier-retire / falsifier-of-self), 77 (audit-append-only)
- theorem citations: Rice 1953 (semantic-property undecidability), Löb 1955 (external trust anchor), Gödel 1931 2nd (no internal consistency proof)
- ordinal: ω+1 (one descent below parent ω-cycle's ω, by axis-extension)
