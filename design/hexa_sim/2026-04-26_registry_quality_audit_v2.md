# Falsifier Registry Quality Audit v2 — 104 entries

**Date**: 2026-04-26
**Scope**: `nexus/design/hexa_sim/falsifiers.jsonl` (104 entries, post-expansion from 12 → 104 this session)
**Charter**: Ω-cycle quality consolidation — distribution, hash collision, near-duplicate clusters, weak entries, soft-retire candidates (raw 71 — REPORT only)
**Predecessor**: `2026-04-26_falsifier_registry_integrity_audit.md` (42-entry baseline)

---

## 1. Distribution

### 1.1 Type tag

| Type tag | Count | Note |
|---|---|---|
| `<none>` (no tag in cmd) | 17 | mostly F1–F12 era + xpoll guards (no atlas tag in grep) |
| `@P` foundation | 26 | dominant |
| `@F` factor / functional | 16 | second-largest |
| `@R` rule / relation | 11 | well represented |
| `@C` compound | 10 | architecture cluster |
| `@X` celestial | 7 | L7 family |
| `@S` structure | 5 | |
| `@L` law | 5 | |
| `@M` methodology meta | 4 | F82 / F108 family |
| `@T` theorem | 3 | hand-promoted T68/T74 |

Total: 104, all `@`-categories represented except `@N` / `@D` / `@E` (none added — also OK, atlas may not use them).

### 1.2 Grade

| Grade | Count |
|---|---|
| `[10]` | 65 |
| `[11]` | 19 |
| `<no_grade>` | 18 |
| `[10*]` | 1 |
| `[11!]` | 1 (F108 — sole strict-strict) |

The `<no_grade>` 18 are F1–F12 (verify-grid family — grade-agnostic, runs hexa runtime), F23 (atlas-DSL regression), F46–F49 (semantic-gap guards — grep across atlas), F113 (proof-theoretic ordinal ladder, grade was lost in cmd template). All are explainable; F113 is the one minor cleanup item.

### 1.3 Cmd primitive

| Primitive | Count | Examples |
|---|---|---|
| grep-anchor | 92 | F19, F20, F21, … bulk |
| hexa-runtime | 9 | F1–F5 + F9–F12 (live bridges) |
| python3 | 2 | F48 self-ref guard, F49 semantic-gap |
| `<other>` | 1 | F23 (`bash atlas_dsl_v2_regression.sh`) |

92/104 = 88% are grep-anchor (atlas literal sentinels). Healthy if interpreted as defense-in-depth, but it skews diversity.

### 1.4 Domain (refined classifier)

| Domain | Count |
|---|---|
| methodology | 21 |
| biology | 17 |
| particle | 14 |
| chemistry | 10 |
| `<other>` (numerology / catch-all) | 10 |
| astronomy | 7 |
| number-theory | 7 |
| cosmology | 6 |
| foundation-anchor (σ/τ/φ family at n=6) | 5 |
| geology | 4 |
| verify-grid | 1 |
| bridge-live | 1 |
| linguistics | 1 |

vs integrity audit (42 entries, 21 atlas domains × 3 cols): the expansion from 42 → 104 mostly went into **methodology + biology + particle + chemistry**. **Single-falsifier domains**: linguistics, bridge-live, verify-grid. Astronomy/cosmology/geology are thin (≤7 each) — same coverage gaps as the integrity audit flagged.

---

## 2. Hash collision check

```
HASH COLLISIONS: NONE
UNIQUE HASHES: 104 / 104
EMPTY/SHORT HASHES: 0
```

Result: **all 104 cmd_sha256 values unique, no collisions, no empty/truncated.** Healthy.

Slug uniqueness: **104/104** unique slugs.
ID uniqueness: **104/104** unique IDs (F1…F114 with 10 gaps from retired/skipped numbers).

---

## 3. Near-duplicate clusters (cmd ratio > 0.85)

29 pairs flagged. They cluster into 3 families:

### 3.1 Verify-grid family (F1 / F2 / F4 / F5)

```
F4/oeis-drift  ↔  F5/counter-overfit         0.973
F1/constants   ↔  F5/counter-overfit         0.970
F1/constants   ↔  F4/oeis-drift              0.966
F2/alpha-drift ↔  F4/oeis-drift              0.962
```
All four invoke `hexa run hexa_sim_verify_grid.hexa --axis X` with different `--axis` flags. **High cmd similarity is structural, not redundant** — different axes test different invariants. Keep all.

### 3.2 σ / τ / φ anchor cluster (F21, F22, F24–F26, F71–F74, F95)

```
F21/sigma-sq-anchor    ↔ F72/sigma-n-anchor         0.943
F71/sigma-tau-anchor   ↔ F72/sigma-n-anchor         0.939
F21                    ↔ F71                        0.929
F25/sigma-foundation   ↔ F26/tau-foundation         0.919
F72                    ↔ F74/two-sigma              0.909
```
All grep `^@C foo = expr = N :: architecture [10*]` against `n6/atlas.n6`. Each pins a distinct atlas literal (`sigma_sq=144`, `sigma_tau=48`, `sigma_n=72`, `warp_size=32`, `two_sigma=4096`, `phi_tau=16`). **Cmd is similar by template; semantic targets differ.** They constitute the @C compound architecture coverage axis. Keep — they catch grade drift and atlas-region tampering distinctly.

### 3.3 Convention guard pair (F46 / F47)

```
F46/xpoll-sigma-convention-guard ↔ F47/xpoll-tau-convention-guard  0.953
```
Sister entries: σ(N)=N malformed-pattern guard vs τ(N)=N malformed-pattern guard. Intentional twins. Keep.

### 3.4 Axial tilt pair (F28 / F40)

```
F28/earth-axial-tilt   ↔ F40/l7-mars-axial-tilt    0.949
```
Sister: Earth `J2 - μ = 23` vs Mars `J2 + μ = 25`. Intentional pair (covers ± companion identity). Keep.

**Net**: zero true duplicates. All near-dupe pairs are legitimate sister anchors using a shared grep template — exactly what an atlas-literal layer should look like.

---

## 4. Weak entry list

### 4.1 Reason / fix length audit
**0 entries** with `reason` < 40 chars or `fix` < 30 chars. All 104 have enriched human-written reason+fix (no auto-template skeletons). 

### 4.2 Origin attribution audit
- Unclear-origin entries: **0**
- All 104 carry an `origin` field naming the source axis (atlas_index entry, hive raw N, design doc S§, manual review date)
- 71 entries have `auto-spawn from atlas_index entry …` provenance — these are the bulk Ω-cycle 2026-04-26 backfill
- 7 entries are `hand-promoted from auto-spawn …` (T68, T74, R70, R94, R96 + 2 @M) — the @T / @R / @M layer
- F113 has grade lost in cmd (no `[11_PARADIGM_LADDER]` token) — minor template issue, not weak

### 4.3 Genuine weak / low-marginal entries (3 candidates)

| ID | Slug | Issue |
|---|---|---|
| **F8** | `nxs002-cycle10-lsr-orthogonal-composite` | Cycle-10 finding documentation anchor. Captures a *negative* finding ("LSR axis is orthogonal to composite"). Defense-in-depth for documentation drift, not a substantive identity. F#-count value primarily. |
| **F7** | `nxs002-cycle10-quantum-topology-hurts` | Sister to F8 — same cycle-10 doc anchor (different finding). Pair is somewhat redundant (both check the same NXS-002 cycle-10 doc didn't get rewritten). |
| **F6** | `nxs002-cycle10-q4-qrng-er-null` | Third sibling. Same cycle-10 doc anchor, different finding (QRNG axiom NULL). Three falsifiers on one document is on the heavy side. |

The F6/F7/F8 trio guards a single artifact (`nxs-002 cycle 10` design doc). One representative would suffice if file-checksum coverage exists; absent that, keeping all three is defensible defense-in-depth. **Not recommending retire — flag for later if NXS-002 doc is sealed by hash.**

---

## 5. Coverage matrix update (vs integrity audit baseline of 42)

| Domain | 42-entry baseline | 104 now | Δ |
|---|---|---|---|
| foundation (σ/τ/φ at n=6) | ~6 | 5 | flat (richness preserved via F71–F74 architecture) |
| methodology | ~3 | 21 | **+18** (F46–F49 + F82 + Ω-meta backfill) |
| biology | ~2 | 17 | **+15** (L4 codon/amino expansion) |
| particle | ~3 | 14 | **+11** (L5 SM + neutrino PMNS) |
| chemistry | ~4 | 10 | **+6** (L1/L2 atomic/element backfill) |
| astronomy | ~4 | 7 | +3 (mars/saturn/jupiter additions) |
| number-theory | ~3 | 7 | +4 (OEIS A000203/A000005/A000010 specific anchors) |
| cosmology | ~3 | 6 | +3 (CMB nₛ, Planck, dark-matter) |
| geology | ~2 | 4 | +2 (mantle, ocean, kola) |
| linguistics | 0 | 1 | **+1 (closed sole zero-coverage gap)** |
| verify-grid (runtime axis) | 5 | 1 | -4 in classifier — but F1–F5 still exist; classifier matched them under foundation/methodology |

**Coverage gap closures since integrity audit**:
- Linguistics 0 → 1 (F107 closed)
- Particle SM zero → 14 (F50 + cluster — far exceeded the integrity-audit recommendation)
- @M methodology 0 → 4 (F82, F108, plus 2)

**Persistent thin spots**: bridge-live dynamic (still 1: only F9 horizons), geology 4, astronomy 7. These match the integrity-audit recommendations and were not addressed in this expansion.

---

## 6. Soft-retire candidates (raw 71 — REPORT only, NO auto-retire)

Per integrity audit: load-bearing core was 24/42 → now estimated ~24–30/104 (most additions are defense-in-depth, that's OK). Only flag truly redundant ones:

| ID | Slug | Rationale | Confidence |
|---|---|---|---|
| **F8** | `nxs002-cycle10-lsr-orthogonal-composite` | Third of three anchors on same NXS-002 cycle-10 doc. Lowest novelty of trio. If file-hash seal exists, one of {F6,F7,F8} suffices. | LOW (defensible to keep) |
| **F23** | `atlas-dsl-v2-layer4-vacuous` | Layer 4 sha non-empty — narrow regression catch. Was hand-fixed once; now testing the fix, not the system. Could fold into a generic atlas serializer test. | LOW |
| **F113** | `proof-theoretic-ordinal-ladder` | Grade token missing in cmd template (ladder string only). Either fix the template OR demote — current form contributes structure but not grade-drift detection. | RECOMMEND FIX first, retire only if can't fix |

**3 candidates total, all LOW confidence (raw 71 prefers keep + report).** No HIGH-confidence retires identified. The expansion is healthy.

---

## 7. Recommendations

### 7.1 Continue expansion vs pause for consolidation?

**Recommendation: PAUSE EXPANSION, CONSOLIDATE**, then resume targeted growth.

Reasons:
1. Hash collision: clean (0). Slug/ID dedup: clean. Origin attribution: clean (0 unclear). **Quality fundamentals are intact.**
2. Domain skew: methodology + biology + particle now dominate (52/104 = 50%). Astronomy/cosmology/geology/linguistics/bridge-live remain thin. **Next round should target the thin domains, not bulk @P backfill.**
3. Cmd-primitive skew: 88% grep-anchor. Adding more grep-anchors yields diminishing returns. **Next round should privilege hexa-runtime / python / live-bridge primitives.**
4. Near-duplicates: zero true dupes detected. **No deletion needed before next expansion.**
5. F113 has a grade token missing — small fix, not a blocker.

### 7.2 Action items (priority order)

1. **Fix F113 cmd template** — add `[11_PARADIGM_LADDER]` token so grade is regex-detectable. (5 min)
2. **Targeted expansion**: 5–10 new entries focused on bridge-live dynamic (currently 1), geology (4), astronomy (7), or linguistics (1). Avoid more @C/@P architecture grep-anchors.
3. **Decide F6/F7/F8 trio**: either seal NXS-002 doc by hash and retire two of three, or accept the trio as defense-in-depth.
4. **Document the load-bearing-vs-defense-in-depth split** in registry README so reviewers understand 88% grep-anchor is intentional.

### 7.3 Out of scope

- No retires executed (raw 71 — REPORT only).
- No template/cmd edits applied.
- Main thread batches commits.

---

## Summary tile

```
TOTAL=104  UNIQUE_SLUGS=104  UNIQUE_IDS=104
HASH_COLLISIONS=0  EMPTY_HASHES=0
NEAR_DUP_PAIRS=29  TRUE_DUPES=0  (all sister-anchors using shared template)
WEAK_REASON_FIX=0  UNCLEAR_ORIGIN=0  GRADE_FIX_NEEDED=1 (F113)
SOFT_RETIRE_CANDIDATES=3 (all LOW confidence)
RECOMMENDATION=pause-bulk-grep-expansion + thin-domain-targeted-growth
```
