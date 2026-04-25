# Beyond-Omega Daily Plist — Activation Guide

> **Pair**: `tool/com.nexus.beyond-omega-daily.plist` (cycle 10) ↔ `tool/beyond_omega_ghost_trace.py` (cycle 5 v4 `--cron`)
> **Origin**: `nxs-20260425-004` cycle 10 (registered) → cycle 28 (activation prep, this doc).
> **State**: pre-flight verified, **plist NOT yet loaded into launchd** — user authorization required.

---

## §1 What this activates

A daily LaunchAgent that fires once per day at **03:13 local time** and runs:

```sh
/opt/homebrew/bin/python3 /Users/ghost/core/nexus/tool/beyond_omega_ghost_trace.py --cron
```

`--cron` mode = `--append` + summary snapshot:

- appends new `NEXUS_OMEGA` emits to `state/ghost_ceiling_trace.jsonl` (file:lineno dedup → idempotent)
- writes daily snapshot `state/ghost_ceiling_summary.daily.YYYY-MM-DD.json` (~6-10 KB / day)
- writes/overwrites `state/ghost_ceiling_summary.json` (latest)
- runs in **default protected mode** (`NEXUS_BACK_ACTION_ON` unset) → cycle 5 `SELF_OUTPUTS` skip 활성, first-order distribution timeline 만 누적. cycle 8 second-order echo 는 본 plist 가 측정하지 않음.

Expected disk usage: ≤ 300 KB / 30 days. Recommend `gitignore` for `state/ghost_ceiling_summary.daily.*.json`.

---

## §2 Pre-flight verification (already completed in cycle 28)

| check | command | result |
|---|---|---|
| plist syntax | `plutil -lint tool/com.nexus.beyond-omega-daily.plist` | `OK` |
| python3 binary | `/opt/homebrew/bin/python3 --version` | `Python 3.14.3` |
| probe script exists | `ls tool/beyond_omega_ghost_trace.py` | `11672 bytes, executable` |
| manual --cron one-shot | `/opt/homebrew/bin/python3 tool/beyond_omega_ghost_trace.py --cron` | `files_scanned=492 emits=7 approach=1 elapsed=0.205s` |
| daily snapshot landed | `ls state/ghost_ceiling_summary.daily.2026-04-25.json` | `2412 bytes, schema v4 OK` |

All pre-flight checks pass — plist is safe to load.

---

## §3 Activation (user runs these — requires Full Disk Access / authorization)

```sh
# 1. Copy the plist into LaunchAgents (non-destructive — overwrites only the same Label)
cp /Users/ghost/core/nexus/tool/com.nexus.beyond-omega-daily.plist \
   ~/Library/LaunchAgents/

# 2. Bootstrap into the GUI domain (asks for permission first time on macOS)
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.nexus.beyond-omega-daily.plist

# 3. Enable (not strictly required after bootstrap, but explicit)
launchctl enable gui/$UID/com.nexus.beyond-omega-daily

# 4. (optional) immediate first snapshot — skip waiting for next 03:13
launchctl kickstart -k gui/$UID/com.nexus.beyond-omega-daily
```

---

## §4 Verification (after activation)

```sh
# Listed by launchd?
launchctl list | grep beyond-omega
# → expect:  -    0    com.nexus.beyond-omega-daily

# Full plist dump
launchctl print gui/$UID/com.nexus.beyond-omega-daily

# Stdout / stderr logs (live tail)
tail -F /tmp/nexus_beyond_omega_daily.out.log /tmp/nexus_beyond_omega_daily.err.log

# Daily snapshot files (one per day)
ls -la /Users/ghost/core/nexus/state/ghost_ceiling_summary.daily.*.json

# Today's snapshot content
cat /Users/ghost/core/nexus/state/ghost_ceiling_summary.daily.$(date +%Y-%m-%d).json | head -30
```

If kickstart was used and the run succeeded, expect:

- `/tmp/nexus_beyond_omega_daily.out.log` → one line `⊙ ghost_trace files_scanned=… emits=… approach=… mode=cron new=… elapsed=…s`
- `/tmp/nexus_beyond_omega_daily.err.log` → empty
- `state/ghost_ceiling_summary.daily.<today>.json` → ~6-10 KB schema-v4 JSON

---

## §5 Disable / uninstall

```sh
launchctl bootout gui/$UID/com.nexus.beyond-omega-daily
rm ~/Library/LaunchAgents/com.nexus.beyond-omega-daily.plist
```

`bootout` is the inverse of `bootstrap`. It also removes any pending kickstart and stops the agent. Existing daily snapshots in `state/` are NOT deleted by uninstall.

---

## §6 Troubleshooting

- **`launchctl bootstrap` fails with `Bootstrap failed: 5: Input/output error`** — usually a stale entry. Run `launchctl bootout gui/$UID/com.nexus.beyond-omega-daily` first, then re-bootstrap.
- **plist loads but never runs** — check `launchctl print` `state` field; if `not running` and `last exit code` is non-zero, see `/tmp/nexus_beyond_omega_daily.err.log`.
- **Permission prompt on first bootstrap** — macOS may ask for Full Disk Access for the `python3` binary so it can scan `~/Library/Logs/nexus/`. Grant once.
- **Probe writes 0 new rows** — expected on idle days (no new `NEXUS_OMEGA` emits). The daily snapshot is still produced.
- **Wanting cycle 8 second-order echo** — set `NEXUS_BACK_ACTION_ON=1` in a separate plist (`com.nexus.beyond-omega-echo.plist`); do NOT enable both with the same Label.

---

## §7 References

- `tool/com.nexus.beyond-omega-daily.plist` — the plist itself (top-of-file comments mirror this guide)
- `tool/beyond_omega_ghost_trace.py` — probe (cycle 5 v4, `--cron` / `--append` modes)
- `design/beyond_omega_ladder.md` §13 (cycle 10 registration), §31 (cycle 28 activation prep)
- `state/proposals/inventory.json` `nxs-20260425-004` `cycle_28_finding_2026_04_25`
- Reference plists with the same skeleton: `tool/com.nexus.atlas-meta-scan.plist`, `tool/com.nexus.omega-metrics.plist`
