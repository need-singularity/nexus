//! `nexus6 hook list|enable|disable <name>` — toggles entries in
//! ~/.claude/settings.json. Matches the scripts written by `pack install`.

use std::fs;
use std::path::PathBuf;
use serde_json::Value;

const HOOKS_MARKER: &str = "nexus6-pack";

fn home() -> PathBuf { PathBuf::from(std::env::var("HOME").unwrap_or_else(|_| "/tmp".into())) }
fn claude_settings() -> PathBuf { home().join(".claude").join("settings.json") }
fn hooks_dir() -> PathBuf { home().join(".nexus6").join("hooks") }

fn load() -> Result<Value, String> {
    let p = claude_settings();
    if !p.exists() { return Ok(serde_json::json!({})); }
    let raw = fs::read_to_string(&p).map_err(|e| e.to_string())?;
    if raw.trim().is_empty() { return Ok(serde_json::json!({})); }
    serde_json::from_str(&raw).map_err(|e| e.to_string())
}

fn save(v: &Value) -> Result<(), String> {
    let p = claude_settings();
    if let Some(d) = p.parent() { let _ = fs::create_dir_all(d); }
    let s = serde_json::to_string_pretty(v).map_err(|e| e.to_string())?;
    fs::write(&p, s).map_err(|e| e.to_string())
}

pub fn list() -> Result<(), String> {
    println!("=== nexus6-pack hooks ===");
    // enumerate hook scripts on disk
    let mut names: Vec<String> = Vec::new();
    if let Ok(rd) = fs::read_dir(hooks_dir()) {
        for entry in rd.flatten() {
            if let Some(n) = entry.file_name().to_str() {
                if let Some(stripped) = n.strip_suffix(".sh") {
                    names.push(stripped.to_string());
                }
            }
        }
    }
    names.sort();
    if names.is_empty() {
        println!("  (no hooks installed — run 'nexus6 pack install')");
        return Ok(());
    }
    let settings = load().unwrap_or(serde_json::json!({}));
    for name in names {
        let enabled = is_enabled(&settings, &name);
        let mark = if enabled { "✓ on " } else { "  off" };
        println!("  [{}] {}", mark, name);
    }
    Ok(())
}

fn is_enabled(settings: &Value, name: &str) -> bool {
    let tag = format!("{}:{}", HOOKS_MARKER, name);
    let hooks = match settings.get("hooks").and_then(|v| v.as_object()) {
        Some(h) => h, None => return false,
    };
    for (_event, arr) in hooks {
        if let Some(a) = arr.as_array() {
            for item in a {
                let t = item.pointer("/hooks/0/tag").and_then(|v| v.as_str()).unwrap_or("");
                if t == tag { return true; }
            }
        }
    }
    false
}

pub fn disable(name: &str) -> Result<(), String> {
    let mut settings = load()?;
    let tag = format!("{}:{}", HOOKS_MARKER, name);
    let mut removed = 0;
    if let Some(hooks) = settings.get_mut("hooks").and_then(|v| v.as_object_mut()) {
        for (_e, val) in hooks.iter_mut() {
            if let Some(a) = val.as_array_mut() {
                let before = a.len();
                a.retain(|item| {
                    let t = item.pointer("/hooks/0/tag").and_then(|v| v.as_str()).unwrap_or("");
                    t != tag
                });
                removed += before - a.len();
            }
        }
    }
    save(&settings)?;
    if removed == 0 { println!("  (hook '{}' was not enabled)", name); }
    else { println!("  ✓ disabled {} ({} entries removed)", name, removed); }
    Ok(())
}

pub fn enable(name: &str) -> Result<(), String> {
    // infer event + matcher from known scripts
    let (event, matcher) = match name {
        "post_bash_detect"    => ("PostToolUse", "Bash"),
        "session_start_check" => ("SessionStart", ""),
        "stop_blowup"         => ("Stop", ""),
        _ => return Err(format!("unknown hook '{}'. run 'nexus6 hook list'", name)),
    };
    let script = hooks_dir().join(format!("{}.sh", name));
    if !script.exists() {
        return Err(format!("hook script missing: {} (run 'nexus6 pack install')", script.display()));
    }
    // disable old copies first, then push fresh entry
    disable(name)?;
    let mut settings = load()?;
    let entry = serde_json::json!({
        "matcher": matcher,
        "hooks": [{
            "type": "command",
            "command": script.to_string_lossy(),
            "tag": format!("{}:{}", HOOKS_MARKER, name)
        }]
    });
    let hooks = settings.as_object_mut()
        .ok_or("settings.json root is not an object")?
        .entry("hooks".to_string())
        .or_insert_with(|| serde_json::json!({}));
    let arr = hooks.as_object_mut()
        .ok_or("hooks is not an object")?
        .entry(event.to_string())
        .or_insert_with(|| serde_json::json!([]));
    arr.as_array_mut().ok_or("event entry is not array")?.push(entry);
    save(&settings)?;
    println!("  ✓ enabled {} [{}]", name, event);
    Ok(())
}
