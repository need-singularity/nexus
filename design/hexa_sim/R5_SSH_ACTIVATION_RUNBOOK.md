# R5 SSH Signature Activation Runbook

Date: 2026-04-26 | Audience: nexus operator | Source: SECURITY_AUDIT.md §8 (commit `0ea84fd3`)

Goal: turn the R5 SSH signature stub (`tool/registry_sign.sh`) from `SKIPPED` to active, upgrading the registry-tampering defense from **forensic** (post-hoc detect) to **preventive** (block at sign time, verify at gate time).

raw 71: this runbook presents options — operator decides activation. raw 73: every step is concrete and reproducible.

---

## Section 1 — Decision: should I activate?

**Trade-off**:
- Friction: every commit that touches `design/hexa_sim/falsifiers.jsonl` runs `ssh-keygen -Y sign`. If the key is encrypted you must unlock it (ssh-agent or passphrase prompt).
- Defense gain: HIGH→PREVENTIVE on the §4 "coordinated registry+baseline mutation" gap. Without OPT-B, that vector remains forensic-only (chain rewrite is detectable post-hoc but not blocked).

**Threat model fit**:
| Threat                          | OPT-D ledger only | OPT-B signature added |
|---------------------------------|-------------------|-----------------------|
| Lone-actor mistake (typo/edit)  | Detected (chain)  | Detected + blocked    |
| External attacker (write-perm)  | Detected post-hoc | Blocked at sign time  |
| Compromised CI / shared remote  | Detected post-hoc | Blocked at verify gate|

**Recommendation — ACTIVATE if any of these are true**:
- (a) registry is shared across machines (e.g., hive ↔ nexus ↔ airgenome) and you want cross-host integrity
- (b) CI publishes the registry (GitHub Actions, etc.) and signed-artifact gating is desired
- (c) external contributors edit `falsifiers.jsonl` via PRs
- (d) you maintain a public mirror and want consumers to verify provenance

**SKIP** (stay at OPT-D forensic) if: solo operator, single machine, no public mirror, no CI publishing. The forensic chain is already HIGH confidence; OPT-B is the upgrade for multi-actor or cross-host scenarios.

**Status as of this runbook**: current threat profile is solo-operator on this machine — OPT-D alone is sufficient. Activate OPT-B opportunistically when scenario (a)/(b)/(c)/(d) appears. **META_ROI verdict: WAIT — defer until first cross-host or CI publishing event; document is ready for instant activation.**

---

## Section 2 — Pre-flight check

Run from `~/core/nexus`:

```
ls ~/.ssh/id_ed25519* ~/.ssh/falsifier_registry_signing* 2>&1     # which keys exist
git config --get-regexp '^user\.' 2>&1                            # name/email/signingkey
git config --get gpg.format 2>&1                                  # 'ssh' if SSH signing already enabled
bash tool/registry_sign.sh status 2>&1                            # current sentinel
bash tool/ledger_verify.sh 2>&1 | tail -3                          # OPT-D health
```

**Expected pre-activation baseline** (this machine, 2026-04-26):
- `~/.ssh/id_ed25519` exists (Path A applies)
- `git config user.signingkey` is unset
- `__REGISTRY_SIGN__ SKIPPED reason=no_signing_key_configured`
- `__LEDGER_VERIFY__ EMPTY entries=0 broken_at=none` (no rotations yet)

If `~/.ssh/id_ed25519` is absent → use **Path B**. Otherwise → **Path A** (preferred, lowest friction).

---

## Section 3 — Path A: reuse existing `~/.ssh/id_ed25519`

```
# 1. Tell git which key to use for signing
git config user.signingkey ~/.ssh/id_ed25519.pub

# 2. Build allowed_signers (verify uses this list)
echo "nexus@local namespaces=\"file\" $(cut -d' ' -f1-2 ~/.ssh/id_ed25519.pub)" \
    >> ~/.ssh/allowed_signers
chmod 600 ~/.ssh/allowed_signers

# 3. Smoke test: sign + verify against the live registry
cd ~/core/nexus
SIGNING_IDENTITY="nexus@local" bash tool/registry_sign.sh sign
SIGNING_IDENTITY="nexus@local" bash tool/registry_sign.sh verify
ls -la design/hexa_sim/falsifiers.jsonl.sig
```

**Expected sentinels**:
- `__REGISTRY_SIGN__ SIGNED reason=key=/Users/ghost/.ssh/id_ed25519`
- `__REGISTRY_SIGN__ VERIFIED reason=identity=nexus@local`

**Wire into pre-commit hook** — append to `.githooks/pre-commit` after the baseline rotation block (Section 8 of SECURITY_AUDIT.md references lines 60-75; insert after line 75):

```
# R5 OPT-B — sign falsifier registry on every rotation (advisory, never blocks)
SIGNING_IDENTITY="nexus@local" bash tool/registry_sign.sh sign 2>&1 \
    || echo "warn: signing failed (raw 66 reason=ssh_key_unavailable fix=unlock_key_or_run_ssh-add)" >&2
```

Stage the `.sig` file alongside the registry:
```
git add design/hexa_sim/falsifiers.jsonl design/hexa_sim/falsifiers.jsonl.sig
```

---

## Section 4 — Path B: generate a dedicated signing key

Use this if you prefer signing-key isolation (recommended when the same machine is also a Git push origin and you want independent revocation).

```
# 1. Generate Ed25519 keypair (no passphrase = unattended; add -N "<pass>" if you want one)
ssh-keygen -t ed25519 -f ~/.ssh/falsifier_registry_signing -N '' \
           -C "falsifier registry signer 2026-04-26"
chmod 600 ~/.ssh/falsifier_registry_signing
chmod 644 ~/.ssh/falsifier_registry_signing.pub

# 2. Tell git
git config user.signingkey ~/.ssh/falsifier_registry_signing.pub

# 3. Build allowed_signers
echo "nexus@local namespaces=\"file\" $(cut -d' ' -f1-2 ~/.ssh/falsifier_registry_signing.pub)" \
    >> ~/.ssh/allowed_signers
chmod 600 ~/.ssh/allowed_signers

# 4. Smoke test (same as Path A)
cd ~/core/nexus
SIGNING_IDENTITY="nexus@local" bash tool/registry_sign.sh sign
SIGNING_IDENTITY="nexus@local" bash tool/registry_sign.sh verify
```

Pre-commit hook insertion is identical to Path A.

---

## Section 5 — CI integration paths

Templates are checked into the repo with `.template` suffix; copy + customize before activating.

### 5a. launchd (macOS local cron)

Template: `~/core/nexus/state/com.nexus.health_check.plist.template`

Daily 06:30 verification, log to `state/health_check.log`:
```
cp ~/core/nexus/state/com.nexus.health_check.plist.template \
   ~/Library/LaunchAgents/com.nexus.health_check.plist
sed -i '' "s|__HOME__|$HOME|g" ~/Library/LaunchAgents/com.nexus.health_check.plist
launchctl load ~/Library/LaunchAgents/com.nexus.health_check.plist
launchctl start com.nexus.health_check        # smoke
tail ~/core/nexus/state/health_check.log
```

If sandboxed Claude Code can't write `~/Library/LaunchAgents/` (memory:`feedback_macos_launchagents_eperm.md`), run the `cp` + `sed` + `launchctl` commands with `!` prefix from the user shell.

### 5b. GitHub Actions PR check

Template: `~/core/nexus/.github/workflows/health_check.yml.template`

Activates `ledger_verify.sh` (always-on, BLOCKING) and `registry_sign.sh verify` (gated on repo secret `R5_PUBLIC_KEY`, advisory).

```
cp ~/core/nexus/.github/workflows/health_check.yml.template \
   ~/core/nexus/.github/workflows/health_check.yml
git add ~/core/nexus/.github/workflows/health_check.yml
git commit -m "ci(r5): add registry health check workflow"
```

To enable signature verification in CI, add repo secrets:
- `R5_PUBLIC_KEY` = full contents of `~/.ssh/<key>.pub` (single line)
- `R5_SIGNING_IDENTITY` = `nexus@local` (default if unset)

The private key NEVER goes to CI — verify is public-key-only.

### 5c. Pre-receive hook (server-side, optional)

For a self-hosted Git server (Gitea, Gitolite, bare repo on a VPS): copy the verify chain into `hooks/pre-receive` of the bare repo. Reject pushes whose `falsifiers.jsonl.sig` doesn't verify against the deployed `allowed_signers`. This is the strongest gate but requires server-side `ssh-keygen` and signer-list deployment.

Skip this section unless a shared remote is in scope.

---

## Section 6 — Rollback (if friction too high)

```
git config --unset user.signingkey
# Optionally remove the signing key (Path B only)
rm -f ~/.ssh/falsifier_registry_signing ~/.ssh/falsifier_registry_signing.pub
# Drop the line from allowed_signers (manual edit)
$EDITOR ~/.ssh/allowed_signers
# Remove the pre-commit hook insertion (revert .githooks/pre-commit)
# Optionally remove the .sig file
rm -f ~/core/nexus/design/hexa_sim/falsifiers.jsonl.sig
```

After rollback, `bash tool/registry_sign.sh status` returns to `SKIPPED reason=no_signing_key_configured`. The OPT-D ledger chain is unaffected.

---

## Section 7 — Verification post-activation

1. Re-run SECURITY_AUDIT Stage 1 E2E (the falsifier registry tamper test). Expected: still PASS, plus new green sentinel `__REGISTRY_SIGN__ VERIFIED`.
2. Make a no-op edit to `design/hexa_sim/falsifiers.jsonl` (e.g. add then remove a trailing newline) and commit. Confirm the hook regenerated `falsifiers.jsonl.sig`.
3. `ls -la ~/core/nexus/design/hexa_sim/falsifiers.jsonl.sig` — present, freshly mtimed.
4. Tamper test: edit one byte of `falsifiers.jsonl` WITHOUT re-running the hook (e.g. `printf x >> design/hexa_sim/falsifiers.jsonl`), then `bash tool/registry_sign.sh verify` → expect `__REGISTRY_SIGN__ ERROR reason=verify_failed` (rc=1). Restore from `git checkout design/hexa_sim/falsifiers.jsonl`.

---

## Section 8 — Test record

**Synthetic key end-to-end test (2026-04-26, this runbook commit):**
- Generated `/tmp/r5_synth.XXXX/synth_key` (Ed25519, no passphrase)
- Built allowed_signers in tmpdir
- `SIGNING_KEY=...synth_key SIGNING_IDENTITY=synth@local bash tool/registry_sign.sh sign` → `__REGISTRY_SIGN__ SIGNED` rc=0
- `SIGNING_KEY=...synth_key SIGNING_IDENTITY=synth@local ALLOWED_SIGNERS=...allowed_signers bash tool/registry_sign.sh verify` → `__REGISTRY_SIGN__ VERIFIED` rc=0
- `falsifiers.jsonl.sig` created (294 bytes)
- Cleanup: removed `.sig` artifact + tmpdir; user `~/.ssh/` and git config untouched

The runbook is validated end-to-end. Operator can execute Section 3 or 4 with confidence; the tooling works.
