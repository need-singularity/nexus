# Bridge Health Check — Ω-cycle 2026-04-26

**Scope**: 16 external API bridge tools registered under `nexus hexa-sim bridge` dispatch.
**Checker**: omega-cycle-2026-04-26 (analogous to falsifier health pattern, see `design/hexa_sim/2026-04-26_falsifier_health_check.md`).
**Runtime**: hexa wrapper → docker hard-landing (`hexa-runner:latest`, cpus=4 mem=4g, container `hexa-exec`). All Hetzner remotes blacklisted (PSI/RAM gated), so every invocation lands in the local container.

## Executive Summary

| Metric | Count |
|--------|-------|
| Total bridges | 16 |
| PASS (rc=0)            | 9 |
| FAIL — live-only, no fallback (rc=1 or 2)  | 6 |
| FAIL — fallback path also broken (rc=2)    | 1 |
| OFFLINE-FALLBACK auto-engaged (PASS)       | 0 (none auto-detect; opt-in via `--no-fetch`) |
| Total wall time         | 22 s (16 sequential selftests, ~1.4 s avg) |

**Root cause of all 7 FAIL**: the `hexa-runner:latest` docker image used by the Mac→docker hard-landing has **no `curl` binary** (`sh: 1: curl: not found`). Every bridge whose live path calls `exec("curl ...")` returns empty body and either fails outright or exposes a fallback gap.

When invoked with `--no-fetch`, the 9 bridges that have a hardcoded fallback all PASS; uniprot also PASSes (it auto-fell-back to its hardcoded P68871 anchor when curl returned empty). The 6 truly network-only bridges (oeis, gw, arxiv, simbad, wikipedia, openalex) have **zero offline path**.

## Bridge Status Table

| bridge | selftest_path | status | duration_s | network_class | notes |
|--------|---------------|--------|-----------:|---------------|-------|
| codata           | tool/codata_bridge.hexa            | PASS | 1 | has-fallback     | live-fetch failed silently, fell back to CODATA 2022 hardcoded α⁻¹=137.035999177; 8 checks pass |
| oeis             | tool/oeis_live_bridge.hexa         | FAIL | 1 | requires-live    | no `--no-fetch`; A000396/203/005/010 all return `fetch_empty_or_parse_failed` |
| gw               | tool/gw_observatory_bridge.hexa    | FAIL | 0 | requires-live    | no `--no-fetch`; events_total=0, latest=NONE |
| horizons         | tool/horizons_bridge.hexa          | PASS | 1 | has-fallback     | JPL Horizons fallback path engaged; all checks pass |
| arxiv            | tool/arxiv_realtime_bridge.hexa    | FAIL | 1 | requires-live    | no `--no-fetch`; 0 entries fetched for cat=gr-qc |
| cmb              | tool/cmb_planck_bridge.hexa        | PASS | 0 | has-fallback     | 11 unit checks (live skip ok); Planck 2018 hardcoded fallback intact |
| nanograv         | tool/nanograv_pulsar_bridge.hexa   | PASS | 5 | has-fallback     | 8 checks; strain/sigma/gamma fmt + n=6 binding |
| simbad           | tool/simbad_bridge.hexa            | FAIL | 4 | requires-live    | no `--no-fetch`; Sirius/M31/Sgr A\*/Polaris all `empty_response` |
| icecube          | tool/icecube_neutrino_bridge.hexa  | PASS | 4 | has-fallback     | 9 checks; PMNS dual-anchor + Glashow + fallback events |
| nist_atomic      | tool/nist_atomic_bridge.hexa       | PASS | 1 | has-fallback     | 9 checks across 6 elements |
| wikipedia        | tool/wikipedia_summary_bridge.hexa | FAIL | 0 | requires-live    | no `--no-fetch`; all 4 refs `fetch_empty`, perfect_extract_len=0 |
| openalex         | tool/openalex_bridge.hexa          | FAIL | 1 | requires-live    | no `--no-fetch`; "perfect number" returned 0 entries |
| gaia             | tool/gaia_bridge.hexa              | PASS | 1 | has-fallback     | 5 fallback stars verified (Vega/Sirius/Polaris/Proxima/Betelgeuse) |
| lhc              | tool/lhc_opendata_bridge.hexa      | PASS | 1 | has-fallback     | 14 unit checks; live SKIPPED, hardcoded reference verified |
| pubchem          | tool/pubchem_bridge.hexa           | PASS | 0 | has-fallback     | 9 checks across 6 compounds + 4 n6 carbon anchors |
| uniprot          | tool/uniprot_bridge.hexa           | FAIL | 1 | has-fallback (broken) | default selftest fails (`fails=fetch_empty_or_short`); under `--no-fetch` PASSes — sentinel emits FAIL when fetch is attempted-and-empty even though fallback data is loaded |

## Per-Failure Diagnostics

### F1. oeis_live_bridge — `__OEIS_LIVE_BRIDGE__ FAIL`
- **Symptom**: `sh: 1: curl: not found` repeated for every OEIS reference (A000396, A000203, A000005, A000010); all parse as `fetch_empty_or_parse_failed`.
- **Cause**: container has no curl; bridge has no offline mode.
- **Suggested fix**:
  1. Add `RUN apt-get update && apt-get install -y curl` to the `hexa-runner` Dockerfile (single-line fix benefits **all** bridges).
  2. As a forward-spec, add `--no-fetch` mode that emits a hardcoded reference table for the 4 sequence anchors used in selftest.

### F2. gw_observatory_bridge — `__GW_BRIDGE__ FAIL events_total=0`
- **Symptom**: 0-byte fetch from GWOSC.
- **Cause**: same `curl: not found`; bridge has no offline mode.
- **Suggested fix**: same Dockerfile patch + add `--no-fetch` returning the GW150914/GW170817 baseline events.

### F3. arxiv_realtime_bridge — `FAIL: 0 entries fetched for cat=gr-qc`
- **Symptom**: bridge already prints its own remediation hint: *"verify connectivity (curl -s --max-time 30 'http://export.arxiv.org/api/query?...') or retry after 3s"*.
- **Cause**: same `curl: not found`.
- **Suggested fix**: same Dockerfile patch. (No fallback by design — arxiv freshness is the point.)

### F4. simbad_bridge — `FAIL: Sirius:empty_response, M31:empty_response, Sgr A*:empty_response, Polaris:empty_response`
- **Symptom**: 4/4 standard reference targets empty.
- **Cause**: same `curl: not found`.
- **Suggested fix**: Dockerfile patch + add hardcoded fallback for the 4 selftest stars (mirror the gaia_bridge pattern — gaia ships 5 fallback stars and PASSes).

### F5. wikipedia_summary_bridge — `__WIKIPEDIA_BRIDGE__ FAIL refs=4 all_ok=false perfect_number_n6_anchor=false perfect_extract_len=0`
- **Symptom**: REST summary endpoint returns 0 bytes for all 4 references including `Pulsar`.
- **Cause**: same `curl: not found`.
- **Suggested fix**: Dockerfile patch. Optional: ship a minimal hardcoded `extract` for the n=6 anchor article (`Perfect number`) to keep selftest green when offline.

### F6. openalex_bridge — `FAIL: live fetch 'perfect number' returned 0 entries`
- **Symptom**: 0 entries.
- **Cause**: same `curl: not found`.
- **Suggested fix**: Dockerfile patch + add `--no-fetch` with one cached OpenAlex entry for "perfect number".

### F7. uniprot_bridge — `__UNIPROT_BRIDGE__ FAIL ... refs=6 all_ok=true`
- **Symptom**: per-ref printout shows `source: fallback`, `function_brief` populated, yet sentinel reports `all_ok=false fails=fetch_empty_or_short`. Under explicit `--no-fetch` the same selftest emits `__UNIPROT_BRIDGE__ PASS`.
- **Cause**: bridge marks `ok=false` when fetch was *attempted-and-empty*, even after fallback data fully populates. Sentinel-classification bug, not a data bug.
- **Suggested fix**: when fallback data successfully fills all required fields, the per-ref `ok` should be `true` with `source=fallback` (gaia uses this pattern correctly). One-line fix in `uniprot_bridge.hexa` ok-decision branch. Independently, the Dockerfile curl patch makes this moot.

## Network Classification Breakdown

| Class | Count | Bridges |
|-------|-------|---------|
| has-fallback (PASS today) | 9 | codata, horizons, cmb, nanograv, icecube, nist_atomic, gaia, lhc, pubchem |
| has-fallback (sentinel bug → FAIL today) | 1 | uniprot |
| requires-live (no offline mode) | 6 | oeis, gw, arxiv, simbad, wikipedia, openalex |

## Recommended Actions

**URGENT (single fix unblocks 7 bridges)**:
1. Patch `hexa-runner` Dockerfile to install `curl` (and consider `wget`, `ca-certificates`, `tini`). Rebuild image, restart `hexa-exec` container. This converts all 6 requires-live FAILs to PASS and removes the silent live-fetch failures masking the codata/horizons/cmb/etc. fallbacks.

**MEDIUM**:
2. Fix uniprot_bridge `ok` decision — when fallback fields are populated, set `ok=true source=fallback` (mirror gaia pattern).
3. Add `--no-fetch` offline mode to the 6 network-only bridges so health checks remain meaningful when the upstream API is rate-limited or down. Selftest fixtures should cover the n=6 anchor used by each bridge (perfect-number for wikipedia/openalex, A000396 for oeis, GW150914 for gw, Sirius/M31 for simbad, top arxiv gr-qc paper for arxiv).

**HEALTHY (no action)**:
- codata, horizons, cmb, nanograv, icecube, nist_atomic, gaia, lhc, pubchem — all PASS with their hardcoded fallbacks even under hostile network conditions. Use these as the gold-standard pattern for items in the MEDIUM list above.

## Methodology Notes

- All invocations: `gtimeout 30 hexa run tool/<name>.hexa --selftest` (sequential, single shell loop).
- 30s hard timeout per bridge; max observed wall = 5s (nanograv).
- Hetzner remote hosts all blacklisted (PSI/RAM/TTL); routing fell through to `hexa-resolver: route=docker reason=mac_safe_landing image=hexa-runner:latest caps=cpus=4,mem=4g` per `project_mac_hard_landing_policy` 2026-04-25.
- Output captured at `/tmp/bridge_health/<name>.out` for post-mortem (ephemeral; not committed).
- Read-only — no bridge file mutated during this Ω-cycle.

## Pointers

- Dispatch table: `cli/run.hexa` `_hexa_sim_bridge_dispatch` (16 cases).
- Witness for prior bridge ω-cycle: `design/hexa_sim/2026-04-25_bridge_tool_jackpot_omega_cycle.json`.
- Sister health check (falsifiers): `design/hexa_sim/2026-04-26_falsifier_health_check.md`.
- Timeline append: `state/atlas_health_timeline.jsonl` (one JSONL line, this cycle).
