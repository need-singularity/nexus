#!/usr/bin/env python3
"""
sync_n6_constants.py — Extract n6 atlas constants and compare with TECS-L math_atlas.json.

Parses atlas-constants.md table rows, extracts (expression, value, application, domain),
then cross-references against math_atlas.json constant_maps to find NEW entries.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

N6_ATLAS = Path.home() / "Dev/n6-architecture/docs/atlas-constants.md"
MATH_ATLAS = Path.home() / "Dev/TECS-L/.shared/math_atlas.json"


def parse_table_rows(text: str) -> list[dict]:
    """Parse markdown table rows with 4+ columns into dicts."""
    rows = []
    lines = text.splitlines()
    header_cols = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            header_cols = None
            continue

        cells = [c.strip() for c in stripped.split("|")[1:-1]]

        # Detect separator line (---|---)
        if all(re.match(r'^[-:]+$', c) for c in cells if c):
            # Previous line was the header
            if i > 0:
                prev = lines[i - 1].strip()
                if prev.startswith("|"):
                    header_cols = [c.strip().lower() for c in prev.split("|")[1:-1]]
            continue

        if len(cells) < 3:
            continue

        # Skip if it looks like a header (bold or all caps keywords)
        first = cells[0].strip()
        if first in ("Expression", "Parameter", "ID", "Symbol", "Code", ""):
            header_cols = [c.strip().lower() for c in cells]
            continue

        # Build row dict
        row = {
            "expression": cells[0].strip().strip("*"),
            "value": cells[1].strip() if len(cells) > 1 else "",
            "application": cells[2].strip() if len(cells) > 2 else "",
            "domain": cells[3].strip() if len(cells) > 3 else "",
        }

        # Skip empty or trivial rows
        if not row["expression"] or row["expression"] == "---":
            continue

        rows.append(row)

    return rows


def load_existing_expressions(atlas_path: Path) -> tuple[set[str], dict]:
    """Extract known n6 expressions and their key-value pairs from math_atlas.json.

    Returns:
        known_exprs: set of normalized expression strings (e.g. "sigma-tau", "12")
        stats: dict with counts by repo
    """
    data = json.load(open(atlas_path))
    known_exprs = set()

    for cm in data.get("constant_maps", []):
        # Collect keys from N6-related constant maps
        vals = cm.get("values", None)
        if isinstance(vals, dict):
            for k, v in vals.items():
                known_exprs.add(str(k).lower().strip())
                if isinstance(v, dict):
                    for field in ("name", "formula"):
                        if field in v:
                            known_exprs.add(str(v[field]).lower().strip())
                else:
                    known_exprs.add(str(v).lower().strip())
        elif isinstance(vals, list):
            for v in vals:
                if isinstance(v, dict):
                    for field in ("name", "formula"):
                        if field in v:
                            known_exprs.add(str(v[field]).lower().strip())

        for k in cm.get("keys", []) or []:
            known_exprs.add(str(k).lower().strip())

    return known_exprs, data.get("stats", {})


def classify_domain(domain_str: str) -> str:
    """Map domain string to a broad category."""
    d = domain_str.lower()
    mappings = [
        (["ai", "llm", "diffusion", "ssm", "training", "rl", "moe", "transformer",
          "attention", "lora", "adam", "gpt", "rope", "inference"], "AI/ML"),
        (["chip", "soc", "semiconductor", "gpu", "hbm", "pim", "wafer", "photonic",
          "sm", "gpc", "tpc", "tsv", "die", "interconnect"], "Chip/Hardware"),
        (["fusion", "tokamak", "plasma", "magnet", "iter", "sparc", "kstar",
          "dt", "mhd", "divertor", "coil", "blanket"], "Fusion/Plasma"),
        (["supercond", "sc", "cryo", "bcs", "cooper", "josephson", "nb",
          "ybco", "squid", "vortex", "flux"], "Superconductor"),
        (["energy", "power", "grid", "solar", "battery", "hydrogen", "hvdc",
          "pue", "voltage", "dc", "atx", "cell", "cathode", "anode", "bms",
          "ess", "ev", "lithium", "lic", "nacl", "nuclear"], "Energy"),
        (["crypto", "network", "blockchain", "aes", "sha", "rsa", "btc",
          "eth", "tcp", "dns", "ipv", "osi", "tls", "bls"], "Crypto/Network"),
        (["biology", "genetic", "neutrino", "particle", "cosmol", "quark",
          "lepton", "higgs", "codon", "amino", "dna", "ckm", "koide",
          "inflation", "standard model", "gauge"], "Science"),
        (["math", "topology", "k-theory", "lattice", "leech", "golay",
          "hamming", "kissing", "sphere pack", "catalan", "dedekind"], "Mathematics"),
        (["optical", "display", "audio", "wdm", "fiber", "mrr", "mzi",
          "wavelength", "hz", "fps", "semitone"], "Display/Optical"),
        (["nuclear", "fission", "control rod", "enrichment", "delayed",
          "breeding", "b-10", "neutron group"], "Nuclear"),
        (["proved", "proof", "theorem"], "Theorem"),
        (["h-fu", "h-sc", "h-sm", "h-tk", "h-chip", "h-cr", "h-net",
          "bt-", "hypothesis"], "Hypothesis"),
    ]
    for keywords, category in mappings:
        if any(kw in d for kw in keywords):
            return category
    return "Other"


def main():
    # 1. Parse n6 atlas
    text = N6_ATLAS.read_text(encoding="utf-8")
    rows = parse_table_rows(text)
    print(f"[n6-atlas] Parsed {len(rows)} table rows from atlas-constants.md")

    # 2. Load existing TECS-L expressions
    existing_exprs, atlas_stats = load_existing_expressions(MATH_ATLAS)
    print(f"[TECS-L]   Loaded {len(existing_exprs)} known expressions from math_atlas.json")
    print(f"[TECS-L]   Repo stats: {atlas_stats}")

    # 3. Deduplicate n6 rows by (expression, value) pair
    seen = {}
    for r in rows:
        key = (r["expression"], r["value"])
        if key not in seen:
            seen[key] = r

    unique_rows = list(seen.values())
    print(f"[n6-atlas] {len(unique_rows)} unique (expression, value) pairs (after dedup)")

    # 4. Normalize expression for matching
    def normalize(s: str) -> str:
        """Normalize Unicode math symbols to ASCII for comparison."""
        s = s.lower().strip()
        # Common Unicode -> ASCII
        for old, new in [("σ", "sigma"), ("τ", "tau"), ("φ", "phi"),
                         ("μ", "mu"), ("²", "^2"), ("³", "^3"),
                         ("⁴", "^4"), ("₂", "2"), ("·", "*"),
                         ("×", "*"), ("−", "-"), ("\u2212", "-")]:
            s = s.replace(old, new)
        s = re.sub(r'\s+', '', s)
        return s

    # 5. Find NEW constants not in TECS-L
    new_rows = []
    matched = 0
    for r in unique_rows:
        expr_norm = normalize(r["expression"])
        val_norm = normalize(r["value"])

        # Exact match on normalized expression or value
        found = (expr_norm in existing_exprs or val_norm in existing_exprs)

        # Also check partial: "sigma-tau" in a known key like "sigma-tau=8"
        if not found:
            for known in existing_exprs:
                if len(expr_norm) > 2 and (expr_norm == known or expr_norm in known):
                    found = True
                    break

        if found:
            matched += 1
        else:
            new_rows.append(r)

    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"  Total unique expressions:  {len(unique_rows)}")
    print(f"  Already in TECS-L:         {matched}")
    print(f"  NEW (not in TECS-L):       {len(new_rows)}")
    print(f"  Coverage:                  {matched/len(unique_rows)*100:.1f}%")

    # 5. Category breakdown of NEW constants
    cat_count = Counter()
    for r in new_rows:
        cat = classify_domain(r["domain"] or r["application"])
        cat_count[cat] += 1

    print(f"\n--- NEW constants by category ---")
    for cat, cnt in cat_count.most_common():
        print(f"  {cat:20s}: {cnt:4d}")

    # 6. Sample new constants (top 15)
    print(f"\n--- Sample NEW constants (first 15) ---")
    print(f"{'Expression':30s} | {'Value':20s} | {'Domain':20s}")
    print(f"{'-'*30}-+-{'-'*20}-+-{'-'*20}")
    for r in new_rows[:15]:
        expr = r["expression"][:30]
        val = r["value"][:20]
        dom = (r["domain"] or r["application"])[:20]
        print(f"{expr:30s} | {val:20s} | {dom:20s}")

    # 7. Write full list to JSON for further processing
    out_path = Path.home() / "Dev/TECS-L/calc/n6_new_constants.json"
    with open(out_path, "w") as f:
        json.dump({
            "total_parsed": len(rows),
            "unique_expressions": len(unique_rows),
            "already_in_tecs_l": matched,
            "new_count": len(new_rows),
            "new_constants": new_rows,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nFull list written to: {out_path}")


if __name__ == "__main__":
    main()
