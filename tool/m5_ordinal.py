"""m5 ordinal CNF parser+comparator (i1+i2). Spec: /spec/m5_ordinal_bnf.txt."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
import unicodedata
class ParseError(Exception): pass
class EmptyInput(ParseError): pass
class NonCanonicalCNFError(Exception): pass
class OrdinalBeyondPredicativeError(Exception): pass
class UnknownSentinel(Exception): pass
class NumericOverflow(Exception): pass
class HomoglyphRejected(Exception): pass
MAX_NAT = 10**18
SENTINELS = ("ε_0", "Γ_0", "ψ(Ω_ω)")
SRANK = {"ε_0": 1, "Γ_0": 2, "ψ(Ω_ω)": 3}
@dataclass
class Ordinal:
    kind: str
    nat: int = 0
    sentinel: str = ""
    terms: List[Tuple["Ordinal", int]] = field(default_factory=list)
class _P:
    def __init__(self, s): self.s, self.i, self.depth = s, 0, 0
    def pk(self, k=0): return self.s[self.i+k] if self.i+k < len(self.s) else ""
    def eat(self, c):
        if self.pk() != c: raise ParseError(f"want {c!r} at {self.i}")
        self.i += 1
def _norm(s):
    s = unicodedata.normalize("NFC", s)
    for b in (" ", " ", "​"):
        if b in s: raise HomoglyphRejected(f"u+{ord(b):04X}")
    s = "".join(c for c in s if not c.isspace())
    if any(c.isalpha() and c not in "ω0εΓψΩ_" for c in s): raise HomoglyphRejected("letter")
    return s
def _nat(p):
    if not p.pk().isdigit() or p.pk() == "0": raise ParseError(f"nat at {p.i}")
    j = p.i
    while p.pk().isdigit(): p.i += 1
    n = int(p.s[j:p.i])
    if n > MAX_NAT: raise NumericOverflow(f"nat>{MAX_NAT}")
    return n
def _sent(p):
    for sn in SENTINELS:
        if p.s.startswith(sn, p.i): p.i += len(sn); return Ordinal("sentinel", sentinel=sn)
    if p.pk() == "ψ" or p.s.startswith("ε_", p.i) or p.s.startswith("Γ_", p.i): raise UnknownSentinel(f"unknown at {p.i}")
    return None
def _carat_exp(p):
    p.i += 1
    if p.pk() == "": raise ParseError("exp after ^")
    return _exp(p)
def _exp(p):
    if p.pk() == "(":
        p.eat("("); p.depth += 1
        if p.depth > 64: raise ParseError("depth>64")
        o = _ord(p); p.eat(")"); p.depth -= 1; return o
    if p.pk() == "0": p.i += 1; return Ordinal("zero")
    if p.pk() == "ω":
        p.eat("ω"); ie = Ordinal("nat", nat=1)
        if p.pk() == "^": ie = _carat_exp(p)
        return Ordinal("cnf", terms=[(ie, 1)])
    return Ordinal("nat", nat=_nat(p))
def _term(p):
    p.eat("ω"); e = Ordinal("nat", nat=1); c = 1
    if p.pk() == "^": e = _carat_exp(p)
    if p.pk() == "·":
        p.i += 1
        if p.pk() == "0": raise NonCanonicalCNFError("·0 (SC2)")
        if not p.pk().isdigit(): raise ParseError(f"nat after · at {p.i}")
        c = _nat(p)
    return e, c
def _ord(p):
    if p.pk() == "0":
        p.i += 1
        if p.pk() in ("", ")"): return Ordinal("zero")
        if p.pk() == "+": raise NonCanonicalCNFError("0+α (SC3)")
        raise ParseError(f"after 0 at {p.i}")
    sn = _sent(p)
    if sn is not None:
        if p.pk() in ("+", "·"): raise OrdinalBeyondPredicativeError("sentinel arith")
        return sn
    if p.pk().isdigit():
        n = _nat(p)
        if p.pk() == "+": raise ParseError(f"nat+ at {p.i}")
        return Ordinal("nat", nat=n)
    if p.pk() != "ω": raise ParseError(f"ord at {p.i}: {p.pk()!r}")
    ts = [_term(p)]
    while p.pk() == "+":
        p.i += 1
        if p.pk() == "0": raise NonCanonicalCNFError("α+0 (SC3)")
        if p.pk() == "ω": ts.append(_term(p))
        elif p.pk().isdigit(): ts.append((Ordinal("zero"), _nat(p)))
        else: raise ParseError(f"term after + at {p.i}")
    for k in range(len(ts)-1):
        if cmp_ord(ts[k][0], ts[k+1][0]) != "GT": raise NonCanonicalCNFError("SC1")
    return Ordinal("cnf", terms=ts)
def parse(s: str) -> Ordinal:
    if s is None or unicodedata.normalize("NFC", s).strip() == "": raise EmptyInput("empty")
    p = _P(_norm(s)); o = _ord(p)
    if p.i != len(p.s): raise ParseError(f"trailing at {p.i}")
    return o
def _tc(o):
    if o.kind == "nat": return [(Ordinal("zero"), o.nat)]
    if o.kind == "cnf": return o.terms
    if o.kind == "zero": return []
    raise OrdinalBeyondPredicativeError("sentinel cnf")
def _r(x, y): return "EQ" if x == y else ("LT" if x < y else "GT")
def cmp_ord(a: Ordinal, b: Ordinal) -> str:
    az = a.kind == "zero" or (a.kind == "nat" and a.nat == 0)
    bz = b.kind == "zero" or (b.kind == "nat" and b.nat == 0)
    if az or bz: return "EQ" if az and bz else ("LT" if az else "GT")
    if a.kind == "sentinel" and b.kind == "sentinel": return _r(SRANK[a.sentinel], SRANK[b.sentinel])
    if a.kind == "sentinel": return "GT"
    if b.kind == "sentinel": return "LT"
    A, B = _tc(a), _tc(b)
    for (ea, ca), (eb, cb) in zip(A, B):
        c = cmp_ord(ea, eb)
        if c != "EQ": return c
        if ca != cb: return _r(ca, cb)
    return _r(len(A), len(B))
def cmp(a: Ordinal, b: Ordinal) -> str: return cmp_ord(a, b)
