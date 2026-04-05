//! Pack: CLI-only nexus6 integration installer.
//!
//! Zero API calls. Pure local filesystem operations:
//!   - symlink nexus6 binary into ~/.cargo/bin
//!   - write hook shell scripts to ~/.nexus6/hooks/
//!   - merge hook entries into ~/.claude/settings.json
//!
//! Removes nothing unless the user calls `nexus6 pack uninstall`.

pub mod hook_cmd;

use std::path::PathBuf;
use std::fs;

use serde_json::{json, Value};

const HOOKS_MARKER: &str = "nexus6-pack";

/// Hook script templates.
/// Each entry: (name, event, matcher, body).
const HOOK_SCRIPTS: &[(&str, &str, &str, &str)] = &[
    (
        "post_bash_detect",
        "PostToolUse",
        "Bash",
        r#"#!/bin/bash
# nexus6-pack hook: pipe bash tool output to nexus6 detect (micro-cycle)
# No network, no API — pure local detection.
set -euo pipefail
# Read JSON payload from stdin (Claude Code hook contract)
PAYLOAD="$(cat)"
# Best-effort extract tool output; skip silently on failure
OUTPUT="$(printf '%s' "$PAYLOAD" | /usr/bin/python3 -c 'import sys,json
try:
  d=json.load(sys.stdin)
  print(d.get("tool_response",{}).get("stdout","") or d.get("tool_output",""))
except Exception:
  pass' 2>/dev/null || true)"
if [ -n "$OUTPUT" ] && command -v nexus6 >/dev/null 2>&1; then
  printf '%s' "$OUTPUT" | nexus6 detect --adaptive --promote >> "$HOME/.nexus6/hook_detect.log" 2>&1 || true
fi
exit 0
"#,
    ),
    (
        "session_start_check",
        "SessionStart",
        "",
        r#"#!/bin/bash
# nexus6-pack hook: ensure nexus6 daemon is alive at session start.
set -euo pipefail
PID_FILE="$HOME/.nexus6/daemon.pid"
ALIVE=0
if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || echo)"
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then ALIVE=1; fi
fi
if [ "$ALIVE" -eq 0 ] && command -v nexus6 >/dev/null 2>&1; then
  nexus6 daemon --interval 30 >/dev/null 2>&1 &
  echo "[nexus6-pack] daemon respawned (pid=$!)" >&2
fi
exit 0
"#,
    ),
    (
        "stop_blowup",
        "Stop",
        "",
        r#"#!/bin/bash
# nexus6-pack hook: trigger a short blowup on session end (best-effort).
set -euo pipefail
if command -v nexus6 >/dev/null 2>&1; then
  nohup nexus6 blowup general --max-depth 3 >> "$HOME/.nexus6/hook_blowup.log" 2>&1 &
fi
exit 0
"#,
    ),
];

fn home() -> PathBuf {
    PathBuf::from(std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string()))
}

fn nexus6_dir() -> PathBuf { home().join(".nexus6") }
fn hooks_dir() -> PathBuf { nexus6_dir().join("hooks") }
fn claude_settings() -> PathBuf { home().join(".claude").join("settings.json") }
fn cargo_bin() -> PathBuf { home().join(".cargo").join("bin") }

/// Absolute path of the currently running nexus6 binary.
fn self_binary() -> Result<PathBuf, String> {
    std::env::current_exe().map_err(|e| format!("current_exe: {}", e))
}

pub fn install(force: bool) -> Result<(), String> {
    let bin_src = self_binary()?;
    let bin_dir = cargo_bin();
    fs::create_dir_all(&bin_dir).map_err(|e| format!("mkdir {}: {}", bin_dir.display(), e))?;
    let link_path = bin_dir.join("nexus6");

    // symlink (replace if force, or if existing link points elsewhere)
    let need_link = match fs::symlink_metadata(&link_path) {
        Ok(md) => {
            if md.file_type().is_symlink() {
                match fs::read_link(&link_path) {
                    Ok(tgt) => tgt != bin_src || force,
                    Err(_) => true,
                }
            } else {
                // regular file exists — only replace if force
                if force { fs::remove_file(&link_path).ok(); true } else { false }
            }
        }
        Err(_) => true,
    };
    if need_link {
        let _ = fs::remove_file(&link_path);
        #[cfg(unix)]
        std::os::unix::fs::symlink(&bin_src, &link_path)
            .map_err(|e| format!("symlink {} -> {}: {}", link_path.display(), bin_src.display(), e))?;
        println!("  ✓ symlink: {} -> {}", link_path.display(), bin_src.display());
    } else {
        println!("  = symlink already points to current binary ({})", link_path.display());
    }

    // write hook scripts
    fs::create_dir_all(hooks_dir()).map_err(|e| format!("mkdir hooks: {}", e))?;
    for (name, _event, _matcher, body) in HOOK_SCRIPTS {
        let p = hooks_dir().join(format!("{}.sh", name));
        fs::write(&p, body).map_err(|e| format!("write {}: {}", p.display(), e))?;
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perm = fs::metadata(&p).map_err(|e| e.to_string())?.permissions();
            perm.set_mode(0o755);
            let _ = fs::set_permissions(&p, perm);
        }
        println!("  ✓ hook: {}", p.display());
    }

    // merge into ~/.claude/settings.json
    merge_hooks_into_settings()?;
    println!("  ✓ hooks registered in {}", claude_settings().display());

    println!("\nInstalled nexus6-pack. Run 'nexus6 pack status' to verify.");
    Ok(())
}

pub fn uninstall() -> Result<(), String> {
    // remove symlink
    let link_path = cargo_bin().join("nexus6");
    if let Ok(md) = fs::symlink_metadata(&link_path) {
        if md.file_type().is_symlink() {
            let _ = fs::remove_file(&link_path);
            println!("  ✓ removed symlink: {}", link_path.display());
        }
    }
    // remove hook scripts
    for (name, _e, _m, _b) in HOOK_SCRIPTS {
        let p = hooks_dir().join(format!("{}.sh", name));
        if p.exists() {
            let _ = fs::remove_file(&p);
            println!("  ✓ removed hook: {}", p.display());
        }
    }
    // remove hooks from settings.json
    remove_hooks_from_settings()?;
    println!("  ✓ unregistered hooks from {}", claude_settings().display());
    Ok(())
}

pub fn status() -> Result<(), String> {
    println!("=== nexus6-pack status ===");
    let link_path = cargo_bin().join("nexus6");
    match fs::symlink_metadata(&link_path) {
        Ok(md) if md.file_type().is_symlink() => {
            let tgt = fs::read_link(&link_path).map(|p| p.display().to_string()).unwrap_or_default();
            println!("  symlink : ✓ {} -> {}", link_path.display(), tgt);
        }
        Ok(_) => println!("  symlink : ⚠ non-symlink file at {}", link_path.display()),
        Err(_) => println!("  symlink : ✗ missing ({})", link_path.display()),
    }
    println!("  hooks dir: {}", hooks_dir().display());
    for (name, event, _m, _b) in HOOK_SCRIPTS {
        let p = hooks_dir().join(format!("{}.sh", name));
        let mark = if p.exists() { "✓" } else { "✗" };
        println!("    {} {} [{}]", mark, name, event);
    }
    let settings = claude_settings();
    if settings.exists() {
        let registered = count_registered_hooks(&settings).unwrap_or(0);
        println!("  settings : ✓ {} ({} pack entries)", settings.display(), registered);
    } else {
        println!("  settings : ✗ {} (not found)", settings.display());
    }
    Ok(())
}

pub fn doctor() -> Result<(), String> {
    println!("=== nexus6-pack doctor ===");
    let mut problems = 0;

    // binary on PATH
    let bin = which_nexus6();
    match bin {
        Some(p) => println!("  [ok] nexus6 on PATH at {}", p.display()),
        None => { println!("  [!!] nexus6 not on PATH — run 'nexus6 pack install'"); problems += 1; }
    }

    // hooks dir
    if !hooks_dir().exists() {
        println!("  [!!] hooks dir missing: {}", hooks_dir().display());
        problems += 1;
    } else {
        println!("  [ok] hooks dir: {}", hooks_dir().display());
    }

    // settings.json readable + contains marker
    match fs::read_to_string(claude_settings()) {
        Ok(s) if s.contains(HOOKS_MARKER) => println!("  [ok] settings.json contains pack hooks"),
        Ok(_) => { println!("  [!!] settings.json exists but has no nexus6-pack hooks"); problems += 1; }
        Err(_) => { println!("  [!!] settings.json unreadable: {}", claude_settings().display()); problems += 1; }
    }

    // daemon alive?
    let pid_file = nexus6_dir().join("daemon.pid");
    let daemon_alive = fs::read_to_string(&pid_file).ok()
        .and_then(|s| s.trim().parse::<i32>().ok())
        .map(|pid| unsafe { libc_kill_zero(pid) })
        .unwrap_or(false);
    if daemon_alive {
        println!("  [ok] nexus6 daemon running");
    } else {
        println!("  [..] nexus6 daemon not running (start with 'nexus6 daemon')");
    }

    if problems == 0 { println!("\n  All checks passed."); Ok(()) }
    else { Err(format!("{} problem(s) found", problems)) }
}

// ─── internal helpers ───

fn which_nexus6() -> Option<PathBuf> {
    let path = std::env::var("PATH").ok()?;
    for dir in path.split(':') {
        let p = PathBuf::from(dir).join("nexus6");
        if p.exists() { return Some(p); }
    }
    None
}

/// Minimal libc kill(pid, 0) wrapper — checks if PID is alive without killing.
unsafe fn libc_kill_zero(pid: i32) -> bool {
    extern "C" { fn kill(pid: i32, sig: i32) -> i32; }
    kill(pid, 0) == 0
}

fn load_settings() -> Result<Value, String> {
    let path = claude_settings();
    if !path.exists() {
        if let Some(dir) = path.parent() { let _ = fs::create_dir_all(dir); }
        return Ok(json!({}));
    }
    let raw = fs::read_to_string(&path).map_err(|e| format!("read {}: {}", path.display(), e))?;
    if raw.trim().is_empty() { return Ok(json!({})); }
    serde_json::from_str(&raw).map_err(|e| format!("parse {}: {}", path.display(), e))
}

fn save_settings(v: &Value) -> Result<(), String> {
    let path = claude_settings();
    if let Some(dir) = path.parent() { let _ = fs::create_dir_all(dir); }
    // backup once per call
    if path.exists() {
        let bak = path.with_extension("json.nexus6-pack.bak");
        let _ = fs::copy(&path, &bak);
    }
    let s = serde_json::to_string_pretty(v).map_err(|e| e.to_string())?;
    fs::write(&path, s).map_err(|e| format!("write {}: {}", path.display(), e))
}

fn merge_hooks_into_settings() -> Result<(), String> {
    let mut settings = load_settings()?;
    // ensure top-level "hooks" object
    let hooks = settings.as_object_mut()
        .ok_or("settings.json root is not an object")?
        .entry("hooks")
        .or_insert_with(|| json!({}));

    for (name, event, matcher, _body) in HOOK_SCRIPTS {
        let script_path = hooks_dir().join(format!("{}.sh", name));
        let entry = json!({
            "matcher": matcher,
            "hooks": [{
                "type": "command",
                "command": script_path.to_string_lossy(),
                "tag": format!("{}:{}", HOOKS_MARKER, name)
            }]
        });
        let arr = hooks.as_object_mut()
            .ok_or("hooks is not an object")?
            .entry(event.to_string())
            .or_insert_with(|| json!([]));
        let a = arr.as_array_mut().ok_or("event entry is not an array")?;
        // remove existing nexus6-pack entries for this hook name
        a.retain(|item| {
            let tag = item.pointer("/hooks/0/tag").and_then(|v| v.as_str()).unwrap_or("");
            !tag.starts_with(&format!("{}:{}", HOOKS_MARKER, name))
        });
        a.push(entry);
    }
    save_settings(&settings)
}

fn remove_hooks_from_settings() -> Result<(), String> {
    let mut settings = load_settings()?;
    if let Some(hooks) = settings.get_mut("hooks").and_then(|v| v.as_object_mut()) {
        for (_event, val) in hooks.iter_mut() {
            if let Some(arr) = val.as_array_mut() {
                arr.retain(|item| {
                    let tag = item.pointer("/hooks/0/tag").and_then(|v| v.as_str()).unwrap_or("");
                    !tag.starts_with(HOOKS_MARKER)
                });
            }
        }
    }
    save_settings(&settings)
}

fn count_registered_hooks(path: &std::path::Path) -> Result<usize, String> {
    let raw = fs::read_to_string(path).map_err(|e| e.to_string())?;
    let v: Value = serde_json::from_str(&raw).map_err(|e| e.to_string())?;
    let mut n = 0;
    if let Some(h) = v.get("hooks").and_then(|v| v.as_object()) {
        for (_e, arr) in h {
            if let Some(a) = arr.as_array() {
                for item in a {
                    let tag = item.pointer("/hooks/0/tag").and_then(|v| v.as_str()).unwrap_or("");
                    if tag.starts_with(HOOKS_MARKER) { n += 1; }
                }
            }
        }
    }
    Ok(n)
}
