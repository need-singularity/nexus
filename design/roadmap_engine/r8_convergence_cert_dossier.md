# r8 — Convergence Certificate Dossier

- Parent ω-cycle: `design/roadmap_engine/2026-04-25_final_form_and_limits_omega_cycle.json`
- Subject: `tool/roadmap_engine.hexa`
- Axis: r8 convergence-certificate
- Theorem anchor: r19 Gödel 2nd incompleteness — `⊢ Con(T)` impossible from within `T`
- Ordinal stamp: **ω+1** (the cert sits one rung above the schedule it certifies)
- Date: 2026-04-25

---

## 1. Problem

The current `roadmap_engine.hexa` schedule path emits an **operational event log** via `emit_schedule_events` (defined near line 1047, called at lines 1186, 1207, 1282, 1288 of `tool/roadmap_engine.hexa`). The events JSONL captures `Plan`, `NodeStart`, `NodeComplete`, `BottleneckShift`, `Replan` — useful for telemetry, but it is **not a logical artifact**:

- It does not state assumptions under which `T_star` is meaningful.
- It does not exhibit the Bellman recurrence instance backing the value.
- It does not anchor the soundness claim to any external well-founded ordinal.
- A consumer cannot, from the events alone, re-verify that the reported `T_star` is an admissible upper bound.

The events log is a **trace**; what the engine lacks is a **witness** — a structured certificate per schedule run that an external verifier can mechanically check, while explicitly disclaiming self-consistency (Gödel 2nd).

---

## 2. Certificate Schema (JSON)

One JSON object per schedule run, appended to `state/roadmap_convergence_cert.jsonl`.

```jsonc
{
  "cert_version": "r8.v1",
  "ordinal_stamp": "ω+1",
  "roadmap_id": "<rm.id>",
  "schedule_run_id": "<uuid-or-hash>",
  "ts": "<ISO-8601>",

  "assumptions": {
    "dag_acyclic":            true,    // toposort succeeded; no back edges
    "eta_positive":           true,    // η_current > 0 over the horizon
    "costs_finite":           true,    // ∀ node n: b(n) < ∞
    "channel_capacity_lower": 1.0      // min concurrent channel capacity assumed
  },

  "T_star_upper_bound": 42.0,          // = Σ b(S_k) on the chosen path

  "bellman_lemma": {
    "form": "V*(S) = min_a [b_a(S) + V*(f(S,a))]",
    "instance": [
      { "S": "s0", "a": "n1", "b_a": 3.0, "V_next": 39.0, "V_S": 42.0 },
      { "S": "s1", "a": "n2", "b_a": 5.0, "V_next": 34.0, "V_S": 39.0 }
      // … one row per state on the chosen path; terminal V* = 0
    ]
  },

  "ordinal_anchor": {
    "system":                "PA",
    "proof_theoretic_ordinal":"ε_0",
    "external_witness":      "Gentzen 1936 — Die Widerspruchsfreiheit der reinen Zahlentheorie"
  },

  "self_cert_disclaimer":
    "this cert does not prove its own consistency (Gödel 2nd); soundness is asserted only relative to the external ε_0 witness above"
}
```

Field semantics:

| Field | Meaning |
|---|---|
| `assumptions` | Predicates the bound depends on; verifier must re-check each. |
| `T_star_upper_bound` | The bound the engine **claims**; admissibility falsifier in §4. |
| `bellman_lemma.instance` | Ledger of `(S, a, b_a, V_next, V_S)` rows with `V_S = b_a + V_next` checkable by arithmetic. |
| `ordinal_anchor` | Names the **external** well-founded ordinal (ε_0) that grounds termination — a Gentzen-style escape from the Gödel 2nd trap. |
| `self_cert_disclaimer` | Object-level acknowledgment that the cert is not self-justifying. |

---

## 3. Verification Protocol

External script: `verify_cert.py` (kept outside the engine — different trust boundary).

Inputs:
- one cert object from `state/roadmap_convergence_cert.jsonl`
- the corresponding events JSONL run (matched by `roadmap_id` + `schedule_run_id`)

Checks (each pass/fail):

1. **Schema check** — all required keys present and well-typed.
2. **Assumption replay** — re-derive `dag_acyclic`, `eta_positive`, `costs_finite` from the events; flag any disagreement.
3. **Bellman recurrence** — for each row in `bellman_lemma.instance`, assert `V_S == b_a + V_next` within float epsilon (e.g., 1e-9).
4. **Path sum** — assert `T_star_upper_bound == Σ b_a` over the rows.
5. **Trace alignment** — the ordered `(S, a)` pairs equal the in-order sequence of `NodeStart` / `NodeComplete` in the events log.
6. **Ordinal anchor presence** — `ordinal_anchor.system == "PA"` and `proof_theoretic_ordinal == "ε_0"`.

Verifier returns: `{verified: bool, failures: [..]}`. The verifier itself is **object-language**; its soundness lives in metalanguage (§5).

---

## 4. Falsifier (raw 71)

**Falsifier construction.** Build a hand-crafted DAG with known optimal makespan `T*_true` (e.g., 4 nodes in a diamond, costs `[1, 2, 3, 4]`, optimal critical path = `7`). Run the engine over it and read the emitted cert.

**Admissibility predicate**

```
T_star_upper_bound  ≥  T*_true
```

If a cert ever reports `T_star_upper_bound < T*_true`, the bound is **inadmissible** and axis r8 is falsified — the certificate is making a stronger claim than is true and must be rejected wholesale, not patched.

A second smoke-test falsifier: introduce a deliberate cycle and confirm that `assumptions.dag_acyclic` becomes `false` and **no** cert is emitted (instead an explicit refusal record).

---

## 5. Gödel / Löb Acknowledgment

The certificate is a **witness**, not a **proof**:

- By **Gödel 2nd**, the engine cannot, from inside its own theory `T`, prove `Con(T)`. So the cert deliberately omits any self-consistency clause and instead *names* the external ordinal anchor (ε_0, Gentzen 1936) on which termination/soundness rests.
- By **Löb's theorem**, were the engine to assert `□φ → φ` for its own proof predicate it would already prove `φ` for any `φ` — another reason internal self-certification is rejected.
- The split is therefore: the **verifier** speaks the **object language** (arithmetic on the recorded rows), while the **soundness statement** ("if the assumptions hold and the Bellman ledger checks, then `T_star_upper_bound` admissibly bounds the true makespan") lives in the **metalanguage** of whoever audits the cert.

The cert thus achieves what a self-cert cannot: **third-party checkability** with an honest disclaimer about its own limits.

---

## 6. Output Path

- **File:** `state/roadmap_convergence_cert.jsonl`
- **Mode:** append-only (one JSON object per line, per schedule run)
- **Co-located with:** the existing events JSONL stream produced by `emit_schedule_events`
- **Retention:** unbounded (cert stream is small — one record per run, not per event)
- **Pairing:** each cert references its events run via `(roadmap_id, schedule_run_id)` so `verify_cert.py` can join the two streams.

---

## 7. Estimated LoC

- Axis budget: **120 LoC**
- Estimate: **≤ 150 LoC**, broken down as:
  - cert struct + JSON serializer: ~40
  - `emit_convergence_cert(rm, sched, path)` (sibling of `emit_schedule_events`): ~50
  - Bellman ledger reconstruction from `sched`: ~40
  - call-site wiring at the four existing emit sites: ~10
  - `verify_cert.py` is **out of scope** (separate file, separate language, separate trust domain)

The 30-LoC overshoot is justified by the bellman ledger row construction — without it, the cert degenerates back into a glorified events line.

---

## 8. Concrete JSON Cert Example

```json
{"cert_version":"r8.v1","ordinal_stamp":"ω+1","roadmap_id":"rm_demo","schedule_run_id":"run_2026-04-25T23:50:00Z_a1b2","ts":"2026-04-25T23:50:00Z","assumptions":{"dag_acyclic":true,"eta_positive":true,"costs_finite":true,"channel_capacity_lower":1.0},"T_star_upper_bound":7.0,"bellman_lemma":{"form":"V*(S) = min_a [b_a(S) + V*(f(S,a))]","instance":[{"S":"s0","a":"n_a","b_a":1.0,"V_next":6.0,"V_S":7.0},{"S":"s1","a":"n_b","b_a":3.0,"V_next":3.0,"V_S":6.0},{"S":"s2","a":"n_d","b_a":3.0,"V_next":0.0,"V_S":3.0}]},"ordinal_anchor":{"system":"PA","proof_theoretic_ordinal":"ε_0","external_witness":"Gentzen 1936"},"self_cert_disclaimer":"this cert does not prove its own consistency (Gödel 2nd); soundness is asserted only relative to the external ε_0 witness above"}
```

(Diamond DAG, optimal path `n_a → n_b → n_d` with costs `1 + 3 + 3 = 7`; falsifier predicate `7.0 ≥ 7.0` holds.)
