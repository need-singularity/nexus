# m3 External Trust Anchor — Git Tag + Detached Signature Workflow

Spec for a6 (Tier-1 of 2026-04-26_m3_p5_tarski_verifier_omega_cycle). Truncates Tarski
meta-verifier regress at V_1 by **epistemic decree**, not formal proof. Stamp: ω·2+2.

## 1. Workflow (anchor publication)

1. **Compute chain_head_hash** — `chain_head_hash = sha256(last_row_of state/meta_decision_cert.jsonl)`,
   the most recent cert row's content-address as maintained by the m3.p3 hash chain. The
   anchor merely *publishes* it.
2. **Derive tag name** — `tag_name = "meta-cert-anchor-YYYY-MM-DD-HHMMSS-<short_hash>"`
   where `short_hash = chain_head_hash[:12]`. UTC. Example:
   `meta-cert-anchor-2026-04-26-143022-a3f2b9c1d4e5`.
3. **Create annotated, signed git tag** — `git tag -a -s <tag_name> -m '<chain_head_hash>'`.
   Annotation message **is exactly** the 64-char hex chain_head_hash (no prefix, no
   newline). `-s` requests detached PGP/SSH signature with the configured key.
4. **Push the tag** — `git push origin <tag_name>`. Third-party (GitHub server) timestamps
   receipt; neither populator nor verifier controls that timestamp.
5. **Record in anchor log** — append one row to `state/meta_cert_anchor_log.jsonl` per
   `spec/m3_anchor_log_schema.json` (ts, chain_head_hash, tag_name, signed_by_keyid,
   anchored_round_range, verification_command); append-only, fsync.

## 2. Trust assumption list

Anchor strength requires **all** of these to hold simultaneously:

1. **Local SSH/PGP signing key** — operator's private key uncompromised; passphrase-protected;
   not exfiltrated. Compromise scenario in §5.
2. **GitHub server (or chosen remote)** — receives the push, records server-side receipt
   time, does not collude with operator to backdate. GitHub is the third-party clock.
3. **Git transport protocol** — TLS to remote intact; no MITM rewriting tag content in flight.
4. **Git's internal hashing (SHA-1)** — git still uses SHA-1 for object IDs as of 2026.
   SHA-1 is **collision-broken** (Stevens et al. 2017 SHAttered; Leurent–Peyrin 2020
   chosen-prefix). Practical exploitation against tag objects is non-trivial but **NOT
   theorem-strong**. SHA-256 git transition (`extensions.objectFormat=sha256`) ongoing;
   honest limitation — anchor is only as strong as git's hash agility.
5. **SHA-256 of cert log content** — chain_head_hash uses SHA-256 (computed by populator),
   independent of git's SHA-1; collision resistance currently sound.
6. **Public observability** — at least one third-party (besides operator) periodically
   fetches tags and could detect retroactive rewrites. Trust degrades to operator-self-trust
   without an observer.

This is **Münchhausen "dogmatic stop"** at the external anchor — not a proof.

## 3. Verification protocol

Anyone with read access to the remote can independently verify:

```
git fetch --tags
git tag -v <tag_name>                       # checks signature, prints keyid
git cat-file -p <tag_name> | sed -n '6p'    # annotation line = chain_head_hash
# Recompute chain_head_hash locally over rounds in anchored_round_range; compare.
```

PASS iff: (a) `git tag -v` exits 0 with a known-trusted keyid AND (b) annotation equals
recomputed chain_head_hash byte-for-byte AND (c) every cert row with `round ∈
anchored_round_range` re-hashes consistently with the chain.

## 4. Rotation policy

> **Anchor every 10 cert rounds OR every 24 hours, whichever comes first.**

10 rounds bounds blast-radius of an undetected populator bug to one anchor window; 24h
ceiling covers low-activity periods so a stale chain_head still gets a fresh public
timestamp daily. Thresholds recorded per row via `anchored_round_range`. Missed rotation
(>24h with ≥1 unanchored round) is itself a falsifier signal (F5, see anchor_falsifier).

## 5. Key-compromise contingency

1. **Stop publishing** under the compromised key immediately.
2. **Generate new keypair**; distribute pubkey through the same channels as before, with
   explicit rotation notice referencing the *last known good* anchor tag.
3. **Republish from last good anchor**: re-anchor current chain_head under the new key.
   New row records `signed_by_keyid = <new_keyid>` and a `notes` field pointing back to
   the last good tag under the old keyid. Chain history before the compromise window is
   not rewritten (append-only); rotation event itself is part of the audit trail. Old
   tags remain as record; consumers treat anchors signed by the revoked keyid *after*
   compromise as **untrusted**.
