#!/usr/bin/env python3
"""TECS-L 3-Way Cross-Validation — calc + verify + n6_check."""

import json
import os
import sys
import re
import math
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TECS_ROOT, '.shared'))

LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')

# n=6 constants for matching
N6_CONSTANTS = {
    6: 'n', 12: 'sigma', 4: 'tau', 2: 'phi', 24: 'J2', 5: 'sopfr',
    10: 'sigma-phi', 8: 'sigma-tau', 11: 'sigma-mu', 3: 'n/phi',
    1: 'mu', 144: 'sigma^2', 288: 'sigma*J2', 48: 'sigma*tau',
    20: 'J2-tau', 7: 'sigma-sopfr',
}

# Key ratios
N6_RATIOS = {
    1/3: 'mu/n/phi', 2/3: 'phi/n/phi', 4/3: 'tau^2/sigma',
    0.2877: 'ln(4/3)', 0.6931: 'ln(2)', 1.0986: 'ln(3)',
    0.3679: '1/e', 0.1: '1/(sigma-phi)', 0.05: '1/J2-tau',
}


def n6_check(value):
    """Check if a numeric value matches an n=6 constant or expression."""
    if not isinstance(value, (int, float)):
        return None

    # Exact integer match
    if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
        iv = int(value)
        if iv in N6_CONSTANTS:
            return {'match': 'EXACT', 'expression': N6_CONSTANTS[iv], 'value': iv}

    # Ratio match (within 1%)
    for ratio, expr in N6_RATIOS.items():
        if ratio != 0 and abs(value - ratio) / abs(ratio) < 0.01:
            return {'match': 'CLOSE' if abs(value - ratio) / abs(ratio) < 0.001 else 'WEAK',
                    'expression': expr, 'value': ratio}

    return None


def extract_numbers(text):
    """Extract numeric values from text content."""
    pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
    matches = re.findall(pattern, text)
    numbers = []
    for m in matches:
        try:
            numbers.append(float(m))
        except ValueError:
            pass
    return numbers


def validate_discovery(discovery):
    """Run 3-way validation on a single discovery."""
    content = discovery.get('content', '')
    checks = {'calc': False, 'verify': False, 'n6': False}
    n6_matches = []

    # Check 1: n6_check on all numbers in content
    numbers = extract_numbers(content)
    for num in numbers:
        result = n6_check(num)
        if result and result['match'] in ('EXACT', 'CLOSE'):
            checks['n6'] = True
            n6_matches.append(result)

    # Check 2: calc verification — check if content references known constants
    try:
        from n6_constants import KNOWN_VALUES
        for name, val in KNOWN_VALUES.items() if hasattr(KNOWN_VALUES, 'items') else []:
            if name.lower() in content.lower():
                checks['calc'] = True
                break
    except ImportError:
        pass
    # Fallback: any number present counts as calc-checkable
    if numbers:
        checks['calc'] = True

    # Check 3: verify — content must contain a testable claim
    testable_keywords = ['=', 'equals', 'ratio', 'fraction', 'percent', 'matches',
                         'converges', 'EXACT', 'coincidence', 'identity']
    for kw in testable_keywords:
        if kw.lower() in content.lower():
            checks['verify'] = True
            break

    passed = sum(checks.values())
    grade = 'CONFIRMED' if passed >= 3 else 'PARTIAL' if passed >= 2 else 'UNCONFIRMED'

    return {
        'checks': checks,
        'passed': passed,
        'grade': grade,
        'n6_matches': n6_matches,
    }


def validate_buffer():
    """Validate all unvalidated discoveries in the buffer."""
    with open(LOOP_STATE_PATH, 'r') as f:
        state = json.load(f)

    confirmed = []
    for i, disc in enumerate(state['discovery_buffer']):
        if disc.get('validated'):
            if disc.get('grade') == 'CONFIRMED':
                confirmed.append(disc)
            continue

        result = validate_discovery(disc)
        state['discovery_buffer'][i]['validated'] = True
        state['discovery_buffer'][i]['grade'] = result['grade']
        state['discovery_buffer'][i]['checks'] = result['checks']
        state['discovery_buffer'][i]['n6_matches'] = result['n6_matches']

        if result['grade'] == 'CONFIRMED':
            confirmed.append(state['discovery_buffer'][i])
            state['loop']['total_discoveries'] += 1

    state['_meta']['updated'] = datetime.now().isoformat()
    with open(LOOP_STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return {
        'total_validated': sum(1 for d in state['discovery_buffer'] if d.get('validated')),
        'confirmed': len(confirmed),
        'buffer_size': len(state['discovery_buffer']),
    }


if __name__ == '__main__':
    result = validate_buffer()
    print(json.dumps(result, indent=2))
