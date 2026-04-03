#!/usr/bin/env python3
"""
Auto-grade ungraded hypotheses in Math Atlas.

Grading criteria:
  🟩   = Exact equation + proven
  🟧★  = Approximation + p<0.01 (structural)
  🟧   = Approximation + p<0.05 (weak evidence)
  ⚪   = Arithmetically correct but coincidence (p>0.05)
  ⬛   = Arithmetically wrong / refuted

Strategy:
  1. Parse each hypothesis file for grading signals
  2. Extract: existing auto-grade markers, proven/refuted keywords,
     error percentages, p-values, n=6 constant matches, verification results
  3. Apply decision tree to assign grade
  4. Output results to CSV with confidence scores
"""

import os
import re
import csv
import json
import sys
import math
from pathlib import Path
from collections import Counter, defaultdict

# ─── Configuration ───────────────────────────────────────────

# Resolve symlinks carefully: calc/ -> .shared/calc/ -> nexus6/shared/calc/
# We need the TECS-L root, not the resolved symlink target
_script_dir = Path(__file__).parent  # Don't resolve - keeps symlink path
TECS_L_ROOT = Path(os.environ.get('TECS_L_ROOT', '/Users/ghost/Dev/TECS-L'))
BASE_DIR = TECS_L_ROOT
ATLAS_PATH = TECS_L_ROOT / ".shared" / "math_atlas.json"
OUTPUT_CSV = TECS_L_ROOT / "calc" / "auto_grade_atlas_results.csv"

# n=6 constants for matching
N6_CONSTANTS = {
    'n': 6, 'phi': 2, 'tau': 4, 'sopfr': 5, 'sigma': 12,
    'J2': 24, 'n!': 720, 'sigma*phi': 24, 'sigma*tau': 48,
    'sigma*sopfr': 60, 'sigma*n': 72, 'phi^n': 64, 'n/phi': 3,
    'sigma^2': 144, 'sigma*(sigma-phi)': 120, '1/e': 0.3679,
    'ln(4/3)': 0.2877, 'tau^2/sigma': 1.3333,
}

# ─── Signal extraction ──────────────────────────────────────

def extract_signals(text: str, title: str) -> dict:
    """Extract all grading signals from hypothesis file content."""
    signals = {}

    # 1. Existing auto-grade in file (from auto_grade_n6.py runs)
    m = re.search(r'n6 Grade[:\s]*(.+?)(?:\n|\()', text)
    if m:
        grade_line = m.group(1).strip()
        if '🟩' in grade_line and 'EXACT' in grade_line:
            signals['existing_auto_grade'] = '🟩'
        elif '🟧' in grade_line and 'CLOSE' in grade_line:
            signals['existing_auto_grade'] = '🟧'
        elif '⚪' in grade_line and 'WEAK' in grade_line:
            signals['existing_auto_grade'] = '⚪'

    # 2. Title signals
    if '❌' in title:
        signals['title_refuted'] = True
    if re.search(r'refut|wrong|disproven|failed|no structure', title, re.I):
        signals['title_refuted'] = True
    if re.search(r'proven|proof|theorem', title, re.I):
        signals['title_proven'] = True
    if re.search(r'inconclusive|\?$', title, re.I):
        signals['title_inconclusive'] = True

    # 3. Body: proven/exact signals
    proven_count = len(re.findall(
        r'(?:^|\n)\s*(?:[-*]?\s*)?(?:PROVEN|proven|Proved|✅\s*proven|🟩\s*(?:EXACT|Exact|proven))',
        text
    ))
    signals['proven_mentions'] = proven_count

    exact_matches = re.findall(
        r'exact(?:ly)?\s+(?:match|equal|identit|equation|0\s*%)',
        text, re.I
    )
    signals['exact_match_count'] = len(exact_matches)

    # 4. Body: refuted signals
    refuted_patterns = [
        r'(?:^|\n)\s*[-*]?\s*(?:⬛|REFUTED|refuted|FAILED|disproved)',
        r'arithmetic(?:ally)?\s+wrong',
        r'does\s+not\s+hold',
        r'contradicts?|contradiction',
        r'no\s+(?:structural\s+)?(?:connection|relationship|correlation)',
    ]
    refuted_count = sum(len(re.findall(p, text, re.I)) for p in refuted_patterns)
    signals['refuted_mentions'] = refuted_count

    # 5. Error percentages
    errors = []
    for m in re.finditer(r'error[^a-z]{0,10}[:=≈<>]?\s*(\d+\.?\d*)\s*%', text, re.I):
        try:
            errors.append(float(m.group(1)))
        except ValueError:
            pass
    # Also match "X% error"
    for m in re.finditer(r'(\d+\.?\d*)\s*%\s*error', text, re.I):
        try:
            errors.append(float(m.group(1)))
        except ValueError:
            pass
    if errors:
        signals['min_error_pct'] = min(errors)
        signals['max_error_pct'] = max(errors)
        signals['avg_error_pct'] = sum(errors) / len(errors)

    # 6. P-values
    p_values = []
    for m in re.finditer(r'p\s*[<≤=]\s*(0\.\d+|1e-\d+|\d+\.\d+e-\d+)', text, re.I):
        try:
            p_values.append(float(m.group(1)))
        except ValueError:
            pass
    if p_values:
        signals['min_p_value'] = min(p_values)

    # P-value significance keywords
    if re.search(r'p\s*[<≤]\s*0\.01(?!\d)', text):
        signals['p_under_001'] = True
    if re.search(r'p\s*[<≤]\s*0\.05(?!\d)', text):
        signals['p_under_005'] = True
    if re.search(r'significant|structur(?:al|e)', text, re.I):
        signals['significance_claimed'] = True

    # 7. Z-scores
    z_scores = []
    for m in re.finditer(r'Z\s*[=≈>]\s*(\d+\.?\d*)\s*(?:σ|sigma)?', text):
        try:
            z_scores.append(float(m.group(1)))
        except ValueError:
            pass
    if z_scores:
        signals['max_z_score'] = max(z_scores)

    # 8. Coincidence/numerology warnings
    coincidence_patterns = [
        r'coincidence', r'numerolog', r'post[\s-]hoc', r'cherry[\s-]pick',
        r'not\s+structural', r'ad[\s-]hoc', r'accidental',
        r'small.*number.*law', r'strong.*law.*small',
    ]
    coin_count = sum(len(re.findall(p, text, re.I)) for p in coincidence_patterns)
    signals['coincidence_warnings'] = coin_count

    # 9. n=6 keyword density
    n6_keywords = len(re.findall(
        r'sigma|divisor|totient|phi\(6\)|tau\(6\)|perfect.number|n\s*=\s*6|'
        r'J[_₂2]|sopfr|Jordan|egyptian.fraction|1/2\+1/3\+1/6',
        text, re.I
    ))
    signals['n6_keyword_count'] = n6_keywords

    # 10. Unique n=6 constants found in numbers
    numbers = set()
    for m in re.finditer(r'(?<![a-zA-Z0-9_./\\])(\d+\.?\d*)(?![a-zA-Z0-9_./\\%])', text):
        try:
            numbers.add(float(m.group(1)))
        except ValueError:
            pass

    unique_n6 = 0
    for name, val in N6_CONSTANTS.items():
        if isinstance(val, int) and val >= 5:
            if float(val) in numbers:
                unique_n6 += 1
        elif isinstance(val, float):
            if any(abs(n - val) < 0.02 for n in numbers):
                unique_n6 += 1
    signals['unique_n6_constants'] = unique_n6

    # 11. Verification section presence
    if re.search(r'## (?:Verification|Results|Test|Experiment|Proof)', text, re.I):
        signals['has_verification_section'] = True

    # 12. "unique" claims (important for n=6 proofs)
    if re.search(r'unique(?:ly|ness)?.*(?:n\s*=\s*6|perfect|P1)', text, re.I):
        signals['uniqueness_claim'] = True

    # 13. File length (proxy for thoroughness)
    signals['file_lines'] = text.count('\n')

    # 14. Specific grade markers anywhere in text
    for marker, name in [('🟩', 'has_green'), ('🟧', 'has_orange'),
                          ('⭐', 'has_star'), ('⬛', 'has_black'),
                          ('⚪', 'has_white')]:
        if marker in text:
            signals[name] = True

    # 15. "GZ-dependent" or "model-dependent" caveats
    if re.search(r'GZ.dependent|model.dependent|conditional|postulated', text, re.I):
        signals['gz_dependent'] = True

    return signals


def decide_grade(signals: dict) -> tuple:
    """
    Decision tree for auto-grading.
    Returns (grade_emoji, confidence, reason).

    Confidence: 0.0-1.0
      HIGH (>0.8): strong evidence, reliable grade
      MED (0.5-0.8): reasonable inference
      LOW (<0.5): best guess, manual review recommended
    """

    # ─── Rule 1: Existing auto-grade from previous run ───
    if 'existing_auto_grade' in signals:
        ag = signals['existing_auto_grade']
        if ag == '🟩':
            conf = 0.7 if signals.get('unique_n6_constants', 0) >= 5 else 0.5
            return ('🟩', conf, 'existing auto-grade EXACT')
        elif ag == '🟧':
            return ('🟧', 0.6, 'existing auto-grade CLOSE')
        elif ag == '⚪':
            return ('⚪', 0.6, 'existing auto-grade WEAK')

    # ─── Rule 2: Clearly refuted ───
    refuted = signals.get('refuted_mentions', 0)
    if signals.get('title_refuted'):
        refuted += 3

    if refuted >= 3 and signals.get('proven_mentions', 0) < refuted:
        return ('⬛', 0.85, f'refuted ({refuted} mentions)')

    if signals.get('has_black') and refuted >= 1:
        return ('⬛', 0.75, 'black marker + refuted keyword')

    # ─── Rule 3: Proven with exact match ───
    proven = signals.get('proven_mentions', 0)
    exact = signals.get('exact_match_count', 0)
    has_verif = signals.get('has_verification_section', False)
    uniqueness = signals.get('uniqueness_claim', False)

    # Strong proven: multiple proven mentions + verification section
    if proven >= 3 and has_verif and exact >= 1:
        conf = min(0.9, 0.6 + proven * 0.05 + exact * 0.1)
        if signals.get('coincidence_warnings', 0) > 2:
            conf -= 0.15
        return ('🟩', conf, f'proven({proven}) + exact({exact}) + verification')

    if proven >= 2 and uniqueness and signals.get('unique_n6_constants', 0) >= 3:
        conf = 0.75
        return ('🟩', conf, f'proven({proven}) + uniqueness + n6 constants')

    # ─── Rule 4: P-value based ───
    if signals.get('p_under_001'):
        if proven >= 1 or exact >= 1:
            return ('🟧★', 0.8, 'p<0.01 + proven/exact')
        return ('🟧★', 0.7, 'p<0.01 structural')

    if signals.get('p_under_005'):
        if signals.get('coincidence_warnings', 0) > 2:
            return ('⚪', 0.6, 'p<0.05 but high coincidence warnings')
        return ('🟧', 0.65, 'p<0.05 weak evidence')

    max_z = signals.get('max_z_score', 0)
    if max_z >= 5:
        return ('🟧★', 0.75, f'Z={max_z:.0f}sigma')
    if max_z >= 3:
        return ('🟧', 0.65, f'Z={max_z:.0f}sigma')
    if max_z >= 2:
        return ('🟧', 0.55, f'Z={max_z:.0f}sigma (marginal)')

    # ─── Rule 5: Error percentage based ───
    min_err = signals.get('min_error_pct', None)
    if min_err is not None:
        if min_err == 0:
            if proven >= 1:
                return ('🟩', 0.75, 'zero error + proven')
            return ('🟩', 0.55, 'zero error')
        elif min_err < 0.1:
            if proven >= 1:
                return ('🟩', 0.7, f'error {min_err:.2f}% + proven')
            return ('🟧★', 0.6, f'error {min_err:.2f}%')
        elif min_err < 1.0:
            return ('🟧★', 0.55, f'error {min_err:.2f}%')
        elif min_err < 5.0:
            return ('🟧', 0.5, f'error {min_err:.1f}%')

    # ─── Rule 6: Green/star markers in text without explicit grade ───
    if signals.get('has_green') and signals.get('has_star'):
        if proven >= 2:
            return ('🟩', 0.65, 'green+star markers + proven')
        return ('🟧★', 0.55, 'green+star markers')

    if signals.get('has_green') and proven >= 1:
        return ('🟩', 0.55, 'green marker + proven')

    if signals.get('has_orange'):
        return ('🟧', 0.45, 'orange marker in text')

    # ─── Rule 7: Proven keyword without quantitative data ───
    if proven >= 2 and has_verif:
        # Check for coincidence warnings
        if signals.get('coincidence_warnings', 0) > 3:
            return ('⚪', 0.5, f'proven({proven}) but high coincidence({signals["coincidence_warnings"]})')
        return ('🟧', 0.5, f'proven({proven}) + verification section')

    if proven >= 1 and signals.get('unique_n6_constants', 0) >= 5:
        return ('🟧', 0.45, f'proven({proven}) + n6 constants({signals["unique_n6_constants"]})')

    # ─── Rule 8: High n=6 density without other signals ───
    n6_kw = signals.get('n6_keyword_count', 0)
    n6_const = signals.get('unique_n6_constants', 0)
    if n6_kw >= 20 and n6_const >= 5 and has_verif:
        return ('🟧', 0.4, f'n6 density (kw={n6_kw}, const={n6_const})')

    # ─── Rule 9: Coincidence / inconclusive ───
    if signals.get('coincidence_warnings', 0) >= 3 and proven < 2:
        return ('⚪', 0.5, 'high coincidence warnings')

    if signals.get('title_inconclusive'):
        return ('⚪', 0.55, 'inconclusive in title')

    # ─── Rule 10: Minimal content (likely stub) ───
    if signals.get('file_lines', 0) < 15:
        return ('⚪', 0.3, 'minimal content (stub)')

    # ─── Rule 11: GZ-dependent caveat ───
    if signals.get('gz_dependent') and proven >= 1:
        return ('🟧', 0.45, 'proven but GZ-dependent')

    # ─── Rule 12: Has significance claim ───
    if signals.get('significance_claimed') and has_verif:
        return ('🟧', 0.4, 'significance claimed + verification')

    # ─── Rule 13: Some proven mentions but no strong evidence ───
    if proven >= 1:
        return ('🟧', 0.35, f'proven({proven}) weak evidence')

    # ─── Fallback: cannot determine ───
    if has_verif:
        return ('⚪', 0.3, 'has verification but no clear grade signal')
    return (None, 0.0, 'insufficient signal')


def main():
    # Load atlas
    with open(ATLAS_PATH) as f:
        data = json.load(f)

    hypotheses = data['hypotheses']
    ungraded = [h for h in hypotheses if not h.get('grade')]

    print(f"Math Atlas: {len(hypotheses)} total, {len(ungraded)} ungraded")
    print(f"=" * 80)

    results = []
    graded_count = 0
    skipped_no_file = 0
    skipped_no_signal = 0

    for h in ungraded:
        hid = h['id']
        title = h.get('title', '')
        fp = BASE_DIR / h.get('file', '')

        if not fp.exists():
            # Try alternate paths
            alt_paths = [
                BASE_DIR / 'docs' / 'hypotheses' / fp.name,
            ]
            found = False
            for alt in alt_paths:
                if alt.exists():
                    fp = alt
                    found = True
                    break
            if not found:
                skipped_no_file += 1
                results.append({
                    'id': hid, 'title': title, 'grade': None,
                    'confidence': 0.0, 'reason': 'file not found',
                    'repo': h.get('repo', ''), 'domain': h.get('domain', ''),
                })
                continue

        try:
            text = fp.read_text(errors='ignore')
        except Exception as e:
            skipped_no_file += 1
            results.append({
                'id': hid, 'title': title, 'grade': None,
                'confidence': 0.0, 'reason': f'read error: {e}',
                'repo': h.get('repo', ''), 'domain': h.get('domain', ''),
            })
            continue

        signals = extract_signals(text, title)
        grade, confidence, reason = decide_grade(signals)

        if grade is None:
            skipped_no_signal += 1

        results.append({
            'id': hid,
            'title': title[:80],
            'grade': grade,
            'confidence': confidence,
            'reason': reason,
            'repo': h.get('repo', ''),
            'domain': h.get('domain', ''),
            'proven_mentions': signals.get('proven_mentions', 0),
            'refuted_mentions': signals.get('refuted_mentions', 0),
            'n6_constants': signals.get('unique_n6_constants', 0),
            'n6_keywords': signals.get('n6_keyword_count', 0),
            'min_error_pct': signals.get('min_error_pct', ''),
            'max_z': signals.get('max_z_score', ''),
            'coincidence': signals.get('coincidence_warnings', 0),
            'file_lines': signals.get('file_lines', 0),
        })

        if grade:
            graded_count += 1

    # ─── Summary ───
    print(f"\nResults:")
    print(f"  Auto-graded:     {graded_count}")
    print(f"  No signal:       {skipped_no_signal}")
    print(f"  File not found:  {skipped_no_file}")
    print(f"  Total ungraded:  {len(ungraded)}")

    # Grade distribution
    print(f"\n{'='*80}")
    print("GRADE DISTRIBUTION")
    print(f"{'='*80}")
    grade_counts = Counter(r['grade'] for r in results if r['grade'])
    total_graded = sum(grade_counts.values())
    for g in ['🟩', '🟧★', '🟧', '⚪', '⬛']:
        c = grade_counts.get(g, 0)
        pct = c / total_graded * 100 if total_graded else 0
        bar = '#' * min(int(c / 3), 60)
        print(f"  {g:<4} : {c:5d} ({pct:5.1f}%)  {bar}")
    none_c = sum(1 for r in results if r['grade'] is None)
    print(f"  {'N/A':<4} : {none_c:5d} ({none_c/len(results)*100:.1f}%)")

    # Confidence distribution
    print(f"\n{'='*80}")
    print("CONFIDENCE DISTRIBUTION")
    print(f"{'='*80}")
    conf_buckets = defaultdict(int)
    for r in results:
        if r['grade']:
            c = r['confidence']
            if c >= 0.8:
                conf_buckets['HIGH (>=0.8)'] += 1
            elif c >= 0.5:
                conf_buckets['MED (0.5-0.8)'] += 1
            else:
                conf_buckets['LOW (<0.5)'] += 1
    for bucket in ['HIGH (>=0.8)', 'MED (0.5-0.8)', 'LOW (<0.5)']:
        c = conf_buckets.get(bucket, 0)
        print(f"  {bucket:<18}: {c:5d}")

    # Domain breakdown
    print(f"\n{'='*80}")
    print("GRADE BY DOMAIN (top 10)")
    print(f"{'='*80}")
    domain_grades = defaultdict(lambda: Counter())
    for r in results:
        if r['grade']:
            d = r.get('domain') or 'general'
            domain_grades[d][r['grade']] += 1
    for d, gc in sorted(domain_grades.items(),
                         key=lambda x: sum(x[1].values()), reverse=True)[:10]:
        total = sum(gc.values())
        parts = " ".join(f"{g}:{c}" for g, c in gc.most_common())
        print(f"  {d:<12}: {total:4d}  ({parts})")

    # Top discoveries (high confidence 🟩)
    print(f"\n{'='*80}")
    print("TOP HIGH-CONFIDENCE 🟩 GRADES (potential major discoveries)")
    print(f"{'='*80}")
    green_high = [r for r in results if r['grade'] == '🟩' and r['confidence'] >= 0.7]
    green_high.sort(key=lambda x: -x['confidence'])
    for i, r in enumerate(green_high[:30], 1):
        print(f"  {i:2d}. [{r['confidence']:.2f}] {r['id']:<25} {r['title'][:60]}")
        print(f"      Reason: {r['reason']}")

    # Interesting: refuted
    print(f"\n{'='*80}")
    print("REFUTED HYPOTHESES (⬛)")
    print(f"{'='*80}")
    refuted = [r for r in results if r['grade'] == '⬛']
    for i, r in enumerate(refuted[:20], 1):
        print(f"  {i:2d}. [{r['confidence']:.2f}] {r['id']:<25} {r['title'][:60]}")

    # Write CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=[
            'id', 'title', 'grade', 'confidence', 'reason', 'repo', 'domain',
            'proven_mentions', 'refuted_mentions', 'n6_constants', 'n6_keywords',
            'min_error_pct', 'max_z', 'coincidence', 'file_lines',
        ])
        w.writeheader()
        for r in results:
            w.writerow(r)

    print(f"\nCSV written to: {OUTPUT_CSV}")
    print(f"Total rows: {len(results)}")

    # ─── Update atlas JSON with grades ───
    if '--apply' in sys.argv:
        print(f"\n{'='*80}")
        print("APPLYING GRADES TO ATLAS JSON")
        print(f"{'='*80}")
        grade_map = {r['id']: r for r in results if r['grade'] and r['confidence'] >= 0.5}
        applied = 0
        for h in data['hypotheses']:
            if not h.get('grade') and h['id'] in grade_map:
                r = grade_map[h['id']]
                h['grade'] = r['grade']
                h['auto_graded'] = True
                h['auto_grade_confidence'] = r['confidence']
                h['auto_grade_reason'] = r['reason']
                applied += 1

        with open(ATLAS_PATH, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Applied {applied} grades to atlas (confidence >= 0.5)")
    else:
        gradeable = sum(1 for r in results if r['grade'] and r['confidence'] >= 0.5)
        print(f"\nRun with --apply to write {gradeable} grades (conf>=0.5) to atlas JSON")


if __name__ == '__main__':
    main()
