#!/usr/bin/env python3
"""Auto-grade ungraded hypotheses by detecting n=6 constant matches."""

import os, re, csv, sys
from pathlib import Path
from collections import defaultdict

HYPO_DIR = Path(__file__).resolve().parent.parent / "docs" / "hypotheses"

# Grade markers — files with any of these are already graded
GRADE_MARKERS = ['🟩', '🟧', '⭐', '🟦', '✅']

# n=6 constants: name -> (value, tolerance_ratio)
# We search for these as standalone numbers in text
N6_CONSTANTS = {
    # Base
    'n=6':        (6,     0),
    'phi=2':      (2,     0),
    'tau=4':      (4,     0),
    'sopfr=5':    (5,     0),
    'sigma=12':   (12,    0),
    'J2=24':      (24,    0),
    # Derived integer
    'sigma-tau=8':    (8,     0),
    'sigma-phi=10':   (10,    0),
    'sigma-mu=11':    (11,    0),
    'sigma+mu=13':    (13,    0),
    'sigma-sopfr=7':  (7,     0),
    'J2-tau=20':      (20,    0),
    'sigma^2=144':    (144,   0),
    'sigma*tau=48':   (48,    0),
    'sigma*sopfr=60': (60,    0),
    'sigma*n=72':     (72,    0),
    'sigma*(sigma-phi)=120': (120, 0),
    'phi^n=64':       (64,    0),
    'n/phi=3':        (3,     0),
    # Derived fractional — match with tolerance
    '1/e=0.368':      (0.368,  0.03),
    'ln(4/3)=0.288':  (0.288,  0.02),
    'tau^2/sigma=4/3': (1.333, 0.01),
    '1/(sigma-phi)=0.1': (0.1, 0.005),
    'phi/tau=0.5':    (0.5,   0),      # too common, skip below
    '16/27_Betz':     (0.593, 0.01),
    'sigma/sigma-phi=1.2': (1.2, 0.01),
}

# For integer constants, we need context — bare "2" or "3" are too common.
# Only count integers >= 5 as standalone, or smaller ones with n6 context.
SMALL_INT_SKIP = {2, 3, 4}  # Too common as bare numbers

# Regex: find standalone numbers (integer or decimal)
NUM_RE = re.compile(
    r'(?<![a-zA-Z0-9_./\\])'   # not preceded by alphanum or path chars
    r'(\d+\.?\d*)'              # the number
    r'(?![a-zA-Z0-9_./\\%])'   # not followed by alphanum or path chars
)

# n6 keyword patterns (boost score if these appear)
N6_KEYWORDS = re.compile(
    r'sigma|divisor|totient|phi\(6\)|tau\(6\)|perfect.number|n\s*=\s*6|'
    r'J[_₂2]\s*=?\s*24|sopfr|M[öo]bius|Jordan|Euler.totient|Leech|'
    r'egyptian.fraction|1/2\+1/3\+1/6',
    re.IGNORECASE
)


def is_graded(text: str) -> bool:
    return any(m in text for m in GRADE_MARKERS)


def extract_numbers(text: str) -> list[float]:
    """Extract all standalone numbers from text."""
    nums = []
    for m in NUM_RE.finditer(text):
        try:
            v = float(m.group(1))
            nums.append(v)
        except ValueError:
            pass
    return nums


def find_n6_matches(text: str, numbers: list[float]) -> dict[str, int]:
    """Find which n6 constants appear in the numbers list."""
    matches = {}
    num_set = set(numbers)

    for name, (val, tol) in N6_CONSTANTS.items():
        # Skip small integers — too many false positives
        if tol == 0 and val in SMALL_INT_SKIP:
            continue

        if tol == 0:
            # Exact integer match
            if val in num_set:
                count = numbers.count(val)
                matches[name] = count
        else:
            # Approximate match for decimals
            count = sum(1 for n in numbers if abs(n - val) <= tol)
            if count > 0:
                matches[name] = count

    return matches


def count_n6_keywords(text: str) -> int:
    return len(N6_KEYWORDS.findall(text))


def main():
    files = sorted(HYPO_DIR.glob("*.md"))
    print(f"Total hypothesis files: {len(files)}")

    graded = []
    ungraded = []

    for f in files:
        text = f.read_text(errors='ignore')
        if is_graded(text):
            graded.append(f)
        else:
            ungraded.append(f)

    print(f"Already graded: {len(graded)}")
    print(f"Ungraded: {len(ungraded)}")
    print()

    # Analyze ungraded files
    results = []
    for f in ungraded:
        text = f.read_text(errors='ignore')
        numbers = extract_numbers(text)
        matches = find_n6_matches(text, numbers)
        kw_count = count_n6_keywords(text)

        n6_score = sum(matches.values()) + kw_count * 2  # keywords worth 2x
        unique_constants = len(matches)

        results.append({
            'file': f.name,
            'n6_score': n6_score,
            'unique_n6': unique_constants,
            'keyword_hits': kw_count,
            'matches': matches,
            'num_count': len(numbers),
        })

    # Sort by score descending
    results.sort(key=lambda x: (-x['n6_score'], -x['unique_n6']))

    # Summary stats
    has_matches = [r for r in results if r['n6_score'] > 0]
    strong = [r for r in results if r['unique_n6'] >= 3]

    print("=" * 80)
    print(f"RESULTS: {len(has_matches)}/{len(ungraded)} ungraded files have n6 matches")
    print(f"  Strong candidates (3+ unique constants): {len(strong)}")
    print(f"  Any match: {len(has_matches)}")
    print(f"  No match: {len(ungraded) - len(has_matches)}")
    print("=" * 80)

    # Top 50
    print(f"\n{'='*80}")
    print("TOP 50 CANDIDATES FOR n=6 GRADING")
    print(f"{'='*80}")
    print(f"{'#':>3} {'Score':>5} {'Uniq':>4} {'KW':>3} {'File':<50} Constants")
    print("-" * 120)
    for i, r in enumerate(results[:50], 1):
        consts = ", ".join(f"{k}({v})" for k, v in sorted(r['matches'].items(), key=lambda x: -x[1])[:5])
        print(f"{i:3d} {r['n6_score']:5d} {r['unique_n6']:4d} {r['keyword_hits']:3d} {r['file']:<50} {consts}")

    # Score distribution
    print(f"\n{'='*80}")
    print("SCORE DISTRIBUTION")
    print(f"{'='*80}")
    buckets = defaultdict(int)
    for r in results:
        if r['n6_score'] == 0:
            buckets['0'] += 1
        elif r['n6_score'] <= 3:
            buckets['1-3'] += 1
        elif r['n6_score'] <= 10:
            buckets['4-10'] += 1
        elif r['n6_score'] <= 20:
            buckets['11-20'] += 1
        else:
            buckets['21+'] += 1

    for bucket in ['0', '1-3', '4-10', '11-20', '21+']:
        count = buckets.get(bucket, 0)
        bar = '#' * min(count, 60)
        print(f"  {bucket:>5}: {count:4d} {bar}")

    # Most common constants
    print(f"\n{'='*80}")
    print("MOST COMMON n=6 CONSTANTS IN UNGRADED FILES")
    print(f"{'='*80}")
    const_freq = defaultdict(int)
    for r in results:
        for k, v in r['matches'].items():
            const_freq[k] += v
    for k, v in sorted(const_freq.items(), key=lambda x: -x[1])[:20]:
        print(f"  {k:<30} appears {v:5d} times across files")

    # Write CSV
    csv_path = HYPO_DIR.parent.parent / "calc" / "auto_grade_results.csv"
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file', 'n6_score', 'unique_n6_constants', 'keyword_hits',
                     'top_matches', 'suggested_grade'])
        for r in results:
            top = "; ".join(f"{k}" for k in sorted(r['matches'].keys()))
            if r['unique_n6'] >= 5:
                grade = 'STRONG_CANDIDATE'
            elif r['unique_n6'] >= 3:
                grade = 'MODERATE'
            elif r['n6_score'] > 0:
                grade = 'WEAK'
            else:
                grade = 'NO_MATCH'
            w.writerow([r['file'], r['n6_score'], r['unique_n6'],
                        r['keyword_hits'], top, grade])

    print(f"\nCSV written to: {csv_path}")
    print(f"\nSuggested grade breakdown:")
    grades = defaultdict(int)
    for r in results:
        if r['unique_n6'] >= 5:
            grades['STRONG_CANDIDATE'] += 1
        elif r['unique_n6'] >= 3:
            grades['MODERATE'] += 1
        elif r['n6_score'] > 0:
            grades['WEAK'] += 1
        else:
            grades['NO_MATCH'] += 1
    for g in ['STRONG_CANDIDATE', 'MODERATE', 'WEAK', 'NO_MATCH']:
        print(f"  {g:<20}: {grades.get(g, 0):4d}")


if __name__ == '__main__':
    main()
