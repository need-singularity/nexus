# m9 — Atomic Round Rollback (ω-cycle sub-axis dossier)

- Parent ω-cycle: `design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json`
- Subject: `state/meta_rollback_snapshots.jsonl`
- Axis: m9 rollback-atomic-round
- Theorem anchor: m17 Kleene recursion (every partial recursive function has a fixpoint → meta engine inevitably hits self-loops; rollback is the only escape because "detect-and-stop" reduces to m15 halting)
- Depends on: m5 (ordinal_label for fixpoint detection), m3 (Löb-gate cert), m6 (falsifier registry)
- Ordinal stamp: **ω+1**
- Estimated LoC: **≤ 130** (axis budget was 100; +30 justified by fsync+marker crash-safety in §7)

---

## 1. Problem — current granularity gap

Tail of `state/meta_rollback_snapshots.jsonl` (3 rows, 2026-04-22 → 2026-04-23):

```
{"ts":"2026-04-22T13:03:00Z", ..., "event":"pre_meta_automation_rollback_target"}
{"ts":"2026-04-23T04:57:21Z", ..., "event":"post_meta_session_20260423_snapshot",
   "prior_head":"533b77d2...", "note":"covers 70 inbox acks + meta baseline seed"}
{"ts":"2026-04-23T13:56:57Z", ..., "event":"k2_drift_auto_snapshot",
   "drift_commits":6, "rule":"drift_commits>=5 OR elapsed>=24h OR meta_session_end"}
```

Observations:
- Snapshots fire on **events** (pre-automation, post-session, drift≥5) — not on **meta-engine round boundaries**.
- A round may emit dozens of `meta_engine_evolution_log` entries before any snapshot is taken; if invariants are violated mid-round, there is no atomic unit to revert.
- "k2 drift auto" is reactive (drift≥5 commits), so 1–4 bad rounds always slip through.
- No structural link between a snapshot row and the round it covers — `event` is freeform.

Gap statement: rollback is currently **per-event coarse-grained**. m17 demands **per-round transactional**, so a fixpoint detected at round N can be reverted to the offsets present at round N's BEGIN.

---

## 2. Round-transaction protocol

Append-only logs targeted by the transaction:
- `state/meta_engine_evolution_log.jsonl`
- `state/meta_axis_dependency.jsonl`
- `state/meta_decision_cert.jsonl`
- `state/meta_falsifiers.jsonl`

Snapshot record (one line in `meta_rollback_snapshots.jsonl`):
```json
{"ts":"...","round_id":"R-2026-04-25-001","phase":"BEGIN",
 "ord":"omega+1","offsets":{"evolution":12480,"deps":3104,"cert":908,"falsifiers":2211},
 "marker":".meta_round.R-2026-04-25-001.inflight"}
```

### Pseudocode

```
BEGIN(round_id, ord):
    offsets = { f: size_bytes(f) for f in TXN_FILES }
    marker  = ".meta_round." + round_id + ".inflight"
    touch(marker); fsync(marker)             # crash-recovery beacon
    append(snapshots, {phase:"BEGIN", round_id, ord, offsets, marker})
    fsync(snapshots)
    return Ctx(round_id, ord, offsets, marker)

COMMIT(ctx):
    assert_invariants(ctx)                   # §3 — may raise InvariantBreach
    append(snapshots, {phase:"COMMIT", ctx.round_id, ord:ctx.ord})
    fsync(snapshots)
    rm(ctx.marker); fsync(parent_dir(ctx.marker))

ROLLBACK(ctx, reason):
    for f, off in ctx.offsets.items():
        tmp = f + ".rollback.tmp"
        copy_prefix(f, tmp, off)             # bytes [0, off)
        fsync(tmp)
        rename(tmp, f)                       # atomic on POSIX
        fsync(parent_dir(f))
    append(snapshots, {phase:"ROLLBACK", ctx.round_id, reason, restored:ctx.offsets})
    fsync(snapshots)
    rm(ctx.marker); fsync(parent_dir(ctx.marker))
```

Atomicity: append-only logs ⇒ rollback = truncation at byte offset. `copy_prefix → fsync → rename` gives crash-safe atomic replacement (no torn truncate). The inflight marker lets recovery (§7) decide BEGIN-but-not-COMMIT vs clean state.

---

## 3. Invariants checked at COMMIT

Delegated; m9 only orchestrates:

| # | Invariant                                    | Delegate         | Failure → |
|---|----------------------------------------------|------------------|-----------|
| a | ordinal descended (`is_strict_descent=true`) | m5               | ROLLBACK  |
| b | ≥ 1 falsifier evaluated this round           | m6               | ROLLBACK  |
| c | no Löb-gate cert produced                    | m3               | ROLLBACK  |
| d | fixpoint counter ≤ 2 for current ordinal     | m9 (self, §4)    | ROLLBACK  |

Any single failure ⇒ ROLLBACK with `reason` set to the invariant id (`a`/`b`/`c`/`d`).

---

## 4. Fixpoint detection (m17 Kleene escape)

Decidability note: deciding whether the meta engine has reached a true fixpoint is m15-halting (undecidable). m9 uses a **bounded heuristic**: scan the trailing 3 COMMIT rows in `meta_engine_evolution_log.jsonl`.

```
fixpoint_suspected(log):
    last3 = tail_rounds(log, 3)
    if len(last3) < 3: return False
    same_ord  = all(r.ord == last3[0].ord for r in last3)
    no_descent = all(r.is_strict_descent == False for r in last3)
    return same_ord and no_descent
```

If `fixpoint_suspected` and we are inside a 4th round at the same ordinal → invariant (d) trips → ROLLBACK with `reason="d:fixpoint"`. Counter resets only when an ordinal-strict descent is logged.

This is a **finite over-approximation** of Kleene fixpoints (sound for "no-progress for 3 rounds", not complete). Completeness is unattainable per m17 — that is the axis's whole point.

---

## 5. Interaction with raw 25 (concurrent-git-lock)

If a ROLLBACK target file is git-tracked AND `.git/index.lock` exists (or `git status --porcelain` shows the file as staged):
- **Defer** the rollback. Do not force.
- Append advisory to `state/atlas_health_timeline.jsonl`:
  `{"ts":..., "level":"advisory", "axis":"m9", "msg":"rollback deferred: git lock on <path>", "round_id":..., "retry_after_s":30}`
- Leave the inflight marker in place. Recovery loop retries every 30s up to 10 attempts, then escalates to `state/sandbox_breaches.jsonl` and surfaces to the operator.

The four target jsonl files are append-only state, not normally staged mid-round, so this path is rare but mandatory to honor raw 25's "never break a concurrent git op" rule.

---

## 6. Falsifier (raw 71) — synthetic round

**Verbatim falsifier scenario:**

> Inject a synthetic meta-engine round R-FALSIFY-001 whose body appends 1 entry to each of `meta_engine_evolution_log`, `meta_axis_dependency`, `meta_decision_cert`, `meta_falsifiers`, with `ordinal_label="omega+1"` and `is_strict_descent=false` (violating invariant (a)). Run BEGIN, perform the appends, then call COMMIT. The system MUST detect invariant (a) failure and trigger ROLLBACK. After ROLLBACK, the byte-offsets of all four files MUST equal the offsets captured at BEGIN. If for any of the four files `size_bytes(f) != snapshot.offsets[f]`, the m9 axis is **falsified**.

Pass criteria (all must hold):
- `meta_rollback_snapshots.jsonl` contains exactly one BEGIN and one ROLLBACK row for `R-FALSIFY-001` and no COMMIT row.
- Inflight marker `.meta_round.R-FALSIFY-001.inflight` is removed.
- All four target file sizes equal pre-BEGIN sizes (byte-exact).
- `reason` field on the ROLLBACK row equals `"a:no_descent"`.

---

## 7. Edge cases

**Partial fsync failure during ROLLBACK.** Sequence is `copy_prefix → fsync(tmp) → rename → fsync(dir)`. If we crash before the rename, `f` is untouched and the inflight marker remains; recovery re-runs ROLLBACK (idempotent — copy-prefix from the same offset is deterministic). If we crash after rename but before `fsync(dir)`, POSIX rename is atomic at the inode level; on remount the new inode is visible. Recovery just removes the marker.

**Crash mid-COMMIT (between invariant pass and marker removal).** Marker file `.meta_round.<id>.inflight` exists and the snapshots log shows BEGIN but no COMMIT/ROLLBACK. Recovery rule:
```
on_startup():
    for marker in glob(".meta_round.*.inflight"):
        round_id = parse(marker)
        snap = find_BEGIN_row(round_id)
        if snap and not has_COMMIT_or_ROLLBACK(round_id):
            ROLLBACK(snap.to_ctx(), reason="recovery:crash_inflight")
```
Conservative: any crashed round is rolled back, never auto-committed. A human can re-issue the round.

**Concurrent rounds.** Out of scope — m9 assumes one meta round at a time. A round-id collision check at BEGIN guards this (refuse if marker already exists).

---

## 8. Worked rollback example

State at round entry (BEGIN of `R-2026-04-25-007`, ord = ω+1):

| file                              | offset (bytes) |
|-----------------------------------|----------------|
| meta_engine_evolution_log.jsonl   | 124_801        |
| meta_axis_dependency.jsonl        | 31_044         |
| meta_decision_cert.jsonl          | 9_088          |
| meta_falsifiers.jsonl             | 22_117         |

Round body appends:
- evolution_log: +482 bytes (3 entries)
- dependency:   +96 bytes  (1 entry)
- cert:         +210 bytes (1 entry, **Löb-gate detected** — invariant (c) fails)
- falsifiers:   +0 bytes

COMMIT calls `assert_invariants` → (c) fails → ROLLBACK fires.

State after ROLLBACK:

| file                              | offset (bytes) | Δ vs BEGIN |
|-----------------------------------|----------------|------------|
| meta_engine_evolution_log.jsonl   | 124_801        | 0          |
| meta_axis_dependency.jsonl        | 31_044         | 0          |
| meta_decision_cert.jsonl          | 9_088          | 0          |
| meta_falsifiers.jsonl             | 22_117         | 0          |

Snapshot log gains two rows:
```
{"phase":"BEGIN",   "round_id":"R-2026-04-25-007","ord":"omega+1",
 "offsets":{"evolution":124801,"deps":31044,"cert":9088,"falsifiers":22117}}
{"phase":"ROLLBACK","round_id":"R-2026-04-25-007","reason":"c:lob_gate",
 "restored":{"evolution":124801,"deps":31044,"cert":9088,"falsifiers":22117}}
```

The Löb-gate cert is gone; the engine is back at ord = ω+1 BEGIN; m3's lesson is preserved as a falsifier-registry entry (separate path, untouched by rollback).

---

## 9. LoC budget

| Component                         | LoC est. |
|-----------------------------------|----------|
| BEGIN / COMMIT / ROLLBACK core    | 55       |
| invariant dispatch (delegators)   | 20       |
| fixpoint heuristic (§4)           | 15       |
| crash recovery (§7)               | 20       |
| git-lock advisory (§5)            | 15       |
| **total**                         | **125**  |

Within the relaxed 130 budget; the +25 over the original 100 is spent on §7 crash-safety, which §6 falsifier alone does not exercise but raw 25 + raw 71 together demand.
