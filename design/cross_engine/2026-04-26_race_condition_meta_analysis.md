# Parallel-Agent Race Condition Meta-Analysis (ω·3)

**Scope**: 2026-04-25 / 2026-04-26 ω-cycle batches (10 / 4 / 13 / 4 / 4 agents, ~35 dispatches)
**Ordinal**: ω·3 (third-level meta over the whole 2026-04-25/26 batch)
**Author**: meta-analysis agent (post-hoc, transcript-blind — see §8 honesty bound)
**Rule basis**: raw 71 (conservative falsifier), raw 73 (minimal grouping), raw 77 (audit append-only)

---

## 1. Catalog of Known Race Events

| # | Event | Type | Severity | Recovery Mechanism | Time-to-Detect |
|---|-------|------|----------|--------------------|----------------|
| 1 | Sweep agent + commit-grouping agent both staged 17 `.hexa` files for commit `a339b29c` (nested-if+continue B1 sweep) | write-write convergent | LOW | Byte-identical patches → git's content-addressable storage produced same blob; no merge conflict | Detected at stage time; no blocking event |
| 2 | F999/F998 temp falsifier emission (`cmd_sha256=deadbeef… / feedface…`, `.fix='remove after test'`) by concurrent agent before commit-grouping ran | write-then-self-clean | NONE (in steady state) | Emitting agent self-cleaned before grouping agent staged anything; no test artifact reached any commit | Pre-flight by grouping agent (`falsifiers.jsonl` scan) |
| 3 | Concurrent agent racily deleted `.githooks/` directory; commit-grouping agent's pre-commit hook fired on k6 | working-tree mutation under stage | MEDIUM | `git checkout HEAD -- .githooks/pre-commit` restore from HEAD; hook re-fired clean | At commit time, surfaced via missing-file error |
| 4 | Stale brief: 49 files described as "untracked" in dispatch context had already been committed by `dd147a165` + `b99adc958` upstream | read-stale-state | MEDIUM | Grouping agent re-ran `git status` at preflight, recognized evolved-layer state, proceeded on next-layer surface (k1–k6) | Preflight (first command of grouping agent) |
| 5 | Atlas-ingest a2: parent dossier said "lines 814-819" but bug was at lines 624-630 | parent-output-stale | LOW | Fix agent grep'd buggy substring, located real lines, applied fix | At first read of stated lines (no match) |

Concurrent witness commit `0ea84fd3` (orphan ω-cycle witnesses) was emitted by another background agent during the grouping run — not a race per se, but evidence that ≥3 agents were live in the same window.

---

## 2. Hypothesized Race Classes That Did Not Manifest

These are plausible failure modes given 10–13 parallel agents and a single working tree:

**H1 — Write-write divergent on same file.** Two agents edit the same `.hexa` source with *different* patches (e.g., one adds a guard, the other refactors a loop). Git would surface this only at stage time as a partial overwrite (last-writer-wins on the inode, not a merge), silently destroying the earlier patch. The 17-file sweep / grouping convergence (Event 1) was *idempotent*; a divergent variant would have lost work.

**H2 — Producer/consumer ordering.** Agent A consumes the output of Agent B (e.g., a witness sha256 propagation, M5 BNF sha → m5_bnf_witness pointer). If A runs before B's commit lands, A reads stale content, propagates the wrong sha. The k2 axis explicitly bundled "2 upstream witness sha256 propagations alongside BNF text — they are causally locked" — implying this race was *anticipated and serialized inside one commit*, not solved system-wide.

**H3 — Transitive cache invalidation.** `falsifiers.jsonl` is read by ≥4 tools (`atlas_health_timeline`, `falsifier_health.sh`, `registry_sign.sh`, pre-commit hook). If agent A appends F113-tightening while agent B is mid-read for snapshot generation, B's snapshot may show 104 entries while the registry is at 105. Atlas health timeline (`105-total: 103 CLEAN + 2 HIT`) was internally consistent at commit time — but consistency *during* the run is unverifiable from artifacts.

**H4 — Signal-handler / hexa selftest interaction.** `hexa_runtime_check.sh` (Tier-1 i2 watchdog, commit `5891fab1`) runs hexa selftests. Under SIGTERM during a parallel parser run, partial state could persist. No incident logged, but no fault-injection test exists either.

**H5 — File-descriptor exhaustion.** 13-agent batch × open `state/atlas_health_timeline.jsonl` for append + open repo for status + open hooks → ~50–80 fds per batch. Below macOS default `ulimit -n 256`, but no headroom test was done.

**H6 — Lock-free append interleave.** Multiple agents `>>` to the same JSONL file (`atlas_health_timeline.jsonl`, `sandbox_breaches.jsonl`). POSIX `O_APPEND` guarantees atomicity *only up to PIPE_BUF (4096 bytes)*; a witness line exceeding 4 KB could interleave. Witness lines observed are ≤1.5 KB → safe in practice, but unverified invariant.

---

## 3. Structural Reasons Races Resolved Cleanly

1. **Append-only invariants (raw 77).** No agent destructively rewrites history. `git push --force` and `git commit --amend` are policy-banned; `falsifiers.jsonl` is append-only by tool contract. Result: divergent writes show up as multiple commits, not lost commits.
2. **Low cross-agent file overlap by design.** The 5-batch dispatcher partitions axes (security R5 / m5+roadmap / interp-quirk / falsifier-audit / dashboard-honesty), and each axis names disjoint file sets. Event 1 was the rare exception (sweep + grouping both touched all 17 `.hexa`).
3. **Idempotent operations.** The B1-fix sweep is mechanically determined: "flatten nested if-continue into single guarded if". Any agent that runs the same rewrite produces the same bytes. Git's content-addressable hashing means same-bytes → same-blob → no conflict.
4. **Git's content-addressable nature.** Even when two agents stage the same change, the resulting tree object is identical; `git add` on the second run is a no-op. This is the *root structural defense* against Event 1 turning into data loss.
5. **Preflight habits (raw 71).** The commit-grouping agent ran `git status` at preflight and detected the stale-brief condition (Event 4) before acting. This is convention, not enforcement.

---

## 4. Residual Fragility — What Breaks at N=100

| Pressure | N=10 behavior | Projected N=100 failure |
|----------|---------------|-------------------------|
| `.git/index.lock` contention | Rare retry | Frequent stage-time retries; agents may abort with "another git process is running" |
| Working-tree races on shared dirs (`.githooks/`, `state/`) | Event 3 (1 occurrence) | ~10× rate; some not recoverable from HEAD if the deletion lands between stage and commit |
| Stale-brief frequency | Event 4 (1 occurrence in 35 dispatches) | Most briefs stale by dispatch time; preflight burden dominates useful work |
| FD / inode pressure | Below `ulimit` | Approaches 256-fd ceiling; sporadic `EMFILE` |
| JSONL append interleave | Within PIPE_BUF | Larger witnesses cross PIPE_BUF; corruption likely |
| Idempotency assumption | Holds for sweep | Two agents writing *non-idempotent* but overlapping refactors would silently lose work |
| Pre-commit hook serial bottleneck | k6 only | Hook becomes the throughput ceiling; agents queue on `flock` of registry |

The *qualitative* break is: at N=100, the design's "low overlap by partition" assumption fails — birthday-paradox collisions on file paths become routine.

---

## 5. Recommendations

1. **Advisory file locking (`flock`)** for hexa tool sources during edits. Wrap rewrites: `flock tool/x.hexa -c 'rewrite_pass …'`. Cheap, blocks Event 1's divergent variant.
2. **Cross-agent message bus.** A shared `state/agent_bus.jsonl` (append-only) where every agent emits `{agent_id, ts, claimed_files[], phase}` at preflight + commit. Other agents see live claims. Currently agents are ships in the night.
3. **Phase barriers.** Some classes must complete before others start: e.g., *falsifier emit* before *registry_sign*; *witness propagation* after *upstream commit*. A simple dependency DAG with `phase` markers in dispatch metadata, enforced by a coordinator agent.
4. **Stale-brief mitigation as enforced preflight.** Every agent's first command must be `git rev-parse HEAD && git status --short`; brief checksum verified against current HEAD, mismatch triggers re-plan rather than blind execution.
5. **JSONL append safety.** Switch to `>> /dev/stderr | flock-wrapped tee -a` pattern, or chunk witness emission to ≤ PIPE_BUF.
6. **FD budget.** Add `ulimit -n 1024` to dispatch scaffold; budget per-agent at ~10 fds.

---

## 6. Falsifier (raw 71) — Hand-Constructed Conflict Scenario

**Scenario "F-RACE-1: Divergent sweep on tool/atlas_ingest.hexa".**

> Agent A is dispatched at T₀ with the brief: "tighten error-message strings in all `.hexa` tools — atlas-ingest line 627 reads `panic("bad")` → make it `panic("atlas: malformed BT row")`".
> Agent B is dispatched at T₀+5s with the brief: "fix B2 quirk — flatten nested-if-continue across all `.hexa` tools" (extension of `a339b29c` work) — at atlas-ingest, B's flattening rewrites lines 624–630 *including* the very `panic("bad")` line A intends to edit.
> Both agents read the file at T₀+10s, prepare patches in memory, stage at T₀+30s.
>
> Outcome under current setup: last-writer-wins on the working-tree inode. Whoever calls `git add tool/atlas_ingest.hexa` second silently overwrites the first's patch with their version of the file. No conflict is raised because neither agent went through `git merge` — both wrote directly to the working tree. The losing agent's commit will *not* contain the edit it claimed to make; the witness will state "edited line 627" but the blob will not reflect it.

**Why this isn't covered by Event 1's defense**: Event 1 worked because both agents produced *identical* bytes. F-RACE-1 produces *different* bytes for overlapping regions. No git-level conflict detection fires for working-tree-direct stages; conflicts only surface in `merge`/`rebase`/`cherry-pick` paths.

**Minimal mitigation**: advisory `flock(2)` on each `.hexa` source for the duration of read→edit→stage. Pseudo-discipline:

```
exec 9>/var/lock/nexus-tool-atlas_ingest.hexa.lock
flock -x 9
# read, patch, git add tool/atlas_ingest.hexa
flock -u 9
```

Cost: one syscall per file per agent. Benefit: serializes overlapping edits into a deterministic order; the second agent re-reads the post-A state and either (a) re-targets, (b) detects its target line moved, or (c) cleanly aborts with witness. Does not require coordinator infrastructure or rewriting the dispatch model.

---

## 7. Verdict

**WARN** on systemic ω-cycle parallelism health.

- **Why not PASS**: Event 1 was a near-miss saved by idempotency, not by design. Event 3 (`.githooks/` deletion) was recovered by ad-hoc `git checkout HEAD --`, not by an enforced protocol. F-RACE-1 is constructible with current tools and would silently destroy work. The 35-dispatch sample is too small to claim safety at scale; the 1-of-35 race rate (Event 1) extrapolates to ~3 races per 100-agent batch under same-axis collision pressure.
- **Why not FAIL**: zero data loss observed across the actual 35 dispatches. Append-only invariants and content-addressable git provided real (if accidental) defense-in-depth. Recovery mechanisms, while ad-hoc, worked.
- **Path to PASS**: implement Recommendations 1 (flock) + 2 (agent_bus) + 4 (preflight git-status); re-evaluate after a ≥50-agent batch.

---

## 8. Honesty Bound (raw 71)

The author of this dossier did not see live agent transcripts, only post-hoc artifacts:
- commit messages and patches in `git log`
- `design/cross_engine/2026-04-26_commit_grouping_omega_cycle.json` (which provided Events 1–4)
- the user-supplied dispatch context (which provided Event 5)

What is **not known**:
- exact dispatch timestamps of each agent (T₀ values are illustrative in §6)
- whether Events 1–4 had *additional* near-misses upstream that were silently absorbed
- whether the 5 listed events are representative or cherry-picked by the commit-grouping agent's own self-reporting bias
- the actual N for the 13-agent batch (claimed, not verified)

H4 (signal-handler) and H5 (FD exhaustion) are unverified hypotheses; absence of incident in artifacts is *not* absence of incident in the live run.

---

**Cited incidents**: Event 1 → `a339b29c`; Event 2 → preflight of `2026-04-26_commit_grouping_omega_cycle.json`; Event 3 → `fixpoint_marker` of same; Event 4 → upstream `dd147a165` + `b99adc958`; Event 5 → user-supplied dispatch context. Concurrent witness emission → `0ea84fd3`.
