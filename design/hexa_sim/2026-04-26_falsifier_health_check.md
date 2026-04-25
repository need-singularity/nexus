# Falsifier Registry Health Check — 2026-04-26 Ω-cycle

- **Registry**: `/Users/ghost/core/nexus/design/hexa_sim/falsifiers.jsonl` (17 entries: F1–F12 + F19–F23)
- **Runner**: bash-direct `eval` of each `cmd` field (bypassing `hexa_sim_falsifier.hexa` for speed); cmd extracted via `python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["cmd"])'`
- **Runtime gate**: `bash hexa_runtime_check.sh` → `__HEXA_RUNTIME_CHECK__ PASS stage=5 reason="hexa runtime healthy (wrapper + real + exec + hello)"`
- **Checker**: `omega-cycle-2026-04-26`
- **UTC ts**: `2026-04-25T16:11:51Z` (date -u, machine clock vs. content-day 2026-04-26)

## Executive summary

| metric | value |
|---|---|
| total falsifiers | **17** |
| CLEAN (passed sentinel + ec=0) | **17** |
| HIT (no sentinel, ec=0) | 0 |
| ERROR (ec≠0) | 0 |
| total wall time | **12 938 ms** |
| latency outliers (>5 s) | **1** (F12 = 6709 ms) |
| network-dependent at runtime | **2** (F9 horizons, F11 cmb-Planck — both have offline fallback) |

All 17 falsifiers are CLEAN.  No urgent action required.

## Result table

| id  | slug                                         | status | ec | duration_ms | network        | atlas line | notes |
|-----|----------------------------------------------|--------|----|-------------|----------------|-----------:|-------|
| F1  | constants-drift                              | CLEAN  | 0  | 283         | OFFLINE-OK     | 1          | sigma=12 tau=4 phi=2 sopfr=5 J2=24 |
| F2  | alpha-drift                                  | CLEAN  | 0  | 211         | OFFLINE-OK     | 2          | alpha^-1=137 integer identity intact |
| F3  | byte-eq-seal-drift                           | CLEAN  | 0  | 414         | OFFLINE-OK     | 3          | two consecutive `--json` runs byte-equal |
| F4  | oeis-drift                                   | CLEAN  | 0  | 207         | OFFLINE-OK     | 4          | A000203/A000005/A000010 match for n=1..6 |
| F5  | counter-overfit                              | CLEAN  | 0  | 211         | OFFLINE-OK     | 5          | h/e/G mantissae remain unrelated to sigma=12 |
| F6  | nxs002-cycle10-q4-qrng-er-null               | CLEAN  | 0  | 5           | OFFLINE-OK     | 6          | abstraction_ceiling.md grep |
| F7  | nxs002-cycle10-quantum-topology-hurts        | CLEAN  | 0  | 3           | OFFLINE-OK     | 7          | abstraction_ceiling.md grep |
| F8  | nxs002-cycle10-lsr-orthogonal-composite      | CLEAN  | 0  | 3           | OFFLINE-OK     | 8          | abstraction_ceiling.md grep |
| F9  | tp8-mars-2g-4d-broken                        | CLEAN  | 0  | 1069        | NETWORK (JPL)  | 9          | horizons_bridge fetches; falls back if offline. deviation_pct=-24.10 |
| F10 | cross-bridge-fractional-gap-resonance        | CLEAN  | 0  | 422         | OFFLINE-OK     | 10         | cmb+codata `--selftest` (no fetch) |
| F11 | hubble-tension-persists                      | CLEAN  | 0  | 714         | NETWORK (Wiki) | 11         | cmb_planck_bridge default does curl; H0=67.36 (also offline default) |
| F12 | triple-source-n6-anchor-corroboration        | CLEAN  | 0  | **6709**    | OFFLINE-OK     | 12         | three `--selftest` chained (codata+oeis_live+wikipedia) — outlier |
| F19 | mu-anchor                                    | CLEAN  | 0  | 3           | OFFLINE-OK     | 13         | atlas.n6 grep |
| F20 | mersenne-anchor                              | CLEAN  | 0  | 3           | OFFLINE-OK     | 14         | atlas.n6 grep |
| F21 | sigma-sq-anchor                              | CLEAN  | 0  | 3           | OFFLINE-OK     | 15         | atlas.n6 grep |
| F22 | phi-tau-anchor                               | CLEAN  | 0  | 3           | OFFLINE-OK     | 16         | atlas.n6 grep |
| F23 | atlas-dsl-v2-layer4-vacuous                  | CLEAN  | 0  | 1871        | OFFLINE-OK     | 17         | atlas_dsl_v2_regression.sh layer 4 sample 100 → NON_EMPTY |

## Per-failure diagnostic

None. All 17 CLEAN.

(Note: an earlier extraction pass produced spurious `unknown arg PASS` errors on F1/F2/F4/F5 because a sed-based regex greedily consumed past the cmd field. Switched to `python3 -c 'json.loads(...)'` extraction; all subsequent runs CLEAN. The registry file itself is intact and was never modified.)

## Network-dependent subset (cron-scheduling note)

Only **2 of 17** falsifiers attempt outbound HTTP at runtime; both still produce a verdict offline (hardcoded fallbacks, so a network outage does NOT flip CLEAN→HIT):

- **F9 tp8-mars-2g-4d-broken** — `horizons_bridge.hexa` (no `--no-fetch`) → `https://ssd.jpl.nasa.gov/api/horizons.api` (curl --max-time 30)
- **F11 hubble-tension-persists** — `cmb_planck_bridge.hexa` (no `--no-fetch`) → `https://en.wikipedia.org/wiki/Planck_(spacecraft)` (curl --max-time 15, 600 KB)

If a future cron job needs strict offline determinism, append `--no-fetch` to the F9 and F11 cmds. Today's run did NOT need that — both came back fast and CLEAN.

The remaining 15 falsifiers (F1–F8, F10, F12, F19–F23) are pure local: hexa simulator axes, file greps, or `--selftest` paths that explicitly skip fetch. All cron-friendly without modification.

## Latency outliers (>5 s threshold)

| id  | duration_ms | reason |
|-----|------------:|--------|
| F12 | 6709        | three `--selftest` invocations chained: `codata_bridge` + `oeis_live_bridge` + `wikipedia_summary_bridge` — each spins a fresh hexa interpreter (~2 s startup × 3) |

Suggested mitigation (not urgent): teach `hexa_sim_falsifier.hexa` to batch-load these three bridges in one interpreter session, or split F12 into F12a/F12b/F12c so cron parallelism amortises startup.

## Recommended action

**No urgent action.** Registry is healthy. Optional cleanup tickets:

1. (P3) Append `--no-fetch` to F9 / F11 cmds when net-isolated CI is desired (current curl-with-fallback is fine for ad-hoc).
2. (P3) Consider splitting F12 (6.7 s) for better cron parallelism — only relevant once total registry exceeds ~30 entries.

## Provenance

- Runner script (ephemeral, not committed): `/tmp/falsifier_health_runner.sh`
- Raw TSV results: `/tmp/falsifier_health_results.tsv`
- Timeline append: `/Users/ghost/core/nexus/state/atlas_health_timeline.jsonl`
