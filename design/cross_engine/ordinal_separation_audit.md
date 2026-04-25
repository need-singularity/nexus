# Ordinal Separation Audit — Roadmap Engine × Meta Engine

- audit_id: 2026-04-25_ordinal_separation_audit
- audit_ordinal_stamp: ω·2 (two-engine product; this audit straddles both)
- ts: 2026-04-25
- auditor: independent cross-cutting review (separate from cycle authors)
- raw_anchors: raw 70 (multi-axis), raw 71 (falsifier), raw 77 (audit append-only)
- parent ω-cycles audited:
  - roadmap: trawl_id `2026-04-25_roadmap_engine_final_form_and_limits_omega_cycle`
    (`design/roadmap_engine/2026-04-25_final_form_and_limits_omega_cycle.json`)
  - meta:    trawl_id `2026-04-25_meta_engine_final_form_and_limits_omega_cycle`
    (`design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json`)
- coupling dossier audited: `design/cross_engine/r10_m10_coupling_dossier.md` (235 lines, present)

---

## 1. Ordinal Claims Extracted

From the two parent ω-cycles and the coupling dossier:

| System            | Claimed ordinal | Anchor in source                                  |
|-------------------|-----------------|---------------------------------------------------|
| Roadmap engine    | ε_0             | r19 (Gödel 2nd) mitigation cites Gentzen ε_0; coupling §2.1 |
| Meta engine       | Γ_0             | m18 limit_axes; m12 mitigation; coupling §2.2     |
| Joint coupling    | ψ(Ω_ω) or higher | m5 ordinal_anchor_explicit lists "ψ(Ω_ω)"; coupling header `ω·2` (informal) |
| This audit (meta-meta) | ω·2 (informal product label)            | as constraint of task                                  |

Both parent cycles explicitly state in `cross_cycle_coupling.joint_omega_stop`:
"양 엔진 분리 ordinal 유지 (Gentzen ε_0 / Γ_0 / 더 높은 추후 escalation) — m12 Gödel 2nd 회피".

---

## 2. Ordinal Separation Non-Triviality Check

**ε_0 vs Γ_0 in standard ordinal arithmetic.**

- ε_0 is the least ordinal α with α = ω^α (first fixpoint of the map β ↦ ω^β),
  reached as the limit of ω, ω^ω, ω^ω^ω, … (Cantor; proof-theoretic ordinal of
  PA per Gentzen 1936).
- Γ_0 is the least ordinal α with α = φ_α(0), where φ is the Veblen hierarchy
  (first fixpoint of β ↦ φ_β(0); Feferman 1964 / Schütte 1965 — proof-theoretic
  ordinal of ATR_0 / predicative analysis).
- Standard inequality: **ε_0 = φ_1(0) < φ_2(0) < … < Γ_0**, i.e. ε_0 is strictly
  below Γ_0 in the Veblen hierarchy. Verified by ordinal-arithmetic identities;
  this is textbook (Pohlers, *Proof Theory: The First Step Into Impredicativity*).

→ **Separation is non-trivial.** The roadmap proof-theoretic strength is
strictly bounded below the meta proof-theoretic strength.

**Joint system bound by ψ(Ω_ω)?**

- Buchholz's collapsing function ψ at Ω_ω is the proof-theoretic ordinal of
  Π^1_1-CA + BI / ID_ω (Buchholz 1981). It is far above Γ_0.
- The cycles do *not* prove the joint system reaches ψ(Ω_ω); they merely
  reserve it as headroom in m5's ordinal-anchor schema. Audit accepts this as
  a **declarative ceiling, not a derived bound**. Any actual claim that the
  composite engine attains that strength would require external proof-theory
  expert review — not internally verifiable.

→ Verifiable: ε_0 < Γ_0 (yes). Declared but not proven: joint ≤ ψ(Ω_ω).
   Audit flags the latter as **assertion-only**, no internal violation.

---

## 3. Shared Theorem Citations — Cross-Engine Consistency Risk

The two cycles cite three identical theorem families. For each, the audit
asks: does the shared citation create a derivation of the form
`⊢_X Con(Y)` where X ≠ Y? If yes, **VIOLATION** (Gödel 2nd).

| Pair                                | Same theorem? | Same Gödel universe? | Cross-claim? | Verdict |
|-------------------------------------|---------------|----------------------|--------------|---------|
| r19 Gödel 2nd ↔ m12 Gödel 2nd       | yes (Gödel 1931) | NO — each engine cites it as a *limit on its own* self-cert | NO     | OK     |
| r14 K-uncomputable ↔ m16 Solomonoff | sibling (Σ_2^0 family; Chaitin / Solomonoff) | NO — r14 bounds verify-cost estimation; m16 bounds axis-prior posterior | NO     | OK     |
| r12 halting ↔ m15 halting           | yes (Turing 1936) | NO — r12 applies to η-divergence detection; m15 applies to round-fixpoint termination | NO     | OK     |

For each pair the citations are used as **inward-facing limit anchors**
(each engine restricts itself), never as **outward-facing claims**
(engine A asserting Y about engine B). The coupling dossier §5 hard-rule
"neither engine emits a row asserting the OTHER engine is
consistent/sound/converging" is the structural enforcement.

→ **No shared citation creates a cross-engine consistency claim.** No
violation flagged from §3.

---

## 4. Bus Protocol Audit (vs `r10_m10_coupling_dossier.md`)

Coupling dossier exists (235 lines, present). Reviewed §§1–9.

**Q4a. Does either engine emit certificates ABOUT the other engine's
consistency?**

- Coupling §5 explicitly forbids it: "Forbidden: 'engine Y is consistent' /
  'engine Y will halt' / 'engine Y's axis A is true'."
- Coupling §6 (raw 71 falsifier) implements a writer-side guard:
  `assert payload.get("target_engine", source) == source`.
- Audit verifies the **design** prohibits cross-consistency claims. **NO**
  such certificates are emitted by construction.

  Caveat: the guard is described in the dossier but not yet implemented in
  code (no `state/cross_engine_bus.jsonl` exists yet — this is design-stage).
  Once implemented, runtime falsification of the design would be detectable.

**Q4b. Does the rate-limit prevent feedback oscillation?**

- Chosen value: **5 s wall clock per source** (coupling §7.1).
- Defense-in-depth: hysteresis (0.1 fire / 0.05 release band, §7.2),
  round quantum floor `T_meta_round_quantum ≥ 5 s` (§7.3), cycle detector
  on alternating triples within 60 s (§7.4).
- Audit assessment: 5 s is **adequate as a coarse mutual-exclusion floor**
  (one engine cannot retrigger the other faster than its own minimum work
  unit). Combined with the round-quantum floor it is sufficient to bound
  oscillation frequency below 0.2 Hz per direction. **WARN-level note:**
  no formal Lyapunov argument is given that the coupled system
  *converges*; only that it cannot oscillate faster than 5 s. This is
  acceptable for a Tier-1 design but should be revisited if r9
  (adversarial-robustness) is implemented.

---

## 5. Verdict & Recommendations

**Overall verdict: PASS (with one WARN).**

- Ordinal separation ε_0 < Γ_0 is **textbook-verifiable** and non-trivial.
- Three shared theorem citations are **inward-facing only** (no engine
  certifies the other). Self-cert avoidance is structural, not merely
  procedural.
- Bus protocol forbids cross-consistency rows by design and falsifier guard.
- Rate-limit (5 s) prevents oscillation on the timescales examined.

**WARN:** the joint-system upper bound ψ(Ω_ω) is **declared, not derived**.
This is fine as a design ceiling but should be marked as such in m5
documentation; an external proof-theory review is required before any
formal claim of joint ordinal strength.

**Axes flagged for rework:** none. r10 and m10 as designed are sound.

Optional follow-ups (non-blocking):
- m5 should distinguish "anchor (declared)" from "anchor (derived)" in its
  ordinal field schema.
- r8 convergence-certificate impl should explicitly emit its ordinal stamp
  as ε_0 (not stronger), to keep the asymmetry observable in artifacts.
- Add a runtime test: append a synthetic row with `target_engine != source`
  to a sandbox bus file and verify the guard rejects it (tests the §6
  falsifier mechanism end-to-end).

---

## 6. Falsifier for THIS Audit (raw 71)

**This audit is falsified iff** any future round of either engine emits a
row on `state/cross_engine_bus.jsonl` (or any successor cross-engine
artifact) such that:

```
row.target_engine != row.source
AND row.claim_kind == "consistency"
```

Equivalently, any row where engine X asserts a consistency property of
engine Y ≠ X. Detection method: a one-line `jq` filter

```
jq -c 'select(.payload.target_engine != null and .payload.target_engine != .source and (.payload.claim_kind // "") == "consistency")'
```

run over all cross-engine bus / cert files. A non-empty result falsifies
this audit and triggers re-audit at ordinal ω·2 + 1.

Honesty disclosure (raw 77):
- I can verify ε_0 < Γ_0 from standard proof-theory references.
- I can verify the **design** of the bus dossier forbids cross-consistency
  claims.
- I cannot verify the joint system's actual proof-theoretic strength
  reaches ψ(Ω_ω); that is an external-expert claim.
- I cannot verify runtime behaviour because no bus rows exist yet.

End of audit.
