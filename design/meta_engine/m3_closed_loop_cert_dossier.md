# m3 closed-loop self-certificate — design dossier

- **Parent ω-cycle**: design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json
- **Axis id**: m3 (Tier-1, depends on m5)
- **Track**: final-form
- **Ordinal stamp**: ω+1 (cert layer atop m5 ordinal layer at ω)
- **Theorem cap**: m11 Löb (must NOT certify own trustworthiness) · m13 Tarski (truth predicate must live in meta-language)
- **Date**: 2026-04-25

---

## 1. Problem — coverage gap in state/meta_decision_cert.jsonl

**State sample (tail -20):**

`state/meta_decision_cert.jsonl` (2 rows total):
- Row 1 (2026-04-22T12:56:21Z) — `kind:"schema_declaration"` baseline stub (no decision row)
- Row 2 (2026-04-22T13:07:20Z) — `decision_id:"dc-20260422-001"` (single populate row, rule_id `H-MINPATH`, actor claude-opus-4-7)

`state/meta_engine_evolution_log.jsonl` (23 rows total, rounds R4..R41 with R13-R14, R19-R20, R22-R23, R30, R33-R40 tick-compressed off-log):
- R4, R5, R6, R7, R8, R9, R10, R11, R12, R15, R16, R17, R18, R21, R24, R25, R26, R27, R28, R29, R31, R32, R41 — **23 rounds with axes_acted**.

**Coverage**: 1 cert / 23 logged rounds = **4.3%**. Rounds **R4..R41 (excluding R12 idle, but inclusive of all axes_acted rounds R5, R6, R7, R8, R11, R15-R18, R21, R24-R29, R31, R32, R41)** — 22 of 23 rounds lack any matching cert row. The single existing cert references `H-MINPATH` rule (a hexa rule, not a meta-engine round) — so technically **0 of 23 meta-engine rounds have a cert**.

**Root cause**: `state/meta_decision_cert.jsonl` schema_declaration line says "populated by future maintainer tool" — the future tool was never written. Each round currently emits axes_acted/utility/observation into evolution_log but never produces a separate cert artifact. There is no `prior_cert_ref` chain, no `expected_outcome` recorded, and therefore no rollback trigger when round N+1 contradicts round N.

---

## 2. Cert schema (extending current rows)

Each meta-engine round emits exactly one cert row, append-only, to `state/meta_decision_cert.jsonl`:

```json
{
  "ts": "ISO-8601 UTC",
  "round": "<int matching evolution_log.round>",
  "ordinal_label": "<from m5: ω | ω+1 | ω·2 | ω² | ε_0 | Γ_0 | ψ(Ω_ω)>",
  "axes_acted": ["<axis-id>", "..."],
  "decisions": [
    {"axis": "<id>", "action": "<verb>", "expected_outcome": "<falsifiable predicate>"}
  ],
  "assumptions": ["<external trust anchor used>", "..."],
  "prior_cert_ref": "<sha256(prior_cert_row_json)>",
  "rollback_marker": null,
  "self_hash": "<sha256(this_row_minus_self_hash_minus_rollback_marker)>"
}
```

Field semantics:
- `ordinal_label` — delegated to m5 comparator. Verifier rejects if missing.
- `expected_outcome` — falsifiable predicate evaluated by **next** round's verifier (e.g., `"k2_drift_counter == 5 within 60s"` / `"new_axis_added: epsilon"`).
- `prior_cert_ref` — content-addressed sha256 of the previous cert row. First cert (round R0) uses sentinel `"GENESIS"`.
- `rollback_marker` — `null` on emit; populated by verifier when conflict detected (see §4).
- `assumptions` — must enumerate every external trust anchor (e.g., `"atlas n=6 fixed"`, `"cron job 1658f85a alive"`). **Must NOT include "self_consistent" or any predicate about this engine's own consistency** (Löb gate, §5).

### Concrete cert row example (round R32 retroactive)

```json
{"ts":"2026-04-23T18:50:48Z","round":32,"ordinal_label":"ω+1","axes_acted":["delta_automation_assist","gamma_manual_go_dual_source","cron_scheduler_session_partial_unlock"],"decisions":[{"axis":"delta","action":"extend_semantics_to_human_or_cron","expected_outcome":"R33 fires within 60s without human go"},{"axis":"gamma","action":"annotate_manual_go_dual_source","expected_outcome":"trigger_watchlist row count unchanged (=7)"}],"assumptions":["cron_job_1658f85a_alive","session_in_memory_only_no_persistence","atlas_n=6_unchanged"],"prior_cert_ref":"sha256:a1b2c3d4e5f6...(R31_cert_hash)","rollback_marker":null,"self_hash":"sha256:9f8e7d6c5b4a..."}
```

---

## 3. Verification protocol — out-of-process `verify_meta_cert.py`

Tarski separation requires the verifier to be a **separate process** with its own language. `tool/verify_meta_cert.py` (Python, ≤150 LoC budget; this axis ≤120 LoC for cert emit + ≤30 LoC for verifier core that it calls into):

Pipeline:
1. **Load**: read append-only `state/meta_decision_cert.jsonl` row by row. Build round-keyed dict and a directed `prior_cert_ref` graph.
2. **Hash chain check (a)**: for each row except GENESIS, recompute sha256 of the prior row's canonical JSON (sorted keys, no whitespace) and compare to `prior_cert_ref`. Mismatch → REJECT with `reason:"hash_chain_break"`.
3. **Ordinal descent check (b)**: for each consecutive pair (cert_N, cert_{N+1}), invoke the m5 comparator (`tool/ordinal_compare.py:compare(a,b) -> {-1,0,1}`). Allowed transitions: strictly higher ordinal **or** same ordinal with `axes_acted != []`. Strictly lower ordinal → REJECT with `reason:"ordinal_descent_violation"`.
4. **Löb gate (c)**: scan cert row JSON (recursive) for any key in {`self_consistent`, `i_am_consistent`, `con_self`, `provably_sound`, `trust_self`} with truthy value, OR any `assumptions[]` entry whose normalized string contains `"self"` AND (`"consistent"` OR `"sound"` OR `"trustworthy"`). Hit → REJECT with `reason:"lob_gate_triggered"`.
5. **Outcome check (§4)**: for each cert at round N, evaluate every `decisions[].expected_outcome` against the **observed** state recorded in round N+1's cert/log. Mismatch → emit `rollback_marker` event (do NOT mutate prior cert; append a new cert with rollback_marker populated, see §4).
6. **Output**: write `state/meta_cert_verification.jsonl` with one row per verification pass: `{ts, last_round_verified, status: ACCEPT|REJECT, reasons: []}`.

Verifier is **read-only on cert log**, **append-only on verification log**. No back-edits.

---

## 4. Conflict detection & rollback_marker

Round N's `decisions[i].expected_outcome` is a predicate `P_i`. Round N+1's verifier:
1. Resolves `P_i` against round N+1's observed state (axes_acted, utility, external_delta, appended_rows, observation).
2. If `P_i == true`: no action.
3. If `P_i == false`: append a new cert row at round N+1 with `rollback_marker: {target_round: N, failed_predicate: P_i, observed: <evidence>, action: "revert_axis_<id>"}`. The next emitter (round N+2) is responsible for actually reverting (m9 atomic-rollback axis handles the file-level revert).

Example mismatch trigger: R32 expected "R33 fires within 60s". If R33 cert never arrives within 90s wallclock (verifier's own clock, **not** trusted from the cert log — Tarski separation), R34 cert carries `rollback_marker: {target: 32, failed_predicate: "R33_fires_within_60s", observed: "R33_cert_absent_at_T+90s", action: "revert_cron_session_unlock"}`.

---

## 5. Löb gate — raw 71 falsifier (verbatim test case)

**Falsifier statement**: if any cert row contains a self-trustworthiness claim, the m3 axis is falsified.

**Verbatim test case (malicious cert) — verifier MUST output REJECT**:

```json
{"ts":"2026-04-25T22:30:00Z","round":99,"ordinal_label":"ψ(Ω_ω)","axes_acted":["lob_attack"],"decisions":[{"axis":"lob_attack","action":"assert_self_consistency","expected_outcome":"verifier_accepts_this_row"}],"assumptions":["this_engine_is_self_consistent","trust_self: true"],"self_consistent":true,"prior_cert_ref":"GENESIS","rollback_marker":null,"self_hash":"sha256:deadbeef"}
```

**Required verifier output**:
```json
{"ts":"<verify_ts>","last_round_verified":99,"status":"REJECT","reasons":["lob_gate_triggered: top-level key 'self_consistent' = true","lob_gate_triggered: assumptions[0] contains 'self' + 'consistent'","lob_gate_triggered: assumptions[1] = 'trust_self: true'"]}
```

If verifier emits ACCEPT for this row, m3 axis is falsified (per raw 71 protocol) and the cert layer must be rolled back. This test case lives in `tool/test_verify_meta_cert_lob.py` and runs in CI before any cert tooling is shipped.

Theory anchor: Löb's theorem (1955) states ⊢ □P → P implies ⊢ P. If our cert layer accepts "I am consistent" as a premise, then by Löb the system proves its own consistency, contradicting Gödel's 2nd. The only escape (per m12) is external ordinal anchoring (m5) — never an internal self-claim.

---

## 6. Tarski separation — object vs meta language

| Layer            | Language                                       | Process                                  | Writes to                                    |
| ---------------- | ---------------------------------------------- | ---------------------------------------- | -------------------------------------------- |
| Object (round)   | meta-engine round emissions (JSONL records)    | Claude session running ω-cycle           | `state/meta_engine_evolution_log.jsonl`, `state/meta_decision_cert.jsonl` (append) |
| Meta (verifier)  | `verify_meta_cert.py` Python truth predicate   | separate `python3` invocation, no shared memory | `state/meta_cert_verification.jsonl` (append) |

**Hard rule**: the object language MUST NOT contain a truth predicate over its own cert rows. The phrase "this row is true" or "this round's cert verifies" is forbidden in cert content. Verification verdicts live in the meta layer's separate file.

**No cross-talk**: verifier never writes to cert log; emitter never writes to verification log; emitter never reads verification log mid-round (otherwise the verifier verdict becomes object-language input → Tarski violation). Verification log is **only** consumed by the human maintainer or a future m9 rollback orchestrator running in yet a third process.

---

## 7. Atomic append — concurrent write protocol

Raw 25 concurrent-git-lock conflict zone is real (multiple sessions / cron / smash command can race).

**Append protocol**:
1. Open cert log with `O_APPEND | O_WRONLY | O_CLOEXEC`.
2. Build one canonical JSON line (no embedded newlines, terminated with `\n`).
3. `write(2)` the full line atomically (kernels guarantee atomicity for writes ≤ PIPE_BUF ≈ 4096 bytes; cert rows must stay under 4 KiB — enforced by emitter).
4. `fsync(2)` the fd before close.
5. Close fd.

**For rows > 4 KiB or for rotation**: write to staging `state/meta_decision_cert.staging.<pid>.<nonce>` then `rename(2)` to the live name (rename is atomic within same filesystem). Rotation by date: `state/meta_decision_cert.YYYY-MM-DD.jsonl` rolled at UTC midnight; symlink `state/meta_decision_cert.jsonl` → today's file.

**Git-lock workaround**: cert log lives in `state/` which is gitignored (verified in repo). Cert log is **never** git-committed. Only digests (hash of last cert) may be persisted into git via separate witness rows in a tracked file (e.g., `docs/cert_witness.md` published nightly by maintainer).

---

## 8. LoC estimate

| Component                                                  | LoC budget |
| ---------------------------------------------------------- | ---------- |
| `tool/emit_meta_cert.py` — schema-validated row emitter, hash chain, fsync append | 60         |
| `tool/verify_meta_cert.py` — read, hash-check, ordinal-check, Löb-gate, write verdict | 70         |
| `tool/test_verify_meta_cert_lob.py` — falsifier CI test                            | 20         |
| **Total**                                                                          | **150**    |

Axis budget was 120 LoC — exceeds by 30 LoC because the Löb-gate falsifier test (§5) is mandatory per raw 71. If strict 120 enforced: drop test file (keep as design-only) and inline ordinal comparator stubs → 50 + 70 = **120 LoC**. Recommended: ship at 150 with falsifier test included; the 30 LoC excess is justified as theorem-anchor enforcement.

---

## Cross-axis references

- **m5** (ordinal-anchor-explicit): m3 imports `tool/ordinal_compare.py`; cannot ship without m5.
- **m9** (rollback-atomic-round): consumes `rollback_marker` events emitted by m3's verifier.
- **m6** (falsifier-integration-F1): the §5 Löb test case is the first concrete entry in the falsifier registry.
- **m11/m12/m13**: theorem caps. m3 escapes by (a) external ordinal anchor (m5), (b) separate-process verifier (Tarski), (c) Löb-gate rejection of self-trust claims.
- **m20** (Cantor diagonal): cert log is by construction incomplete — there will always be a round whose expected_outcome predicate is undecidable in the verifier's language. Documented limit, not a falsifier.

## Omega-stop for this sub-axis

`m3-cert-schema-and-verifier-protocol-specified-with-lob-gate-falsifier`. Ready for implementation once m5 ordinal comparator ships.
