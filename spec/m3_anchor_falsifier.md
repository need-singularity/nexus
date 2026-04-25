# m3 External Anchor — Raw 71 Falsifier

Companion to `m3_external_anchor_workflow.md` + `m3_anchor_log_schema.json`. Specifies
conditions under which a published anchor is **REFUTED**.

For any row in `state/meta_cert_anchor_log.jsonl`, anchor is REFUTED if **any** holds:

- **F1 — signature failure.** `git fetch --tags && git tag -v <tag_name>` exits non-zero,
  OR exits zero but reports a keyid ≠ row's `signed_by_keyid`, OR reports a key revoked
  at or before `ts`.
- **F2 — annotation mismatch.** Tag annotation (via `git cat-file -p <tag_name>`) does
  NOT byte-for-byte equal the row's `chain_head_hash`.
- **F3 — chain divergence.** Recomputing sha256 over `state/meta_decision_cert.jsonl`
  across `anchored_round_range` produces a chain head ≠ `chain_head_hash`. Equivalently:
  ANY cert row with `round ∈ anchored_round_range` hashes differently from the chain
  leading to `chain_head_hash`.
- **F4 — missing tag.** The tag is absent from `git tag -l` after fetching from the
  canonical remote.
- **F5 — rotation breach.** Round R exists with `R > max(to_round)` AND
  `(now - latest ts) > 24h` AND `R - latest to_round ≥ 10`.

Any single F1–F4 failure falsifies that anchor row. F5 falsifies operator adherence to
rotation policy, not a published anchor itself. A REFUTED anchor does NOT retroactively
un-publish (append-only): the next anchor row MUST include a `notes` field citing the
refuted tag and failing falsifier ID.

Out of scope: Rice-undecidability of verifier semantics (b5); Löb-style self-trust
collapse (b6); SHA-1 collision attacks on git internals (acknowledged limitation,
external collision evidence required — not falsifiable here).
