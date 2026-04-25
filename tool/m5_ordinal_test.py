"""m5 ordinal test harness. Loads spec corpora and asserts parse+cmp behaviour."""
from __future__ import annotations
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m5_ordinal import (parse, cmp, ParseError, EmptyInput, NonCanonicalCNFError,
    OrdinalBeyondPredicativeError, UnknownSentinel, NumericOverflow, HomoglyphRejected)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERR = {"ParseError": ParseError, "EmptyInput": EmptyInput,
    "NonCanonicalCNFError": NonCanonicalCNFError,
    "OrdinalBeyondPredicativeError": OrdinalBeyondPredicativeError,
    "UnknownSentinel": UnknownSentinel, "NumericOverflow": NumericOverflow,
    "HomoglyphRejected": HomoglyphRejected,
    "SentinelArithmeticError": OrdinalBeyondPredicativeError}

def fail(m): print(f"__M5_ORDINAL__ FAIL {m}"); sys.exit(1)
def rows(path):
    with open(path, encoding="utf-8") as f:
        return [r for r in csv.reader(f, delimiter="\t") if r and not r[0].startswith("#")]

def main():
    nc = nf = 0
    hdr, *data = rows(os.path.join(ROOT, "spec", "m5_ordinal_corpus.tsv"))
    assert hdr == ["a","b","cmp"], f"corpus header {hdr}"
    for i, r in enumerate(data, 2):
        if len(r) < 3: continue
        a, b, want = r[0], r[1], r[2]
        try: got = cmp(parse(a), parse(b))
        except Exception as e: fail(f"corpus {i} ({a!r},{b!r}) raised {type(e).__name__}: {e}")
        if got != want: fail(f"corpus {i} cmp({a!r},{b!r})={got} want {want}")
        nc += 1
    hdr, *data = rows(os.path.join(ROOT, "spec", "m5_ordinal_fuzzer_corpus.tsv"))
    assert hdr == ["input","expected_error_class"], f"fuzzer header {hdr}"
    for i, r in enumerate(data, 2):
        if len(r) < 2: continue
        inp, ec = r[0], r[1]
        ex = ERR.get(ec)
        if ex is None: fail(f"fuzzer {i} unknown class {ec}")
        try: parse(inp); fail(f"fuzzer {i} parse({inp!r}) should raise {ec}")
        except ex: pass
        except SystemExit: raise
        except Exception as e: fail(f"fuzzer {i} parse({inp!r}) raised {type(e).__name__} not {ec}")
        nf += 1
    print(f"__M5_ORDINAL__ PASS corpus={nc} fuzzer={nf}")

if __name__ == "__main__": main()
