# INDEX — design/hexa_sim/ file-by-file

> Per-file table for the hexa_sim corpus. See [`README.md`](README.md) for navigation by topic.
> Future: auto-regeneratable via a `tool/atlas_witness_registry.sh`-style script.

**Generated**: 2026-04-26 · **Total files**: 39 (excluding README/INDEX)

| File | Type | Date | Bytes | Description |
|------|------|------|-------|-------------|
| `2026-04-25_bridge_tool_jackpot_omega_cycle.json` | witness | 2026-04-25 | 16089 | External-API bridge pattern abstraction (26 axes → Tier-1/2/3) |
| `2026-04-25_falsifier_integration_omega_cycle.json` | witness | 2026-04-25 | 13221 | Falsifier integration design (12 axes; precedes hexa_sim_falsifier impl) |
| `2026-04-25_omega_cycle_implementation.json` | witness | 2026-04-25 | 10045 | First ω-cycle: 10-axis verify_grid impl, byte-eq fixpoint |
| `2026-04-26_atlas_ingest_a2_self_path_strip_omega_cycle.json` | witness | 2026-04-26 | 20476 | a2 axis follow-through (escape-hatch flag, 3-path falsifier corpus) |
| `2026-04-26_atlas_ingest_arg_fix_omega_cycle.json` | witness | 2026-04-26 | 14545 | Runner-detection + self-path-strip arg fix |
| `2026-04-26_atlas_ingest_omega_cycle.json` | witness | 2026-04-26 | 7663 | Bridge → atlas auto-ingest design |
| `2026-04-26_atlas_ingest_tool_evolution_omega_cycle.json` | witness | 2026-04-26 | 10163 | Single-domain → all-Ω-cycle absorber evolution path |
| `2026-04-26_atlas_semantic_gap_audit.md` | audit | 2026-04-26 | 8065 | Notation A/B sigma/tau mismatch sweep (21 MISMATCH baseline) |
| `2026-04-26_atlas_semantic_gap_audit.py` | script | 2026-04-26 | 18121 | Audit driver — invoked by F49 sentinel |
| `2026-04-26_bridge_health_check.md` | audit | 2026-04-26 | 9614 | 16 external-API bridges health (curl/payload-size) |
| `2026-04-26_cross_bridge_correlation_hunt.md` | audit | 2026-04-26 | 13821 | F10-pattern replication across 14 numeric bridges |
| `2026-04-26_cross_repo_absorption_refresh_omega_cycle.json` | witness | 2026-04-26 | 9423 | 24h-delta refresh of anima/hexa-lang/n6-arch shards |
| `2026-04-26_cross_shard_dedup_audit.md` | audit | 2026-04-26 | 7996 | Cross-shard atlas dedup (skip → preserve policy) |
| `2026-04-26_dedup_strategy_evolution_omega_cycle.json` | witness | 2026-04-26 | 8878 | Dedup: skip → preserve edge/witness/cross-source |
| `2026-04-26_dockerfile_curl_patch_omega_cycle.json` | witness | 2026-04-26 | 6711 | hexa-runner curl/wget/ca-cert patch (7/16 unblocked) |
| `2026-04-26_F19_F23_falsifier_expansion_omega_cycle.json` | witness | 2026-04-26 | 5511 | i11 auto-spawn → F19–F23 + Mertens labeling discovery |
| `2026-04-26_F23_resolution_omega_cycle.json` | witness | 2026-04-26 | 9568 | F23 vacuous-PASS sealed (ec=0+non-empty stdout double-guard) |
| `2026-04-26_F45_decision.md` | decision | 2026-04-26 | 8142 | F45 declined (3.5% triplet collapses to doublet) |
| `2026-04-26_F46_F49_semantic_guards_omega_cycle.json` | witness | 2026-04-26 | 8137 | F46–F49 atlas semantic-gap guards + convention doc |
| `2026-04-26_falsifier_health_check.md` | audit | 2026-04-26 | 6243 | Falsifier registry health (per-entry pass/HIT/drift) |
| `2026-04-26_health_check_productionization_omega_cycle.json` | witness | 2026-04-26 | 7763 | 3 health-checks → bash + cron + nexus CLI |
| `2026-04-26_i11_cmd_hardening_omega_cycle.json` | witness | 2026-04-26 | 5251 | i11 PRESENCE → VALUE+DOMAIN+GRADE anchor hardening |
| `2026-04-26_improvement_ideas_omega_cycle.json` | witness | 2026-04-26 | 9683 | Aggregate post-session improvement surface |
| `2026-04-26_oeis_gw_oom_resolution_omega_cycle.json` | witness | 2026-04-26 | 7863 | oeis_live + gw OOM → shell payload trim (16/16 bridges) |
| `2026-04-26_phase4_atlas_dsl_v2_and_lens_injection_omega_cycle.json` | witness | 2026-04-26 | 15843 | Atlas DSL v2 (M/T/compound) + lens-orchestrator injection |
| `2026-04-26_uniprot_registry_2fix_omega_cycle.json` | witness | 2026-04-26 | 7556 | uniprot sentinel-classification + axes-as-number 2-fix |
| `cross_repo_dashboard.md` | dashboard | 2026-04-26 | 1499 | Cross-repo atlas dashboard (Tier-2 i13 generated) |
| `F13_F22_candidate_review.md` | review | 2026-04-26 | 7248 | F13–F22 + F23 candidate triage |
| `F24_F30_candidate_review.md` | review | 2026-04-26 | 14675 | F24–F30 chemistry / biology candidate triage |
| `F31_F37_candidate_review.md` | review | 2026-04-26 | 21644 | F31–F37 cross-domain candidate triage |
| `F38_F44_candidate_review.md` | review | 2026-04-26 | 19471 | F38–F44 L-prefix bridge candidate triage |
| `falsifier_history.jsonl` | data | 2026-04-25 | 2960 | Append-only chained ledger (prev_hash + current_hash) |
| `falsifiers.jsonl` | data | 2026-04-26 | 45026 | Falsifier registry SSOT — 42 entries (F1–F12, F19–F44, F46–F49) |
| `hexa_lang_atlas_ssot_decision.md` | decision | 2026-04-26 | 3949 | hexa-lang atlas SSOT — nexus single origin (4/5 OPT-A) |
| `M3_true_definition_audit.md` | decision | 2026-04-26 | 9604 | M3 = mersenne(6) = 7 (not mertens M(6) = -1) |
| `NEXT_SESSION_HANDOFF.md` | session | 2026-04-25 | 9451 | Handoff checklist for next session |
| `SESSION_FINAL_REPORT.md` | session | 2026-04-26 | 7260 | What-happened companion to NEXT_SESSION_HANDOFF |
| `SYNTHESIS_2026-04-26.md` | synthesis | 2026-04-25 | 36580 | Paper-grade n=6 synthesis (HEXA-SIM external-verification infra) |

## Counts by category

| Category | Count |
|----------|-------|
| witness (`*_omega_cycle.json`) | 17 |
| audit (`*_audit.md` / `*_check.md` / correlation hunt) | 5 |
| candidate review (`F*_F*_candidate_review.md`) | 4 |
| decision (`*_decision.md` + M3 audit) | 3 |
| session handoff (`NEXT_SESSION_HANDOFF` + `SESSION_FINAL_REPORT`) | 2 |
| synthesis (`SYNTHESIS_*.md`) | 1 |
| dashboard (`cross_repo_dashboard.md`) | 1 |
| script (`*_audit.py`) | 1 |
| data (`*.jsonl`) | 2 |
| navigation (`README.md` + `INDEX.md`) | 2 |
| **Total** | **38 + 2 nav = 40** |
