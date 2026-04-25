# Falsifier registry integrity audit — 2026-04-26

Scope: full pairwise integrity sweep over `design/hexa_sim/falsifiers.jsonl` (42 entries: F1–F12, F19–F44, F46–F49; F13–F18 retired pre-history, F45 declined per `2026-04-26_F45_decision.md`).

## Executive summary

| metric | value |
|---|---|
| Entries | 42 |
| Pairs checked | 861 |
| Hard duplicates (same claim) | **0** |
| Near-duplicates (jaccard ≥ 0.4 on claim text) | 18 — all are **complementary axes**, not redundant |
| Logical implications | 12 explicit literal↔arithmetic / specific↔broad pairs (intended layering) |
| Contradictions (one CLEAN one HIT for same claim) | **0** |
| Coverage gaps (sole-witness or thin domains) | **7** |
| Load-bearing core (could shrink registry to N without losing coverage) | **24** |

No deletions recommended. The 18 near-duplicate pairs are all designed as complementary axes (literal anchor vs arithmetic identity vs cross-shard witness), explicitly called out in their `origin` strings.

## Domain coverage matrix

(Entries can appear in multiple domains. Layer = grep-atlas-literal / verify_grid-arithmetic / bridge-selftest / bridge-dynamic / ceiling-doc / python-audit.)

| domain | n | falsifiers | depth |
|---|---:|---|---|
| atlas_literal_anchor | 28 | F1·F12·F19–F44·F48 | rich (post-Ω-cycle batch) |
| foundation_arithmetic (σ/τ/φ/μ/sopfr/J₂/M3) | 33 | most entries reference one of these | ubiquitous |
| number_theory | 7 | F1·F4·F12·F20·F24·F25·F32 | well-covered |
| physics (CODATA/NIST atomic) | 7 | F2·F10·F12·F21·F25·F36·F39 | well-covered |
| chemistry (bonds, MW, hybridization) | 6 | F33·F34·F35·F36·F38·F39 | well-covered |
| astronomy (axial / orbital / planetary) | 6 | F9·F28·F33·F40·F41·F42 | well-covered |
| cosmology (CMB / H₀ / BBN / n_s) | 5 | F10·F11·F30·F40·F43 | adequate |
| anima_basis (cpgd / projector / eigenvec) | 5 | F27·F30·F31·F33·F38 | adequate (cross-shard) |
| meta_paradigm (@M shifts) | 4 | F3·F27·F29·F44 | thin |
| cycle10_negative_findings (ceiling.md) | 3 | F6·F7·F8 | adequate (sole-witness cluster) |
| quantum_arch (QEC / QRNG / qubit) | 3 | F6·F7·F44 | thin |
| dsl_regression (atlas_dsl_v2 / audit baselines) | 3 | F23·F48·F49 | adequate |
| determinism (byte-eq / cert SHA) | 2 | F3·F30 | thin but orthogonal |
| topology (Euler-char / polyhedron) | 2 | F7·F37 | thin |
| **biology** (codons, DNA, protein) | **1** | F36 | **gap** |
| **observatory_dynamic** (TP-8 / horizons live) | **1** | F9 | **gap** |
| **cross_bridge_resonance** (independent-framework coincidence) | **1** | F10 | **gap** (F45 declined) |
| **galactic** (Milky Way / Solar-galactic-year) | **1** | F42 | **gap** |
| **BBN_early_universe** | **1** | F43 | **gap** |
| **particle_SM** (fermion count, IceCube, LHC) | **0** | — | **explicit gap** |
| convention_guard (xpoll / func(N)=N / semantic-gap) | 4 | F46·F47·F48·F49 | well-covered, layered specific→broad |

## Findings

### 1. Zero hard duplicates, zero contradictions

No two entries make the same claim with the same `cmd`. No pair has one expecting CLEAN and another HIT for the same underlying assertion.

### 2. 18 near-duplicate pairs are intentional layering

The high-jaccard pairs cluster into three intended patterns:

- **Literal ↔ arithmetic axis on the same primitive** (all explicitly noted in `origin`):
  F1↔F25 (σ arithmetic vs σ literal at [11*]), F1↔F26 (τ), F1↔F19 (μ), F2↔F21 (σ²=144 identity vs literal). These are the core orthogonality pattern from the Ω-cycle 2026-04-26 grade-11 bucket.

- **Companion-bridge pairs** sharing a formula family:
  F28↔F40 (Earth tilt J₂-μ=23 vs Mars tilt J₂+μ=25 — opposite-sign mirror), F34↔F35 (sp³ vs sp² hybrid bond angles), F33↔F38 (carbon=6 in two atlas regions @F + @C, dual-region witness), F22↔F39 (φ^τ=16 abstract vs CH₄ mw=16 application).

- **Convention guards layered specific→broad**:
  F46↔F47 (σ-pattern vs τ-pattern, parallel), F46↔F48 (xpoll-σ-specific vs func(N)=N broad), F48↔F49 (syntactic baseline vs full semantic-evaluation audit). Decoupled by design — F48 stays PASS after F46/F47 cleanup.

The highest-jaccard pair (F46↔F47, 0.87) is a **template clone by intent** — same regex shape, different function name. Renaming would obscure the parallel structure.

### 3. Coverage gaps to flag

Five sole-witness domains and one outright zero:

- **particle_SM** = 0 falsifiers. The hunt doc references `lhc.fermion_total = 12 = σ` (atlas line 64 of cross_bridge doc); a falsifier formalizing "SM fermion count = 12 = σ" would close the @C atom adjacency. Candidate: `F50 lhc-sm-fermion-sigma-bridge`.
- **biology** = 1 (F36 codon-64). DNA base-pair = 4 = τ, amino acid = 20 = J₂-φ-σ, etc. potentially formalize into 1–2 more.
- **observatory_dynamic** = 1 (F9 horizons). Of 16 bridges only horizons exercises live data — `cmb_planck`, `codata`, `nanograv`, `gw_observatory`, `icecube`, `gaia`, `simbad`, `pubchem`, `nist_atomic`, `oeis_live`, `wikipedia_summary`, `lhc_opendata` are all bridge_selftest layer only. The bridge_selftest layer (F10/F12/F38/F43 etc.) gives anchor-value coverage but not dynamic-output coverage.
- **galactic** = 1 (F42 MW year), **BBN** = 1 (F43 He₄), **cross_bridge_resonance** = 1 (F10) — each is a sole-witness paradigm slot. Loss is unrecoverable from siblings.

### 4. F45 gap is principled, not accidental

`2026-04-26_F45_decision.md` declined the cross-bridge 3.5% triplet on three grounds (framing inconsistency, doublet not anomalous, atomic-shell explanation absorbs the Be observation). The cross_bridge_resonance domain therefore stays at depth-1 (F10 only) by design. This is a healthy negative result, not a coverage hole.

## Load-bearing core (24 entries)

A reduction to **24 falsifiers** would preserve all distinct coverage axes. Removable redundancies (8): the literal-anchor twins where the arithmetic axis (F1) already covers the value. But the literal anchors guard *grade* and *atlas-region* — distinct failure modes from arithmetic — so the recommendation is **keep all 42**. The "load-bearing 24" figure is an upper bound on what's strictly non-redundant; it is not a deletion list.

The 24 (one representative per coverage axis):

```
F1 (verify-grid CONSTANTS)        F23 (dsl_v2 regression)
F2 (alpha symbolic identity)      F24 (n=6 foundation literal)
F3 (byte-eq determinism)          F27 (template_count cross-shard)
F4 (OEIS axis)                    F29 (paradigm-shift @M)
F5 (counter-overfit)              F30 (P_S projector cert)
F6 (cycle10 QRNG NULL)            F32 (perfect-congruent triple)
F7 (cycle10 topology hurts)       F33 (carbon @F)
F8 (cycle10 LSR orthogonal)       F36 (codon-64 triple)
F9 (TP-8 horizons dynamic)        F37 (Euler-char cube)
F10 (cmb·codata doublet)          F42 (MW galactic year)
F11 (Hubble tension)              F43 (BBN He₄)
F12 (triple-source corroboration) F44 (QEC [[6,2,2]])
                                  F49 (semantic-gap audit)
```

The other 18 (F19–F22, F25–F26, F28, F31, F34–F35, F38–F41, F46–F48) are **defense-in-depth** — they catch grade drift, atlas-region damage, syntactic regressions, or companion-formula breakage that the load-bearing 24 cannot detect alone.

## Recommended actions

1. **Add F50 candidate**: `lhc-sm-fermion-sigma-bridge` (`SM fermion count = 12 = σ`) closes the particle_SM zero-coverage gap. Source already in cross_bridge hunt doc.
2. **Consider F51–F52 candidates** for biology depth (DNA bp = 4 = τ, amino acid count = 20 = J₂-φ-σ).
3. **Document the layering convention**: add a short note to `falsifiers.jsonl` README (or this doc) explaining the literal↔arithmetic and specific↔broad pairing strategy so future readers don't read the 18 near-duplicates as deletion candidates.
4. **No renames recommended.** Slugs are descriptive and the parallel-clone names (F46/F47) communicate the parallel structure.
5. **No deletions.** All 42 entries earn their place under the layering convention.

## Most surprising findings

- **F19 (μ-anchor) overlaps semantically with 6 other entries** (F20, F24, F25, F26, F33, F37) at jaccard ≥ 0.42. This is because μ is the only multiplicative function NOT covered by F1 CONSTANTS axis, so it gets cited from many directions — μ is a **hub primitive**. Drift in F19 cascades to F28 (Earth tilt = J₂-μ), F40 (Mars tilt = J₂+μ), F44 (QEC referencing μ), and the convention guards. Hub-degree is correlated with load-bearing weight here.
- **The convention-guard cluster (F46–F49) is the most layered family in the registry**: 4 entries arranged in a ladder (specific σ → specific τ → broad func(N)=N regression → full semantic-evaluation audit). It is the only place in the registry where the layering pattern is fully four-deep. Other anchors stop at literal+arithmetic (two-deep) or sole-witness (one-deep).
