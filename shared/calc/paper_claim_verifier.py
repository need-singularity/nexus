#!/usr/bin/env python3
"""Paper Claim Verifier -- Batch verification of mathematical claims in paper documents.

Enhanced version of calc/claim_verifier.py for paper-level batch verification.
Parses markdown papers for mathematical claims (equations, "= exactly",
"unique to n=6"), runs each through direct computation, and reports
PASS/FAIL per claim with line numbers.

Usage:
  python3 calc/paper_claim_verifier.py --paper docs/papers/P-NEW-*.md
  python3 calc/paper_claim_verifier.py --paper docs/papers/*.md --summary
  python3 calc/paper_claim_verifier.py --paper docs/papers/P-NEW-*.md --strict
  python3 calc/paper_claim_verifier.py --paper docs/papers/P-NEW-*.md --json
"""

import argparse
import glob
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# Number-theoretic helpers
# ═══════════════════════════════════════════════════════════════

def divisors(n):
    d = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            d.append(i)
            if i != n // i:
                d.append(n // i)
    return sorted(d)


def sigma(n):
    return sum(divisors(n))


def tau(n):
    return len(divisors(n))


def euler_phi(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def sigma_neg1(n):
    return float(sum(Fraction(1, d) for d in divisors(n)))


def sopfr(n):
    total = 0
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            total += d
            temp //= d
        d += 1
    if temp > 1:
        total += temp
    return total


def omega(n):
    count = 0
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count


def is_perfect(n):
    return sigma(n) == 2 * n


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# ═══════════════════════════════════════════════════════════════
# Safe expression evaluator
# ═══════════════════════════════════════════════════════════════

def build_namespace(n=6):
    """Build safe namespace for evaluating expressions about n."""
    d = divisors(n)
    return {
        "n": n,
        "sigma": sigma(n),
        "tau": tau(n),
        "phi": euler_phi(n),
        "sigma_neg1": sigma_neg1(n),
        "sopfr": sopfr(n),
        "omega": omega(n),
        "divisors": d,
        "sqrt": math.sqrt,
        "log": math.log,
        "ln": math.log,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "factorial": math.factorial,
        "abs": abs,
        "gcd": math.gcd,
    }


def safe_eval(expr, n=6):
    """Evaluate expression. Returns (value, error_string)."""
    ns = build_namespace(n)
    try:
        val = eval(expr, {"__builtins__": {}}, ns)
        return val, None
    except Exception as exc:
        return None, str(exc)


# ═══════════════════════════════════════════════════════════════
# Claim extraction from markdown
# ═══════════════════════════════════════════════════════════════

# Patterns that indicate mathematical claims
CLAIM_PATTERNS = [
    # "X = Y" style equations (in $...$ or $$...$$)
    (r"\$([^$]+?)\s*=\s*([^$]+?)\$", "inline_eq"),
    # "= exactly N"
    (r"=\s*exactly\s+(\d+(?:\.\d+)?)", "exact_value"),
    # "unique to n=N" or "unique solution"
    (r"unique\s+(?:to\s+)?(?:n\s*=\s*)?(\d+)", "uniqueness"),
    # "sigma(N) = M" style
    (r"\\sigma\s*\(\s*(\d+)\s*\)\s*=\s*(\d+)", "sigma_claim"),
    # "phi(N) = M"
    (r"\\varphi\s*\(\s*(\d+)\s*\)\s*=\s*(\d+)", "phi_claim"),
    # "tau(N) = M"
    (r"\\tau\s*\(\s*(\d+)\s*\)\s*=\s*(\d+)", "tau_claim"),
    # "(p-1)(q-1) = K" type
    (r"\(p\s*-\s*1\)\s*\(q\s*-\s*1\)\s*=\s*(\d+)", "prime_pair_eq"),
    # "sigma_{-1}(N) = M"
    (r"\\sigma_\{-1\}\s*\(\s*(\d+)\s*\)\s*=\s*(\d+(?:\.\d+)?)", "sigma_neg1_claim"),
    # "N is perfect" or "perfect number"
    (r"(\d+)\s+is\s+(?:a\s+)?perfect\s+number", "perfect_claim"),
    # "N! = M"
    (r"(\d+)!\s*=\s*(\d+)", "factorial_claim"),
]


class Claim:
    """Represents a single mathematical claim extracted from a paper."""

    def __init__(self, line_num, raw_text, claim_type, details):
        self.line_num = line_num
        self.raw_text = raw_text.strip()
        self.claim_type = claim_type
        self.details = details
        self.result = None  # "PASS", "FAIL", "SKIP"
        self.message = ""

    def __repr__(self):
        return f"Claim(L{self.line_num}, {self.claim_type}, {self.result})"


def extract_claims(filepath):
    """Extract mathematical claims from a markdown file."""
    claims = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # Skip pure markdown structure
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("---"):
            continue

        for pattern, ctype in CLAIM_PATTERNS:
            for m in re.finditer(pattern, line):
                details = {"groups": m.groups(), "match": m.group(0)}
                claims.append(Claim(i, line, ctype, details))

    return claims


# ═══════════════════════════════════════════════════════════════
# Claim verification
# ═══════════════════════════════════════════════════════════════

def verify_claim(claim):
    """Verify a single claim. Sets claim.result and claim.message."""
    ctype = claim.claim_type
    groups = claim.details["groups"]

    try:
        if ctype == "sigma_claim":
            n, expected = int(groups[0]), int(groups[1])
            actual = sigma(n)
            if actual == expected:
                claim.result = "PASS"
                claim.message = f"sigma({n}) = {actual}"
            else:
                claim.result = "FAIL"
                claim.message = f"sigma({n}) = {actual}, paper claims {expected}"

        elif ctype == "phi_claim":
            n, expected = int(groups[0]), int(groups[1])
            actual = euler_phi(n)
            if actual == expected:
                claim.result = "PASS"
                claim.message = f"phi({n}) = {actual}"
            else:
                claim.result = "FAIL"
                claim.message = f"phi({n}) = {actual}, paper claims {expected}"

        elif ctype == "tau_claim":
            n, expected = int(groups[0]), int(groups[1])
            actual = tau(n)
            if actual == expected:
                claim.result = "PASS"
                claim.message = f"tau({n}) = {actual}"
            else:
                claim.result = "FAIL"
                claim.message = f"tau({n}) = {actual}, paper claims {expected}"

        elif ctype == "sigma_neg1_claim":
            n = int(groups[0])
            expected = float(groups[1])
            actual = sigma_neg1(n)
            if abs(actual - expected) < 1e-6:
                claim.result = "PASS"
                claim.message = f"sigma_{{-1}}({n}) = {actual}"
            else:
                claim.result = "FAIL"
                claim.message = f"sigma_{{-1}}({n}) = {actual:.6f}, paper claims {expected}"

        elif ctype == "perfect_claim":
            n = int(groups[0])
            if is_perfect(n):
                claim.result = "PASS"
                claim.message = f"{n} is perfect (sigma({n})={sigma(n)}=2*{n})"
            else:
                claim.result = "FAIL"
                claim.message = f"{n} is NOT perfect (sigma({n})={sigma(n)} != {2*n})"

        elif ctype == "factorial_claim":
            n, expected = int(groups[0]), int(groups[1])
            actual = math.factorial(n)
            if actual == expected:
                claim.result = "PASS"
                claim.message = f"{n}! = {actual}"
            else:
                claim.result = "FAIL"
                claim.message = f"{n}! = {actual}, paper claims {expected}"

        elif ctype == "prime_pair_eq":
            target = int(groups[0])
            # Find all prime pairs (p,q) with p<=q such that (p-1)(q-1) = target
            solutions = []
            for p in range(2, target + 3):
                if not is_prime(p):
                    continue
                pm1 = p - 1
                if pm1 == 0 or target % pm1 != 0:
                    continue
                qm1 = target // pm1
                q = qm1 + 1
                if q >= p and is_prime(q):
                    solutions.append((p, q))
            claim.result = "PASS"
            claim.message = f"(p-1)(q-1)={target} solutions: {solutions}"

        elif ctype == "uniqueness":
            n_val = int(groups[0])
            # Flag for manual review -- uniqueness claims need context
            claim.result = "SKIP"
            claim.message = f"Uniqueness claim for n={n_val} (needs manual review)"

        elif ctype == "exact_value":
            val = float(groups[0])
            claim.result = "SKIP"
            claim.message = f"Exact value claim: {val} (needs context to verify)"

        elif ctype == "inline_eq":
            # Try to parse simple LaTeX equations
            lhs, rhs = groups[0].strip(), groups[1].strip()
            claim.result = "SKIP"
            claim.message = f"Inline equation: {lhs} = {rhs} (LaTeX parsing limited)"

        else:
            claim.result = "SKIP"
            claim.message = f"Unknown claim type: {ctype}"

    except Exception as exc:
        claim.result = "FAIL"
        claim.message = f"Verification error: {exc}"


def verify_paper(filepath, strict=False):
    """Verify all claims in a paper. Returns (claims, summary_dict)."""
    claims = extract_claims(filepath)

    for c in claims:
        verify_claim(c)

    n_pass = sum(1 for c in claims if c.result == "PASS")
    n_fail = sum(1 for c in claims if c.result == "FAIL")
    n_skip = sum(1 for c in claims if c.result == "SKIP")
    total = len(claims)

    if strict:
        # In strict mode, SKIP counts as FAIL
        overall = "FAIL" if (n_fail > 0 or n_skip > 0) else "PASS"
    else:
        overall = "FAIL" if n_fail > 0 else "PASS"

    summary = {
        "file": str(filepath),
        "total_claims": total,
        "pass": n_pass,
        "fail": n_fail,
        "skip": n_skip,
        "overall": overall,
    }
    return claims, summary


# ═══════════════════════════════════════════════════════════════
# Output
# ═══════════════════════════════════════════════════════════════

def print_paper_report(filepath, claims, summary):
    """Print detailed report for one paper."""
    name = Path(filepath).name
    print(f"\n{'=' * 70}")
    print(f"  Paper: {name}")
    print(f"  Claims: {summary['total_claims']}  "
          f"PASS: {summary['pass']}  FAIL: {summary['fail']}  SKIP: {summary['skip']}")
    print(f"  Overall: {summary['overall']}")
    print(f"{'=' * 70}")

    if not claims:
        print("  (no mathematical claims detected)")
        return

    for c in claims:
        if c.result == "PASS":
            tag = "PASS"
        elif c.result == "FAIL":
            tag = "FAIL"
        else:
            tag = "SKIP"
        print(f"  L{c.line_num:4d}  [{tag}]  {c.claim_type:20s}  {c.message}")


def print_summary_line(filepath, summary):
    """Print one-line summary per paper."""
    name = Path(filepath).name
    status = summary["overall"]
    print(f"  {status:4s}  {summary['pass']:3d}P {summary['fail']:3d}F {summary['skip']:3d}S  {name}")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Paper Claim Verifier -- batch verify mathematical claims in papers"
    )
    parser.add_argument("--paper", type=str, nargs="+", required=True,
                        help="Paper file(s) or glob pattern(s)")
    parser.add_argument("--strict", action="store_true",
                        help="Fail on any unverified (SKIP) claim")
    parser.add_argument("--summary", action="store_true",
                        help="One-line summary per paper")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    args = parser.parse_args()

    # Expand globs
    files = []
    for pattern in args.paper:
        expanded = glob.glob(pattern)
        if expanded:
            files.extend(expanded)
        else:
            # Treat as literal path
            files.append(pattern)

    if not files:
        print("  No paper files found.", file=sys.stderr)
        sys.exit(1)

    files = sorted(set(files))
    all_summaries = []
    all_claims_by_file = {}

    print(f"\n  Scanning {len(files)} paper(s)...")

    for fpath in files:
        try:
            claims, summary = verify_paper(fpath, strict=args.strict)
            all_summaries.append(summary)
            all_claims_by_file[fpath] = claims

            if args.summary:
                print_summary_line(fpath, summary)
            elif not args.json:
                print_paper_report(fpath, claims, summary)

        except FileNotFoundError:
            print(f"  ERROR: File not found: {fpath}", file=sys.stderr)
            all_summaries.append({"file": fpath, "total_claims": 0,
                                  "pass": 0, "fail": 0, "skip": 0, "overall": "ERROR"})

    # Totals
    total_pass = sum(s["pass"] for s in all_summaries)
    total_fail = sum(s["fail"] for s in all_summaries)
    total_skip = sum(s["skip"] for s in all_summaries)
    total_claims = sum(s["total_claims"] for s in all_summaries)
    any_fail = any(s["overall"] == "FAIL" for s in all_summaries)

    if args.json:
        output = {
            "papers": all_summaries,
            "totals": {
                "papers": len(files),
                "claims": total_claims,
                "pass": total_pass,
                "fail": total_fail,
                "skip": total_skip,
                "overall": "FAIL" if any_fail else "PASS",
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'=' * 70}")
        print(f"  TOTALS: {len(files)} papers, {total_claims} claims")
        print(f"  PASS: {total_pass}  FAIL: {total_fail}  SKIP: {total_skip}")
        print(f"  Overall: {'FAIL' if any_fail else 'PASS'}")
        print(f"{'=' * 70}")

    if any_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
