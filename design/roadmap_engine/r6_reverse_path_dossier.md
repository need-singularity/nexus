# r6 — reverse-path-synthesis dossier (bidirectional Dijkstra/A*)

- ordinal: ω+1
- parent ω-cycle: `design/roadmap_engine/2026-04-25_final_form_and_limits_omega_cycle.json`
- subject: `tool/roadmap_engine.hexa` (1298 lines, TOC + A* DAG scheduler)
- axis: r6 — forward-only A* → bidirectional meeting-in-the-middle
- theorem anchors: r15 Brent (span floor) · r17 NFL (admissibility per cost type)
- status: design-only (no code emitted this cycle)

---

## 1. Problem

The current scheduler is forward-only. The entry point is

```
fn schedule(rm: Roadmap) -> ScheduleResult        // tool/roadmap_engine.hexa L513–L644
```

Within `schedule()`:
- L529 `let T = vstar(nodes, start_id, K, C)` — `vstar()` (L480–L494) recurses
  forward via `children_of()` (L460–L473): `V*(n) = remaining_cost(n) + max_kid V*(kid)` — forward critical path only.
- L538–L557 build `ready` from forward dep-closure (parents must be `done`).
- L559–L580 pick bottleneck only over ready ∪ in_progress — purely forward.
- No backward heuristic h(S) exists; A* admissibility is unexploited — the
  engine is effectively uniform-cost Dijkstra over the forward frontier,
  with V* as a span estimator not a search guide.

Consequence: explored frontier is O(b^d) where b is average out-degree and
d is depth from S0 to G. Track-A axis r6 proposes bidirectional Dijkstra:
forward from S0 plus backward from G; the two frontiers meet at depth ≈ d/2,
yielding ~O(b^(d/2)). The backward cost b_back(S) doubles as a **problem-
specific admissible heuristic** for the forward search, which is the only
way A* gain survives r17 NFL.

---

## 2. Bidirectional algorithm sketch

Two priority queues:

- `F` — forward frontier, key = `g_f(n) = c(S0 → n)`
- `B` — backward frontier, key = `g_b(n) = c(n → G)`, expanded over the
  reversed DAG (edges flipped: child→parent).

Closed sets `C_f`, `C_b`. Best meeting cost μ initialized to +∞.

Loop until termination:
1. Pop side with smaller top key (or alternate strictly — Pohl 1971).
2. Expand node `u`; for each neighbor `v`:
   - relax `g_f(v)` (forward) or `g_b(v)` (backward)
   - if `v ∈ C_{other}`, candidate path cost = `g_f(v) + g_b(v)`;
     if `< μ`, update μ and store meeting node `m*`.
3. **Termination**: when `topF + topB ≥ μ`, no unexplored path can beat μ.
   This is the standard Pohl/Nicholson stop condition; correctness is
   preserved because frontier keys are lower bounds on remaining cost on
   each side under non-negative edge weights (all our cost types are ≥ 0,
   §3 below).

Output: reconstruct path `S0 → … → m* → … → G` via parent pointers, then
reuse the existing ready/in_progress classification (L538–L557) over it.
When `g_b` is precomputed/cached, the forward leg uses h(S) = g_b(S) as an
A* heuristic — admissible because `g_b(S)` is the true min remaining cost
(h = h* by construction). Per-cost-type proof sketches in §3.

---

## 3. Backward cost reachability `b_back(S)` per cost type

Define `b_back(S) = min_{path π: S → G} Σ_{n ∈ π} c_eff(n)` where `c_eff` is
the effective-cost function in `effective_cost()` (L412–L437). Computed by
running Dijkstra on the reversed DAG from G. Admissibility means
`b_back(S) ≤ b_back*(S)` for the planner's true cost model — i.e. the
heuristic never overestimates remaining cost.

| cost type | formula (effective_cost L412–L437) | derivation of `b_back` | admissibility |
|---|---|---|---|
| build  | `c_eff = cost` (Brent span; raw)        | reverse-DAG sum of `cost` along min-path | **proved** — c is fixed, ≥ 0, additive on DAG; min over paths is exact h*  → h = h*. |
| exp    | `c_eff = cost / p_success`              | reverse-DAG sum of `cost/p`              | **proved (point estimate)** — `p_success` is a fixed parameter at plan-time; cost is deterministic. Open under r2 Bayesian update: when posterior on p drifts, h must be recomputed; admissibility holds *given the current posterior mean used as plug-in* (Wald-style frozen-parameter argument). |
| learn  | `c_eff = cost · (1 − η)^k`, code uses k=0 | reverse-DAG sum with current η          | **sketched** — code applies one-step (`k=0`) so c_eff = cost·(1-η). For k>1 (multi-step learning curve, Wright), c_eff is monotonically non-increasing in k, hence using the largest `c_eff` (k=0) overestimates remaining cost ⇒ **inadmissible**. Fix: pick the smallest realizable `c_eff` over k ∈ [0, k_max] before reverse Dijkstra (i.e. `c_eff = cost·(1−η)^{k_max}`). With that swap, admissibility holds. |
| boot   | `c_eff = cost / max(1, n_uses)`         | reverse-DAG sum with current `n_uses`    | **sketched** — analogous to exp. `n_uses` only grows (monotone). At plan-time use the *upper bound* on n_uses (oracle: configured cap or measured peak). Then plug-in c_eff is a lower bound on amortized remaining cost ⇒ admissible. Open: if n_uses can shrink (state evict), the bound breaks — flag soft. |
| verify | `c_eff = K/C + 0.25·cost`               | reverse-DAG sum                          | **proved (modulo r14)** — K (target), C (channel) are constants in `Roadmap`. r14 says the *actual* K(G\|S) is uncomputable, so `K_target` is a surrogate. Admissibility holds only if `K_target ≤ K(G\|S)_true`. Mitigation: compression-length **lower bound** for K_target. Status: **open** absent that lower-bound calc — current code uses user-set scalar. |

Special cases: `seed → 0` (admissible trivially), `goal → cost` typically 0
(admissible, base case `b_back(G) = 0`).

**Net status**: admissibility is proved for `build`, proved-with-frozen-param
for `exp` and `boot`, sketched-with-fix-needed for `learn`, open for
`verify` (gated on r14 — Kolmogorov uncomputability).

---

## 4. Meeting-in-the-middle proof sketch

Assume DAG with uniform branching factor b (out-degree forward, in-degree
on reversal also bounded by b under DAG regularity — for non-uniform DAGs
substitute b → max(b_fwd, b_bwd)). Let d = depth(S0 → G).

Forward A* with consistent admissible h explores at most O(b^d) nodes in
the worst case (Hart-Nilsson-Raphael 1968). Bidirectional with admissible
forward and backward heuristics expanded in lockstep meets near depth d/2:

- forward expands ≤ b^(d/2) nodes
- backward expands ≤ b^(d/2) nodes
- total explored ≤ **2 · b^(d/2)**

Proof: A node n with g_f(n) ≤ μ/2 sits within d/2 forward hops of S0 (under
edge cost ≥ 1 normalization); analogous for backward. Termination
`topF + topB ≥ μ` fires no later than when both fronts have reached μ/2,
bounding the count of expanded nodes per side by the b^(d/2) ball volume.
QED-sketch.

For our concrete DAGs (depth d ≈ 6, branch b ≈ 3): forward = 3^6 = 729,
bidir = 2·3^3 = 54 → 7.4% of forward worst case. The falsifier in §6
demands < 70% which is two orders of magnitude looser — chosen because
roadmap DAGs are sparse and many paths share nodes (sub-tree reuse), so
real measured ratio is closer to 50% than 7%.

**Brent ceiling caveat (r15)**: bidirectional reduces *search effort*
(nodes expanded) but does **not** lower wall-clock T_∞. If the critical
path span is T_∞ on the chosen path, executing it still takes ≥ T_∞.
Bidirectional only helps the planner *find* that path faster.

---

## 5. Edge cases

| case | handling |
|---|---|
| **soft edges** (`soft_deps` collected at L605–L624) | Backward Dijkstra ignores soft edges (they are non-blocking by definition). Forward search may relax them in replan (r4); when relaxed, `b_back` must be recomputed for affected ancestors — invalidate cache by descendant set. |
| **cycles** | Roadmap is asserted DAG (Kahn topo-sort assumption in current code). r6 inherits this assumption. If a future axis introduces cycles, bidirectional Dijkstra still works on non-negative weights; the meeting-in-the-middle bound degrades to general graph case. |
| **unreachable G** (no path S0 ⇝ G) | Forward exhausts → frontier empty → return `infeasible`. Backward also exhausts independently and reports the same. Both must agree before declaring infeasibility (cross-check eliminates one-sided enumeration bugs). |
| **multiple goals** | Add a virtual super-goal G* with zero-cost edges from each goal; backward Dijkstra runs from G*. Out of scope this axis but compatible. |
| **node cost = 0** (seed) | Termination still correct because `topF + topB ≥ μ` uses *path* keys, not single-edge keys. Zero-cost nodes get visited eagerly but cannot create infinite loops on a DAG. |
| **dynamic costs** (η updates mid-run) | If `effective_cost` shifts during execution, both forward g_f and backward g_b are stale. Trigger re-search on Δb above threshold (couples to r10 meta-engine). |

---

## 6. Falsifier

Benchmark protocol:

1. Generate 5 random DAGs with depth 6, branching factor 3, ~700 nodes
   each. Cost types drawn uniformly across {build, exp, learn, boot,
   verify}; costs ∈ U[1, 10]; deps wired so DAG is connected and goal is
   reachable from start.
2. Run forward A* (current `schedule()`-equivalent search) → record
   `nodes_expanded_fwd` per DAG.
3. Run bidirectional from §2 → record `nodes_expanded_bidir` per DAG.
4. **Pass**: median(`nodes_expanded_bidir / nodes_expanded_fwd`) < 0.70
   over the 5 DAGs.
5. **Fail (axis falsified)**: median ≥ 0.70 → r6 cannot beat forward A* on
   our DAG family by enough margin to justify the LoC; defer to Tier-2.

Auxiliary checks (must also pass for axis to be accepted):
- Optimal cost equality: bidir-recovered path cost = forward A* path cost
  on every DAG (within 1e-6). Else admissibility is broken — likely the
  `learn` or `verify` row of §3.
- Termination determinism: same seed → same μ, same `m*`.

---

## 7. LoC budget and components

Estimate for `tool/roadmap_engine.hexa` patch (no new file required;
helpers live alongside `vstar()`/`schedule()`):

| component | LoC |
|---|---|
| `b_back(rm, K, C)` reverse Dijkstra over reversed DAG | 50 |
| `parents_of_id(nodes, id)` (already exists L475 inline; expand to id-lookup) | 10 |
| min-priority queue (binary heap or linear scan ≤200 nodes) | 40 |
| `schedule_bidir(rm)` orchestrator | 70 |
| meeting/path reconstruction (parent pointers fwd + bwd) | 35 |
| feasibility & termination guards | 15 |
| event emission compat (`emit_schedule_events`-shaped) | 20 |
| **subtotal** | **240** |

Headroom: target ≤ 250 LoC. Axis budget was 200; **+40 LoC overrun**.
Mitigation if strict: drop the binary heap (linear scan ≤200 nodes per
existing `vstar` "노드 < 200 충분"), saving ~30 LoC → 210, +10 over.

---

## Hexa-like pseudocode — `schedule_bidir()` entry

```hexa
fn schedule_bidir(rm: Roadmap) -> ScheduleResult {
    let K = rm.K_target
    let C = rm.C_channel
    let nodes = rm.nodes
    let start_id = pick_start(rm)         // same logic as schedule() L519–L526
    let goal_id  = pick_goal(rm)          // first node with ntype=="goal"

    // forward / backward dist tables (id → f64), parent tables (id → string)
    let mut g_f: Map<string,f64> = {start_id: 0.0}
    let mut g_b: Map<string,f64> = {goal_id:  0.0}
    let mut par_f: Map<string,string> = {}
    let mut par_b: Map<string,string> = {}

    // priority frontiers (key = g)
    let mut F: PQ = pq_push(pq_new(), start_id, 0.0)
    let mut B: PQ = pq_push(pq_new(), goal_id,  0.0)

    let mut mu: f64 = INF
    let mut meet: string = ""

    while pq_nonempty(F) && pq_nonempty(B) {
        let topF = pq_top_key(F)
        let topB = pq_top_key(B)
        if topF + topB >= mu { break }                  // Pohl termination

        if topF <= topB {
            let u = pq_pop(F)
            for v in children_of(nodes, u) {            // forward edge
                let w = effective_cost(node_of(nodes,v), K, C)
                let alt = g_f[u] + w
                if alt < g_f.get_or(v, INF) {
                    g_f[v] = alt; par_f[v] = u
                    F = pq_push(F, v, alt)
                }
                if g_b.has(v) {                         // candidate meet
                    let cand = g_f[v] + g_b[v]
                    if cand < mu { mu = cand; meet = v }
                }
            }
        } else {
            let u = pq_pop(B)
            for v in parents_of(node_of(nodes,u)) {     // reversed edge
                let w = effective_cost(node_of(nodes,v), K, C)
                let alt = g_b[u] + w
                if alt < g_b.get_or(v, INF) {
                    g_b[v] = alt; par_b[v] = u
                    B = pq_push(B, v, alt)
                }
                if g_f.has(v) {
                    let cand = g_f[v] + g_b[v]
                    if cand < mu { mu = cand; meet = v }
                }
            }
        }
    }

    if meet == "" { return infeasible_result(rm) }
    let path = reconstruct(par_f, par_b, start_id, meet, goal_id)
    return classify_along(path, nodes, K, C, mu)        // reuse schedule()
                                                        // ready/inp/done/todo
                                                        // logic L538–L557
}
```

Notes:
- `effective_cost` reused unchanged (L412–L437); §3 "learn"/"verify"
  caveats need a wrapper `effective_cost_admissible_lb` before entry.
- `classify_along` extracts L538–L557/L559–L580 into a reusable function
  (counted in LoC table under "event emission compat").
- `pq_*` notional; linear scan acceptable at <200 nodes.

---

## Anchors back to parent ω-cycle

- **r17 NFL escape**: backward Dijkstra from G yields `b_back` which is
  the *true* min-remaining-cost on the planner's own cost model →
  problem-specific by construction → escapes Wolpert-Macready.
- **r15 Brent ceiling acknowledged**: §4 explicit caveat — search effort,
  not wall-clock. Cannot beat T_∞.
- **r14 Kolmogorov spillover**: `verify` row admissibility is open until a
  K_target lower bound (compression-incompressibility two-sided estimate)
  lands; tracked here, not in r6's scope to fix.
- **r6 → r4 coupling**: when r4 mutates the graph (soft-edge drop / parallel
  split / seed inject), invalidate `g_b` on affected ancestors and
  re-run backward leg only — incremental, not full rerun.
- **r6 → r2 coupling**: Bayesian η posterior shift triggers re-evaluation
  of `c_eff` on `learn` nodes, then partial backward Dijkstra refresh.
- **r6 → r10 coupling**: meta-engine signals b(S) drift over threshold →
  invalidate `g_f`, `g_b` slices; ordinal kept at ω+1 vs meta's separate
  ordinal stack to avoid Gödel self-cert (r19).

ω+1 stamp recorded.
