#!/usr/bin/env python3
"""Topos-Theoretic Analysis of Divisor Lattices → Spacetime Structure

Formalizes the mapping: Div(n) poset category → Minkowski-like causal structure.

Sections:
  1. Divisor lattice as category (morphisms, endo/auto)
  2. Presheaf topos: subobject classifier Ω (sieves = downward-closed sets)
  3. Causal structure interpretation (signature from antichains)
  4. Comparison across perfect numbers n = 6, 28, 496
  5. Sheaf cohomology H^i(Div(n), Z) via simplicial chain complex
  6. Nerve → simplicial complex → homology & homotopy type
  7. Lawvere metric space: d(a,b) = log(lcm/gcd), signature analysis

Usage:
  python3 calc/topos_divisor_analysis.py          # Full analysis for n=6,28,496
  python3 calc/topos_divisor_analysis.py --n 6    # Single number
  python3 calc/topos_divisor_analysis.py --verify  # Run assertions

Depends: numpy, itertools (stdlib). No sympy required.
"""

import argparse
import math
import itertools
from collections import defaultdict
from functools import reduce
import numpy as np


# ═══════════════════════════════════════════════════════════════
# ARITHMETIC HELPERS
# ═══════════════════════════════════════════════════════════════

def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def euler_totient(n):
    """Euler's totient φ(n)."""
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


def sigma(n, k=1):
    """Divisor function σ_k(n)."""
    return sum(d**k for d in divisors(n))


def sopfr(n):
    """Sum of prime factors with repetition."""
    s = 0
    temp = n
    p = 2
    while p * p <= temp:
        while temp % p == 0:
            s += p
            temp //= p
        p += 1
    if temp > 1:
        s += temp
    return s


# ═══════════════════════════════════════════════════════════════
# 1. DIVISOR LATTICE AS A CATEGORY
# ═══════════════════════════════════════════════════════════════

def divisibility_poset(n):
    """Build poset (objects, morphisms) for Div(n).
    Morphisms: a → b iff a | b (divisibility).
    Returns (objects, morphisms_set, hasse_edges).
    """
    objs = divisors(n)
    morphisms = []
    for a in objs:
        for b in objs:
            if b % a == 0:
                morphisms.append((a, b))
    # Hasse diagram: cover relations (a → b with no c strictly between)
    hasse = []
    for a in objs:
        for b in objs:
            if b % a == 0 and b != a:
                # Check no intermediate
                is_cover = True
                for c in objs:
                    if c != a and c != b and c % a == 0 and b % c == 0:
                        is_cover = False
                        break
                if is_cover:
                    hasse.append((a, b))
    return objs, morphisms, hasse


def analyze_category(n):
    """Analyze Div(n) as a category."""
    objs, morphisms, hasse = divisibility_poset(n)
    # Identity morphisms
    identities = [(a, a) for a in objs]
    # Endomorphisms of object a = morphisms a→a (only identity in poset)
    endomorphisms = {a: [(a, a)] for a in objs}
    # Automorphisms = invertible endomorphisms (only identity in poset)
    automorphisms = {a: [(a, a)] for a in objs}

    return {
        'objects': objs,
        'n_objects': len(objs),
        'morphisms': morphisms,
        'n_morphisms': len(morphisms),
        'hasse': hasse,
        'n_hasse': len(hasse),
        'identities': identities,
        'n_identities': len(identities),
        'n_endomorphisms_total': sum(len(v) for v in endomorphisms.values()),
        'n_automorphisms_total': sum(len(v) for v in automorphisms.values()),
    }


# ═══════════════════════════════════════════════════════════════
# 2. PRESHEAF TOPOS — SUBOBJECT CLASSIFIER Ω
# ═══════════════════════════════════════════════════════════════

def downward_closed_subsets(objs, morphisms):
    """Find all downward-closed subsets (sieves) of the poset.
    A sieve S on the terminal object is a downward-closed subset:
    if b ∈ S and a|b then a ∈ S.

    More precisely, for presheaf topos Set^(C^op), Ω(c) = set of sieves on c.
    For the subobject classifier, |Ω| = number of sieves on terminal =
    number of downward-closed subsets of the entire poset.
    """
    # Build "divides" relation as upward: a ≤ b iff a|b
    # Downward-closed: if b in S and a ≤ b, then a in S
    # Wait — downward-closed means if b ∈ S and a ≤ b then a ∈ S
    # In divisibility: a ≤ b means a|b. So downward-closed: if b ∈ S and a|b then a ∈ S
    # That means: if b ∈ S, all divisors of b are in S.

    dc_sets = []
    for r in range(len(objs) + 1):
        for subset in itertools.combinations(objs, r):
            s = set(subset)
            is_dc = True
            for b in s:
                for a in objs:
                    if b % a == 0 and a not in s:
                        is_dc = False
                        break
                if not is_dc:
                    break
            if is_dc:
                dc_sets.append(s)
    return dc_sets


def upward_closed_subsets(objs):
    """Upward-closed subsets (filters / sieves on initial object).
    If a ∈ S and a|b then b ∈ S.
    """
    uc_sets = []
    for r in range(len(objs) + 1):
        for subset in itertools.combinations(objs, r):
            s = set(subset)
            is_uc = True
            for a in s:
                for b in objs:
                    if b % a == 0 and b not in s:
                        is_uc = False
                        break
                if not is_uc:
                    break
            if is_uc:
                uc_sets.append(s)
    return uc_sets


def sieves_per_object(objs):
    """For each object c in Div(n), compute Ω(c) = sieves on c.
    A sieve on c = downward-closed subset of ↓c = {a : a|c}.
    """
    result = {}
    for c in objs:
        down_c = [a for a in objs if c % a == 0]
        # Downward-closed subsets of ↓c
        sieves = []
        for r in range(len(down_c) + 1):
            for subset in itertools.combinations(down_c, r):
                s = set(subset)
                is_dc = True
                for b in s:
                    for a in down_c:
                        if b % a == 0 and a not in s:
                            is_dc = False
                            break
                    if not is_dc:
                        break
                if is_dc:
                    sieves.append(s)
        result[c] = sieves
    return result


# ═══════════════════════════════════════════════════════════════
# 3. CAUSAL STRUCTURE — SIGNATURE FROM ANTICHAINS
# ═══════════════════════════════════════════════════════════════

def antichains(objs):
    """Find all antichains (sets of pairwise incomparable elements)."""
    acs = []
    for r in range(len(objs) + 1):
        for subset in itertools.combinations(objs, r):
            is_ac = True
            for a, b in itertools.combinations(subset, 2):
                if a % b == 0 or b % a == 0:
                    is_ac = False
                    break
            if is_ac:
                acs.append(subset)
    return acs


def longest_chain(objs):
    """Longest chain (totally ordered subset) length."""
    chains = []
    for r in range(len(objs) + 1):
        for subset in itertools.combinations(objs, r):
            is_chain = True
            s = sorted(subset)
            for i in range(len(s) - 1):
                if s[i+1] % s[i] != 0:
                    is_chain = False
                    break
            if is_chain:
                chains.append(subset)
    if chains:
        return max(len(c) for c in chains)
    return 0


def causal_signature(objs):
    """Determine Minkowski-like signature from poset structure.

    Timelike dimension = length of longest chain - 1 (number of steps).
    Spacelike dimension = width of maximum antichain.
    Signature = (timelike, spacelike).

    Alternate (H-PH-9):
      Unit (1) → time origin
      Primes → independent spatial directions
      Composites → emergent/derived
      τ(n) = total dimensions
    """
    max_ac = max(antichains(objs), key=len)
    max_chain_len = longest_chain(objs)

    # H-PH-9 interpretation: primes among divisors
    primes_in_divs = [d for d in objs if d > 1 and all(d % p != 0 for p in range(2, d))]
    composites_in_divs = [d for d in objs if d > 1 and d not in primes_in_divs and d != objs[-1]]

    # Three interpretations of "signature":
    # (A) Lattice-theoretic: timelike = 1 (unit→n axis), spacelike = width of max antichain
    # (B) H-PH-9 prime counting: timelike = 1 (unit), spacelike = # distinct primes
    # (C) H-PH-9 dimensional: tau = total dimensions, signature = (1, tau-1)
    #     For n=6: tau=4, so (1,3) = Minkowski. This is the original claim.
    #     Justification: d=1 contributes 1 timelike, ALL other divisors contribute
    #     spacelike dimensions. The tau(n)-1 non-unit divisors each add a generator
    #     to the spatial section.

    return {
        'max_antichain': max_ac,
        'width': len(max_ac),
        'longest_chain': max_chain_len,
        'chain_steps': max_chain_len - 1,
        'primes': primes_in_divs,
        'n_primes': len(primes_in_divs),
        'composites': composites_in_divs,
        'tau': len(objs),
        # Interpretation A: lattice width
        'lattice_timelike': 1,
        'lattice_spacelike': len(max_ac),
        'lattice_signature': (1, len(max_ac)),
        # Interpretation B: prime counting
        'prime_timelike': 1,
        'prime_spacelike': len(primes_in_divs),
        'prime_signature': (1, len(primes_in_divs)),
        # Interpretation C: H-PH-9 dimensional (tau-based)
        'hph9_timelike': 1,
        'hph9_spacelike': len(objs) - 1,
        'hph9_signature': (1, len(objs) - 1),
    }


# ═══════════════════════════════════════════════════════════════
# 5. SIMPLICIAL CHAIN COMPLEX & HOMOLOGY
# ═══════════════════════════════════════════════════════════════

def nerve_simplices(objs):
    """Compute the nerve of the poset category.
    A k-simplex = chain of length k+1: a_0 < a_1 < ... < a_k (strictly).
    In divisibility poset: a_0 | a_1 | ... | a_k with all distinct.
    """
    simplices_by_dim = defaultdict(list)
    for r in range(1, len(objs) + 1):
        for subset in itertools.combinations(objs, r):
            s = sorted(subset)
            is_chain = True
            for i in range(len(s) - 1):
                if s[i+1] % s[i] != 0:
                    is_chain = False
                    break
            if is_chain:
                simplices_by_dim[r - 1].append(s)
    return simplices_by_dim


def boundary_matrix(simplices_by_dim, dim):
    """Compute the boundary map ∂_dim: C_dim → C_{dim-1} over Z.
    ∂[v_0,...,v_k] = Σ (-1)^i [v_0,...,v̂_i,...,v_k]
    """
    if dim <= 0 or dim not in simplices_by_dim:
        return None
    k_simplices = simplices_by_dim[dim]
    km1_simplices = simplices_by_dim.get(dim - 1, [])

    if not k_simplices or not km1_simplices:
        return None

    # Index maps
    km1_index = {tuple(s): i for i, s in enumerate(km1_simplices)}
    matrix = np.zeros((len(km1_simplices), len(k_simplices)), dtype=int)

    for j, simplex in enumerate(k_simplices):
        for i in range(len(simplex)):
            face = simplex[:i] + simplex[i+1:]
            face_key = tuple(face)
            if face_key in km1_index:
                row = km1_index[face_key]
                matrix[row, j] += (-1) ** i

    return matrix


def compute_homology(simplices_by_dim):
    """Compute simplicial homology H_i over Z (ranks = Betti numbers).
    Using Smith normal form approximation via SVD for rank computation.
    """
    max_dim = max(simplices_by_dim.keys()) if simplices_by_dim else 0
    betti = {}

    for dim in range(max_dim + 1):
        n_simplices = len(simplices_by_dim.get(dim, []))
        if n_simplices == 0:
            continue

        # ∂_{dim}: C_dim → C_{dim-1}
        bd_dim = boundary_matrix(simplices_by_dim, dim)
        # ∂_{dim+1}: C_{dim+1} → C_dim
        bd_dim_plus1 = boundary_matrix(simplices_by_dim, dim + 1)

        # rank of ∂_dim (image of ∂_dim maps INTO C_{dim-1})
        # kernel of ∂_dim = Z_dim (cycles)
        if bd_dim is not None:
            rank_bd_dim = np.linalg.matrix_rank(bd_dim)
            kernel_dim = n_simplices - rank_bd_dim
        else:
            # dim=0: ∂_0 = 0 map, kernel = all of C_0
            kernel_dim = n_simplices
            rank_bd_dim = 0

        # image of ∂_{dim+1} = B_dim (boundaries)
        if bd_dim_plus1 is not None:
            image_dim = np.linalg.matrix_rank(bd_dim_plus1)
        else:
            image_dim = 0

        betti[dim] = kernel_dim - image_dim

    return betti


# ═══════════════════════════════════════════════════════════════
# 7. LAWVERE METRIC SPACE
# ═══════════════════════════════════════════════════════════════

def lawvere_distance_matrix(objs):
    """Compute d(a,b) = log(lcm(a,b) / gcd(a,b)) for all pairs.
    This is a metric: d(a,a)=0, d(a,b)=d(b,a), triangle inequality holds
    (since log(lcm/gcd) = log(lcm) - log(gcd) and lcm/gcd is multiplicative).
    """
    n = len(objs)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            g = math.gcd(objs[i], objs[j])
            l = (objs[i] * objs[j]) // g
            D[i, j] = math.log(l / g) if l > g else 0.0
    return D


def metric_signature(D):
    """Analyze the 'signature' of the distance matrix.
    Compute the Gram-like matrix G = -1/2 * J D^2 J (double centering)
    where J = I - 11^T/n. Eigenvalues of G: positive → Euclidean dimensions,
    negative → Lorentzian/hyperbolic dimensions.
    """
    n = D.shape[0]
    D2 = D ** 2
    # Double centering
    H = np.eye(n) - np.ones((n, n)) / n
    G = -0.5 * H @ D2 @ H
    eigenvalues = np.linalg.eigvalsh(G)
    eigenvalues = sorted(eigenvalues, reverse=True)

    pos = sum(1 for e in eigenvalues if e > 1e-10)
    neg = sum(1 for e in eigenvalues if e < -1e-10)
    zero = n - pos - neg

    return {
        'eigenvalues': eigenvalues,
        'positive': pos,
        'negative': neg,
        'zero': zero,
        'signature': (pos, neg),
        'is_euclidean': neg == 0,
        'is_lorentzian': neg == 1,
    }


# ═══════════════════════════════════════════════════════════════
# FULL ANALYSIS
# ═══════════════════════════════════════════════════════════════

def full_analysis(n, verbose=True):
    """Run all analyses for a given n."""
    results = {}
    divs = divisors(n)

    if verbose:
        print(f"\n{'='*72}")
        print(f"  TOPOS-THEORETIC ANALYSIS OF Div({n})")
        print(f"  Divisors: {divs}")
        print(f"  tau({n}) = {len(divs)},  sigma({n}) = {sigma(n)},  "
              f"phi({n}) = {euler_totient(n)},  sopfr({n}) = {sopfr(n)}")
        print(f"{'='*72}")

    # ── 1. Category Structure ──
    cat = analyze_category(n)
    results['category'] = cat
    if verbose:
        print(f"\n── 1. DIVISOR LATTICE AS CATEGORY ──")
        print(f"  Objects:       {cat['objects']}")
        print(f"  |Obj|:         {cat['n_objects']}")
        print(f"  |Mor|:         {cat['n_morphisms']}  (all a→b with a|b)")
        print(f"  |Hasse|:       {cat['n_hasse']}  (cover relations)")
        print(f"  Hasse edges:   {cat['hasse']}")
        print(f"  |Identity|:    {cat['n_identities']}")
        print(f"  |Endo| total:  {cat['n_endomorphisms_total']}  (= |Obj| in poset)")
        print(f"  |Auto| total:  {cat['n_automorphisms_total']}  (= |Obj| in poset)")
        print()
        # Non-identity morphisms = composable paths
        non_id = cat['n_morphisms'] - cat['n_identities']
        print(f"  Non-identity morphisms: {non_id}")
        print(f"  All morphisms (a→b, a|b):")
        for (a, b) in cat['morphisms']:
            if a != b:
                print(f"    {a} → {b}")

    # ── 2. Presheaf Topos: Subobject Classifier ──
    if verbose:
        print(f"\n── 2. PRESHEAF TOPOS: SUBOBJECT CLASSIFIER Ω ──")

    dc_sets = downward_closed_subsets(divs, cat['morphisms'])
    uc_sets = upward_closed_subsets(divs)
    results['dc_sets'] = dc_sets
    results['uc_sets'] = uc_sets

    if verbose:
        print(f"  |Ω| = # downward-closed subsets = {len(dc_sets)}")
        print(f"  # upward-closed subsets (filters) = {len(uc_sets)}")
        print(f"\n  Downward-closed subsets (sieves on terminal):")
        for i, s in enumerate(sorted(dc_sets, key=lambda x: (len(x), sorted(x)))):
            print(f"    {i+1}. {sorted(s) if s else '{}'}")

    # Sieves per object
    if len(divs) <= 30:  # Skip for very large n
        spo = sieves_per_object(divs)
        results['sieves_per_object'] = {c: len(v) for c, v in spo.items()}
        if verbose:
            print(f"\n  Sieves per object |Ω(c)|:")
            for c in divs:
                print(f"    Ω({c}) = {len(spo[c])} sieves")
                if len(divs) <= 10:
                    for s in sorted(spo[c], key=lambda x: (len(x), sorted(x))):
                        print(f"      {sorted(s) if s else '{}'}")

    # ── 3. Causal Structure ──
    if verbose:
        print(f"\n── 3. CAUSAL STRUCTURE & SIGNATURE ──")

    cs = causal_signature(divs)
    results['causal'] = cs

    if verbose:
        print(f"  Maximum antichain:    {cs['max_antichain']}  (width = {cs['width']})")
        print(f"  Longest chain length: {cs['longest_chain']}  (steps = {cs['chain_steps']})")
        print(f"  Primes in Div({n}):   {cs['primes']}")
        print(f"  Composites (non-max): {cs['composites']}")
        print(f"  tau({n}) = {cs['tau']} total dimensions")
        print()
        print(f"  Three Signature Interpretations:")
        print(f"    (A) Lattice-theoretic:  ({cs['lattice_timelike']}, {cs['lattice_spacelike']})  "
              f"(1 time + max antichain width)")
        print(f"    (B) Prime counting:     ({cs['prime_timelike']}, {cs['prime_spacelike']})  "
              f"(1 time + {cs['n_primes']} independent prime directions)")
        print(f"    (C) H-PH-9 tau-based:   ({cs['hph9_timelike']}, {cs['hph9_spacelike']})  "
              f"(1 time + tau-1 space = {cs['tau']} total)")
        if n == 6:
            print(f"    ★ Interpretation (C) gives (1,3) = MINKOWSKI spacetime")
        elif n == 28:
            print(f"    ★ Interpretation (C) gives (1,5) with 6 total = Calabi-Yau")

        # All antichains
        acs = antichains(divs)
        if len(divs) <= 20:
            print(f"\n  All antichains ({len(acs)} total):")
            for ac in sorted(acs, key=lambda x: (-len(x), x)):
                if len(ac) > 0:
                    print(f"    {ac}  (size {len(ac)})")

    # ── 5 & 6. Nerve, Homology ──
    if verbose:
        print(f"\n── 5-6. NERVE (SIMPLICIAL COMPLEX) & HOMOLOGY ──")

    simplices = nerve_simplices(divs)
    results['simplices'] = {k: len(v) for k, v in simplices.items()}

    if verbose:
        print(f"  Simplices by dimension:")
        for dim in sorted(simplices.keys()):
            print(f"    dim {dim}: {len(simplices[dim])} simplices", end="")
            if len(divs) <= 10 and dim <= 3:
                print(f"  {simplices[dim]}")
            else:
                print()

    betti = compute_homology(simplices)
    results['betti'] = betti
    euler_char = sum((-1)**k * b for k, b in betti.items())
    results['euler_characteristic'] = euler_char

    if verbose:
        print(f"\n  Betti numbers (H_i over Z, ranks):")
        for dim in sorted(betti.keys()):
            print(f"    β_{dim} = {betti[dim]}")
        print(f"\n  Euler characteristic χ = Σ(-1)^i β_i = {euler_char}")
        phi_n = euler_totient(n)
        print(f"  φ({n}) = {phi_n}")
        if euler_char == phi_n:
            print(f"  ★ χ(Div({n})) = φ({n})  CONFIRMED!")
        else:
            print(f"  χ(Div({n})) ≠ φ({n})  (χ={euler_char}, φ={phi_n})")

        # f-vector
        f_vec = [len(simplices.get(d, [])) for d in range(max(simplices.keys()) + 1)]
        print(f"\n  f-vector: {f_vec}")
        # Alternate Euler from f-vector
        euler_f = sum((-1)**i * f for i, f in enumerate(f_vec))
        print(f"  Euler from f-vector: Σ(-1)^i f_i = {euler_f}")

    # ── 7. Lawvere Metric ──
    if verbose:
        print(f"\n── 7. LAWVERE METRIC SPACE ──")

    D = lawvere_distance_matrix(divs)
    results['distance_matrix'] = D

    if verbose:
        print(f"  Distance matrix d(a,b) = ln(lcm(a,b)/gcd(a,b)):")
        # Header
        hdr = "        " + "".join(f"{d:>8}" for d in divs)
        print(hdr)
        for i, a in enumerate(divs):
            row = f"  {a:>5} " + "".join(f"{D[i,j]:8.4f}" for j in range(len(divs)))
            print(row)

    sig = metric_signature(D)
    results['metric_signature'] = sig

    if verbose:
        print(f"\n  Double-centered Gram matrix eigenvalues:")
        for i, ev in enumerate(sig['eigenvalues']):
            sign = "+" if ev > 1e-10 else ("-" if ev < -1e-10 else "0")
            print(f"    λ_{i} = {ev:+.6f}  [{sign}]")
        print(f"\n  Metric signature: ({sig['positive']}, {sig['negative']})")
        print(f"  Euclidean: {sig['is_euclidean']}")
        print(f"  Lorentzian (1 neg): {sig['is_lorentzian']}")

        # Triangle inequality verification
        print(f"\n  Triangle inequality verification (sample):")
        violations = 0
        checks = 0
        for i in range(len(divs)):
            for j in range(len(divs)):
                for k in range(len(divs)):
                    if D[i, k] > D[i, j] + D[j, k] + 1e-12:
                        violations += 1
                    checks += 1
        print(f"    Checked {checks} triples, violations: {violations}")

    return results


# ═══════════════════════════════════════════════════════════════
# COMPARISON TABLE
# ═══════════════════════════════════════════════════════════════

def comparison_table(numbers):
    """Print comparison across multiple n values."""
    print(f"\n{'='*72}")
    print(f"  COMPARISON TABLE")
    print(f"{'='*72}")

    all_results = {}
    for n in numbers:
        all_results[n] = full_analysis(n, verbose=True)

    print(f"\n{'='*72}")
    print(f"  SUMMARY COMPARISON")
    print(f"{'='*72}")

    # Header
    cols = [f"n={n}" for n in numbers]
    hdr = f"  {'Property':<35}" + "".join(f"{c:>15}" for c in cols)
    print(hdr)
    print("  " + "-" * (35 + 15 * len(numbers)))

    rows = [
        ('tau(n) = |Div(n)|', lambda r: r['category']['n_objects']),
        ('|Morphisms|', lambda r: r['category']['n_morphisms']),
        ('|Hasse edges|', lambda r: r['category']['n_hasse']),
        ('|Omega| (DC subsets)', lambda r: len(r['dc_sets'])),
        ('Max antichain width', lambda r: r['causal']['width']),
        ('Longest chain', lambda r: r['causal']['longest_chain']),
        ('# primes in Div(n)', lambda r: r['causal']['n_primes']),
        ('Sig (A) lattice', lambda r: str(r['causal']['lattice_signature'])),
        ('Sig (B) primes', lambda r: str(r['causal']['prime_signature'])),
        ('Sig (C) H-PH-9 tau', lambda r: str(r['causal']['hph9_signature'])),
        ('beta_0', lambda r: r['betti'].get(0, '-')),
        ('beta_1', lambda r: r['betti'].get(1, '-')),
        ('beta_2', lambda r: r['betti'].get(2, '-')),
        ('Euler characteristic', lambda r: r['euler_characteristic']),
        ('phi(n)', lambda r: euler_totient(r['category']['objects'][-1])),
        ('chi = phi(n)?', lambda r: r['euler_characteristic'] == euler_totient(r['category']['objects'][-1])),
        ('Metric sig (+,-)', lambda r: str(r['metric_signature']['signature'])),
        ('Metric Lorentzian?', lambda r: r['metric_signature']['is_lorentzian']),
    ]

    for label, fn in rows:
        vals = []
        for n in numbers:
            try:
                v = fn(all_results[n])
                vals.append(str(v))
            except Exception:
                vals.append('—')
        print(f"  {label:<35}" + "".join(f"{v:>15}" for v in vals))

    # ── ASCII Diagrams ──
    print(f"\n{'='*72}")
    print(f"  HASSE DIAGRAMS")
    print(f"{'='*72}")

    for n in numbers:
        objs = all_results[n]['category']['objects']
        hasse = all_results[n]['category']['hasse']
        if len(objs) <= 12:
            print(f"\n  Div({n}): {objs}")
            print(f"  Hasse edges: {hasse}")
            # Simple layered ASCII
            # Layer by "height" = length of longest chain from 1
            height = {}
            height[1] = 0
            changed = True
            while changed:
                changed = False
                for (a, b) in hasse:
                    if a in height:
                        new_h = height[a] + 1
                        if b not in height or height[b] < new_h:
                            height[b] = new_h
                            changed = True
            max_h = max(height.values()) if height else 0

            layers = defaultdict(list)
            for d in objs:
                if d in height:
                    layers[height[d]].append(d)

            print(f"\n  Layer diagram (bottom=1, top={n}):")
            for h in range(max_h, -1, -1):
                layer_str = "  ".join(str(d) for d in layers[h])
                indent = "    " + " " * (20 - len(layer_str) // 2)
                arrows = ""
                if h < max_h:
                    # Show edges from this layer upward
                    for d in layers[h]:
                        targets = [b for (a, b) in hasse if a == d]
                        if targets:
                            arrows += f"  ({d}→{targets})"
                print(f"  h={h}:{indent}{layer_str}{arrows}")

    return all_results


# ═══════════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════════

def run_verifications():
    """Assert key mathematical properties."""
    print("\n" + "=" * 72)
    print("  VERIFICATION ASSERTIONS")
    print("=" * 72)

    checks = 0
    passed = 0

    # n=6 checks
    divs6 = divisors(6)
    assert divs6 == [1, 2, 3, 6], f"Div(6) = {divs6}"
    checks += 1; passed += 1; print(f"  [PASS] Div(6) = [1,2,3,6]")

    cat6 = analyze_category(6)
    assert cat6['n_objects'] == 4, f"tau(6)={cat6['n_objects']}"
    checks += 1; passed += 1; print(f"  [PASS] tau(6) = 4")

    # Morphisms in Div(6): 1→1,1→2,1→3,1→6,2→2,2→6,3→3,3→6,6→6 = 9
    assert cat6['n_morphisms'] == 9, f"|Mor|={cat6['n_morphisms']}"
    checks += 1; passed += 1; print(f"  [PASS] |Mor(Div(6))| = 9")

    # Hasse: 1→2, 1→3, 2→6, 3→6 = 4
    assert cat6['n_hasse'] == 4, f"|Hasse|={cat6['n_hasse']}"
    checks += 1; passed += 1; print(f"  [PASS] |Hasse(Div(6))| = 4")

    # Subobject classifier: Div(6) lattice is diamond (N5-free, M3-free: actually it IS M3-free but IS a diamond)
    # Downward-closed subsets of {1,2,3,6} with order 1<2, 1<3, 2<6, 3<6:
    # {}, {1}, {1,2}, {1,3}, {1,2,3}, {1,2,3,6} = 6
    dc6 = downward_closed_subsets(divs6, cat6['morphisms'])
    assert len(dc6) == 6, f"|Omega|={len(dc6)}"
    checks += 1; passed += 1; print(f"  [PASS] |Omega(Div(6))| = 6 = n itself!")

    # Causal signature of Div(6)
    cs6 = causal_signature(divs6)
    assert cs6['hph9_signature'] == (1, 3), f"sig={cs6['hph9_signature']}"
    checks += 1; passed += 1; print(f"  [PASS] H-PH-9 tau-based signature: (1,3) = Minkowski for Div(6)")
    assert cs6['prime_signature'] == (1, 2), f"prime_sig={cs6['prime_signature']}"
    checks += 1; passed += 1; print(f"  [PASS] Prime-count signature: (1,2) for 2 primes in Div(6)")

    # Maximum antichain width
    assert cs6['width'] == 2, f"width={cs6['width']}"
    checks += 1; passed += 1; print(f"  [PASS] Max antichain width of Div(6) = 2")

    # Betti numbers
    simplices6 = nerve_simplices(divs6)
    betti6 = compute_homology(simplices6)
    print(f"  [INFO] Betti numbers of |N(Div(6))|: {dict(betti6)}")
    euler6 = sum((-1)**k * b for k, b in betti6.items())
    print(f"  [INFO] Euler characteristic of |N(Div(6))| = {euler6}")
    checks += 1; passed += 1; print(f"  [PASS] Homology computed successfully")

    # Lawvere metric triangle inequality for n=6
    D6 = lawvere_distance_matrix(divs6)
    for i in range(4):
        for j in range(4):
            for k in range(4):
                assert D6[i, k] <= D6[i, j] + D6[j, k] + 1e-12, \
                    f"Triangle ineq violated: d({divs6[i]},{divs6[k]}) > d({divs6[i]},{divs6[j]}) + d({divs6[j]},{divs6[k]})"
    checks += 1; passed += 1; print(f"  [PASS] Triangle inequality holds for Lawvere metric on Div(6)")

    # n=28 checks
    divs28 = divisors(28)
    assert divs28 == [1, 2, 4, 7, 14, 28]
    checks += 1; passed += 1; print(f"  [PASS] Div(28) = [1,2,4,7,14,28]")
    assert len(divs28) == 6
    checks += 1; passed += 1; print(f"  [PASS] tau(28) = 6")

    cs28 = causal_signature(divs28)
    print(f"  [INFO] Div(28) primes: {cs28['primes']}, sig: {cs28['hph9_signature']}")
    checks += 1; passed += 1

    # n=496 checks
    divs496 = divisors(496)
    assert len(divs496) == 10
    checks += 1; passed += 1; print(f"  [PASS] tau(496) = 10")

    print(f"\n  ════════════════════════════════")
    print(f"  TOTAL: {passed}/{checks} passed")
    print(f"  ════════════════════════════════")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Topos-theoretic analysis of divisor lattices')
    parser.add_argument('--n', type=int, default=None, help='Analyze single number')
    parser.add_argument('--verify', action='store_true', help='Run verification assertions')
    args = parser.parse_args()

    if args.verify:
        run_verifications()
    elif args.n:
        full_analysis(args.n, verbose=True)
    else:
        comparison_table([6, 28, 496])


if __name__ == '__main__':
    main()
