#!/usr/bin/env python3
"""
Search OEIS for matching sequences via the web API.
"""
import urllib.request
import urllib.parse
import json
import time

def search_oeis(terms, label=""):
    """Search OEIS for a sequence of integers."""
    query = ",".join(str(t) for t in terms)
    url = f"https://oeis.org/search?q={urllib.parse.quote(query)}&fmt=json"
    print(f"\n{'='*60}")
    print(f"Searching OEIS for {label}: {query}")
    print(f"URL: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        if data.get("results"):
            count = data.get("count", 0)
            print(f"  Found {count} result(s)!")
            for i, r in enumerate(data["results"][:3]):
                aid = r.get("number", "?")
                name = r.get("name", "?")
                seq = r.get("data", "")[:80]
                print(f"  [{i+1}] A{aid:06d}: {name}")
                print(f"       Data: {seq}...")
        else:
            print(f"  NO MATCHES FOUND — potentially new!")
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(2)  # be polite to OEIS

# Sequence A: {n : R(n) is integer}
search_oeis([1, 6, 28, 54, 96, 120, 135, 196, 224, 234, 270, 360, 496],
            "Seq A: n where sigma*phi/(n*tau) is integer")

# Sequence D: {n : tau(sigma(n)) = n}
search_oeis([1, 2, 3, 6], "Seq D: tau(sigma(n))=n")

# Sequence F: {n : phi(n)^2 = tau(n)} — only {1,6}
search_oeis([1, 6], "Seq F: phi(n)^2=tau(n)")

# Sequence J: {n : n | lcm(sigma(n), phi(n))}
search_oeis([1, 6, 24, 28, 40, 84, 96, 117, 120, 224, 234, 252, 288, 360],
            "Seq J: n divides lcm(sigma(n),phi(n))")

# Sequence K: Dirichlet convolution collapse
search_oeis([1, 6], "Seq K: Dirichlet conv collapse (sigma*phi)(n)=sigma(n)*phi(n)")

# tau(sigma(n)) as a sequence
search_oeis([1, 2, 3, 2, 4, 6, 4, 4, 2, 6, 6, 6, 4, 8, 8, 2, 6, 4, 6, 8],
            "tau(sigma(n)) values")

# R(n) numerators
search_oeis([1, 3, 4, 7, 12, 1, 24, 15, 26, 9, 60, 14, 84, 18, 16],
            "R(n) numerators")

# R(n) denominators
search_oeis([1, 4, 3, 6, 5, 1, 7, 8, 9, 5, 11, 9, 13, 7, 5],
            "R(n) denominators")

# Record R(n) at primes: p*(p-1)/2 pattern check
# For prime p: R(p) = (p+1)*(p-1)/(2p) = (p^2-1)/(2p)
# Records always at primes. The numerators: 1, 4, 12, 24, 60, 84, 144, 180, 264...
search_oeis([1, 4, 12, 24, 60, 84, 144, 180, 264, 420, 480, 684, 840, 924, 1104],
            "R(p) numerators = (p^2-1)/2 at primes")

# Seq I check
search_oeis([1, 2, 6, 42, 1806, 47058],
            "Seq I: n'=n-1 (primary pseudoperfect)")

print("\n" + "=" * 60)
print("DONE — check results above for matches/novelty")
