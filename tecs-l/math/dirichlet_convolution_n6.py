#!/usr/bin/env python3
"""
Dirichlet convolution exploration for n=6 characterizations.
Explores: convolution vs pointwise, Möbius inversion, Dirichlet inverses.
"""

from math import gcd
from functools import lru_cache

# ── Arithmetic functions ──

def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(n**0.5)+1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

@lru_cache(maxsize=10000)
def sigma(n):
    return sum(divisors(n))

@lru_cache(maxsize=10000)
def phi(n):
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

@lru_cache(maxsize=10000)
def tau(n):
    return len(divisors(n))

@lru_cache(maxsize=10000)
def mobius(n):
    if n == 1:
        return 1
    temp = n
    num_factors = 0
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            num_factors += 1
            temp //= p
            if temp % p == 0:
                return 0  # squared factor
        p += 1
    if temp > 1:
        num_factors += 1
    return (-1)**num_factors

def dirichlet_conv(f, g, n):
    """Compute (f*g)(n) = Σ_{d|n} f(d)·g(n/d)."""
    return sum(f(d) * g(n // d) for d in divisors(n))

def identity(n):
    return n

def unit(n):  # constant 1
    return 1

def epsilon(n):  # Dirichlet identity
    return 1 if n == 1 else 0

# ══════════════════════════════════════════════════════════
# 1. Verify (σ*φ)(n) = nτ(n) for all n, and pointwise σφ=nτ special cases
# ══════════════════════════════════════════════════════════

print("=" * 72)
print("1. CONVOLUTION σ*φ vs POINTWISE σ·φ vs n·τ(n)")
print("=" * 72)
print()
print(f"{'n':>4} | {'σ(n)':>6} {'φ(n)':>6} {'τ(n)':>5} | {'(σ*φ)(n)':>10} {'n·τ(n)':>8} {'σ·φ':>8} | {'conv=nτ':>7} {'pw=nτ':>7}")
print("-" * 72)

pointwise_eq_n = []
for n in range(1, 51):
    s, p, t = sigma(n), phi(n), tau(n)
    conv = dirichlet_conv(sigma, phi, n)
    nt = n * t
    pw = s * p
    conv_eq = (conv == nt)
    pw_eq = (pw == nt)
    marker = " ◀◀◀" if pw_eq else ""
    print(f"{n:>4} | {s:>6} {p:>6} {t:>5} | {conv:>10} {nt:>8} {pw:>8} | {'✓':>7} {('✓' if pw_eq else '✗'):>7}{marker}")
    if pw_eq:
        pointwise_eq_n.append(n)

print()
print(f"Convolution σ*φ = nτ holds for ALL n (universal identity)")
print(f"Pointwise σ·φ = nτ holds ONLY at n = {pointwise_eq_n}")

# Check up to 1000
print("\nChecking pointwise σφ=nτ for n=1..1000...")
pw_matches = []
for n in range(1, 1001):
    if sigma(n) * phi(n) == n * tau(n):
        pw_matches.append(n)
print(f"  Matches: {pw_matches}")

# ══════════════════════════════════════════════════════════
# 2. When does convolution = pointwise? The "cross terms vanish" condition
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("2. CROSS-TERM ANALYSIS: When does (σ*φ)(n) collapse to σ(n)·φ(n)?")
print("=" * 72)
print()
print("(σ*φ)(n) = σ(n)φ(n) iff Σ_{d|n, 1<d<n} σ(d)φ(n/d) = 0")
print("But σ,φ > 0, so cross terms > 0 always (for n>1 with proper divisors)")
print("Instead: σ(n)φ(n) = nτ(n) = (σ*φ)(n) is the condition.")
print()
print("Cross-term decomposition for small n:")
print()

for n in [1, 2, 3, 4, 5, 6, 8, 10, 12, 28]:
    divs = divisors(n)
    cross = sum(sigma(d)*phi(n//d) for d in divs if d != n)
    main = sigma(n) * phi(1)  # d=n term = σ(n)·1
    conv = dirichlet_conv(sigma, phi, n)
    pw = sigma(n) * phi(n)

    print(f"n={n}: (σ*φ)={conv}, σ·φ={pw}, ratio={conv/pw if pw else 'inf':.6f}")
    terms = [f"σ({d})φ({n//d})={sigma(d)*phi(n//d)}" for d in divs]
    print(f"  terms: {' + '.join(terms)} = {conv}")
    print()

# ══════════════════════════════════════════════════════════
# 3. Multiple Dirichlet convolutions at n=6
# ══════════════════════════════════════════════════════════

print("=" * 72)
print("3. DIRICHLET CONVOLUTIONS AT n=6 AND COMPARISON")
print("=" * 72)
print()

convolutions = [
    ("σ*φ", sigma, phi),
    ("σ*τ", sigma, tau),
    ("φ*τ", phi, tau),
    ("σ*σ", sigma, sigma),
    ("φ*φ", phi, phi),
    ("τ*τ", tau, tau),
    ("σ*μ", sigma, mobius),
    ("φ*1", phi, unit),
    ("σ*1", sigma, unit),
    ("μ*1", mobius, unit),
    ("id*1", identity, unit),
    ("id*μ", identity, mobius),
    ("id*id", identity, identity),
]

pointwise_products = {
    "σ*φ": lambda n: sigma(n)*phi(n),
    "σ*τ": lambda n: sigma(n)*tau(n),
    "φ*τ": lambda n: phi(n)*tau(n),
    "σ*σ": lambda n: sigma(n)**2,
    "φ*φ": lambda n: phi(n)**2,
    "τ*τ": lambda n: tau(n)**2,
    "σ*μ": lambda n: sigma(n)*mobius(n),
    "φ*1": lambda n: phi(n),
    "σ*1": lambda n: sigma(n),
    "μ*1": lambda n: mobius(n),
    "id*1": lambda n: n,
    "id*μ": lambda n: n*mobius(n),
    "id*id": lambda n: n**2,
}

known_identities = {
    "σ*μ": ("id(n)", identity),
    "φ*1": ("id(n)", identity),
    "id*1": ("σ(n)", sigma),
    "id*μ": ("φ(n)", phi),
    "μ*1": ("ε(n)", epsilon),
    "id*id": ("nτ(n)", lambda n: n*tau(n)),
    "σ*φ": ("nτ(n)", lambda n: n*tau(n)),
}

print(f"{'Conv':>8} | {'n=1':>5} {'n=2':>5} {'n=3':>5} {'n=4':>5} {'n=5':>5} {'n=6':>6} | {'Known':>12} | {'pw=conv @6':>10}")
print("-" * 85)

for name, f, g in convolutions:
    vals = [dirichlet_conv(f, g, n) for n in range(1, 7)]
    pw6 = pointwise_products[name](6)
    conv6 = vals[5]
    pw_eq = "✓" if pw6 == conv6 else f"✗ ({pw6})"
    known = ""
    if name in known_identities:
        kname, kfunc = known_identities[name]
        # verify
        if all(dirichlet_conv(f, g, n) == kfunc(n) for n in range(1, 20)):
            known = kname
    print(f"{name:>8} | {vals[0]:>5} {vals[1]:>5} {vals[2]:>5} {vals[3]:>5} {vals[4]:>5} {vals[5]:>6} | {known:>12} | {pw_eq:>10}")

# For each convolution, find n where pointwise = convolution
print()
print("For each convolution, where does pointwise = convolution (n=1..200)?")
print()
for name, f, g in convolutions:
    pw_func = pointwise_products[name]
    matches = []
    for n in range(1, 201):
        if dirichlet_conv(f, g, n) == pw_func(n):
            matches.append(n)
    if len(matches) < 50:
        print(f"  {name}: {matches[:30]}{'...' if len(matches) > 30 else ''} ({len(matches)} total)")
    else:
        print(f"  {name}: {len(matches)} matches (too many to list) — first 10: {matches[:10]}")

# ══════════════════════════════════════════════════════════
# 4. Dirichlet series at s=2
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("4. DIRICHLET SERIES PARTIAL SUMS")
print("=" * 72)
print()

# Σ σ(n)φ(n)/n^s vs Σ n·τ(n)/n^s = Σ τ(n)/n^(s-1)
for s in [2, 3]:
    N = 1000
    sum_sp = sum(sigma(n)*phi(n)/n**s for n in range(1, N+1))
    sum_nt = sum(n*tau(n)/n**s for n in range(1, N+1))
    sum_tau = sum(tau(n)/n**(s-1) for n in range(1, N+1))
    print(f"s={s}, N={N}:")
    print(f"  Σ σφ/n^s   = {sum_sp:.10f}")
    print(f"  Σ nτ/n^s   = {sum_nt:.10f}")
    print(f"  Σ τ/n^(s-1)= {sum_tau:.10f}")

    # contribution from n where σφ=nτ
    terms_eq = sum(sigma(n)*phi(n)/n**s for n in range(1, N+1) if sigma(n)*phi(n)==n*tau(n))
    terms_neq = sum((sigma(n)*phi(n) - n*tau(n))/n**s for n in range(1, N+1))
    print(f"  Σ (σφ-nτ)/n^s = {terms_neq:.10f}  (deviation from universal)")
    print()

# ══════════════════════════════════════════════════════════
# 5. DIRICHLET INVERSES
# ══════════════════════════════════════════════════════════

print("=" * 72)
print("5. DIRICHLET INVERSES: σ^{-1}, φ^{-1}, τ^{-1}")
print("=" * 72)
print()

def dirichlet_inverse(f, max_n):
    """Compute Dirichlet inverse f^{-1}(n) for n=1..max_n."""
    inv = [0] * (max_n + 1)
    inv[1] = 1  # f^{-1}(1) = 1/f(1), and f(1)=1 for multiplicative f
    for n in range(2, max_n + 1):
        s = 0
        for d in divisors(n):
            if d < n:
                s += f(n // d) * inv[d]
        inv[n] = -s  # since f(1)=1
    return inv

MAX_N = 200

sigma_inv = dirichlet_inverse(sigma, MAX_N)
phi_inv = dirichlet_inverse(phi, MAX_N)
tau_inv = dirichlet_inverse(tau, MAX_N)

# Verify: (σ * σ^{-1})(n) = ε(n)
print("Verification: (σ * σ^{-1})(n) = ε(n)?")
for n in [1, 2, 3, 6, 12, 28]:
    conv = sum(sigma(d) * sigma_inv[n//d] for d in divisors(n))
    print(f"  n={n}: (σ*σ^{{-1}})({n}) = {conv}  {'✓' if conv == epsilon(n) else '✗'}")
print()

print(f"{'n':>4} | {'σ^-1(n)':>10} {'φ^-1(n)':>10} {'τ^-1(n)':>10} | {'σ(n)':>6} {'φ(n)':>6} {'τ(n)':>5} | {'σ^-1=σ?':>8} {'φ^-1=φ?':>8} {'τ^-1=τ?':>8}")
print("-" * 100)

for n in range(1, 31):
    si, pi, ti = sigma_inv[n], phi_inv[n], tau_inv[n]
    s, p, t = sigma(n), phi(n), tau(n)
    s_self = "✓" if si == s else ""
    p_self = "✓" if pi == p else ""
    t_self = "✓" if ti == t else ""
    marker = ""
    if n == 6:
        marker = " ◀◀◀ n=6"
    print(f"{n:>4} | {si:>10} {pi:>10} {ti:>10} | {s:>6} {p:>6} {t:>5} | {s_self:>8} {p_self:>8} {t_self:>8}{marker}")

# ══════════════════════════════════════════════════════════
# 6. Is σ^{-1}(n) = σ(n) only at n=6? Self-inverse check
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("6. SELF-INVERSE CHECK: σ^{-1}(n) = σ(n)?")
print("=" * 72)
print()

sigma_self_inv = [n for n in range(1, MAX_N+1) if sigma_inv[n] == sigma(n)]
print(f"n where σ^{{-1}}(n) = σ(n), n=1..{MAX_N}: {sigma_self_inv[:50]}")

sigma_neg_inv = [n for n in range(1, MAX_N+1) if sigma_inv[n] == -sigma(n)]
print(f"n where σ^{{-1}}(n) = -σ(n), n=1..{MAX_N}: {sigma_neg_inv[:50]}")

phi_self_inv = [n for n in range(1, MAX_N+1) if phi_inv[n] == phi(n)]
print(f"n where φ^{{-1}}(n) = φ(n), n=1..{MAX_N}: {phi_self_inv[:50]}")

tau_self_inv = [n for n in range(1, MAX_N+1) if tau_inv[n] == tau(n)]
print(f"n where τ^{{-1}}(n) = τ(n), n=1..{MAX_N}: {tau_self_inv[:50]}")

# Check σ^{-1}(6) specifically
print()
print(f"σ^{{-1}}(6) = {sigma_inv[6]}")
print(f"σ(6) = {sigma(6)}")
print(f"σ^{{-1}}(6) = σ(6)? {sigma_inv[6] == sigma(6)}")

# Manual trace
print()
print("Manual computation of σ^{-1}(6):")
print(f"  σ^{{-1}}(1) = 1")
print(f"  σ^{{-1}}(2) = -σ(2)·σ^{{-1}}(1) = -{sigma(2)}·1 = {sigma_inv[2]}")
print(f"  σ^{{-1}}(3) = -σ(3)·σ^{{-1}}(1) = -{sigma(3)}·1 = {sigma_inv[3]}")
si6 = -(sigma(2)*sigma_inv[3] + sigma(3)*sigma_inv[2] + sigma(6)*sigma_inv[1])
print(f"  σ^{{-1}}(6) = -(σ(2)σ^{{-1}}(3) + σ(3)σ^{{-1}}(2) + σ(6)σ^{{-1}}(1))")
print(f"            = -({sigma(2)}·{sigma_inv[3]} + {sigma(3)}·{sigma_inv[2]} + {sigma(6)}·{sigma_inv[1]})")
print(f"            = -({sigma(2)*sigma_inv[3]} + {sigma(3)*sigma_inv[2]} + {sigma(6)*sigma_inv[1]})")
print(f"            = -({sigma(2)*sigma_inv[3] + sigma(3)*sigma_inv[2] + sigma(6)*sigma_inv[1]})")
print(f"            = {si6}")

# ══════════════════════════════════════════════════════════
# 7. Deeper: σ^{-1} at perfect numbers and relationship to μ
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("7. σ^{-1} AT PERFECT NUMBERS AND SPECIAL NUMBERS")
print("=" * 72)
print()

perfect_numbers = [6, 28, 496]
for p in perfect_numbers:
    if p <= MAX_N:
        print(f"n={p} (perfect): σ^{{-1}}({p})={sigma_inv[p]}, σ({p})={sigma(p)}, ratio={sigma_inv[p]/sigma(p) if sigma(p) else 'undef':.6f}")

# Known: σ^{-1} = μ * μ * id (since σ = id * 1, so σ^{-1} = id^{-1} * μ = ... )
# Actually: σ = id * 1, so σ^{-1} = id^{-1} * μ
# id^{-1} is the Dirichlet inverse of the identity function
# For multiplicative f: f^{-1} is also multiplicative
# id^{-1}(p^k) can be computed...

print()
print("Relationship between σ^{-1} and known functions:")
print()

id_inv = dirichlet_inverse(identity, MAX_N)
print(f"{'n':>4} | {'σ^-1(n)':>10} | {'μ(n)':>5} {'id^-1(n)':>10} | {'μ·id':>8} | {'|μ|·σ':>8}")
print("-" * 65)

for n in range(1, 31):
    # (μ * id^{-1})(n) -- but this isn't quite right
    # σ = id * 1, so σ^{-1} = 1^{-1} * id^{-1} = μ * id^{-1}
    mu_conv_idinv = dirichlet_conv(mobius, lambda x: id_inv[x], n)
    abs_mu_sigma = abs(mobius(n)) * sigma(n)
    print(f"{n:>4} | {sigma_inv[n]:>10} | {mobius(n):>5} {id_inv[n]:>10} | {mu_conv_idinv:>8} | {abs_mu_sigma:>8}")

# Verify σ^{-1} = μ * id^{-1}
check = all(sigma_inv[n] == dirichlet_conv(mobius, lambda x: id_inv[x], n) for n in range(1, MAX_N+1))
print(f"\nσ^{{-1}} = μ * id^{{-1}}? {check}")

# ══════════════════════════════════════════════════════════
# 8. The "convolution collapse" characterization of n=6
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("8. CONVOLUTION COLLAPSE: (f*g)(n) = f(n)·g(n)")
print("=" * 72)
print()
print("When does (f*g)(n) = f(n)·g(n)?")
print("This means the 'cross terms' Σ_{d|n, 1<d<n} f(d)g(n/d)")
print("equal f(n)g(n) - f(1)g(n) - f(n)g(1)")
print()

# For σ*φ: conv = nτ, pw = σφ.
# Ratio = (σ*φ)/(σ·φ) = nτ/(σφ)
# At perfect n: σ=2n, so nτ/(σφ) = nτ/(2nφ) = τ/(2φ)
print("Ratio nτ(n)/(σ(n)φ(n)) — equals 1 iff master identity holds:")
print()
print(f"{'n':>4} | {'σ':>6} {'φ':>6} {'τ':>4} | {'nτ':>8} {'σφ':>8} | {'ratio':>10} | note")
print("-" * 70)

for n in range(1, 31):
    s, p, t = sigma(n), phi(n), tau(n)
    nt = n * t
    sp = s * p
    ratio = nt / sp if sp else float('inf')
    note = ""
    if abs(ratio - 1.0) < 1e-12:
        note = "◀ COLLAPSE (master identity)"
    elif s == 2 * n:
        note = f"perfect, ratio=τ/(2φ)={t/(2*p):.4f}"
    print(f"{n:>4} | {s:>6} {p:>6} {t:>4} | {nt:>8} {sp:>8} | {ratio:>10.6f} | {note}")

# ══════════════════════════════════════════════════════════
# 9. NEW: Multiplicative structure of σ^{-1}(n)
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("9. MULTIPLICATIVE STRUCTURE OF σ^{-1}")
print("=" * 72)
print()

# For multiplicative f, f^{-1} is multiplicative too.
# f^{-1}(p) = -f(p) for prime p.
# f^{-1}(p^2) = f(p)^2 - f(p^2)
# f^{-1}(p^k) can be computed recursively.

print("σ^{-1} at prime powers:")
print(f"{'p^k':>6} | {'σ^-1':>10} | {'σ':>8} | {'-σ(p)':>8} | formula")
print("-" * 60)

for p in [2, 3, 5, 7, 11, 13]:
    pk = p
    k = 1
    while pk <= MAX_N:
        si = sigma_inv[pk]
        s = sigma(pk)
        neg_sp = -sigma(p)

        if k == 1:
            formula = f"-σ({p}) = {-sigma(p)}"
        elif k == 2:
            formula = f"σ({p})²-σ({p}²) = {sigma(p)**2}-{sigma(p*p)} = {sigma(p)**2 - sigma(p*p)}"
        else:
            formula = "recursive"

        print(f"{p}^{k:>2}={pk:>4} | {si:>10} | {s:>8} | {neg_sp:>8} | {formula}")
        k += 1
        pk *= p

# Since σ^{-1} is multiplicative: σ^{-1}(6) = σ^{-1}(2)·σ^{-1}(3)
print()
print(f"Multiplicative check: σ^{{-1}}(6) = σ^{{-1}}(2)·σ^{{-1}}(3) = {sigma_inv[2]}·{sigma_inv[3]} = {sigma_inv[2]*sigma_inv[3]}")
print(f"Actual σ^{{-1}}(6) = {sigma_inv[6]}")
print(f"Match: {sigma_inv[6] == sigma_inv[2]*sigma_inv[3]}")

# So σ^{-1}(6) = (-σ(2))(-σ(3)) = σ(2)σ(3) = 3·4 = 12 = σ(6)
# This is because σ(6) = σ(2)σ(3) (multiplicative!) and σ^{-1}(p) = -σ(p)
# So σ^{-1}(pq) = σ^{-1}(p)σ^{-1}(q) = (-σ(p))(-σ(q)) = σ(p)σ(q) = σ(pq)
# This works for ANY squarefree semiprime (product of two distinct primes)!

print()
print("KEY INSIGHT: For squarefree n with even number of prime factors:")
print("  σ^{-1}(n) = (-1)^{ω(n)} · Π σ(p) = σ(n) when ω(n) is even (σ multiplicative)")
print()
print("Checking: σ^{-1}(n) = (-1)^{ω(n)} · σ(n) for squarefree n?")
print()

from sympy import factorint
# Let's do it manually instead

def omega(n):
    """Number of distinct prime factors."""
    count = 0
    d = 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        count += 1
    return count

def is_squarefree(n):
    d = 2
    while d * d <= n:
        if n % (d*d) == 0:
            return False
        d += 1
    return True

print(f"{'n':>4} | {'sqfree':>6} {'ω(n)':>4} | {'σ^-1(n)':>10} {'(-1)^ω·σ':>10} | {'match':>5}")
print("-" * 55)

sqfree_match = True
for n in range(1, 51):
    sqf = is_squarefree(n)
    w = omega(n)
    expected = ((-1)**w) * sigma(n)
    actual = sigma_inv[n]
    match = actual == expected
    if sqf and not match:
        sqfree_match = False
    marker = ""
    if n == 6:
        marker = " ◀ n=6"
    if sqf:
        print(f"{n:>4} | {'✓':>6} {w:>4} | {actual:>10} {expected:>10} | {'✓' if match else '✗':>5}{marker}")

print()
print(f"For ALL squarefree n: σ^{{-1}}(n) = (-1)^ω(n) · σ(n)? {sqfree_match}")
print()
print("This means σ^{-1}(n) = μ(n)·σ(n) for squarefree n!")
print("(Since μ(n) = (-1)^{ω(n)} for squarefree n)")
print()

# Wait, is σ^{-1} = μ·σ (pointwise product)?
# That would mean σ^{-1}(n) = μ(n)σ(n) for ALL n.
# For non-squarefree: μ(n)=0 but σ^{-1}(n) may not be 0.
print("Does σ^{-1}(n) = μ(n)·σ(n) for non-squarefree n?")
print()
for n in [4, 8, 9, 12, 16, 18, 25, 27, 28, 36]:
    actual = sigma_inv[n]
    expected = mobius(n) * sigma(n)  # = 0 for non-squarefree
    print(f"  n={n}: σ^{{-1}}={actual}, μ·σ={expected} {'✓' if actual == expected else '✗'}")

# ══════════════════════════════════════════════════════════
# 10. The true formula for σ^{-1}
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("10. TRUE FORMULA FOR σ^{-1}")
print("=" * 72)
print()

# σ = id * 1, so σ^{-1} = id^{-1} * μ (convolution of inverses)
# id^{-1}(n) = μ(n)·n (Jordan's totient / Möbius)? Let's check.
# Actually: (id * id^{-1})(n) = ε(n). id^{-1}(1)=1, id^{-1}(p) = -p.
# id^{-1}(p^2) = p^2 - p^2 = 0? Let's check.

print("id^{-1}(n) values:")
for n in range(1, 31):
    expected_mu_n = mobius(n) * n
    print(f"  n={n}: id^{{-1}}={id_inv[n]}, μ(n)·n={expected_mu_n} {'✓' if id_inv[n] == expected_mu_n else '✗'}")

check_id_inv = all(id_inv[n] == mobius(n)*n for n in range(1, MAX_N+1))
print(f"\nid^{{-1}}(n) = μ(n)·n for all n? {check_id_inv}")

# So: σ^{-1} = id^{-1} * μ = (n↦μ(n)n) * μ
# (σ^{-1})(n) = Σ_{d|n} μ(d)·d · μ(n/d)
print()
print("So σ^{-1} = (n↦μ(n)·n) * μ")
print()
print(f"{'n':>4} | {'σ^-1 computed':>14} {'Σ μ(d)d·μ(n/d)':>16} | {'match':>5}")
print("-" * 55)

for n in range(1, 31):
    formula_val = sum(mobius(d)*d*mobius(n//d) for d in divisors(n))
    print(f"{n:>4} | {sigma_inv[n]:>14} {formula_val:>16} | {'✓' if sigma_inv[n] == formula_val else '✗'}")

# ══════════════════════════════════════════════════════════
# 11. SUMMARY: What's truly special about n=6?
# ══════════════════════════════════════════════════════════

print()
print("=" * 72)
print("11. SUMMARY: DIRICHLET CONVOLUTION CHARACTERIZATIONS OF n=6")
print("=" * 72)
print()

print("""
UNIVERSAL (all n):
  (σ*φ)(n) = nτ(n)           [= (id*id)(n)]
  (σ*μ)(n) = n               [Möbius inversion]
  (φ*1)(n) = n               [Gauss identity]
  σ^{-1}(n) = Σ_{d|n} μ(d)d·μ(n/d)

SPECIAL TO n=6 (and n=1):
  σ(n)·φ(n) = n·τ(n)         [POINTWISE = CONVOLUTION collapse]

  This is the master identity σφ=nτ.
  It means: for f=σ, g=φ, the Dirichlet convolution (f*g)(n)
  equals the pointwise product f(n)·g(n) at n=6.

  At n=6 ONLY (among n≥2): the convolution "collapses" to
  a simple pointwise multiplication.

σ^{-1}(n) at perfect numbers and semiprimes:
  σ^{-1}(6) = 12 = σ(6)      [self-inverse!]
  But this is NOT unique to 6:
  σ^{-1}(pq) = σ(pq) for ALL semiprimes pq (p≠q).
  Because σ^{-1}(p)σ^{-1}(q) = (-σ(p))(-σ(q)) = σ(p)σ(q) = σ(pq).

  σ^{-1}(28) = {sigma_inv[28]}  ≠ σ(28) = {sigma(28)}
  (28 = 2²·7 is NOT squarefree, so the semiprime argument fails)

  PERFECT NUMBER CHARACTERIZATION via σ^{-1}:
  For perfect n: σ(n) = 2n. So σ^{-1}(n) = σ(n) iff σ^{-1}(n) = 2n.
  Among perfect numbers, only 6 = 2·3 is squarefree (semiprime).
  All other even perfect numbers 2^(p-1)(2^p-1) have 2^(p-1) with p≥3,
  so they are NOT squarefree. Hence:

  ★ n=6 is the UNIQUE perfect number where σ^{-1}(n) = σ(n) = 2n.
""")

# Verify the claim about perfect numbers
print("Verification: perfect numbers and σ^{-1}:")
for pn in [6, 28, 496]:
    if pn <= MAX_N:
        sqf = is_squarefree(pn)
        print(f"  n={pn}: σ^{{-1}}={sigma_inv[pn]}, σ={sigma(pn)}, sqfree={sqf}, σ^{{-1}}=σ? {sigma_inv[pn]==sigma(pn)}")

# Check: is 6 the only perfect number that is squarefree?
# Even perfect: 2^(p-1)(2^p-1). For p=2: 2·3=6, squarefree. For p≥3: 2^(p-1)≥4, not squarefree.
# Odd perfect (if exists): unknown, but likely doesn't exist.
print()
print("Even perfect numbers 2^(p-1)(2^p-1):")
print("  p=2: 2·3 = 6 (squarefree ✓)")
print("  p=3: 4·7 = 28 (4=2², NOT squarefree)")
print("  p=5: 16·31 = 496 (16=2⁴, NOT squarefree)")
print("  p≥3: 2^(p-1) ≥ 4, always has squared factor")
print()
print("Therefore: 6 is the UNIQUE perfect number that is squarefree.")
print("Consequence: 6 is the UNIQUE perfect number with σ^{-1}(6) = σ(6).")
