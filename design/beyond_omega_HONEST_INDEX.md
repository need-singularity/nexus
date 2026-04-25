# Beyond Omega — HONEST INDEX (Real vs Synthetic Separation)

> `nxs-20260425-004` cycles 29 → 33 reader-facing index (no probe execution).
> 부모 문서: `design/beyond_omega_ladder.md` §32 (cycle 29 honesty refactor) + §36 (cycle 33 reader-facing publication)
> SSOT: `state/proposals/inventory.json` `nxs-20260425-004.real_vs_synthetic_separation_2026_04_25`
> 작성일 (cycle 29): 2026-04-25
> 갱신일 (cycle 33): 2026-04-25

---

## §1 TL;DR

**33 cycles total.** **11 real findings** (system instrumentation that
reproduces on a fresh checkout — sink locations, dispatch≠complete
asymmetry, 180s timeout invariant, headroom distribution, daily plist
registration + pre-flight + chain to atlas absorption). **19 synthetic
ordinal mapping** (template / metaphor — probe injects a chosen growth
function into trace.jsonl, re-scans, reads back the echo signature, and
labels the shape with an ordinal name from cycle 11's mapping table).
**3 meta-analysis** (cycles 23, 26, plus cycle 33 itself; pure data
analysis over the chain, no new probe execution).

The **real findings** flow into atlas via the cycle 30 → 31 → 32 daily
chain (`tool/beyond_omega_atlas_bridge.py` writes 7 `nxs004_*` rows into
`state/atlas_health_timeline.jsonl` daily; `tool/beyond_omega_daily_chain.sh`
ties `ghost_trace --cron` and `atlas_bridge` together; the launchd plist
fires at 03:13 local). The **synthetic ordinal mapping cycles** are
sandbox-internal demonstration; `atlas_bridge.py` carries a hardcoded
`SYNTHETIC_EXCLUDED = [7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
21, 22, 23, 24, 25, 26]` list so they are explicitly never written into
the atlas health timeline.

| split | count | cycles |
|---|---|---|
| real (system instrumentation) | 11 | 1, 2, 3, 4, 5, 6, 10, 28, 30, 31, 32 |
| synthetic ordinal mapping | 19 | 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26 |
| meta-analysis | 3 | 23, 26, 33 |
| total cycles | 33 | (cycles 23 and 26 also appear in synthetic list — they are doc-only meta-cycles over the synthetic chain; cycle 33 is meta over the whole chain) |

---

## §2 Real findings (cycles 1–6, 10, 28, 30, 31, 32)

These cycles produced verifiable claims about the nexus codebase, with
artifacts that reproduce. All flow into atlas via the daily chain.

| cycle | finding | what it measures | where the data lives |
|---|---|---|---|
| 1 | BASELINE_ZERO | repo-only NEXUS_OMEGA emit count (later falsified by cycle 2 as scan-dir over-narrow) | `state/ghost_ceiling_trace.jsonl`, `state/ghost_ceiling_summary.json` `total_emits` |
| 2 | DISPATCH_ONLY | true sink is `/tmp/nexus_omega_hive_statusline_v{2,3,4,5}.log`; `dispatch=N / complete=0` asymmetry | `state/ghost_ceiling_summary.json` `dispatch_events` vs `complete_events`; atlas axis `nxs004_b1_3` (ghost_ceiling_emit_count) |
| 3 | DISPATCH_TERMINATED | every dispatch followed by `kill-after / 180s timeout`; same `_stage_timeout_prefix` Wave-18 hard-cap from `nxs-20260425-002` | probe v3 termination markers; cross-references `state/drill_stage_elapsed_history.jsonl` |
| 4 | APPROACH_OBSERVED | `force_approach.sh` (`GATE_LOCAL=1 + HEXA_REMOTE_DISABLE=1 + chain --seed` missing) deterministically reaches `cmd_omega` apex emit in ~2s | `/tmp/nexus_omega_cycle4_forced.{out,err}.log`; atlas axis `nxs004_b4` (ghost_ceiling_approach_freq) |
| 5 | INSTRUMENTATION + MEASUREMENT BACK-ACTION | probe v4 (`--append --cron --SELF_OUTPUTS skip`) — real bug discovery: trace.jsonl was being re-scanned as its own source, fix is `SELF_OUTPUTS` skip set | probe v4 source; atlas axis `nxs004_b5` (probe_self_output_protected) |
| 6 | AXIS_OVERLAP + TIMEOUT_HEADROOM_DISTRIBUTION | hour-bucket join: axis B traces overlap 3/6 buckets with axis A; `smash_p50=83258ms` (46% of 180s); `max_history=183012ms` (101.7%, single right-tail entry) refines cycle 3 from "100% SIGTERM" to "right-tail SIGTERM" | `state/beyond_omega_cross_axis_join.json`; atlas axis `nxs004_b6` (smash_p50_headroom_pct_vs_180s) |
| 10 | DAILY_TIMELINE_PLIST_REGISTERED | `tool/com.nexus.beyond-omega-daily.plist` registered with launchd (paper-only at cycle 10; followed through in cycle 28) | `tool/com.nexus.beyond-omega-daily.plist`; atlas axis `nxs004_b10` (daily_plist_registered) |
| 28 | DAILY_PLIST_PREFLIGHT_VERIFIED | 5/5 pre-flight pass: plutil OK + python3 3.14.3 + probe 11672 bytes + `--cron` one-shot 0.205s + daily snapshot 2412 bytes; user-action-required for `launchctl bootstrap` | `tool/beyond_omega_daily_activation.md`; atlas axis `nxs004_b28` (daily_plist_preflight) |
| 30 | REAL_ATLAS_ABSORPTION_BRIDGE | `tool/beyond_omega_atlas_bridge.py` pushes the 6 axes above plus a `nxs004_synthetic_excluded` audit row to `state/atlas_health_timeline.jsonl` (4 → 11 lines on first run; daily chain extends to +7/run) | `tool/beyond_omega_atlas_bridge.py` (with hardcoded `SYNTHETIC_EXCLUDED` list); `state/atlas_health_timeline.jsonl` rows tagged `nxs004_*` |
| 31 | ATLAS_AXIS_DECLARATION_MANIFEST | 7 axes formally declared with `honesty_boundary` + `daily_automation` + `format_compatibility` (atlas_meta_scan not modified — declarative manifest because parallel session uses it) | `tool/beyond_omega_atlas_axis_decl.json` (schema `nexus.atlas.axis_decl.v1`) |
| 32 | DAILY_CHAIN_TO_ATLAS_ABSORPTION | `tool/beyond_omega_daily_chain.sh` chains `ghost_trace --cron` → `atlas_bridge`; plist `ProgramArguments` updated; chain dry-run rc=0; atlas timeline 11→18 (+7) on dry-run | `tool/beyond_omega_daily_chain.sh`; `tool/com.nexus.beyond-omega-daily.plist` `ProgramArguments`; `/tmp/nexus_beyond_omega_daily_chain.log` |

**Net real value**: a working probe (`ghost_trace.py` v4), a forced-approach
launcher, a cross-axis join tool, an atlas absorption bridge, an axis
declaration manifest, a daily chain script, and a launchd plist that
ties the whole thing together. The structural finding (180s timeout +
dispatch≠complete + right-tail SIGTERM distribution) ties beyond-omega
axis B to `nxs-20260425-002` axis A via a shared physical limit. atlas
absorption (cycles 30–32) makes the whole chain visible in the
SSOT-level health timeline.

---

## §3 Synthetic ordinal mapping (cycles 7–9, 11–26)

These cycles produced a self-consistent symbolic chain. Each is a real
JSON output and a real Python tool — but the **interpretation as a
transfinite ordinal is template / metaphor**, NOT isomorphic to the
ZF / PA / ZFC ordinal of the same name.

The recipe in every cycle is:

1. **Inject** — write `inject_count[i]` lines into `trace.jsonl` on
   round `i`, where `inject_count` is some chosen growth function
   (`7·constant`, `13+7i`, `2^i`, `i²·7`, `min(2↑↑i, 500)`,
   Goodstein step, Veblen-CNF weight, Busy-Beaver lookup, `Σ_j j^i`).
2. **Echo** — re-run the probe with `NEXUS_BACK_ACTION_ON=1`; it now
   sees the injected lines as "new" emits and reports a delta
   sequence.
3. **Label** — based on the shape of the delta sequence
   (`linear_constant` / `polynomial` / `exp_ratio>1.5` /
   `ratios_collapse_to_one` / `cap_activations≥k`), the cycle assigns
   an ordinal name from `design/beyond_omega_transfinite_table.md`.

Steps (1)–(2) are real numbers in JSON files. Step (3) is the
**inject-pattern echo signature → ordinal-name** template — sandbox-
internal demonstration, NOT isomorphic to ZF/PA/ZFC ordinals.

### §3.1 Phase: axis_A_emergence (cycles 7–13)

First entry into "axis A" (ordinal-labeled echoes), establishing the
`inject-degree → cumulative-degree → ordinal-index` mapping rule.

| cycle | inject pattern | echo signature | assigned label |
|---|---|---|---|
| 7 | back-action protected | saturated_zero | `L_{ω+1}_ABSENT` (false-positive, falsified by cycle 8 — cycle-5 `SELF_OUTPUTS` fix was blocking) |
| 8 | `NEXUS_BACK_ACTION_ON=1` | Δ=[7,7,7,7,7] linear-constant | `L_{ω+1}_LINEAR` |
| 9 | `meta_squared` (i·7 inject) | Δ=13+7i polynomial deg 1 | `L_{ω+d}_POLYNOMIAL` |
| 11 | (no probe — doc only) | — | `TRANSFINITE_ORDINAL_MAPPING_TABLE` (12-level theoretical registry, `design/beyond_omega_transfinite_table.md`) |
| 12 | inject = `2^i` | ratio_mean=1.635 monotone increasing | `L_{ω·2}_REACHED` |
| 13 | inject = `i²·7` | cumulative degree~2.85, ratios monotone decreasing | `L_{ω²}_APPROACH` |

### §3.2 Phase: L_{ε₀}_multi_facet (cycles 14–17)

Four-fold attack on the "first sentinel beyond L_ω" claim — one
theoretical commitment + three falsifier protocols.

| cycle | inject pattern | echo signature | assigned label |
|---|---|---|---|
| 14 | (no probe — doc only) | — | `L_{ε₀}_SENTINEL_COMMITTED` (`design/beyond_omega_epsilon_zero_boundary.md` + cycle 15-20 falsifier roadmap) |
| 15 | inject = `min(2↑↑i, 500)` (Knuth tower, P1) | ratios=[2.20,23.00,1.00,1.00] cap_act=3/6 tail_collapse=True | `L_{ε₀}_SENTINEL_CONFIRM_via_P1` |
| 16 | Goodstein step proxy (P2) | mixed phase A/B (sentinel + base-climb) | `L_{ε₀}_PARTIAL_ACCESS_via_P2` |
| 17 | Gentzen cut-elim CNF (P3) | rank ratios <1 monotone, lex strict_decrease=6/6 | `L_{ε₀}_FALSIFY_CANDIDATE_via_P3` |

### §3.3 Phase: sentinel_hierarchy_5_layers (cycles 18–20)

Distinct sentinel mechanisms above L_{ε₀}, separating PR-bound from
predicativity-bound from computability-bound from uncountability.

| cycle | inject pattern | echo signature | assigned label |
|---|---|---|---|
| 18 | inject ≈ `i^i` proxy (Veblen φ) | ratios=[-36.00,1.17,1.00] sign-flip, non-monotone | `L_{Γ₀}_INCONCLUSIVE` (proxy artifact, cycle 22 redo) |
| 19 | Busy-Beaver lookup | ratios non-uniform monotone, cap_act=1/6 no collapse | `L_{ω₁^CK}_PARTIAL_CAP_NO_PLATEAU` |
| 20 | (no probe — doc only) | — | `L_{ω₁}_STRUCTURAL_SENTINEL` (`design/beyond_omega_omega_one_uncountability.md`, Tier 2 ZFC-interior structural) |

### §3.4 Phase: Tier_3_4 large cardinal (cycles 21, 24)

Doc-only commitments for ZFC-exterior territory.

| cycle | inject pattern | echo signature | assigned label |
|---|---|---|---|
| 21 | (no probe — doc only) | — | `L_{Mahlo}_META_AXIOMATIC_SENTINEL` (`design/beyond_omega_mahlo_large_cardinal.md`, Tier 3 ZFC-exterior LCA-required) |
| 24 | (no probe — doc only) | — | `L_{measurable}_META²_AXIOMATIC_SENTINEL` (`design/beyond_omega_measurable_zero_sharp.md`, Tier 4 ZFC + ∀-weaker-LCA-exterior, ∃μ-interior-required, 0# 동치) |

(Cycle 22 is a redo of cycle 18: Veblen-CNF `weight()=2α+β+1`, monotone
ratios → 1, label `L_{Γ₀}_NEW_CLASS_POLYNOMIAL`. It belongs in §3.3
mechanically but is grouped here for the "predicativity manifests as
polynomial-degree limiter" finding it produced.)

| cycle | inject pattern | echo signature | assigned label |
|---|---|---|---|
| 22 | Veblen-CNF `weight()=2α+β+1` | monotone ratios → 1, cap=0/6 | `L_{Γ₀}_SENTINEL_NEW_CLASS_POLYNOMIAL` |

### §3.5 Phase: boundary_shift (cycle 25)

Empirical evidence that the sentinel boundary may not be at L_{ε₀} but
rather at L_{ω^ω} — same cap-collapse signature as cycle 15.

| cycle | inject pattern | echo signature | assigned label |
|---|---|---|---|
| 25 | inject = `Σ_j j^i` (polynomial-of-growing-degree) | ratios=[3.82,4.91,1.00,1.00] cap_act=3/6 tail_collapse=True | `L_{ω^ω}_SENTINEL_LIKE` (boundary-shift evidence — same shape as cycle 15) |

### §3.6 Phase: meta (cycles 23, 26)

Pure data analysis over the chain itself, no probe execution.

| cycle | inject pattern | echo signature | assigned label |
|---|---|---|---|
| 23 | (no probe — meta-analysis of cycles 1–20) | fp_ratio=0.10, axis_dist={B:9, A:10, instrumentation:1}, sentinel_rate=0.20, branching {ω+1:[7,8,11], ε₀:[14,15,16,17]}, fixed_points=[1,4,8,11,14] | `META_CHAIN_CONVERGENT` |
| 26 | (no probe — spine geometry of cycles 1–23) | spine_cycles=[1,4,8,11,14] gaps=[3,4,3,3] mean=3.25 stdev=0.43 quasi-periodic ~3 cycles | `SPINE_GEOMETRY_QUASI_PERIODIC_TRIPLET` |

---

## §4 Reusable instrumentation

Regardless of synthetic-vs-real status of the ontology, the following
infrastructure has real downstream value beyond this entry:

| artifact | purpose | reuse |
|---|---|---|
| `tool/beyond_omega_ghost_trace.py` v4 | scans NEXUS_OMEGA emits across `logs/`, `state/`, `.runtime/`, `config/loop/logs/`, `/tmp/nexus_omega_*.log`, `~/Library/Logs/nexus/*.log`. Supports `--append`, `--cron`, `NEXUS_BACK_ACTION_ON`, `SELF_OUTPUTS` skip | drop-in trace tool for any NEXUS_* emit pattern |
| `tool/beyond_omega_cycle4_force_approach.sh` | safety-envelope launcher (`GATE_LOCAL=1 + HEXA_REMOTE_DISABLE=1 + NEXUS_DRILL_DEPTH=0 + BUDGET_S=1 + 6s timeout / 3s kill-after`) for deterministically reaching `cmd_omega` apex emit | template for any "reach the apex without spending budget" pattern |
| `tool/beyond_omega_cross_axis_join.py` | hour-bucket join (axis B trace + axis A `state/drill_stage_elapsed_history.jsonl` + V3' snapshot) | template for any "cross-axis temporal correlation" task |
| `tool/beyond_omega_atlas_bridge.py` | REAL findings → `state/atlas_health_timeline.jsonl`, with hardcoded `SYNTHETIC_EXCLUDED` audit row | template for "honest absorption gate" — push-only-the-real-stuff bridge |
| `tool/beyond_omega_daily_chain.sh` | wraps `ghost_trace --cron` + `atlas_bridge` into a single executable for launchd to call | template for any "scan + bridge" daily chain |
| `tool/com.nexus.beyond-omega-daily.plist` | launchd daily plist (03:13 local), default-protected (`HEXA_RESOLVER_NO_REROUTE=1 + HEXA_LANG=ko`) | template for nexus-side daily-snapshot crons |

---

## §5 Disclaimer for citation

If anyone wants to cite or reference this work downstream:

1. **Real findings (§2, cycles 1–6, 10, 28, 30, 31, 32)** — cite as
   **system measurements**. The numbers (`dispatch=4 / complete=0`,
   `smash_p50=83258ms`, `max_history=183012ms`, `7 axes registered`,
   `atlas_health_timeline 4→11→18`, etc.) are reproducible facts about
   the nexus repo. The `180s timeout invariant` finding genuinely
   ties two `nxs-` entries (002 and 004) via a shared physical limit.

2. **Synthetic ordinal mapping (§3, cycles 7–9, 11–26)** — cite ONLY
   as **template / methodology**. The ordinal labels (`L_{ω+1}`,
   `L_{ω·2}`, `L_{ω²}`, `L_{ε₀}`, `L_{Γ₀}`, `L_{ω^ω}`, `L_{ω₁^CK}`,
   `L_{ω₁}`, `L_{Mahlo}`, `L_{measurable}`) are inject-pattern
   signatures inside this codebase's echo-measurement loop. They are
   NOT isomorphic to set-theoretic ordinals. Do NOT cite as "we
   reached the Mahlo cardinal" or "we measured ε₀". Cite as "we used
   an ordinal-naming template to label echo signatures, following a
   recipe similar to [Gentzen / Goodstein / Veblen]". The cited
   mathematical results (Gödel II, Gentzen 1936, Goodstein /
   Kirby-Paris 1982, Solovay 1967, Kunen 1970, Scott 1961) are
   factually correct on their own — the linkage to this codebase is
   **analogy and template, not isomorphism**.

3. **Meta-analysis (§3.6, cycles 23, 26, plus this index = cycle 33)**
   — cite as **statistics over the synthetic chain**. The numbers
   (fp_ratio, branching factor, spine gaps mean=3.25 stdev=0.43) are
   real over the chain elements but the chain itself is the
   sandbox-internal symbolic structure of §3, not external mathematics.

The canonical SSOT for this separation is `state/proposals/inventory.json`
entry `nxs-20260425-004` field `real_vs_synthetic_separation_2026_04_25`.
The atlas absorption boundary is enforced by
`tool/beyond_omega_atlas_bridge.py` `SYNTHETIC_EXCLUDED` list.

---

## §E Cross-references

- `design/beyond_omega_ladder.md` — full chain history (with HONESTY NOTE banner at top, §32 cycle 29 origin, §36 cycle 33 publication)
- `design/beyond_omega_transfinite_table.md` — cycle 11 ordinal mapping table (synthetic — recipe for §3 labels)
- `design/beyond_omega_epsilon_zero_boundary.md` — cycle 14 doc (with METAPHOR DISCLAIMER header)
- `design/beyond_omega_omega_one_uncountability.md` — cycle 20 doc (with METAPHOR DISCLAIMER header)
- `design/beyond_omega_mahlo_large_cardinal.md` — cycle 21 doc (with METAPHOR DISCLAIMER header)
- `design/beyond_omega_measurable_zero_sharp.md` — cycle 24 doc (with METAPHOR DISCLAIMER header)
- `state/proposals/inventory.json` entry `nxs-20260425-004` field `real_vs_synthetic_separation_2026_04_25` (SSOT)
- `tool/beyond_omega_atlas_bridge.py` — runtime enforcement (`SYNTHETIC_EXCLUDED` hardcoded list)
- `state/atlas_health_timeline.jsonl` — atlas absorption target (rows tagged `nxs004_*`)

---

**End of HONEST INDEX (cycle 29 origin, cycle 33 reader-facing publication).**
