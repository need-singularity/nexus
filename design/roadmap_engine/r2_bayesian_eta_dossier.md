# r2 — Online Bayesian η for roadmap_engine.hexa

**Ordinal stamp:** ω+1
**Parent ω-cycle:** `design/roadmap_engine/2026-04-25_final_form_and_limits_omega_cycle.json`
**Subject:** `tool/roadmap_engine.hexa`
**Axis budget:** 100 LoC (estimated 130 — see §7)
**Date:** 2026-04-25

---

## 1. Problem statement

`tool/roadmap_engine.hexa::parse_node` (around line 290) reads `eta` and
`p_success` as fixed scalars from the node JSON:

```hexa
let p   = json_num(raw, "p_success")
let p2  = if p <= 0.0 { 1.0 } else { p }
let eta = json_num(raw, "eta")
```

These values feed the Wright learning curve `T_k = T0 · (1−η)^k` inside
`c_learn(...)` and the geometric expected-attempts term inside `c_exp(...)`.
Once the JSON is authored, η and p never move — even after the planner has
observed dozens of trials whose empirical hit-rates contradict the prior.
Result: schedule choices fossilize around the human author's first guess.

**Goal of r2:** replace each scalar with an **online Beta posterior** updated
from observed (success, fail) trials, sampled at every Bellman backup via
Thompson sampling. The author's JSON value becomes the **prior mean**, not a
hard fact.

---

## 2. Beta–Bernoulli posterior

Each node carries two conjugate posteriors — one for `p_success`, one for the
per-iteration learning hit-rate `η` (each successful "use" of the node counts
as one Bernoulli draw against η).

- Prior: `Beta(α0, β0)` with default `α0 = β0 = 1` (Jeffreys uniform). When the
  author supplies a JSON `eta = m` (or `p_success = m`) we seed
  `α0 = 1 + κ·m`, `β0 = 1 + κ·(1−m)` with pseudo-count `κ = 2`, so authored
  hints decay quickly under real evidence.
- Update: after observing `a` successes and `b` failures,
  `Beta(α0 + a, β0 + b)`.
- Posterior mean: `(α0 + a) / (α0 + β0 + a + b)`.
- Credible interval (95%): `BetaInv(0.025, α, β)`, `BetaInv(0.975, α, β)`.

Sufficient statistics `(α, β, n_trials, last_outcome)` are the **only** state
that needs to persist between planner runs.

---

## 3. Thompson sampling at the Bellman backup

The current backup is deterministic in η and p. We make it **stochastic** by
drawing once per node per backup-pass:

```hexa
fn sample_eta(post: BetaPost) -> f64 {
    // Draw a single Thompson sample from Beta(alpha, beta).
    return beta_sample(post.alpha, post.beta)
}

fn backup_node(n: Node, post_eta: BetaPost, post_p: BetaPost) -> f64 {
    let eta_s = sample_eta(post_eta)        // η ~ Beta(α_η, β_η)
    let p_s   = sample_eta(post_p)          // p ~ Beta(α_p, β_p)
    let learn = c_learn(n.cost, eta_s, n.n_uses)
    let exp_c = c_exp(learn, p_s)
    return exp_c
}
```

Across many backups this gives the explore/exploit trade-off for free:
high-uncertainty nodes (small α+β) produce wide samples → planner occasionally
schedules them to gather evidence; well-sampled nodes converge to their MAP
value and stop perturbing the schedule.

---

## 4. Persistence schema

File: `state/roadmap_eta_posterior.jsonl` (append-only, one row per update).

```json
{"ts":"2026-04-25T12:34:56Z","node_id":"BT-541","kind":"eta",
 "alpha":3.0,"beta":7.0,"n_trials":8,"last_outcome":"fail"}
{"ts":"2026-04-25T12:34:56Z","node_id":"BT-541","kind":"p",
 "alpha":5.0,"beta":1.0,"n_trials":5,"last_outcome":"success"}
```

Fields:
- `ts` — ISO-8601 UTC timestamp of the update.
- `node_id` — matches `Node.id` from `parse_node`.
- `kind` — `"eta"` or `"p"` (two posteriors per node).
- `alpha`, `beta` — current posterior parameters **after** the update.
- `n_trials` — `a + b` cumulative Bernoulli draws fed into this posterior.
- `last_outcome` — `"success"` | `"fail"` (the trial that produced this row).

Replay: at engine boot, fold the JSONL forward per `(node_id, kind)`, keeping
the last row's `(alpha, beta, n_trials)` as the live posterior. The author's
JSON `eta`/`p_success` is consulted **only** when no posterior row exists.

---

## 5. Hexa-like pseudocode — `update_posterior()`

```hexa
struct BetaPost {
    alpha: f64,
    beta:  f64,
    n_trials: i64,
    last_outcome: string
}

fn update_posterior(post: BetaPost, success: bool) -> BetaPost {
    let a_inc = if success { 1.0 } else { 0.0 }
    let b_inc = if success { 0.0 } else { 1.0 }
    return BetaPost {
        alpha: post.alpha + a_inc,
        beta:  post.beta  + b_inc,
        n_trials: post.n_trials + 1,
        last_outcome: if success { "success" } else { "fail" }
    }
}

fn record_trial(node_id: string, kind: string, success: bool) {
    let post  = load_posterior(node_id, kind)        // tail-fold JSONL
    let post2 = update_posterior(post, success)
    append_jsonl("state/roadmap_eta_posterior.jsonl",
                 jsonl_row(now_iso8601(), node_id, kind, post2))
}
```

`beta_sample(α, β)` is a 30-line Marsaglia-Tsang gamma-ratio sampler — it does
not call out to numpy/scipy, keeping the engine dependency-clean.

---

## 6. Honest scope (raw 71 falsifier)

**Stationary case (in scope).** Synthetic environment: a single node with true
η = 0.3, draws are i.i.d. Bernoulli(0.3). Run the engine for 50 trials,
recording posterior mean after each trial.

> **Falsifier (verbatim):** On a synthetic stationary environment with true
> η = 0.3, the posterior mean must converge to within ±0.05 of 0.3 within 50
> trials; if it does not, the axis is falsified for the stationary case.

Sanity check: with `α0 = β0 = 1`, after 50 trials the expected posterior
variance is ≈ `0.3·0.7 / 52 ≈ 0.004`, so std ≈ 0.063 — the ±0.05 bound is
tight but achievable at the posterior-mean level (not pointwise).

**Non-stationary case (out of scope).** If the true η drifts (e.g. as the
codebase matures, learning slows), a stationary Beta posterior will lag
arbitrarily. Proper handling needs a **particle filter** or **Bayesian
change-point detector** (e.g. BOCPD, Adams & MacKay 2007). r2 explicitly does
**not** ship that — a follow-up axis r2.1 is registered in the parent ω-cycle.

---

## 7. r12 acknowledgment — halting undecidable

The parent ω-cycle's theorem anchor r12 states that the planner cannot decide
whether the schedule's total time T* is finite. The Bayesian posterior does
**not** repeal r12:

- The posterior gives a **finite-horizon credible interval** for η at each
  node, conditional on the trials seen so far.
- It never produces a proof that T* converges. Even if every node's posterior
  collapses to a Dirac, the recursion `T_{k+1} = T_k · (1−η)` only proves
  **asymptotic** convergence in the limit, which is unobservable in finite
  trials.
- Concretely: a posterior with `α = 1000, β = 1` still permits η = 0 with
  prior probability mass `≈ 1/(α+β+1)` — small, but non-zero — and η = 0
  makes T* infinite.

So r2 narrows credible intervals; it does **not** decide halting. The
engine's existing `--max-iter` cap remains the only finitary safeguard.

---

## 8. LoC estimate

| Piece                                  | Lines |
|----------------------------------------|------:|
| `BetaPost` struct + accessors          |     8 |
| `beta_sample` (Marsaglia-Tsang)        |    30 |
| `update_posterior` + `record_trial`    |    18 |
| `load_posterior` (JSONL tail-fold)     |    22 |
| `parse_node` patch (seed prior from JSON) | 12 |
| `backup_node` Thompson hooks           |    14 |
| JSONL append helper + iso8601 stamp    |    10 |
| Falsifier harness `tools/r2_falsify.sh`|    16 |
| **Total**                              | **130** |

**130 LoC vs. 100 budget — overrun 30%.** The overrun lives almost
entirely in `beta_sample` (30 LoC). Mitigation options for the implementation
ω-cycle:

1. Accept the overrun (document in axis-close note).
2. Replace `beta_sample` with a 6-LoC normal approximation
   `η ~ N(μ, μ(1−μ)/(α+β+1))` valid for `α+β > 30` — falls back to uniform
   sampling otherwise. Saves 24 LoC, brings axis to 106.
3. Defer Thompson, ship posterior-mean only (greedy). Saves 30 LoC, brings
   axis to 100, but loses the explore/exploit story.

Recommendation: option (2). Document the approximation regime in the falsifier
harness output.

---

## 9. Out-of-scope / parked

- Hierarchical priors across sibling nodes.
- Correlated η/p posteriors via a 2D Dirichlet — current model treats them independent.
- JSONL compaction snapshot (r2.2); non-stationary η particle filter (r2.1, §6).

*End of dossier — r2 online-bayesian-eta — ω+1*
