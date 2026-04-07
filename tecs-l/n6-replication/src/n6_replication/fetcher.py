"""Tier 3 repo fetcher -- clone/update external repos and generate tier3.json."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPOS = {
    "SEDI": "https://github.com/need-singularity/sedi.git",
    "anima": "https://github.com/need-singularity/anima.git",
    "ph-training": "https://github.com/need-singularity/ph-training.git",
    "golden-moe": "https://github.com/need-singularity/golden-moe.git",
    "conscious-lm": "https://github.com/need-singularity/conscious-lm.git",
    "energy-efficiency": "https://github.com/need-singularity/energy-efficiency.git",
}

FETCH_DIR = Path.home() / ".n6-replication" / "repos"
STATE_FILE = Path.home() / ".n6-replication" / "fetch_state.json"
REGISTRY_DIR = Path(__file__).resolve().parent.parent.parent / "registry"


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def _load_state() -> dict:
    """Load fetch state from JSON file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def _save_state(state: dict) -> None:
    """Persist fetch state to JSON file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _run_git(args: list[str], cwd: Path | None = None,
             verbose: bool = False) -> subprocess.CompletedProcess:
    """Run a git command, optionally printing output."""
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if verbose and result.stdout.strip():
        print(result.stdout.strip())
    if verbose and result.returncode != 0 and result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result


def _clone_repo(name: str, url: str, verbose: bool = False) -> bool:
    """Shallow-clone a repo into FETCH_DIR/<name>. Returns True on success."""
    dest = FETCH_DIR / name
    if dest.exists():
        if verbose:
            print(f"[fetch] {name}: already exists, skipping clone")
        return True
    if verbose:
        print(f"[fetch] {name}: cloning {url}")
    result = _run_git(
        ["clone", "--depth", "1", url, str(dest)],
        verbose=verbose,
    )
    return result.returncode == 0


def _pull_repo(name: str, verbose: bool = False) -> bool:
    """Pull latest changes for an existing clone. Returns True on success."""
    dest = FETCH_DIR / name
    if not dest.exists():
        if verbose:
            print(f"[fetch] {name}: not cloned yet, skipping pull")
        return False
    if verbose:
        print(f"[fetch] {name}: pulling latest")
    result = _run_git(["pull", "--ff-only"], cwd=dest, verbose=verbose)
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Tier 3 scanner
# ---------------------------------------------------------------------------

def _scan_tier3() -> list[dict]:
    """Scan each fetched repo's verify/ dir and build tier3 entries."""
    entries: list[dict] = []

    for name in sorted(REPOS):
        repo_dir = FETCH_DIR / name
        verify_dir = repo_dir / "verify"
        if not verify_dir.is_dir():
            continue

        for script in sorted(verify_dir.glob("*.py")):
            entry = {
                "id": f"{name}/{script.name}",
                "repo": name,
                "path": f"verify/{script.name}",
                "abs_path": str(script),
                "depends_on": [],
                "requires_gpu": False,
                "timeout": 120,
                "tier": 3,
            }
            entries.append(entry)

    # Write tier3.json
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REGISTRY_DIR / "tier3.json"
    with open(out_path, "w") as f:
        json.dump(entries, f, indent=2)

    return entries


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_all(verbose: bool = True) -> dict:
    """Shallow-clone all repos, save state, and scan for tier3 scripts.

    Returns the updated state dict.
    """
    FETCH_DIR.mkdir(parents=True, exist_ok=True)
    state = _load_state()
    now = datetime.now(timezone.utc).isoformat()

    for name, url in REPOS.items():
        ok = _clone_repo(name, url, verbose=verbose)
        state[name] = {
            "url": url,
            "status": "cloned" if ok else "failed",
            "last_fetch": now,
            "path": str(FETCH_DIR / name),
        }

    _save_state(state)

    entries = _scan_tier3()
    if verbose:
        print(f"[fetch] Scanned {len(entries)} tier-3 scripts across "
              f"{len(REPOS)} repos")

    return state


def update_all(verbose: bool = True) -> dict:
    """Pull latest for all cloned repos, save state, and rescan tier3.

    Returns the updated state dict.
    """
    state = _load_state()
    now = datetime.now(timezone.utc).isoformat()

    for name, url in REPOS.items():
        dest = FETCH_DIR / name
        if dest.exists():
            ok = _pull_repo(name, verbose=verbose)
            state[name] = {
                "url": url,
                "status": "updated" if ok else "update_failed",
                "last_fetch": now,
                "path": str(dest),
            }
        else:
            if verbose:
                print(f"[fetch] {name}: not yet cloned, cloning now")
            ok = _clone_repo(name, url, verbose=verbose)
            state[name] = {
                "url": url,
                "status": "cloned" if ok else "failed",
                "last_fetch": now,
                "path": str(dest),
            }

    _save_state(state)

    entries = _scan_tier3()
    if verbose:
        print(f"[fetch] Scanned {len(entries)} tier-3 scripts across "
              f"{len(REPOS)} repos")

    return state
