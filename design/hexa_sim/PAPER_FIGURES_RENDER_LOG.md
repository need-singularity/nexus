---
title: "Paper figures rendering log — matplotlib install + Fig 1/4 generation"
date: 2026-04-26
parent: PAPER_FIGURES_PLAN.md
related: PAPER_DRAFT_v5.md §12.1 (Fig 1), §12.4 (Fig 4)
status: matplotlib OK; Fig 1 + Fig 4 rendered (SVG + PNG @ 300 dpi)
---

# Paper figures render log (2026-04-26)

Ω-cycle Axis 4-A. Goal: attempt matplotlib install and render Fig 1 + Fig 4
raster outputs; otherwise graceful-degrade to ASCII fallback (paper §12).

## 1. matplotlib install attempt

| step                                                 | result                                                            |
|------------------------------------------------------|-------------------------------------------------------------------|
| `python3 -c "import matplotlib"` (initial probe)     | FAIL — `ImportError: Matplotlib requires dateutil>=2.7; you have 2.6.1` |
| `python3 -m pip install --user --upgrade python-dateutil` | FAIL — PEP 668 externally-managed-environment block          |
| `python3 -m pip install --user --break-system-packages --upgrade python-dateutil` | OK — `python-dateutil-2.9.0.post0` installed (vastai 0.5.0 conflict logged, non-blocking) |
| `python3 -c "import matplotlib; print(matplotlib.__version__)"` (re-probe) | OK — `3.10.8`                                       |

matplotlib itself was already installed; only the `dateutil` runtime
dependency needed an upgrade. Result: figures **rendered live** rather than
falling back.

## 2. Fig 1 — falsifier distribution (115 → 168 update)

- **script.** `design/hexa_sim/figs/render_fig1_falsifier_distribution.py`
- **data.** `design/hexa_sim/falsifiers.jsonl` (168 lines, verified)
- **delta.** initial registry 115 → 168 after F126-F185 cross-engine deeper
  integration (R2/R4/R6/R8/R10/M3/M5). Per-type [10]/[11] split rebalanced
  to sum to 168 (140 baseline + 28 strict load-bearing).
- **output.**
  - `figs/fig1_falsifier_distribution.svg`  — 64,505 B  (vector)
  - `figs/fig1_falsifier_distribution.png`  — 106,426 B (300 dpi raster)
- **sentinel-equivalent.** `[fig1] falsifiers.jsonl total = 168` /
  `[fig1] [10] sum = 140, [11] sum = 28, total split = 168`

## 3. Fig 4 — cross-shard uniqueness (11 → 16 shards / 9165 → 9174 unique)

- **script.** `design/hexa_sim/figs/render_fig4_cross_shard_uniqueness.py`
- **data.** `state/atlas_sha256.tsv` (16 shards after header-row strip);
  `tool/atlas_cross_shard_collision.sh` re-witness:
  `__ATLAS_CROSS_SHARD_COLLISION__ PASS shards=16 total=9174 unique=9174 dup=0 conflict=0`
- **delta.** 5 deeper shards added (`cross-engine-meta-roadmap`, `m3-deeper`,
  `m5-deeper`, `r4-deeper`, `cross-engine-r10-deeper`, `r2-r6-r8-deeper`;
  +47 raw lines, +9 unique tuples).
- **output.**
  - `figs/fig4_cross_shard_uniqueness.svg`  — 96,188 B  (vector)
  - `figs/fig4_cross_shard_uniqueness.png`  — 223,828 B (300 dpi raster)
- **title-line.** rendered as
  `Cross-shard uniqueness: 16 shards / 9,174 tuples / 0 collisions`

## 4. Paper §12 update

Both `PAPER_DRAFT_v5.md` §12.1 and §12.4 updated to reflect new totals plus
**Raster.** subsection pointing at SVG/PNG paths. ASCII tables retained as
authoritative-at-submission fallback per PAPER_FIGURES_PLAN.md guidance.

## 5. Reproduce from clean clone

```
python3 -m pip install --user --break-system-packages --upgrade python-dateutil
python3 -m pip install --user --break-system-packages matplotlib   # if missing
python3 design/hexa_sim/figs/render_fig1_falsifier_distribution.py
python3 design/hexa_sim/figs/render_fig4_cross_shard_uniqueness.py
```

## 6. Outstanding

- Fig 5/6/7 raster polish — still ASCII-only (PAPER_FIGURES_PLAN.md flags
  these as optional polish).
- vastai 0.5.0 dateutil pinning conflict — non-blocking; pin would need
  vastai upstream relax.

raw 71 honoured: only `figs/` outputs created; no upstream falsifiers.jsonl
or atlas_sha256.tsv mutation.
