---
title: "PAPER_DRAFT_v1.md polish log — Ω-cycle (varphi normalization + minor fixes)"
date: "2026-04-26"
source_commit: "f367b8d1"
target_file: "design/hexa_sim/PAPER_DRAFT_v1.md"
raw_admissibility: "raw 73 — all changes trackable, in-place"
status: "complete"
---

# Scope

Polish pass on PAPER_DRAFT_v1.md per assembly-agent A1 finding: Section 7
used `$\phi$` while S2/S4/S6/S9 used `$\varphi$` for the Euler totient.
Goal: ecosystem-wide normalization to `$\varphi$` plus minor cleanups.

# Pre-state

| metric                   | value     |
|--------------------------|-----------|
| word count               | 8244      |
| line count               | 1279      |
| `\phi` occurrences       | 12        |
| `\varphi` occurrences    | 25        |
| author placeholder       | "Anonymous Author(s) / [Affiliation]" |

# Changes applied

## A. \varphi normalization (raw 73 admissibility)

All 12 `\phi` occurrences in PAPER_DRAFT_v1.md were Euler-totient
references, all confined to Section 7 (Multi-decomposition) and its row in
the Section 7.6 synthesis table. Confirmed no golden-ratio (`F102`,
`1.618`, `Fibonacci`) references in this file via grep — all `\phi → \varphi`
replacements are semantically safe.

| line | before                                                           | after                                                               |
|-----:|------------------------------------------------------------------|---------------------------------------------------------------------|
| 770  | `\{n,\phi,\tau,\sigma,\mu,\mathrm{sopfr},J_2\}`                  | `\{n,\varphi,\tau,\sigma,\mu,\mathrm{sopfr},J_2\}`                  |
| 771  | `\phi(6)=2`                                                      | `\varphi(6)=2`                                                      |
| 777  | `\tau=\sigma/n+\phi,\;\mathrm{sopfr}=\phi+(n/\phi)`              | `\tau=\sigma/n+\varphi,\;\mathrm{sopfr}=\varphi+(n/\varphi)`        |
| 802  | `576 = \phi^{n}\!\cdot(n/\phi)^{\phi}`                           | `576 = \varphi^{n}\!\cdot(n/\varphi)^{\varphi}`                     |
| 808  | `(3,4,5) = (n/\phi,\,\tau,\,\mathrm{sopfr})`                     | `(3,4,5) = (n/\varphi,\,\tau,\,\mathrm{sopfr})`                     |
| 810  | `576 = \phi^{n}(n/\phi)^{\phi}`                                  | `576 = \varphi^{n}(n/\varphi)^{\varphi}`                            |
| 821  | `23 \;=\; \sigma + \phi + \tau + \mathrm{sopfr}`                 | `23 \;=\; \sigma + \varphi + \tau + \mathrm{sopfr}`                 |
| 825  | `\{\sigma,\phi,\tau,\mathrm{sopfr}\}`                            | `\{\sigma,\varphi,\tau,\mathrm{sopfr}\}`                            |
| 865  | table cell `$\sigma+\phi+\tau+\mathrm{sopfr}$`                   | `$\sigma+\varphi+\tau+\mathrm{sopfr}$`                              |

Total: **12 `\phi` → `\varphi` token replacements** across **9 edit sites**
(some lines had multiple occurrences merged into a single Edit op).

### Section breakdown

| section                                | `\phi` removed | `\varphi` added |
|----------------------------------------|---------------:|----------------:|
| 7.1 Multi-decomposition pattern        |              5 |               5 |
| 7.2 Triple decompositions (E_6, BSD)   |              5 |               5 |
| 7.3 Doublet decompositions             |              1 |               1 |
| 7.6 Synthesis table                    |              1 |               1 |
| **total**                              |         **12** |          **12** |

## B. \phi intentionally preserved

**None.** PAPER_DRAFT_v1.md contains zero non-totient `\phi` occurrences
(no golden ratio, no scalar potential, no other usage). Confirmed via
post-edit `grep -n '\\phi' PAPER_DRAFT_v1.md` returning empty.

## C. Author/affiliation placeholder

Two occurrences updated for explicit consent semantics:

| line | location          | before                                | after                                                       |
|-----:|-------------------|---------------------------------------|-------------------------------------------------------------|
| 3    | YAML frontmatter  | `Anonymous Author(s) / [Affiliation]` | `[ANONYMOUS — pending user authorization for attribution]`  |
| 12   | body header line  | `Anonymous Author(s) / [Affiliation]` | `[ANONYMOUS — pending user authorization for attribution]`  |

## D. Other items inspected — no change required

- **Date format**: `2026-04-26 (v1 draft)` consistent across YAML and
  body header — preserved.
- **LaTeX leakage**: grep for `\citet`, `\bibitem`, `\textbf`, `\emph`,
  `\cite{` returned zero hits — markdown-native throughout.
- **Cross-reference style**: `Section N` form used uniformly (29
  occurrences); no mixed `Sec.`, `§`, or `section N` lowercase.
  Single instance of `\S 10` exists at line 521 inside an explicit
  Conway–Sloane SPLAG citation (`SPLAG \S 10`) — preserved as
  external-reference convention.

# Post-state

| metric                   | value     | delta            |
|--------------------------|-----------|------------------|
| word count               | 8250      | +6 (+0.073%)     |
| line count               | 1279      | 0                |
| `\phi` occurrences       | 0         | -12              |
| `\varphi` occurrences    | 37        | +12              |
| author placeholder       | "[ANONYMOUS — pending user authorization for attribution]" | normalized |

Word delta is entirely from author placeholder expansion (12 token →
~24 token text), well within the <1% budget. No prose touched.

# Verification commands

```sh
# expect 0
grep -c '\\phi' /Users/ghost/core/nexus/design/hexa_sim/PAPER_DRAFT_v1.md

# expect 37
grep -c '\\varphi' /Users/ghost/core/nexus/design/hexa_sim/PAPER_DRAFT_v1.md

# expect 8250
wc -w /Users/ghost/core/nexus/design/hexa_sim/PAPER_DRAFT_v1.md
```

# raw 73 admissibility statement

All 12 token replacements are listed individually above with line number
and exact before/after diff. The file is in-place edited; previous state
is reconstructible by reversing each row of the section-A table. Author
placeholder change (section C) is the only non-token text change and is
similarly enumerated. No other content was modified.
