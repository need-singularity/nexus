---
section: §2
title: "Primitives — the n=6 foundation"
parent: "n=6 as foundational invariant: a multi-domain falsifier-grounded framework"
draft: v1
generated: 2026-04-26
status: section draft (target ~400-500 words)
---

# §2 Primitives

## 2.1 Foundation: $n = 6$

The framework's seed primitive is the integer $n = 6$. The choice is
fixed by three independent properties: (a) $6$ is the smallest perfect
number, $\sigma(6) = 12 = 2 \cdot 6$; (b) it satisfies the Diophantine
identity $\sigma(n)\!\cdot\!\varphi(n) = n\!\cdot\!\tau(n)$ uniquely
among integers $n \geq 2$ (cf.\ §6, F100); and (c) the symmetric group
$S_6$ is the sole $S_n$ admitting a non-trivial outer automorphism,
$\mathrm{Out}(S_6) \cong \mathbb{Z}/2$ (cf.\ §6, F75). The seed is
anchored as F24 at \texttt{n6/atlas.n6:25}, carrying the grade
\texttt{[11*]} reserved for foundation literals; F24's command
\texttt{grep -qE '\^@P n = 6 :: foundation \textbackslash[11\textbackslash*\textbackslash]'}
falsifies the entire derivation cascade if the seed line drifts in
value, domain, or grade.

## 2.2 Number-theoretic functions at $n = 6$

Six classical multiplicative functions plus the Mersenne literal
$M_3$ form the primitive basis $\mathcal{P}_6$ used throughout the
paper.

| Function | Definition | Value at $n=6$ | Atlas anchor |
|---|---|---:|---|
| $\sigma(n)$ | divisor sum | $\sigma(6) = 1+2+3+6 = 12$ | F25 |
| $\varphi(n)$ | Euler totient | $\varphi(6) = 2$ | F1 (CONSTANTS axis) |
| $\tau(n)$ | divisor count | $\tau(6) = 4$ | F26 |
| $\mathrm{sopfr}(n)$ | sum of prime factors w/ multiplicity | $\mathrm{sopfr}(6) = 2+3 = 5$ | F1 |
| $J_2(n)$ | Jordan totient (order 2) | $J_2(6) = 24$ | F1 |
| $\mu(n)$ | Möbius function | $\mu(6) = \mu(2)\mu(3) = 1$ | F19 |
| $M_3 = 2^3-1$ | Mersenne (exponent 3) | $M_3 = 7$ | F20 (relabeled) |

Each row is independently atlas-anchored: F25 and F26 verify the
\texttt{[11*]} foundation grade of $\sigma$ and $\tau$ literals; F19
verifies the $\mu$ entry orthogonally to the F1 \texttt{CONSTANTS}
arithmetic axis; F1 jointly probes $\varphi$, $\mathrm{sopfr}$, and
$J_2$ via \texttt{hexa\_sim\_verify\_grid.hexa --axis CONSTANTS}.

## 2.3 The $M_3$ labeling correction — methodology vignette

The atlas line \texttt{n6/atlas.n6:53} originally read
\texttt{M3 = mertens(6) = 7}, but the canonical Mertens function gives
$M(6) = \sum_{k=1}^{6} \mu(k) = -1$, not $7$. A high-confidence audit
(\texttt{M3\_true\_definition\_audit.md}) determined that the value $7$
is load-bearing across $\geq 20$ downstream identities (e.g.\
$B_6 = 1/(n\!\cdot\!M_3)$, ethylene molecular weight $= \tau\!\cdot\!M_3$)
and that the intended referent was the third Mersenne literal,
$M_3 = \mathrm{mersenne}(3) = 2^3 - 1 = 7$. The atlas was relabeled at
commit \texttt{d84a0601} and F20's \texttt{cmd} regex updated to anchor
the new literal. This is a methodology success: the falsifier framework
caught a labeling error that natural-language documentation had carried
unchallenged for prior cycles. See §9.2 for the full provenance entry.

## 2.4 Perfect-number identity

$n = 6$ is the smallest perfect number: $\sigma(6) = 12 = 2 \cdot 6$,
equivalently $\sigma(n) - n = n$ (the proper-divisor sum equals $n$).
The Euclid--Euler theorem characterises every even perfect number as
$2^{p-1}(2^p-1)$ where $2^p-1$ is a Mersenne prime; at $p = 2$ this
yields $2 \cdot 3 = 6$, exhibiting $n = 6$ as the $p=2$ instance of the
Mersenne--perfect pairing. F111 anchors the closed form
$R(2^{p-1}(2^p-1)) = 2^{p-1}(2^{p-1}-1)/p$ at grade \texttt{[11*]},
verified numerically at $p \in \{2,3,5,7\}$.

## 2.5 Cross-domain primitive bridges (preview)

Each primitive recurs as a cardinal in independently-measured domains:
$\sigma = 12$ matches the Standard Model gauge generator count
$\dim\,\mathrm{SU}(3)\!\times\!\mathrm{SU}(2)\!\times\!\mathrm{U}(1) = 8\!+\!3\!+\!1 = 12$
(F64), the $12$ cranial nerves, the zodiacal $12$, and twelve months;
$\varphi = 2$ matches the Watson--Crick DNA strand count (F99) and the
two Majorana phases distinguishing PMNS from CKM (F94); $\tau = 4$
matches the four DNA bases, the four-stage divisor partition (F26), and
the four independent CKM parameters (F69); $n = 6$ itself matches the
six quark flavors (F98), the six lepton numbers, and the six-fold MCM
helicase ring (F57). §4 develops these bridges in detail.

## 2.6 Notation conventions

We use two atlas notations for primitive references:

- **Notation A** (shorthand): \texttt{sigma = 12} — implicit anchor at
  $n = 6$; equivalent to $\sigma(6) = 12$.
- **Notation B** (function call): \texttt{sigma(N) = K} — explicit
  argument; reads as "$\sigma$ at $N$ gives $K$".

Disambiguation is documented in
\texttt{design/atlas\_function\_call\_convention.md}. A prior batch of
$19$ \texttt{xpoll-*} entries that had used Notation B as Notation A
shorthand (e.g.\ \texttt{sigma(12) = 12}) was cleaned at commit
\texttt{368209c0}. Subsequent sections rely on Notation A unless an
explicit non-default argument is given.
