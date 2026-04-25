#!/usr/bin/env bash
# lint_nested_if_continue.sh — B1 prevention lint
# Pattern: while/for { ... if-block {... continue ...} ... i = i + 1 }
#   inner continue skips outer-loop's i++ → infinite loop.
# Usage: lint_nested_if_continue.sh [path]   path = repo-root | dir | .hexa file
# Exits: 0 clean, 1 bug found, 2 scan error.
# Limit: regex+indent — false-negative on exotic layouts (mixed tabs, single-line nests).
set -u
ARG="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
PY="$(command -v python3 || command -v python)"
[ -z "$PY" ] && { echo "lint:scan_error:no_python" >&2; exit 2; }
exec "$PY" - "$ARG" <<'PYEOF'
import os, re, sys
arg = sys.argv[1]
RULE="B1-nested-if-continue"; DESC="loop tail i=i+1 skipped by nested-if continue"
targets=[]
if os.path.isfile(arg) and arg.endswith(".hexa"): targets=[arg]
elif os.path.isdir(arg):
    bases=[arg] if os.path.basename(arg) in ("tool","shared","lint_test_fixtures") else \
          [os.path.join(arg,s) for s in ("tool","shared") if os.path.isdir(os.path.join(arg,s))]
    skip_fixtures = "lint_test_fixtures" not in arg
    for b in bases:
        for dp,_,fs in os.walk(b):
            if skip_fixtures and "lint_test_fixtures" in dp: continue
            for f in fs:
                if f.endswith(".hexa"): targets.append(os.path.join(dp,f))
loop_p=re.compile(r'^(\s*)(while|for)\b.*\{\s*$'); if_p=re.compile(r'^(\s*)if\b.*\{\s*$')
inc_p=re.compile(r'\bi\s*=\s*i\s*\+\s*1\b'); upd_p=re.compile(r'\bi\s*=\s*[^=]')
cont_p=re.compile(r'\bcontinue\b')
def fc(L,s,ind):
    for j in range(s+1,len(L)):
        ls=L[j].rstrip()
        if ls.strip()=="}" and (len(ls)-len(ls.lstrip()))==ind: return j
    return -1
hits=0; err=0
for path in sorted(set(targets)):
    try: lines=open(path,encoding="utf-8").readlines()
    except Exception as e: print(f"{path}:0:0:scan_error:{e}",file=sys.stderr); err+=1; continue
    for i,line in enumerate(lines):
        ml=loop_p.match(line)
        if not ml: continue
        li=len(ml.group(1)); lc=fc(lines,i,li)
        if lc<0: continue
        body=lines[i+1:lc]
        ti=-1
        for k in range(len(body)-1,-1,-1):
            if body[k].strip(): ti=k; break
        if ti<0 or not inc_p.search(body[ti]): continue
        flagged=False; k=0
        while k<ti:
            mi=if_p.match(body[k])
            if mi and len(mi.group(1))>li:
                ii=len(mi.group(1)); ic=-1
                for kk in range(k+1,len(body)):
                    bls=body[kk].rstrip()
                    if bls.strip()=="}" and (len(bls)-len(bls.lstrip()))==ii: ic=kk; break
                if ic<0: k+=1; continue
                inner=body[k+1:ic]; kk=0
                while kk<len(inner):
                    bl=inner[kk]; ml2=loop_p.match(bl)
                    if ml2 and len(ml2.group(1))>ii:
                        ni=len(ml2.group(1)); kkc=kk+1
                        while kkc<len(inner):
                            ls2=inner[kkc].rstrip()
                            if ls2.strip()=="}" and (len(ls2)-len(ls2.lstrip()))==ni: break
                            kkc+=1
                        kk=kkc+1; continue
                    if cont_p.search(bl) and not bl.lstrip().startswith("//"):
                        if not upd_p.search("".join(inner[:kk+1])): flagged=True
                        break
                    kk+=1
                if flagged: break
                k=ic+1
            else: k+=1
        if flagged:
            col=ml.group(0).index(ml.group(2))+1
            print(f"{path}:{i+1}:{col}:{RULE}:{DESC}"); hits+=1
sys.exit(2 if err else (1 if hits else 0))
PYEOF
