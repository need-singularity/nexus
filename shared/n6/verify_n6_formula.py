#!/usr/bin/env python3
"""
verify_n6_formula.py — n6 산술 공식 수치 검증 헬퍼
Agent/script 가 공식 제안 시 사전 검증 용도.

usage:
    python3 verify_n6_formula.py <target> <formula>
    python3 verify_n6_formula.py 155 "n*J2+sigma-mu"
    # exit 0 if within tolerance, 1 otherwise

n6 constants: n=6, sigma=12, tau=4, phi=2, sopfr=5, M3=7, J2=24, P2=28, mu=1
operators: + - * / ^ ( ) (^ is exponent, not XOR)
tolerance: 5% of target or 0.01 absolute minimum
"""
import sys
import re

N6_CTX = {'n':6, 'sigma':12, 'tau':4, 'phi':2, 'sopfr':5,
          'M3':7, 'J2':24, 'P2':28, 'mu':1}

def verify(target_str: str, formula: str) -> tuple[bool, float, float, str]:
    """
    Returns (ok, target, computed, message).
    ok = True if |target-computed| within tolerance.
    """
    try:
        target = float(target_str)
    except ValueError:
        return False, 0.0, 0.0, f"invalid target: {target_str!r}"

    # Normalize: ^ → **, unicode math → python
    expr = formula.replace('^', '**').replace('²', '**2').replace('³', '**3')
    if re.search(r'[^\x00-\x7f]', expr):
        return False, target, 0.0, f"non-ASCII in formula: {formula!r}"

    try:
        computed = eval(expr, {'__builtins__': {}}, N6_CTX)
    except Exception as e:
        return False, target, 0.0, f"eval error: {e}"

    if not isinstance(computed, (int, float)):
        return False, target, 0.0, f"non-numeric result: {type(computed).__name__}"

    computed = float(computed)
    tol = max(0.05 * abs(target), 0.01)
    diff = abs(computed - target)
    ok = diff <= tol
    msg = f"{formula} = {computed} (target={target}, diff={diff:.4f}, tol={tol:.4f})"
    return ok, target, computed, msg

def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    target_str, formula = sys.argv[1], sys.argv[2]
    ok, target, computed, msg = verify(target_str, formula)
    status = "✓ OK" if ok else "✗ FAIL"
    print(f"{status}: {msg}")
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
