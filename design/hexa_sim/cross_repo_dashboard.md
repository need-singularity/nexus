# Cross-Repo Atlas Dashboard

> generated: `2026-04-26T08:05Z` (UTC) — Honesty-triad ω-cycle refresh
> tool: `tool/atlas_cross_repo_dashboard.sh` (Tier-2 i13)
> origin: `2026-04-26_honesty_triad_refresh_omega_cycle.json`

## Repo health table (ω-cycle re-run + direct verification)

| Repo | Atlas | Lines | Entries | Last Commit (atlas) | Honesty 5/5 | Δ vs prior |
|------|-------|------:|--------:|---------------------|------------:|------------|
| **nexus** | `n6/atlas.n6` | 21850 | 9624 | `d84a0601` 2026-04-26 01:09 | 5/5 | unchanged |
| **n6-architecture** | `atlas/atlas.n6` | 21800 | 9612 | `98a23750` 2026-04-25 12:54 | 5/5 | unchanged |
| **anima** | `n6/atlas.n6` (symlink → n6-arch) | 21800 | 9612 | (symlink target) | 5/5 | unchanged |
| **hexa-lang** | (no atlas SSOT) | 0 | 0 | — | 4/5 | unchanged (OPT-A ceiling) |

**Aggregate**: repos=4, atlas_lines=65450, atlas_facts=28848, **honesty_pass=3/4** (unchanged vs prior reading 2026-04-25T15:13).

## 5-precondition × 4-repo matrix (direct verification)

| Precondition | nexus | n6-arch | anima | hexa-lang |
|--------------|:-----:|:-------:|:-----:|:---------:|
| (a) git-tracked SSOT | PASS (`.git/HEAD` + `n6/atlas.n6` ls-files) | PASS (`atlas/atlas.n6` ls-files) | PASS (`n6/atlas.n6` symlink ls-files) | PASS (`.git/HEAD`) |
| (b) design corpus (md ≥1) | PASS (design 61, docs 51, papers 10, reports 1) | PASS (docs 7, papers 176, reports 423) | PASS (docs 959) | PASS (docs 16) |
| (c) tool ecosystem (≥3 files) | PASS (tool 3662, scripts 77, bin 35) | PASS (tool 29, scripts 24, bin 3) | PASS (tool 337, scripts 69, bin 15) | PASS (tool 293, bin 7) |
| (d) atlas SSOT exists | PASS (`n6/atlas.n6` 21850 L) | PASS (`atlas/atlas.n6` 21800 L) | PASS (symlink → n6-arch 21800 L) | **FAIL** (none of `n6/atlas.n6`, `atlas/atlas.n6`, `atlas.n6`) |
| (e) LLM agents indicator | PASS (`.claude/agents/`) | PASS (`.claude/agents/`) | PASS (`CLAUDE.md`) | PASS (`.claude/agents/`) |
| **TOTAL** | **5/5** | **5/5** | **5/5** | **4/5** |

## Per-precondition: which repos satisfy

- (a) git-tracked SSOT: **all 4** (nexus, n6-arch, anima, hexa-lang)
- (b) design corpus: **all 4**
- (c) tool ecosystem: **all 4**
- (d) atlas SSOT: **3** (nexus, n6-arch, anima — anima via git-tracked symlink)
- (e) LLM agents indicator: **all 4**

## Dashboard-vs-reality drift

| Finding | Status |
|---------|--------|
| Dashboard repo health table accuracy | Accurate. All 4 PASS counts match direct verification. |
| Dashboard "Last Commit" blank for anima | Cosmetic gap. anima `n6/atlas.n6` is a symlink → `~/core/n6-architecture/atlas/atlas.n6`; `git log -- n6/atlas.n6` from inside anima returns empty because the symlink target is in another repo. The aggregate count is unaffected; only the display row is empty. |
| Dashboard precondition (a) check | Only checks `.git/HEAD` not actual git ls-files of the SSOT. All 4 happen to PASS direct ls-files verification anyway, so no false-positive emerges this cycle. Latent risk: a repo with `.git/HEAD` but un-tracked SSOT would falsely PASS (a). |
| 24h activity since prior reading | nexus 246 commits, anima 146, n6-arch 29, hexa-lang 41 — high churn but no precondition flips. |
| New atlas in hexa-lang? | No. `find -name '*.n6' -maxdepth 3` returns 0 hits. OPT-A architectural ceiling holds. |

## hexa-lang ceiling reconfirm (OPT-A)

Per `design/hexa_sim/hexa_lang_atlas_ssot_decision.md`, OPT-A (no atlas SSOT in hexa-lang; toolchain repo by design) was selected as the architectural decision. Reconfirmed this cycle:

- 41 commits in last 24h, none introduced an atlas.n6 file at any candidate path
- `state/` directory contains telemetry JSONs (hx_*.json, convergence.jsonl, cross_repo_links.jsonl) but none are atlas-SSOT-shaped
- **Ceiling: 4/5 PARTIAL stays correct.** Honesty triad portability remains 3/4 by design.

## Cross-repo defense-doc scan (analogous to nexus's security posture)

Searched `find -iname 'SECURITY*'` and `'THREAT*'` across the 4 repos:

| Repo | Defense artifacts found |
|------|-------------------------|
| nexus | `tool/security_scan.hexa` (Hexa scanner); no top-level `SECURITY.md` / `SECURITY_AUDIT.md` |
| n6-architecture | (none) |
| anima | `state/security_roi_audit.json` (ROI-shaped audit state) |
| hexa-lang | `doc/security/os-level-enforcement-limits.md` (raw 66 enforcement-layer doc, 10.7 KB) |

**Cross-repo alignment opportunity**: Each repo has a different defense expression — nexus tool-shaped (scanner), anima state-shaped (audit JSON), hexa-lang doc-shaped (enforcement limits). A common `SECURITY.md` skeleton (or atlas-tracked `@F security_*` facts) could give the dashboard a 6th precondition (f) "defense surface declared" that the triad currently underweights. This is **not** a regression — purely an ω-extension candidate.

## Improvements / next ω-cycles

- (latent) Tighten precondition (a) in `tool/atlas_cross_repo_dashboard.sh` to also `git ls-files | grep -q <SSOT>` — prevents future false-positive when SSOT is on disk but un-tracked.
- (cosmetic) Dashboard "Last Commit" for symlink SSOTs: dereference symlink before `git log` so anima row shows the n6-arch target's commit.
- (extension) Optional 6th precondition (f) "defense doc/tool/atlas-fact" — would give a finer security-readiness signal.

---

__ATLAS_CROSS_REPO_DASHBOARD__ repos=4 total_atlas_lines=65450 total_facts=28848 honesty_pass=3/4 ceiling=hexa-lang@4/5(OPT-A) drift=none
