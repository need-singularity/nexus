# Nexus Honesty Triad

> Deployed 2026-04-25 from n6-architecture audit at:
> `~/core/n6-architecture/reports/sessions/omega-audit-nexus-honesty-triad-portability-2026-04-25.md`

## Three constraints

### (1) Promotion-counter banner
At session start, record `nxs_promotion_count: <N0>` (read from `state/proposals/inventory.json` length or [10*] count). At session end, assert `nxs_promotion_count: <N1> unchanged` (i.e., N1 == N0) UNLESS explicit promotion via atlas-agent occurred. The banner is a first-line filter against premature promotion.

Form: `nxs_promotion_count: N/N0 unchanged` in session report front-matter (analogous to n6's `millennium_resolved: 0/7 unchanged`).

### (2) Write-barrier
Session/research agents must NOT modify these paths:
- `~/core/nexus/n6/atlas.blowup.jsonl`
- `~/core/nexus/state/proposals/inventory.json`
- `~/core/nexus/state/atlas_health_timeline.jsonl`
- `~/core/nexus/state/agent_lock_ledger.jsonl`
- `~/core/nexus/lenses/omega_state_space_lens.hexa`
- `~/core/nexus/CLAUDE.md` (when active) and `~/core/nexus/project-claude/nexus.md`

Explicitly NOT in barrier (mutable session output):
- `state/` other than the listed files
- `tool/nxs_002_composite.py` (tool patches require this)
- `design/` (research notes)
- `reports/` (when created — currently absent)

Privileged-path-only: atlas-agent / growth-agent. Other agents must use proposal-inbox or inventory-add tooling.

### (3) No-fabrication guard
- DO NOT FABRICATE numerical values, file paths, tool names, citations, or measurement results.
- When data/tool is missing, return UNKNOWN / INCONCLUSIVE / TIMEOUT with diagnostic.
- Verified by past near-violations NV-1 (cycle-43 self-disclosure 6772aede) and NV-2 (cycle 47-51 root-cause chain).

## Use in agent prompts

Each session-agent prompt should include this preset (3 lines):

```
- Honesty: nxs_promotion_count unchanged this session.
- Write-barrier: do NOT modify atlas/state/inventory paths listed in design/honesty_triad.md. Session reports only.
- No-fabrication: UNKNOWN/INCONCLUSIVE > invented values. If tool/data missing, stop with diagnostic.
```

## Audit lineage
This triad is verified by 3-of-3 KEEP_AS_IS audits in n6-architecture (2026-04-25):
- `reports/sessions/omega-audit-constraint-honesty-counter-2026-04-25.md`
- `reports/sessions/omega-audit-constraint-write-barrier-2026-04-25.md`
- `reports/sessions/omega-audit-constraint-no-fabrication-2026-04-25.md`

Plus nexus-side cross-repo audit verified KEEP/KEEP_BUT_ADAPT verdicts at:
- `reports/sessions/omega-audit-nexus-honesty-triad-portability-2026-04-25.md`
