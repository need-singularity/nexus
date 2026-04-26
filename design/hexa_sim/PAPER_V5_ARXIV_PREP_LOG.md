# PAPER_DRAFT_v5 arXiv submission prep log

- **Date.** 2026-04-26
- **Operator.** dancinlife (Ω-cycle session, Axis 4-A)
- **Trigger.** Ω-cycle (오메가 사이클) — arXiv submission preparation; v4 is
  fully populated with author block, but three blockers remained (license,
  ORCID, final pandoc dry-run).
- **Predecessor commit.** `0c854cbd` (the latest v4 commit; per the user's
  note, "직전 author 채워짐"; superseded `a0e74a7a` on author block).

## Decisions

| field          | choice                                           | rationale                                                                                              |
|----------------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| License        | CC-BY-4.0                                        | Most reproducibility-research friendly; CC-BY is the de-facto standard for open scholarly preprints. arXiv-perpetual would give arXiv distribution rights but no derivative-work or commercial-reuse permission to readers. CC-BY is strictly more permissive and is consistent with the falsifier-grounded methodology (every claim should be re-runnable and re-distributable by any third party). |
| License file   | `design/hexa_sim/LICENSE-CC-BY-4.0.md` (~50 L)   | Co-located with the paper drafts; references the CC-BY-4.0 legal text URL; spells out the relationship to the repo-wide MIT license (code vs prose). |
| ORCID          | Option C — note "pending registration"           | User has no ORCID yet (auto-memory, MEMORY.md). Option A (silent omit) is hostile to readers who expect attribution; option B (placeholder string) clutters the author block. Option C names the gap and the resolution path (free at <https://orcid.org>) and is the smallest audit-trackable wedge. Author block carries: "ORCID iD: pending registration ... will be amended in a follow-up commit per raw 77 audit-append-only". |
| MSC2020        | Primary `11A25`; secondary `03B30` + `68V20`     | `11A25` (multiplicative arithmetic functions) covers σ, φ, τ, J₂, μ — the foundation primitives in §2 and the F100 biconditional in §6. `03B30` (higher-order arithmetic) covers the formal admissibility framework (raw 73, §3.6, §9). `68V20` (reproducibility and replicability) covers the executable falsifier infrastructure and the 14-stage independent reproduction protocol (§13). |
| arXiv primary  | `math.HO` (history and overview)                 | The paper is a cross-domain mathematical exposition with explicit historical framing (Sierpiński 1988, Erdős–Surányi 2003); the central artefact is a *framework* rather than a single new theorem. `math.NT` was considered but rejected — the paper is methodological, not new pure-NT. |
| arXiv x-list   | `cs.MS` + `cs.LO`                                | `cs.MS` carries the falsifier executable infrastructure cited in §11.4 and §13. `cs.LO` carries the formal admissibility rule (raw 73, §3.6) and the five-layer defense audit (§8.2). The triple classification reflects the framework's three loci: number-theoretic biconditional, software reproducibility infrastructure, and a logical admissibility calculus. |
| Abstract       | Dual: in-body (LaTeX, ~2,472 chars) + arXiv ASCII (1,887 chars) | The arXiv submission form has a 1,920-char ceiling on the abstract field. The in-body abstract is the canonical scientific abstract (LaTeX math glyphs, section pointers); the arXiv-form abstract is the same content with ASCII math (sigma, varphi, tau, sopfr, J_2, mu; iso for ≅; iff for ⇔; e.g. 5e4 for 5×10⁴) and parenthetical section pointers removed. Claims are identical; only typography differs. |

## Files updated

| file                                                  | change                                                                                                                  |
|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `design/hexa_sim/PAPER_DRAFT_v5.md` (NEW)             | v4 body byte-identical (raw 77) + new YAML frontmatter (license, license-url, license-file, MSC, arXiv) + new author-block ORCID note + new License line + new "## arXiv submission metadata" pre-TOC section. Word count 14,855 (delta from v4 = +499; under the +500 cap). |
| `design/hexa_sim/LICENSE-CC-BY-4.0.md` (NEW)          | Full CC-BY-4.0 license declaration co-located with the paper; cross-links to the repo-wide MIT license; arXiv interaction note; recommended attribution string.                                                                          |
| `design/hexa_sim/PAPER_V5_ARXIV_PREP_LOG.md` (NEW)    | This file (~75 L; per spec ~50 L target, slightly exceeded for traceability).                                           |

## Files NOT modified (intentional, raw 77 audit-append-only)

- `design/hexa_sim/PAPER_DRAFT_v{1..4}.md` — historical record; the v4
  body lives byte-identically inside v5 from `## Table of contents`
  onward.
- `design/hexa_sim/PAPER_AUTHOR_DECISION_LOG.md` — author-block rationale
  log; v5 only adds ORCID handling and license, which are recorded in
  this file rather than amending the author log.
- `design/hexa_sim/PAPER_BIBLIOGRAPHY.md` — 88-entry references unchanged.
- `LICENSE` (repo top-level, MIT) — code license, untouched.

## Verification

- `wc -w PAPER_DRAFT_v5.md` → 14,855 (delta +499 vs v4's 14,356; cap +500).
- `wc -c arxiv_abstract` → 1,887 chars (cap 1,920).
- `diff <(tail -n +17 v4) <(awk '/^## Table of contents$/{flag=1} flag' v5)` → 0
  lines (body byte-identical from `## Table of contents` onward).
- `grep -c '115\|9,165\|F100\|F75\|F36\|raw 73\|raw 77' v5` → claims/numerics
  preserved; no in-body edits.

## Pandoc dry-run (NOT executed by this revision)

The pandoc command is documented inline in v5's `## arXiv submission metadata`
section. Operator runs pre-submit:

```bash
pandoc design/hexa_sim/PAPER_DRAFT_v5.md \
  --from markdown+yaml_metadata_block+tex_math_dollars+raw_tex \
  --to latex --standalone --pdf-engine=xelatex \
  --output /tmp/PAPER_DRAFT_v5.pdf \
  --resource-path=design/hexa_sim -V geometry:margin=1in 2>&1 \
  | tee /tmp/pandoc_v5.log
```

Expected output: PDF 1–4 MB; pandoc warnings 0 or soft-only. Hard failures
(unresolved cross-refs, missing figures, LaTeX errors) are pre-submit
blockers and must be fixed before upload.

## Submission readiness

- [x] Author block + email
- [x] License (CC-BY-4.0) + LICENSE file
- [x] MSC2020 + arXiv categories
- [x] arXiv abstract within 1,920-char cap
- [x] Body byte-identical to v4 (raw 77)
- [x] References + reproduction protocol intact
- [ ] ORCID iD (optional; user can add via follow-up commit)
- [ ] Pandoc dry-run (operator pre-submit)
- [ ] math.HO endorsement check (<https://arxiv.org/help/endorsement>)
- [ ] Operator decision to upload (NOT performed by this revision)

## Out of scope

This revision does not execute the arXiv submission. The four trailing
unchecked items are explicitly external operator actions. The user has
authorized the *preparation* (license + ORCID + metadata + log + LICENSE
file), not the *upload* — the latter is a separate user-explicit action,
consistent with the Ω-cycle's "NOT execute: 실제 arXiv submit" constraint.

## Relationship to prior cycles

- raw 77 audit-append-only: enforced; v4 body byte-identical inside v5.
- raw 73 admissibility rule: cited in arXiv `cs.LO` cross-list rationale.
- ORCID future-amendment is itself audit-trackable as a separate commit
  on top of this one (per the v4 author-decision log § "Future amendment").
