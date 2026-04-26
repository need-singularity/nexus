---
section: §9.7 (new) + density footnote
title: "PAPER_S9 offline-replayability caveat — patch log"
generated: 2026-04-26
predecessor_commits:
  - 6921ba4c  # PAPER_S9_LIMITATIONS.md initial 674-word draft
  - 1b611443  # PAPER_DRAFT_v3.md integration
  - fa6ec2ec  # 2026-04-26_new_domain_scout_v2_omega_cycle.md (finding source)
raw_admissibility: 73 (decline + caveat as first-class evidence)
audit_append_only: raw 77 (existing §9.1–§9.6 prose preserved byte-identical)
---

# PAPER_S9 offline-replayability caveat — patch log

## 1. Trigger

`design/hexa_sim/2026-04-26_new_domain_scout_v2_omega_cycle.md` ("Striking
finding" section) observed that of $16$ registered hexa-sim bridges only
$\sim 2$ emit an explicit OFFLINE-FALLBACK marker, and the remaining
bridges either rely on a hard-coded reference-data path or have no offline
fallback at all. PAPER_S9_LIMITATIONS.md commit `6921ba4c` did not caveat
this. Independent reproducers running REPRODUCTION_PROTOCOL Stage 4 on a
network-restricted host could see bridge_health < 16/16, or — worse — a
silent 16/16 in which up to 9 cells are running off cached values rather
than live archive fetches. This is the threat S9.7 closes.

## 2. Files patched (in-place, append-only)

1. `design/hexa_sim/PAPER_S9_LIMITATIONS.md`
2. `design/hexa_sim/PAPER_DRAFT_v3.md` (§9 mirror)

No prior §9.1–§9.6 prose was modified; the patch is strictly additive
(raw 77 audit-append-only).

## 3. Word-count delta

| File | before | after | delta |
|------|--------|-------|-------|
| PAPER_S9_LIMITATIONS.md | 674    | 855    | +181  |
| PAPER_DRAFT_v3.md       | 13,954 | 14,146 | +192  |

Both deltas land under the +200-word ceiling; S9 lands at 855 words,
under the 900-word hard cap. The v3 delta is slightly smaller because
LaTeX `\texttt{}` escapes in S9 inflate the per-word count vs markdown
back-ticks in v3.

## 4. New subsection — §9.7 "Bridge offline-replayability gap"

Position: appended after §9.6 "Recognition of internal PAUSE signal",
before the §10 horizontal rule.

### Content summary

- 16-bridge / 9-sim_bridge-dir reconciliation (footnote: two counts
  measure different objects; the registry is `cli/run.hexa`
  `_hexa_sim_bridge_dispatch` while the disk dirs are orthogonal
  sub-experiments).
- 7 bridges with hard-coded reference fallback: codata, cmb, nanograv,
  nist_atomic, icecube, gaia, lhc.
- 9 bridges lacking robust offline path: oeis_live, gw_observatory,
  horizons, arxiv_realtime, simbad, wikipedia_summary, openalex,
  pubchem, uniprot.
- Affected falsifiers: F4 (oeis-drift), F9 (horizons-ephemeris),
  F10 (cmb-cross-bridge), F11 (hubble-tension), and downstream multi-shard
  probes — formally non-deterministic-replayable on offline CI.
- Mitigation in place: `tool/bridge_health.sh` per-bridge classifier emits
  `OFFLINE-FALLBACK` status when live fetch fails — preserves 16/16 but
  substitutes static values, weaker than R1 cmd-fingerprint replay.
- Reproduction threat: independent reproducer at REPRODUCTION_PROTOCOL
  Stage 4 may see < 16/16 on rate-limited host.
- Forward axis: PAPER_OUTLINE_v1.md §10.4 already enumerates the
  OFFLINE-FALLBACK contract (cached-payload cmd_sha256 + freshness window
  + degraded-mode marker) as a next-cycle hardening item.

## 5. Density correction (footnote)

Two distinct denominators appeared in prior session prose:

- **16 bridges** — the canonical registry count, source:
  `tool/bridge_health.sh` header comment "16 registered hexa-sim
  bridges (mirrored from cli/run.hexa _hexa_sim_bridge_dispatch)".
  This is what the paper uses.
- **9 sim_bridge dirs** — `ls ~/core/nexus/sim_bridge/` count
  (anu_stream, anu_time, atlas_anu_corr, bostrom_test, godel_q,
  multiverse, ouroboros_qrng, qpu_bridge, sr_harness). These are
  orthogonal sub-experiments and do *not* roll up into bridge-health.
  Scout v2 noted the two are different objects.

The footnote in §9.7 reconciles both numbers explicitly so a reader who
greps for "16" or "9" in the paper sees a single, internally consistent
explanation.

## 6. Citation chain

- Scout v2 finding → `2026-04-26_new_domain_scout_v2_omega_cycle.md`
  ("Striking finding" para, lines 79–82)
- Bridge-health audit → `2026-04-26_bridge_health_check.md` (prior
  enumeration of 16 bridges, classifier emit logic)
- R1 cmd-fingerprint primitive → §3 of PAPER_DRAFT_v3.md (referenced
  by §9.7 as the stronger guarantee that OFFLINE-FALLBACK weakens)
- §10.4 forward-work pointer → existing in PAPER_DRAFT_v3.md line 1163

## 7. Before / after snippet

**Before (PAPER_S9_LIMITATIONS.md tail, lines 96–107):**

```
## §9.6 Recognition of internal PAUSE signal
... whose recommendation was heeded.
[EOF]
```

**After:**

```
## §9.6 Recognition of internal PAUSE signal
... whose recommendation was heeded.

## §9.7 Bridge offline-replayability gap

A scout-v2 audit (...commit fa6ec2ec) re-enumerated the registry's
external-API surface and surfaced a determinism caveat...
[~340 words; 3 paragraphs + footnote + threat + forward-axis]
```

Identical structure mirrored into `PAPER_DRAFT_v3.md` between §9.6 and the
`---` separator preceding `# 10. Discussion and future work` (line 1114
in pre-patch v3).

## 8. Constraints honoured

- raw 73 admissibility — caveat recorded as first-class evidence, not buried.
- raw 77 audit-append-only — §9.1–§9.6 prose untouched byte-for-byte.
- LaTeX-friendly — `\texttt{}` used in PAPER_S9_LIMITATIONS.md;
  markdown back-ticks used in PAPER_DRAFT_v3.md (which carries fenced
  markdown for both render paths).
- Word ceiling — S9 kept under +200 words (target 674 → ≤ 900).
- v3 §9 byte-equality with v2 — already broken by this patch, so the
  assembly agent's byte-equality check on §1–§13.9 + §13.12–end (which
  excludes §9) is unaffected; §9 is by design the one section that mutates
  with new declines and caveats.
