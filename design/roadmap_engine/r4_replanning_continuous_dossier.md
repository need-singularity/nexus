# r4 replanning-continuous — design dossier

- ordinal stamp: ω+1 (one step beyond current schedule fixpoint)
- parent ω-cycle: design/roadmap_engine/2026-04-25_final_form_and_limits_omega_cycle.json
- subject: tool/roadmap_engine.hexa (1298 lines)
- track: final-form, Tier-1
- theorem anchor: NFL (Wolpert-Macready 1997) — pre-req limits respected: r12 halting undecidable, r15 Brent floor

## 1. Problem statement

The current schedule() at tool/roadmap_engine.hexa L582–L643 computes
η = 1 − b(S_{k+1})/b(S_k) (L596–L599) and sets

    replan: bool = (eta <= 0.0) && (todo>0) && (in_progress>0 || ready>1)   (L603)

`replan_needed` is then surfaced two ways:
1. render_flowchart prints a hint at L990–L997 (`⟲ REPLAN hint — η ≤ 0`) and dumps `soft_drop_candidates` (L991–L996). The graph is **not** mutated.
2. main() at L1290–L1294 treats it as a fatal divergence:

    if s.replan_needed && s.ready_set.len() == 0 && s.in_progress.len() == 0 {
        eprintln("WARN: η ≤ 0 and nothing actionable — replan required")
        exit(1)                                   // ← dead path
    }

Trigger conditions for the dead path: η ≤ 0 AND no ready node AND no in-progress node AND todo > 0. This is exactly the configuration where the scheduler cannot pick a next action — Bellman backup has no admissible successor — yet the DAG itself may still admit a feasible plan if soft edges drop, parallelism opens, or a seed is injected. r4 replaces `exit(1)` with bounded graph mutation.

## 2. Three mutation strategies

All three are pure functions over a snapshot of `ScheduleResult` and the parsed Roadmap. Each returns a *candidate mutated DAG* plus a provenance tag for atomic rollback.

    type Mutation = { kind: string, target: string, payload: any, provenance: string }
    type DagDelta = { added_edges: [Edge], removed_edges: [Edge], added_nodes: [Node], reason: Mutation }

Signatures:

    fn mutate_soft_drop(rm: Roadmap, s: ScheduleResult) -> [DagDelta]
        // for each id in s.soft_drop_candidates, emit a delta that removes
        // exactly that soft edge. one delta per candidate.

    fn mutate_parallel_split(rm: Roadmap, s: ScheduleResult) -> [DagDelta]
        // bottleneck_node bn with cost b*: if bn declares `parallel_factor > 1`
        // in its meta, emit delta cloning bn into k siblings sharing a join,
        // each with cost b*/k. respects r15 Brent: cannot reduce below T_∞.

    fn mutate_seed_inject(rm: Roadmap, s: ScheduleResult) -> [DagDelta]
        // for blocked nodes whose hard parents are all done==false but whose
        // c_boot can be amortized by a known reusable seed (n_uses>1),
        // inject an alternative seed source node with c_boot/n_uses cost.

Each strategy is *hand-tuned* — see §5.

## 3. MCTS budget envelope

UCB1 selection with c=√2 over the union of deltas from §2.

    fn schedule_replan(rm: Roadmap, s0: ScheduleResult) -> Option<Plan> {
        if !s0.replan_needed || (s0.ready_set.len()>0 || s0.in_progress.len()>0) {
            return None                              // no-op fast path
        }
        let root = MctsNode { rm: rm, s: s0, visits: 0, reward: 0.0 }
        let mut budget_rollouts: i64 = 0
        while budget_rollouts < 32 {                 // ≤ 32 rollouts
            let leaf = ucb1_descend(root, c = 1.41421356, max_depth = 3)
            let deltas =
                mutate_soft_drop(leaf.rm, leaf.s)
                ++ mutate_parallel_split(leaf.rm, leaf.s)
                ++ mutate_seed_inject(leaf.rm, leaf.s)
            if deltas.len() == 0 { break }
            let pick = expand_random(leaf, deltas)
            let rm2 = apply_delta(leaf.rm, pick.delta)
            let s2  = schedule(rm2)                  // re-run existing scheduler
            let r   = reward(s0, s2)                 // see §4
            backprop(pick, r)
            budget_rollouts = budget_rollouts + 1
        }
        let best = argmax_visits(root.children)
        if best.is_none() || reward(s0, best.s) <= 0.0 { return None }
        return Some(Plan { delta: best.delta, T_star: best.s.T_star })
    }

Reward function (sign-correct, bounded):

    reward(s0, s2) = clamp((s0.T_star - s2.T_star) / max(s0.T_star, ε), -1.0, +1.0)

Limits:
- depth ≤ 3 (chained mutations bounded — keeps search tree ≤ |M|^3)
- rollouts ≤ 32 (matches a single-second wall-clock budget on current schedule() perf)
- UCB1 c=√2 (textbook exploration constant; not problem-tuned, see r17)
- per-rollout cost: one full schedule() call (~O(V+E))

## 4. Falsifier (raw 71)

**Statement.** Build a benchmark suite of N ≥ 5 toy DAGs that each trigger η ≤ 0 with ready=∅, in_progress=∅, todo>0. For each DAG, record T*_pre = schedule(rm).T_star (the value that would have led to exit(1)) and T*_post = schedule(apply(rm, schedule_replan(rm).delta)).T_star.

> r4 is **falsified** iff, on the suite, the geometric mean of T*_post / T*_pre ≥ 1 + ε for ε = 0.01, OR if for ≥ 2 of N benchmarks T*_post > T*_pre + ε·T*_pre.

Equivalently, replanning must cut wall-clock T* on the strict majority of triggering instances by at least 1%, otherwise the strategy pool is no better than the dead path. The suite must be checked into design/roadmap_engine/r4_bench/ before merge. r12 halting reminds us the suite is finite and timeout-bounded; we do not claim convergence in general.

## 5. NFL acknowledgment

Wolpert-Macready 1997: averaged over **all** cost landscapes, no search heuristic beats random. The three strategies of §2 are explicitly not universal:
- soft_drop assumes problem encodes optionality via `soft_deps` field
- parallel_split assumes the bottleneck node carries a `parallel_factor` hint
- seed_inject assumes c_boot reuse with n_uses > 1

These priors are roadmap-domain priors, not algorithm priors. On adversarial DAGs lacking these annotations, schedule_replan() returns None and main() falls back to the legacy exit(1). r4 therefore narrows but does not eliminate the dead path.

## 6. Failure modes + atomic rollback

| failure | detection | rollback |
|---|---|---|
| MCTS exceeds wall budget | rollout counter | break loop, return None |
| best delta has reward ≤ 0 | reward() check | return None (do not mutate) |
| apply_delta() makes DAG cyclic | post-mutation Kahn topo check | discard delta, mark child dead |
| mutated DAG schedule() re-triggers replan | recursion guard `replan_depth ≤ 1` | return None, propagate exit(1) |
| seed_inject references unknown seed | seed-table lookup miss | strategy yields zero deltas |

Atomicity: `apply_delta` operates on an in-memory clone of Roadmap (the source roadmap.json on disk is never written). Either the entire delta is accepted (best chosen) or the original roadmap proceeds to exit(1). No partial mutation is ever surfaced. provenance string carries `kind:target:rollout_id` so events sentinel can audit.

The events JSONL gains one new record kind `replan_attempt` with fields {pre_T, post_T, delta_kind, accepted}. Dispatch-plan (L1049, L1089) extends with `replan_applied: bool`.

## 7. LoC estimate

Honest revision: parent ω-cycle stated 150 LoC. After enumerating §2 (3 strategies × ~25 LoC), §3 MCTS (UCB1 + backprop + reward ≈ 80 LoC), §6 guards (~20 LoC), and events extension (~10 LoC), realistic total ≈ **190 LoC** — within the dossier ceiling of 200 but **40 LoC over** the original 150 axis budget. Acknowledged drift; trade-off is accepting one extra strategy (seed_inject) the original budget would have cut.

## Pre-req limit citations

- r12 halting: schedule_replan terminates by rollout counter (not by detecting convergence) — Lyapunov surrogate is the reward bound.
- r15 Brent: parallel_split honors `parallel_factor` from node metadata; will never drive T* below the user-declared T_∞ floor on the bottleneck node.
- r17 NFL: §5 explicit.

## Cross-axis touch

- r2 online_bayesian_eta: future replacement for the static `n_uses` lookup in seed_inject.
- r6 reverse_path_synthesis: bidirectional admissible h would tighten `reward()` so MCTS doesn't waste rollouts on useless deltas.
- r8 convergence_certificate: each accepted replan emits a certificate fragment (delta + pre/post T*).
