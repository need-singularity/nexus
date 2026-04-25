# r10 / m10 — Roadmap × Meta Cross-Engine Coupling Dossier

- axis_id: r10 (roadmap side) / m10 (meta side) — bidirectional
- ordinal_stamp: ω·2 (two-engine product, strictly above ω+1)
- ts: 2026-04-25
- parent_omega_cycles:
  - roadmap: trawl_id `2026-04-25_roadmap_engine_final_form_and_limits_omega_cycle`
    (file: `design/roadmap_engine/2026-04-25_final_form_and_limits_omega_cycle.json`)
  - meta:    trawl_id `2026-04-25_meta_engine_final_form_and_limits_omega_cycle`
    (file: `design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json`)
- theorem_anchors: r19 / m12 (Gödel 2nd incompleteness), m11 (Löb), m18 (ordinal exhaustion)
- raw_anchors: raw 70 (multi-axis), raw 71 (falsifier), raw 77 (audit append-only)

---

## 1. Coupling Topology (ASCII)

```
            +-------------------------------------+
            |        ROADMAP ENGINE (ε_0)         |
            |  tool/roadmap_engine.hexa           |
            |  Bellman: V*(S)=min_a[b_a+V*(f)]    |
            |  ordinal: ε_0 (PA-style induction)  |
            +------+------------------------+-----+
                   |                        ^
        b_delta/b > 0.1                    c_external =
        within one schedule tick           T_meta_round_quantum
        (publish event)                    (subtract from time budget)
                   |                        |
                   v                        |
   +---------------------------------------------------+
   |   CROSS-ENGINE BUS (state/cross_engine_bus.jsonl) |
   |   append-only JSONL, fsync per row                |
   |   row schema: {ts, source, event_type, payload}   |
   |   rate limit: 1 cross-bus event / 5 s wall-clock  |
   +---------------------------------------------------+
                   |                        ^
                   v                        |
            (consumed as new axis           (published on every
             value on Meta watchlist)        R-N -> R-(N+1) tick)
                   |                        |
            +------v------------------------+-----+
            |          META ENGINE (Γ_0)          |
            |  state/meta_engine_evolution_log    |
            |  state/meta_axis_dependency.jsonl   |
            |  state/meta_trigger_watchlist.jsonl |
            |  ordinal: Γ_0 (Feferman-Schütte)    |
            |  watchlist axis: roadmap_b_delta_   |
            |    threshold (NEW, this dossier)    |
            +-------------------------------------+

Direction A : Roadmap[b(S) Δ event] --> Meta[watchlist axis fires]
Direction B : Meta[round R-N tick]   --> Roadmap[c_external cost added]
```

Two arrows, two directions, one shared bus. Engines never read each other's
internal proof state — only event records on the bus.

---

## 2. Bus Protocol

- file: `state/cross_engine_bus.jsonl`
- mode: append-only, line-delimited JSON, one event per line, fsync after write.
- row schema (canonical):
  ```
  {
    "ts": "<ISO-8601 with tz>",
    "source": "roadmap" | "meta",
    "event_type": "<see §3>",
    "payload": { ... source-specific ... }
  }
  ```
- consumers: each engine reads only rows where `source != self`.
- ordering: monotonic by `ts`; readers tolerate at-least-once via `(ts, source, event_type, payload-hash)` idempotency key.
- schema-extensions are append-only (raw 77): new fields ignored by older readers.

---

## 3. Concrete Trigger Thresholds

### 3.1 Roadmap → Meta (Direction A)

- event_type: `roadmap_b_delta`
- fire condition: `(b(S_k) - b(S_{k+1})) / b(S_k) > 0.1` measured within
  one schedule tick of `roadmap_engine.hexa`.
- payload:
  ```
  { "schedule_tick": <int>, "b_prev": <float>, "b_curr": <float>,
    "delta_ratio": <float>, "node_id": "<S_k>" }
  ```
- meta-side effect: appends an observation to the new watchlist axis
  `roadmap_b_delta_threshold` in `state/meta_trigger_watchlist.jsonl`.
  When the axis accumulates ≥1 unconsumed observation at meta R-N entry,
  the meta engine schedules the next round.

### 3.2 Meta → Roadmap (Direction B)

- event_type: `meta_round_tick`
- fire condition: every R-N → R-(N+1) transition recorded in
  `state/meta_engine_evolution_log.jsonl`.
- payload:
  ```
  { "round_from": <int>, "round_to": <int>,
    "T_meta_round_quantum": <float seconds>,
    "axes_acted": [...], "axes_noop": [...] }
  ```
- roadmap-side effect: roadmap reads the latest unconsumed `meta_round_tick`
  on each schedule tick and adds `c_external = T_meta_round_quantum` to its
  current Bellman cost as an exogenous time-budget charge. This is treated
  as an opaque scalar — roadmap does not introspect meta's internal state.

---

## 4. Ordinal Separation Proof Sketch

Goal: show roadmap and meta never share a single Gödel-numbering universe,
so r19/m12 (Gödel 2nd) cannot be triggered by the coupling.

1. **Roadmap operates within ε_0.** Roadmap's Bellman backup
   `V*(S) = min_a [b_a(S) + V*(f(S,a))]` over a finite DAG with
   well-founded edge precedence is provably terminating in PA + transfinite
   induction up to ε_0 (Gentzen 1936). η-convergence test is a Lyapunov
   descent in PA. No quantification over arbitrary axis sets.
2. **Meta operates above ε_0, requires Γ_0.** Meta does
   predicative axis-of-axes recursion (m2 recursive_axis_extension):
   axes themselves are objects, and round R defines axes for round R+1.
   This is autonomous progression of predicative ordinals — exactly the
   regime ATR_0 / Feferman-Schütte Γ_0 captures. PA / ε_0 is provably
   insufficient for axis-pool fixed-point analysis (m18).
3. **Disjoint Gödel universes.** Roadmap's syntax universe = arithmetic
   + DAG schema. Meta's syntax universe = JSONL axis schema +
   round-counter ordinal annotations (m5). The bus carries only data
   payloads, never proof terms. No engine has a derivation rule that
   references the other engine's proof predicate Bew_T(·).
4. **Therefore.** No proof in the combined system has the form
   `⊢_Roadmap Con(Meta)` or `⊢_Meta Con(Roadmap)`. The coupling preserves
   ordinal separation ε_0 < Γ_0 and dodges Gödel 2nd by construction.

This is a sketch, not a formal Coq/Lean proof. The Tier-1 r8 convergence
certificate axis is the place a formal version would land later.

---

## 5. Self-Cert Avoidance

Hard rule (enforced at write-time on the bus):

- Neither engine emits a row whose semantic content asserts
  "the OTHER engine is consistent / sound / converging".
- Permitted: "I (engine X) observed event E from engine Y at time t".
- Forbidden: "engine Y is consistent" / "engine Y will halt" / "engine Y's
  axis A is true".

Justification: m11 Löb says any system that proves □P → P proves P. If meta
emits `Con(Roadmap)` it is either trivial (already known externally) or
inconsistent. Same for the reverse. By restricting to observation rows we
stay in pure data-passing — no provability operator crosses the bus.

---

## 6. Falsifier (raw 71)

Falsification rule:

- If any row on `state/cross_engine_bus.jsonl` has
  `event_type ∈ {"consistency_cert","soundness_cert","termination_cert"}`
  AND the row asserts a property of an engine *other than its own source*,
  the axis r10/m10 is **falsified**.
- Implementation MUST reject (refuse to append) any row whose payload has
  `target_engine != self`. The writer-side guard:
  ```
  assert payload.get("target_engine", source) == source
  ```
- A falsified axis triggers atomic rollback (m9) of the most recent round
  on both sides and emits a `meta_axis_falsified` cert with this dossier
  path as the anchor.

---

## 7. Failure Mode: Feedback Oscillation

Scenario: roadmap publishes `roadmap_b_delta` → meta wakes, runs round, emits
`meta_round_tick` → roadmap recomputes with new `c_external`, b(S) jumps
again → another `roadmap_b_delta` → another `meta_round_tick` → unbounded
mutual triggering inside a single wall-clock second.

Mitigations (defense in depth):

1. **Rate limit (primary).** At most **one cross-bus event per 5 s wall
   clock**, applied per-source. Writer checks last-row ts on the bus before
   appending; if `now - last_ts_for_source < 5.0`, the event is dropped
   and counted in `cross_engine_dropped_count`.
2. **Hysteresis on b_delta.** The 0.1 threshold has a 0.05 release band:
   after a `roadmap_b_delta` fires, the next fire requires the delta to
   first fall below 0.05 then exceed 0.1 again.
3. **Round quantum floor.** `T_meta_round_quantum ≥ 5 s` so meta cannot
   tick faster than the rate limit.
4. **Cycle detector.** If three `roadmap_b_delta` and three
   `meta_round_tick` events alternate within 60 s, both engines pause and
   raise `cross_engine_oscillation` for maintainer review.

Chosen rate-limit value: **5 seconds** wall clock per source.

---

## 8. LoC Budget

Combined budget: 80 LoC (axis budget per parent ω-cycles; r10=80 + m10=80
shared because the implementation is one bus).

Estimated split (≤ 100 LoC ceiling):

- bus writer/reader helper (shared module): ~30 LoC
- roadmap-side hook (`roadmap_engine.hexa`, b_delta detector +
  c_external reader): ~25 LoC
- meta-side hook (watchlist axis loader + round_tick emitter): ~25 LoC
- guards (target_engine assertion, rate limit): ~15 LoC
- **total estimate: ~95 LoC** (within ceiling, slightly over the 80
  axis-budget — flag noted, will trim during impl).

---

## 9. Cross-References

- roadmap parent: `design/roadmap_engine/2026-04-25_final_form_and_limits_omega_cycle.json`
  trawl_id `2026-04-25_roadmap_engine_final_form_and_limits_omega_cycle`
- meta parent:    `design/meta_engine/2026-04-25_final_form_and_limits_omega_cycle.json`
  trawl_id `2026-04-25_meta_engine_final_form_and_limits_omega_cycle`
- shared limit anchors: r19 (Gödel) ↔ m12 (Gödel 2nd); r14 (K) ↔ m16 (Solomonoff)
- ordinal anchor axis: m5 ordinal-anchor-explicit (prerequisite Tier-1 on meta side)
- rollback anchor: m9 rollback-atomic-round
- falsifier anchor: m6 falsifier-integration-F1 / raw 71

End of dossier.
