#!/usr/bin/env python3
"""DFS n=6 Composition Miner -- Search for identities involving function composition

Tests patterns like sigma(tau(n)) == f(n), phi(sigma(n)) == g(n), etc.
Also tests more exotic forms: sigma(n) mod tau(n) == k, gcd relations, etc.

Usage:
  PYTHONPATH=. python3 calc/dfs_n6_composition_miner.py --limit 5000
"""

import math
import argparse
import time
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════
# Sieves (same as identity miner)
# ═══════════════════════════════════════════════════════════════

def sieve_sigma(limit):
    s = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for m in range(d, limit + 1, d):
            s[m] += d
    return s

def sieve_tau(limit):
    t = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for m in range(d, limit + 1, d):
            t[m] += 1
    return t

def sieve_phi(limit):
    p = list(range(limit + 1))
    for i in range(2, limit + 1):
        if p[i] == i:
            for j in range(i, limit + 1, i):
                p[j] = p[j] // i * (i - 1)
    return p

def sieve_sopfr(limit):
    s = [0] * (limit + 1)
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i*i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    for n in range(2, limit + 1):
        m = n
        while m > 1:
            p = spf[m]
            s[n] += p
            m //= p
    return s

def sieve_omega(limit):
    w = [0] * (limit + 1)
    for p in range(2, limit + 1):
        if all(p % d != 0 for d in range(2, int(p**0.5) + 1)):
            for m in range(p, limit + 1, p):
                w[m] += 1
    return w

def sieve_Omega(limit):
    O = [0] * (limit + 1)
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i*i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    for n in range(2, limit + 1):
        m = n
        while m > 1:
            O[n] += 1
            m //= spf[m]
    return O

def sieve_rad(limit):
    r = [1] * (limit + 1)
    r[0] = 0
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i*i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    for n in range(2, limit + 1):
        m = n
        seen = set()
        while m > 1:
            p = spf[m]
            if p not in seen:
                r[n] *= p
                seen.add(p)
            m //= p
    return r

def build_tables(limit):
    print(f"  Building sieve tables up to n={limit}...", flush=True)
    t0 = time.time()
    sigma = sieve_sigma(limit)
    tau = sieve_tau(limit)
    phi = sieve_phi(limit)
    sopfr = sieve_sopfr(limit)
    omega = sieve_omega(limit)
    Omega_t = sieve_Omega(limit)
    rad = sieve_rad(limit)
    aliq = [sigma[i] - i if i > 0 else 0 for i in range(limit + 1)]
    t1 = time.time()
    print(f"  Done in {t1-t0:.1f}s")
    return {
        'sigma': sigma, 'tau': tau, 'phi': phi, 'sopfr': sopfr,
        'omega': omega, 'Omega': Omega_t, 'rad': rad, 'aliq': aliq,
    }


# ═══════════════════════════════════════════════════════════════
# Function composition tests
# ═══════════════════════════════════════════════════════════════

FUNC_NAMES = ['sigma', 'tau', 'phi', 'sopfr', 'omega', 'Omega', 'rad']

def safe_get(T, fname, n, limit):
    """Get T[fname][n] safely, return None if out of range."""
    if n < 0 or n > limit:
        return None
    return T[fname][n]


def generate_composition_tests(T, limit):
    """Generate and test composition identities."""
    results = []

    # ─── Type A: f(g(n)) == h(n) ───
    # Also: f(g(n)) == n, f(g(n)) == K (constant)
    print("  Testing f(g(n)) == h(n) compositions...", flush=True)

    for f_name in FUNC_NAMES:
        for g_name in FUNC_NAMES:
            # Test f(g(n)) at n=6
            g6 = T[g_name][6]
            if g6 < 1 or g6 > limit:
                continue
            fg6 = T[f_name][g6]

            # Compare against all h(n) at n=6
            for h_name in FUNC_NAMES + ['n']:
                h6 = T[h_name][6] if h_name != 'n' else 6
                if fg6 != h6 or fg6 == 0:
                    continue

                # Found match at n=6. Full scan.
                name = f"{f_name}({g_name}(n)) == {h_name}"
                hits = []
                for n in range(2, limit + 1):
                    gn = T[g_name][n]
                    if gn < 1 or gn > limit:
                        continue
                    fgn = T[f_name][gn]
                    hn = T[h_name][n] if h_name != 'n' else n
                    if fgn == hn and fgn != 0:
                        hits.append(n)

                if 6 in hits:
                    # Check n=28
                    holds_28 = False
                    if 28 <= limit:
                        g28 = T[g_name][28]
                        if 1 <= g28 <= limit:
                            fg28 = T[f_name][g28]
                            h28 = T[h_name][28] if h_name != 'n' else 28
                            holds_28 = (fg28 == h28)

                    results.append({
                        'name': name,
                        'hits': hits,
                        'n_hits': len(hits),
                        'holds_28': holds_28,
                    })

    # ─── Type B: f(g(n)) == K (constant, 1..60) ───
    print("  Testing f(g(n)) == K compositions...", flush=True)

    for f_name in FUNC_NAMES:
        for g_name in FUNC_NAMES:
            g6 = T[g_name][6]
            if g6 < 1 or g6 > limit:
                continue
            fg6 = T[f_name][g6]
            if fg6 < 1 or fg6 > 60:
                continue

            K = fg6
            name = f"{f_name}({g_name}(n)) == {K}"
            hits = []
            for n in range(2, limit + 1):
                gn = T[g_name][n]
                if gn < 1 or gn > limit:
                    continue
                if T[f_name][gn] == K:
                    hits.append(n)

            if 6 in hits:
                holds_28 = False
                if 28 <= limit:
                    g28 = T[g_name][28]
                    if 1 <= g28 <= limit:
                        holds_28 = (T[f_name][g28] == K)

                results.append({
                    'name': name,
                    'hits': hits,
                    'n_hits': len(hits),
                    'holds_28': holds_28,
                })

    # ─── Type C: f(g(h(n))) == n  (3-fold composition fixed point) ───
    print("  Testing f(g(h(n))) == n (3-fold fixed points)...", flush=True)

    for f_name in FUNC_NAMES:
        for g_name in FUNC_NAMES:
            for h_name in FUNC_NAMES:
                h6 = T[h_name][6]
                if h6 < 1 or h6 > limit:
                    continue
                gh6 = T[g_name][h6]
                if gh6 < 1 or gh6 > limit:
                    continue
                fgh6 = T[f_name][gh6]
                if fgh6 != 6:
                    continue

                name = f"{f_name}({g_name}({h_name}(n))) == n"
                hits = []
                for n in range(2, min(limit + 1, 1001)):  # cap for 3-fold
                    hn = T[h_name][n]
                    if hn < 1 or hn > limit:
                        continue
                    ghn = T[g_name][hn]
                    if ghn < 1 or ghn > limit:
                        continue
                    if T[f_name][ghn] == n:
                        hits.append(n)

                if 6 in hits:
                    holds_28 = False
                    if 28 <= limit:
                        h28 = T[h_name][28]
                        if 1 <= h28 <= limit:
                            gh28 = T[g_name][h28]
                            if 1 <= gh28 <= limit:
                                holds_28 = (T[f_name][gh28] == 28)

                    results.append({
                        'name': name,
                        'hits': hits,
                        'n_hits': len(hits),
                        'holds_28': holds_28,
                    })

    # ─── Type D: sigma(n) mod tau(n) == 0, gcd(sigma,phi)==n, etc. ───
    print("  Testing modular and gcd identities...", flush=True)

    for a_name in FUNC_NAMES + ['n']:
        for b_name in FUNC_NAMES + ['n']:
            if a_name == b_name:
                continue

            a6 = T[a_name][6] if a_name != 'n' else 6
            b6 = T[b_name][6] if b_name != 'n' else 6
            if b6 == 0:
                continue

            # a mod b == 0
            if a6 % b6 == 0:
                name = f"{a_name} mod {b_name} == 0"
                hits = []
                for n in range(2, limit + 1):
                    an = T[a_name][n] if a_name != 'n' else n
                    bn = T[b_name][n] if b_name != 'n' else n
                    if bn != 0 and an % bn == 0:
                        hits.append(n)
                if 6 in hits and len(hits) <= 5:
                    holds_28 = 28 in hits
                    results.append({'name': name, 'hits': hits, 'n_hits': len(hits), 'holds_28': holds_28})

            # gcd(a, b) == c
            g6 = math.gcd(a6, b6)
            for c_name in FUNC_NAMES + ['n']:
                c6 = T[c_name][6] if c_name != 'n' else 6
                if g6 != c6 or g6 == 0:
                    continue
                name = f"gcd({a_name},{b_name}) == {c_name}"
                hits = []
                for n in range(2, limit + 1):
                    an = T[a_name][n] if a_name != 'n' else n
                    bn = T[b_name][n] if b_name != 'n' else n
                    cn = T[c_name][n] if c_name != 'n' else n
                    if math.gcd(an, bn) == cn and cn != 0:
                        hits.append(n)
                if 6 in hits and len(hits) <= 5:
                    holds_28 = 28 in hits
                    results.append({'name': name, 'hits': hits, 'n_hits': len(hits), 'holds_28': holds_28})

    # ─── Type E: sigma(n)/tau(n) == phi(n)*something, ratio identities ───
    print("  Testing exact ratio identities...", flush=True)

    for a_name in FUNC_NAMES + ['n']:
        for b_name in FUNC_NAMES + ['n']:
            if a_name == b_name:
                continue
            a6 = T[a_name][6] if a_name != 'n' else 6
            b6 = T[b_name][6] if b_name != 'n' else 6
            if b6 == 0 or a6 % b6 != 0:
                continue
            ratio6 = a6 // b6

            for c_name in FUNC_NAMES + ['n']:
                c6 = T[c_name][6] if c_name != 'n' else 6
                if ratio6 != c6 or c6 == 0:
                    continue

                name = f"{a_name}/{b_name} == {c_name}"
                hits = []
                for n in range(2, limit + 1):
                    an = T[a_name][n] if a_name != 'n' else n
                    bn = T[b_name][n] if b_name != 'n' else n
                    cn = T[c_name][n] if c_name != 'n' else n
                    if bn != 0 and an % bn == 0 and an // bn == cn and cn != 0:
                        hits.append(n)
                if 6 in hits and len(hits) <= 5:
                    holds_28 = 28 in hits
                    results.append({'name': name, 'hits': hits, 'n_hits': len(hits), 'holds_28': holds_28})

    # ─── Type F: n + f(n) == g(n) * h(n) ───
    print("  Testing n + f == g*h mixed identities...", flush=True)

    for f_name in FUNC_NAMES:
        for g_name in FUNC_NAMES:
            for h_name in FUNC_NAMES:
                f6 = T[f_name][6]
                g6 = T[g_name][6]
                h6 = T[h_name][6]
                if 6 + f6 != g6 * h6:
                    continue
                if 6 + f6 == 0:
                    continue

                name = f"n + {f_name} == {g_name}*{h_name}"
                hits = []
                for n in range(2, limit + 1):
                    fn = T[f_name][n]
                    gn = T[g_name][n]
                    hn = T[h_name][n]
                    if n + fn == gn * hn and gn * hn != 0:
                        hits.append(n)
                if 6 in hits and len(hits) <= 5:
                    holds_28 = 28 in hits
                    results.append({'name': name, 'hits': hits, 'n_hits': len(hits), 'holds_28': holds_28})

    # ─── Type G: f(n)^2 + g(n)^2 == h(n) (Pythagorean-like) ───
    print("  Testing Pythagorean-like f^2+g^2 == h...", flush=True)

    for f_name in FUNC_NAMES + ['n']:
        for g_name in FUNC_NAMES + ['n']:
            if f_name > g_name:
                continue
            f6 = T[f_name][6] if f_name != 'n' else 6
            g6 = T[g_name][6] if g_name != 'n' else 6
            sum_sq6 = f6**2 + g6**2

            for h_name in FUNC_NAMES + ['n']:
                h6 = T[h_name][6] if h_name != 'n' else 6
                if sum_sq6 != h6 or h6 == 0:
                    continue

                name = f"{f_name}^2 + {g_name}^2 == {h_name}"
                hits = []
                for n in range(2, limit + 1):
                    fn = T[f_name][n] if f_name != 'n' else n
                    gn = T[g_name][n] if g_name != 'n' else n
                    hn = T[h_name][n] if h_name != 'n' else n
                    if fn**2 + gn**2 == hn and hn != 0:
                        hits.append(n)
                if 6 in hits and len(hits) <= 5:
                    holds_28 = 28 in hits
                    results.append({'name': name, 'hits': hits, 'n_hits': len(hits), 'holds_28': holds_28})

    # ─── Type H: n! == f*g*h*k (factorial as 4-product of arithmetic funcs) ───
    print("  Testing n! == product of functions...", flush=True)

    fact6 = 720
    for a_name in FUNC_NAMES:
        for b_name in FUNC_NAMES:
            if a_name > b_name:
                continue
            a6 = T[a_name][6]
            b6 = T[b_name][6]
            if a6 * b6 == 0:
                continue
            rem = fact6 // (a6 * b6)
            if fact6 != a6 * b6 * rem:
                continue
            for c_name in FUNC_NAMES:
                for d_name in FUNC_NAMES:
                    if c_name > d_name:
                        continue
                    c6 = T[c_name][6]
                    d6 = T[d_name][6]
                    if a6 * b6 * c6 * d6 != fact6:
                        continue

                    name = f"n! == {a_name}*{b_name}*{c_name}*{d_name}"
                    hits = []
                    for n in range(2, min(21, limit + 1)):  # factorial cap
                        fn = math.factorial(n)
                        an = T[a_name][n]
                        bn = T[b_name][n]
                        cn = T[c_name][n]
                        dn = T[d_name][n]
                        if an * bn * cn * dn == fn and fn != 0:
                            hits.append(n)
                    if 6 in hits and len(hits) <= 3:
                        holds_28 = False  # factorial(28) is huge, skip
                        results.append({'name': name, 'hits': hits, 'n_hits': len(hits), 'holds_28': holds_28})

    return results


def main():
    parser = argparse.ArgumentParser(description="DFS n=6 Composition Miner")
    parser.add_argument("--limit", type=int, default=5000, help="Search limit")
    args = parser.parse_args()

    limit = args.limit
    print()
    print("  ================================================================")
    print("  DFS n=6 Composition Miner")
    print(f"  Search limit: n <= {limit}")
    print("  ================================================================")
    print()

    T = build_tables(limit)

    print(f"  n=6: sigma={T['sigma'][6]}, tau={T['tau'][6]}, phi={T['phi'][6]}, "
          f"sopfr={T['sopfr'][6]}, omega={T['omega'][6]}, Omega={T['Omega'][6]}, "
          f"rad={T['rad'][6]}, aliq={T['aliq'][6]}")
    print()

    t0 = time.time()
    results = generate_composition_tests(T, limit)
    t1 = time.time()
    print(f"\n  Total identities found: {len(results)} in {t1-t0:.1f}s")
    print()

    # Deduplicate by hit signature
    seen = set()
    deduped = []
    for r in results:
        sig = tuple(sorted(r['hits']))
        if sig not in seen:
            seen.add(sig)
            deduped.append(r)

    # Sort by rarity
    deduped.sort(key=lambda r: r['n_hits'])

    # Report
    print("  ================================================================")
    print("  RESULTS (sorted by rarity)")
    print("  ================================================================")
    print()

    for r in deduped:
        unique_6 = r['hits'] == [6]
        near_unique = sorted(r['hits']) in ([6], [1, 6])

        if unique_6:
            tag = "+++"
        elif near_unique:
            tag = "++ "
        elif r['n_hits'] <= 3:
            tag = "+  "
        else:
            tag = "~  "

        hit_str = str(r['hits'][:15])
        if len(r['hits']) > 15:
            hit_str += f"... ({r['n_hits']} total)"
        n28 = "YES" if r['holds_28'] else "NO"
        print(f"  [{tag}] {r['name']}")
        print(f"         Hits: {hit_str}  n=28: {n28}")
        print()

    # Summary
    unique_count = sum(1 for r in deduped if r['hits'] == [6])
    near_count = sum(1 for r in deduped if sorted(r['hits']) in ([1, 6],))
    rare_count = sum(1 for r in deduped if r['n_hits'] <= 3 and r['hits'] != [6] and sorted(r['hits']) not in ([1, 6],))

    print("  ================================================================")
    print("  SUMMARY")
    print("  ================================================================")
    print(f"  UNIQUE to n=6:  {unique_count}")
    print(f"  Near-unique:    {near_count}")
    print(f"  Rare (<=3):     {rare_count}")
    print(f"  Total patterns: {len(deduped)}")
    print()


if __name__ == "__main__":
    main()
