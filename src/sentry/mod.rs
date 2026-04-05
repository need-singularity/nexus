//! Sentry: pure-Rust health watcher for nexus6 daemon.
//!
//! Zero API calls. Checks daemon PID, respawns if dead, writes plain log.
//! Runs as an ordinary foreground/background process — no LaunchAgent needed.

use std::fs;
use std::path::PathBuf;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::process::{Command, Stdio};
use std::io::Write;

fn home() -> PathBuf { PathBuf::from(std::env::var("HOME").unwrap_or_else(|_| "/tmp".into())) }
fn nexus6_dir() -> PathBuf { home().join(".nexus6") }
fn sentry_pid_file() -> PathBuf { nexus6_dir().join("sentry.pid") }
fn sentry_log() -> PathBuf { nexus6_dir().join("sentry.log") }
fn daemon_pid_file() -> PathBuf { nexus6_dir().join("daemon.pid") }

unsafe fn pid_alive(pid: i32) -> bool {
    extern "C" { fn kill(pid: i32, sig: i32) -> i32; }
    kill(pid, 0) == 0
}

fn read_pid(p: &std::path::Path) -> Option<i32> {
    fs::read_to_string(p).ok()?.trim().parse().ok()
}

fn now_epoch() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0)
}

fn log(line: &str) {
    let _ = fs::create_dir_all(nexus6_dir());
    if let Ok(mut f) = fs::OpenOptions::new().create(true).append(true).open(sentry_log()) {
        let _ = writeln!(f, "[{}] {}", now_epoch(), line);
    }
}

/// Start the sentry loop. If `foreground=false`, respawn self in background.
pub fn start(interval_sec: u64, foreground: bool) -> Result<(), String> {
    let _ = fs::create_dir_all(nexus6_dir());

    // Reject if an alive sentry already runs
    if let Some(pid) = read_pid(&sentry_pid_file()) {
        if unsafe { pid_alive(pid) } {
            return Err(format!("sentry already running (pid {})", pid));
        } else {
            let _ = fs::remove_file(sentry_pid_file());
        }
    }

    if !foreground {
        // spawn self with --fg
        let exe = std::env::current_exe().map_err(|e| format!("current_exe: {}", e))?;
        let logf = fs::OpenOptions::new().create(true).append(true).open(sentry_log())
            .map_err(|e| format!("open log: {}", e))?;
        let logf2 = logf.try_clone().map_err(|e| e.to_string())?;
        let child = Command::new(exe)
            .args(["sentry", "start", "--interval", &interval_sec.to_string(), "--fg"])
            .stdin(Stdio::null())
            .stdout(Stdio::from(logf))
            .stderr(Stdio::from(logf2))
            .spawn()
            .map_err(|e| format!("spawn sentry: {}", e))?;
        println!("sentry started (pid {}), interval={}s, log={}", child.id(), interval_sec, sentry_log().display());
        return Ok(());
    }

    // Foreground loop
    let my_pid = std::process::id() as i32;
    fs::write(sentry_pid_file(), my_pid.to_string())
        .map_err(|e| format!("write pid: {}", e))?;
    log(&format!("sentry start interval={}s pid={}", interval_sec, my_pid));

    loop {
        match check_once() {
            Ok(msg) => log(&msg),
            Err(e) => log(&format!("check error: {}", e)),
        }
        std::thread::sleep(Duration::from_secs(interval_sec));
    }
}

fn check_once() -> Result<String, String> {
    // daemon liveness
    let daemon_pid = read_pid(&daemon_pid_file());
    let alive = daemon_pid.map(|p| unsafe { pid_alive(p) }).unwrap_or(false);
    if alive {
        return Ok(format!("ok daemon pid={}", daemon_pid.unwrap_or(0)));
    }

    // respawn daemon — invoke nexus6 daemon in background
    let exe = std::env::current_exe().map_err(|e| format!("current_exe: {}", e))?;
    let child = Command::new(&exe)
        .args(["daemon", "--interval", "30"])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("respawn daemon: {}", e))?;
    Ok(format!("respawn daemon (prev_pid={:?}, new_pid={})", daemon_pid, child.id()))
}

pub fn stop() -> Result<(), String> {
    let pid = read_pid(&sentry_pid_file())
        .ok_or_else(|| "sentry not running (no pid file)".to_string())?;
    if !unsafe { pid_alive(pid) } {
        let _ = fs::remove_file(sentry_pid_file());
        return Err(format!("stale pid file; pid {} not alive", pid));
    }
    extern "C" { fn kill(pid: i32, sig: i32) -> i32; }
    let rc = unsafe { kill(pid, 15 /* SIGTERM */) };
    if rc != 0 { return Err(format!("kill({}, SIGTERM) failed", pid)); }
    let _ = fs::remove_file(sentry_pid_file());
    log(&format!("sentry stop pid={}", pid));
    println!("sentry stopped (pid {})", pid);
    Ok(())
}

pub fn status() -> Result<(), String> {
    println!("=== nexus6 sentry status ===");
    match read_pid(&sentry_pid_file()) {
        Some(pid) if unsafe { pid_alive(pid) } => println!("  sentry : ✓ running (pid {})", pid),
        Some(pid) => println!("  sentry : ✗ stale pid file (pid {} not alive)", pid),
        None => println!("  sentry : - not running"),
    }
    match read_pid(&daemon_pid_file()) {
        Some(pid) if unsafe { pid_alive(pid) } => println!("  daemon : ✓ running (pid {})", pid),
        Some(pid) => println!("  daemon : ✗ stale (pid {} not alive)", pid),
        None => println!("  daemon : - not running"),
    }
    println!("  log    : {}", sentry_log().display());
    Ok(())
}

pub fn tail(lines: usize) -> Result<(), String> {
    let raw = fs::read_to_string(sentry_log())
        .map_err(|e| format!("read log: {}", e))?;
    let all: Vec<&str> = raw.lines().collect();
    let start = all.len().saturating_sub(lines);
    for l in &all[start..] { println!("{}", l); }
    Ok(())
}
