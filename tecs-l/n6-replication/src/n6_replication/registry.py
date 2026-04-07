"""Script registry — metadata for all verification scripts."""

import json
from pathlib import Path

REGISTRY_DIR = Path(__file__).parent.parent.parent / "registry"


def load_tier2() -> list:
    path = REGISTRY_DIR / "tier2.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def load_tier3() -> list:
    path = REGISTRY_DIR / "tier3.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def load_all(tiers=None) -> list:
    if tiers is None:
        tiers = [2, 3]
    scripts = []
    if 2 in tiers:
        scripts.extend(load_tier2())
    if 3 in tiers:
        scripts.extend(load_tier3())
    return scripts


def filter_scripts(scripts, *, gpu=False) -> list:
    if gpu:
        return scripts
    return [s for s in scripts if not s.get("requires_gpu", False)]
