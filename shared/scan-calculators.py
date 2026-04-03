#!/usr/bin/env python3
"""Calculator Registry Scanner — Scans TECS-L, anima, SEDI repos and builds unified registry."""

import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # TECS-L root
DEV = BASE.parent  # ~/Dev

# ── Repo definitions: (name, root, scan_paths, categories) ──
REPOS = [
    {
        "name": "TECS-L",
        "root": BASE,
        "scans": [
            {"path": "calc", "category": "calculator"},
            {"path": ".", "glob": "*.py", "category": "engine",
             "include": [
                 "brain_singularity", "compass", "timeline", "formula_engine",
                 "texas_sharpshooter", "complex_compass", "nstate_calculator",
                 "brain_analyzer", "llm_expert_analyzer", "physics_constant_engine",
                 "chemistry_engine", "nuclear_engine", "congruence_chain_engine",
                 "convergence_engine", "dfs_engine", "quantum_formula_engine",
                 "perfect_number_engine", "texas_quantum", "golden_moe",
                 "golden_moe_torch", "golden_moe_cifar", "session_briefing",
                 "model_pure_field", "model_utils",
             ]},
        ],
    },
    {
        "name": "anima",
        "root": DEV / "anima",
        "scans": [
            {"path": ".", "glob": "*.py", "category": "auto",
             "exclude": [
                 "__init__", "setup", "conftest",
                 "finetune_animalm", "finetune_animalm_v2", "finetune_animalm_v3",
                 "finetune_animalm_v4", "finetune_golden_moe",
                 "test_animalm_h100", "test_golden_moe_h100",
                 "run_web_v4",
             ]},
            {"path": "tools", "category": "tool"},
        ],
    },
    {
        "name": "SEDI",
        "root": DEV / "SEDI",
        "scans": [
            {"path": "sedi", "glob": "*.py", "category": "core",
             "exclude": ["__init__"]},
            {"path": "sedi/sources", "glob": "*.py", "category": "source",
             "exclude": ["__init__"]},
        ],
    },
    {
        "name": "n6-architecture",
        "root": DEV / "n6-architecture",
        "scans": [
            {"path": "tools", "category": "calculator"},
            {"path": "tools", "glob": "**/main.rs", "category": "calculator", "lang": "rust"},
            {"path": "techniques", "category": "technique"},
            {"path": "engine", "category": "engine", "exclude": ["__init__"]},
            {"path": "experiments", "category": "experiment"},
        ],
    },
]

# ── Category labels ──
CATEGORY_LABELS = {
    "calculator": "Calculator",
    "engine": "Engine",
    "core": "Core",
    "source": "Data Source",
    "tool": "Tool",
    "agent": "Agent",
    "bench": "Benchmark",
    "model": "Model",
    "training": "Training",
    "serve": "Serving",
    "sense": "Sense",
    "verify": "Verification",
}


def auto_categorize(name):
    """Guess category from filename."""
    if name.startswith("verify_") or name.startswith("validate_"):
        return "verify"
    if name.startswith("bench_"):
        return "bench"
    if name.startswith("train_") or name.startswith("finetune_"):
        return "training"
    if name.startswith("serve_"):
        return "serve"
    if name.endswith("_engine"):
        return "engine"
    if name.endswith("_calculator") or name.endswith("_calc"):
        return "calculator"
    if name.endswith("_analyzer") or name.endswith("_detector") or name.endswith("_checker"):
        return "calculator"
    if name.endswith("_sense") or name.startswith("vision_") or name.startswith("lidar_"):
        return "sense"
    if name.startswith("anima"):
        return "agent"
    if name.endswith("_lm") or name.startswith("conscious_lm") or name.startswith("growing_"):
        return "model"
    return "tool"


def extract_description(filepath):
    """Extract first docstring or comment description from a Python or Rust file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[:30]
    except Exception:
        return ""

    content = "".join(lines)

    # Rust: extract /// doc comments
    if str(filepath).endswith(".rs"):
        for line in lines:
            line = line.strip()
            if line.startswith("///"):
                desc = line[3:].strip()
                if len(desc) > 5:
                    return desc
        return ""

    # Find triple-quote docstring (""" or ''')
    for quote in ['"""', "'''"]:
        idx = content.find(quote)
        if idx >= 0:
            rest = content[idx + 3:]
            # Get text until closing quotes
            end = rest.find(quote)
            if end >= 0:
                docstring = rest[:end].strip()
            else:
                docstring = rest.strip()
            # Take first non-empty line
            for line in docstring.split("\n"):
                line = line.strip()
                if line and len(line) > 5:
                    # Remove trailing punctuation artifacts
                    return line
            break

    # Try comment header (# line near top, skip shebang)
    for line in lines[:8]:
        line = line.strip()
        if line.startswith("# ") and not line.startswith("#!"):
            desc = line[2:].strip()
            if len(desc) > 5:
                return desc

    # Try filename-based description from argparse
    m = re.search(r"description=['\"](.+?)['\"]", content)
    if m:
        return m.group(1).strip()

    return ""


def scan_repo(repo_def):
    """Scan a repo and return list of tool entries."""
    entries = []
    root = repo_def["root"]
    if not root.exists():
        print(f"  SKIP: {root} not found", file=sys.stderr)
        return entries

    for scan in repo_def["scans"]:
        scan_dir = root / scan["path"]
        if not scan_dir.exists():
            continue

        glob_pat = scan.get("glob", "*.py")
        include = set(scan.get("include", []))
        exclude = set(scan.get("exclude", []))

        for filepath in sorted(scan_dir.glob(glob_pat)):
            if filepath.name.startswith("__"):
                continue
            # For Rust main.rs files, use parent directory as name
            lang = scan.get("lang", "python")
            if lang == "rust" and filepath.name == "main.rs":
                name = filepath.parent.name
            else:
                name = filepath.stem
            if include and name not in include:
                continue
            if name in exclude:
                continue

            category = scan["category"]
            if category == "auto":
                category = auto_categorize(name)

            desc = extract_description(filepath)
            rel_path = str(filepath.relative_to(root))

            entries.append({
                "name": name,
                "description": desc,
                "category": category,
                "path": rel_path,
                "repo": repo_def["name"],
            })

    return entries


def build_registry():
    """Scan all repos and build the unified registry."""
    registry = {}
    for repo_def in REPOS:
        name = repo_def["name"]
        print(f"Scanning {name}...", file=sys.stderr)
        entries = scan_repo(repo_def)
        registry[name] = entries
        print(f"  Found {len(entries)} tools", file=sys.stderr)
    return registry


def generate_markdown_table(entries, repo_name, github_base=None):
    """Generate a markdown table for one repo's tools."""
    if not entries:
        return f"*No tools found in {repo_name}*\n"

    # Group by category
    by_cat = {}
    for e in entries:
        cat = e["category"]
        by_cat.setdefault(cat, []).append(e)

    lines = []
    for cat in sorted(by_cat.keys()):
        label = CATEGORY_LABELS.get(cat, cat.title())
        items = by_cat[cat]
        lines.append(f"**{label}** ({len(items)})")
        lines.append("")
        lines.append("| Name | Description | Path |")
        lines.append("|------|-------------|------|")
        for e in sorted(items, key=lambda x: x["name"]):
            desc = e["description"][:80] if e["description"] else "-"
            path = f"`{e['path']}`"
            lines.append(f"| {e['name']} | {desc} | {path} |")
        lines.append("")

    return "\n".join(lines)


def generate_summary_table(registry):
    """Generate a cross-repo summary."""
    lines = []
    lines.append("| Repo | Tools | Categories |")
    lines.append("|------|-------|------------|")
    total = 0
    for repo_name, entries in registry.items():
        cats = set(e["category"] for e in entries)
        cat_str = ", ".join(sorted(CATEGORY_LABELS.get(c, c) for c in cats))
        lines.append(f"| **{repo_name}** | {len(entries)} | {cat_str} |")
        total += len(entries)
    lines.append(f"| **Total** | **{total}** | |")
    lines.append("")
    return "\n".join(lines)


def generate_full_markdown(registry):
    """Generate the complete shared markdown for README sync."""
    lines = []
    lines.append(generate_summary_table(registry))

    for repo_name, entries in registry.items():
        lines.append(f"### {repo_name}")
        lines.append("")
        lines.append(generate_markdown_table(entries, repo_name))

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scan and register calculators across repos")
    parser.add_argument("--json", action="store_true", help="Output JSON registry")
    parser.add_argument("--markdown", action="store_true", help="Output markdown tables")
    parser.add_argument("--summary", action="store_true", help="Output summary only")
    parser.add_argument("--save", action="store_true", help="Save JSON to .shared/calculators.json")
    parser.add_argument("--repo", choices=["TECS-L", "anima", "SEDI"], help="Single repo only")
    args = parser.parse_args()

    if not any([args.json, args.markdown, args.summary, args.save]):
        args.markdown = True
        args.save = True

    registry = build_registry()

    if args.repo:
        registry = {args.repo: registry.get(args.repo, [])}

    if args.save:
        out_path = BASE / ".shared" / "calculators.json"
        with open(out_path, "w") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print(f"Saved: {out_path}", file=sys.stderr)

    if args.json:
        print(json.dumps(registry, indent=2, ensure_ascii=False))
    elif args.summary:
        print(generate_summary_table(registry))
    elif args.markdown:
        print(generate_full_markdown(registry))


if __name__ == "__main__":
    main()
