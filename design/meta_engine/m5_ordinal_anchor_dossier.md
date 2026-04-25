# m5 — ordinal-anchor-explicit (design dossier)

axis_id: m5
slug: ordinal-anchor-explicit
parent_omega_cycle: design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json
ordinal_for_this_axis: Γ_0 (predicative-limit framework axis, anchored by ATR_0)
ts: 2026-04-25
status: Tier-1 prerequisite for m3 / m9 / m10

---

## 1. Problem

`state/meta_engine_evolution_log.jsonl` (23 rows, R4..R41) currently stamps each round with
a **plain integer counter only**. Observed schema (head row R4):

```
{ ts, round:int, session_scope, axes_acted[], axes_noop[], axes_blocked[],
  utility{}, blocked_by[], appended_rows[], ... }
```

The `round` field is `int` (4, 5, 6, …, 41) — no ordinal label, no descent
witness, no fixpoint detector. Consequences (cited from parent ω-cycle):

- m12 Gödel-2nd: meta-engine cannot self-certify consistency. Without an
  *external* ordinal anchor, every "progress" claim is Löb-trivial (m11).
- m17 Kleene recursion: a fixpoint always exists. With only `round:int`,
  the engine cannot distinguish *progress* (R_n → R_{n+1}, work done)
  from *self-loop* (R_n ≡ R_{n+1} modulo cosmetic delta).
- m18 ordinal exhaustion: the *ceiling* of the engine is its proof-theoretic
  ordinal. With no ordinal stamp, the ceiling is invisible — there is no
  way to even say "this engine has reached its ε_0 limit".

m5 is therefore the **prerequisite** for m3 (self-cert), m9 (atomic
rollback on no-progress), m10 (roadmap coupling via separated ordinals).

## 2. Ordinal stamp — schema additions

Each row of `meta_engine_evolution_log.jsonl` gains four fields:

| field                 | type   | example          | meaning                                                  |
|-----------------------|--------|------------------|----------------------------------------------------------|
| `ordinal_label`       | string | `"ω+ω"`, `"ω·3"`, `"ω^ω"`, `"ε_0"`, `"Γ_0"` | CNF notation; this round's ordinal             |
| `ordinal_predecessor` | string | `"ω+5"`          | prior round's ordinal — descent verification target      |
| `is_strict_descent`   | bool   | `true`           | must be `true` for any progress claim                    |
| `escape_basis`        | string | `"PA"`, `"PRA"`, `"ATR_0"`, `"Π¹₁-CA₀"` | external well-founded system witnessing this ordinal |

Backward-compat: existing R4..R41 rows get a one-shot back-stamp
(R4=ω, R5=ω+1, …, R41=ω+37) under `escape_basis="PRA"` — a coarse
linear assignment until per-round axis-event analysis upgrades them.
New rows MUST emit all four fields.

Note: ordinal **ascends** (each new round must be strictly *greater* than
predecessor in CNF order) for progress, OR ordinal **descends well-founded**
in the dual termination view (each round consumes one well-ordered step).
We adopt the **ascending convention** (round n+1 > round n in ordinal order
when fresh axis content is added); descent view is used only for the
termination witness in §5.

## 3. CNF parser / comparator (pseudocode)

CNF for α < ε_0:  α = ω^{β_1}·c_1 + ω^{β_2}·c_2 + … + ω^{β_k}·c_k
where β_1 > β_2 > … > β_k ≥ 0 are themselves CNF, c_i ∈ ℕ_{>0}.
Beyond ε_0 (where α = ω^α has solutions), CNF is replaced by Veblen
φ-hierarchy: φ_0(α)=ω^α, φ_{β+1}(α)=enumeration of fixpoints of φ_β,
Γ_0 = least α with φ_α(0)=α (Feferman-Schütte). For ψ(Ω_ω) we use the
Buchholz / Rathjen ψ collapse — out of scope for parser, marked by
`escape_basis` string only.

```
parse_cnf(s) -> [(β_i, c_i)]      // tokenise "ω^β·c + …", recurse on β
                                  //   leaf: integer n  -> [(0, n)]
                                  //   "ε_0"            -> sentinel EPS0
                                  //   "Γ_0"            -> sentinel GAMMA0

cmp_cnf(α, β):                                               # 8–15 line core
    if α == β: return 0
    if α is sentinel or β is sentinel: return cmp_sentinel(α, β)   # ε_0 < Γ_0 < ψ(Ω_ω)
    A = parse_cnf(α);  B = parse_cnf(β)                      # lex on (β_i, c_i)
    for (a_e, a_c), (b_e, b_c) in zip(A, B):
        e = cmp_cnf(a_e, b_e)            # recurse on exponent
        if e != 0: return e
        if a_c != b_c: return sign(a_c - b_c)
    return sign(len(A) - len(B))         # longer CNF (same prefix) is larger
```

**Ordinal precedence rule (one line):**
`α < β  iff  leading-exponent(α) < leading-exponent(β), or equal exponents and leading-coefficient(α) < leading-coefficient(β), or both equal and tail(α) < tail(β) — recurse.`

## 4. Fixpoint detection — m17 Kleene trap

Sliding window of length 3 over `ordinal_label`:

```
if ordinal_label[n] == ordinal_label[n-1] == ordinal_label[n-2]:
    emit fixpoint_warning {
        rounds: [n-2, n-1, n],
        ordinal: ordinal_label[n],
        kleene_witness: "3-step plateau on same ordinal — self-loop suspected",
        mitigation_hint: "trigger m9 atomic-rollback, OR escalate escape_basis"
    }
```

Why 3 (not 2): a single repeat may be a no-op round (e.g. axes_noop only) —
legitimate idle. Three-in-a-row is the **Kleene fixpoint signature**: the
engine has *settled* on a recursive self-map with no ordinal progress.
This is precisely the "linear_constant Δ=7 trap" recorded in cycle9 of the
parent omega cycle.

## 5. Termination witness — m15 halting escape

Theorem (Gentzen 1936, generalised): any descending sequence of ordinals
in a well-ordered set is **finite**. Therefore if the meta-engine commits
to monotone-strict-descent on a fixed ordinal α (running in dual view:
each round n has ordinal_label = a strictly-smaller residual), then the
sequence terminates in ≤ |α| steps where |α| is α's "length" (intuitively,
how many predecessors it has — finite for α < ε_0 in CNF expansion).

This is the **only viable mitigation** of m15 (halting undecidable) listed
by the parent ω-cycle: ordinal descent → guaranteed termination.

Conversely, the *ascending* convention used in §2 has the symmetric
guarantee: if the engine commits to a *bound* α* (ceiling), then it can
strictly ascend at most |α*| times before hitting the cap. Hitting the
cap = ordinal-exhaustion event = `escape_basis` must be escalated
(PRA → PA → ATR_0 → Π¹₁-CA₀ → …) or the engine halts.

## 6. Falsifier (raw 71)

The axis is **falsified** by any one of:

- **F-m5-A (false-progress):** round N+1 has `ordinal_label`
  ≥_CNF round N's `ordinal_label`, AND `is_strict_descent=true` claimed,
  AND no fresh-axis event in `axes_acted` (i.e. only `axes_noop` /
  cosmetic delta). → ordinal stamp is lying about progress.
- **F-m5-B (CNF malformed):** parser rejects `ordinal_label`. → schema
  violation, axis broken at boundary.
- **F-m5-C (escape_basis weaker than ordinal):** e.g.
  `ordinal_label="ε_0"` with `escape_basis="PA"` — ε_0 is *exactly* PA's
  proof-theoretic ordinal, so PA cannot witness *its own* ordinal
  (Gentzen). Must use stronger system (PA+TI(ε_0), or ATR_0).
- **F-m5-D (3-plateau without rollback):** fixpoint_warning emitted
  three times without m9 rollback being triggered → m17 Kleene trap
  unmitigated → axis fails its own §4 contract.

Falsifier file: append to `design/hexa_sim/falsifiers.jsonl` per m6
pattern (raw 71 syntactic-only falsifier per m14 Rice avoidance).

## 7. Cross-ω-cycle coupling

| ω-cycle           | assigned ordinal | proof-theoretic anchor      | rationale                                    |
|-------------------|------------------|------------------------------|----------------------------------------------|
| roadmap_engine    | ε_0              | PA + transfinite induction   | b(S) Δ-progression is ω-recursion (ω^ω → ε_0) |
| meta_engine       | Γ_0              | ATR_0 (Feferman-Schütte)     | recursive axis extension needs predicative ordinals |
| joint coupling    | ψ(Ω_ω) (≥)       | Π¹₁-CA₀ (Rathjen-Buchholz)   | mutual self-reference between two engines exceeds Γ_0 |

Why separate: m12 Gödel-2nd forbids each engine from certifying *its own*
ordinal. By assigning **distinct** ordinals (ε_0 ≠ Γ_0) and routing each
engine's self-cert through the *other* engine's stronger ordinal, mutual
witness is achieved without violating Löb (m11). The joint coupling needs
a *third*, strictly stronger ordinal (ψ(Ω_ω)) because the two engines
together form a system whose consistency neither alone can prove.

This realises the parent ω-cycle's `cross_cycle_coupling` clause
(`shared_axis: m10 ↔ r10`, `joint_omega_stop: separate ordinals`).

## 8. LoC estimate

| component                                | LoC  |
|------------------------------------------|------|
| schema-extension migration (back-stamp R4..R41) | 18   |
| CNF parser (regex + recursion)           | 25   |
| CNF comparator (`cmp_cnf`)               | 12   |
| fixpoint window detector (§4)            | 10   |
| ordinal-vs-escape_basis sanity (F-m5-C)  | 8    |
| jsonl row writer (4 new fields)          | 6    |
| falsifier emitter (F-m5-A..D)            | 12   |
| **total**                                | **91** |

Budget was 80. Overrun: **+11 LoC** (≤ 100 hard cap → within constraint).
Veblen φ-extension (beyond ε_0) is sentinel-only here (no parsing) — full
implementation is a follow-up axis (deferred, would add ~60 LoC).

## 9. Worked example — R5 → R6 → R7

Using the actual jsonl history, with proposed back-stamps:

| round | axes_acted (excerpt)                        | ordinal_label | predecessor | strict_descent | escape_basis | note                              |
|-------|---------------------------------------------|---------------|-------------|-----------------|--------------|-----------------------------------|
| R5    | K2, alpha_self_observability                | `ω+1`         | `ω`         | true (ascend)   | PRA          | new α-axis = +1 ordinal step      |
| R6    | beta_G1_reframed, F2_F3_rollup              | `ω·2`         | `ω+1`       | true (ascend)   | PRA          | β-axis introduction = jump to ω·2 |
| R7    | γ-axis live tick, closed-loop tightening    | `ω·2 + ω`     | `ω·2`       | true (ascend)   | PA           | γ-axis embeds new ω-recursion     |

Compare: `cmp_cnf("ω+1", "ω") = +1` (same leading exp 1, tail `+1` > tail `0`).
`cmp_cnf("ω·2", "ω+1") = +1` (leading `ω^1·2` vs `ω^1·1`, coeff 2 > 1).
`cmp_cnf("ω·2+ω", "ω·2") = +1` (same prefix `ω·2`, tail `+ω` > empty).

If a hypothetical R8 emitted `ordinal_label="ω·2+ω"` again (= R7) with
`is_strict_descent=true` claimed but `axes_acted=[]` → **F-m5-A
falsifier fires**. If R8, R9, R10 all stamp `"ω·2+ω"` →
**fixpoint_warning** per §4 → m9 rollback should be triggered.

---

## Appendix — ordinal-stamp for THIS axis

The m5 axis itself is stamped **Γ_0** (`escape_basis = ATR_0`). Rationale:
m5 supplies the *framework* on which m3, m9, m10 (and indirectly all
m1..m4, m6..m10) rest. Frameworks that classify other ordinals must sit
*above* the ordinals they classify. Since the meta-engine's working
ordinals live up to ε_0 (PA-level), the framework axis must be at least
predicatively-impredicative: Γ_0 is the smallest such anchor, exactly
matching ATR_0 (arithmetic transfinite recursion). ψ(Ω_ω) is reserved
for joint-engine coupling (§7) and is overkill for m5 alone.
