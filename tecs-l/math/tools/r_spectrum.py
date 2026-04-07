#!/usr/bin/env python3
"""R(n)=σφ/(nτ) spectrum analyzer

Usage:
  python3 r_spectrum.py --range 100000      # R(n) for n=2..N
  python3 r_spectrum.py --value 6           # R at specific n
  python3 r_spectrum.py --find-eq 1         # Find n where R=1
  python3 r_spectrum.py --gap 5             # All R<5 values
  python3 r_spectrum.py --phi-eq-tau 100000 # Find φ=τ up to N
  python3 r_spectrum.py --dual 6            # R and S at n
"""
import argparse, math, sys
from fractions import Fraction

def sigma(n):
    s=0
    for i in range(1,int(n**0.5)+1):
        if n%i==0: s+=i+(n//i if i*i!=n else 0)
    return s

def tau(n):
    t=0
    for i in range(1,int(n**0.5)+1):
        if n%i==0: t+=1+(1 if i*i!=n else 0)
    return t

def phi(n):
    r=n;t=n;p=2
    while p*p<=t:
        if t%p==0:
            while t%p==0: t//=p
            r-=r//p
        p+=1
    if t>1: r-=r//t
    return r

def R(n): return Fraction(sigma(n)*phi(n), n*tau(n))
def S(n): return Fraction(sigma(n)*tau(n), n*phi(n))

def main():
    p = argparse.ArgumentParser(description='R(n) spectrum analyzer')
    p.add_argument('--range', type=int, help='Compute R(n) for n=2..N')
    p.add_argument('--value', type=int, help='R,S at specific n')
    p.add_argument('--find-eq', type=str, help='Find n where R=value (fraction like 1 or 7/6)')
    p.add_argument('--gap', type=float, help='All distinct R<threshold')
    p.add_argument('--phi-eq-tau', type=int, help='Find φ=τ up to N')
    p.add_argument('--dual', type=int, help='R,S,RS at specific n')
    p.add_argument('--N', type=int, default=10000, help='Search range (default 10000)')
    args = p.parse_args()

    if args.value:
        n = args.value
        s,t,p_ = sigma(n), tau(n), phi(n)
        r,sv = R(n), S(n)
        print(f"n={n}: σ={s}, τ={t}, φ={p_}")
        print(f"  R=σφ/(nτ)={r}={float(r):.6f}")
        print(f"  S=στ/(nφ)={sv}={float(sv):.6f}")
        print(f"  RS=(σ/n)²={r*sv}={float(r*sv):.6f}")

    elif args.dual:
        n = args.dual
        r,sv = R(n), S(n)
        print(f"n={n}: R={float(r):.4f}, S={float(sv):.4f}, RS={float(r*sv):.4f}")

    elif args.gap:
        thresh = args.gap
        vals = {}
        for n in range(2, args.N+1):
            r = R(n)
            if float(r) < thresh:
                if r not in vals: vals[r] = n
        for i,(r,n) in enumerate(sorted(vals.items())):
            print(f"{i+1:3d}. R={float(r):10.6f} = {str(r):>12} n={n}")
        print(f"Total: {len(vals)}")

    elif args.phi_eq_tau:
        sols = [n for n in range(2, args.phi_eq_tau+1) if phi(n)==tau(n)]
        print(f"φ=τ, n≤{args.phi_eq_tau}: {sols}")

    elif args.find_eq:
        target = Fraction(args.find_eq)
        sols = [n for n in range(2, args.N+1) if R(n)==target]
        print(f"R={args.find_eq}: {sols}")

    elif args.range:
        for n in range(2, min(args.range+1, 51)):
            r = R(n)
            print(f"n={n:3d}: R={float(r):8.4f}")

    else:
        p.print_help()

if __name__=='__main__':
    main()