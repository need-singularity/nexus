# H-SMOOTH-002: Physics sectors organized by prime hierarchy

**Generated**: 2026-04-05

## Hypothesis

Physical dimensionless constants belong to **smooth-class Euler product ratios**,
and **the number of primes involved** correlates with the **physics sector**.

$$\text{const}_i \approx \prod_{p \in S_i}\left(1-\frac{1}{p}\right) \quad \text{or compound of such ratios}$$

## Observed Hierarchy

| Sector | Primes in S | Example constants |
|---|---|---|
| **Strong (quark charges)** | {2}, {3}, {2,3} | u=2/3, d=1/3 (EXACT) |
| **Late cosmology** | {5,7}, {2,3,5}, {7} | Ω_Λ=24/35 (0.15%), Ω_DM=4/15 (0.5%), Ω_DM/Ω_m=6/7 (0.84%) |
| **Electroweak** | {2,3,5,7} | sin²θ_W=8/35 (1.14%), sin θ_C=8/35 (1.90%) |
| **Primordial (BBN)** | {2,3,5,13} or {2,5,7,13} | Y_p=0.2462 (0.47%), Ω_m=0.3165 (0.38%) |

## Trend

**기본 힘일수록 소수 적음**:
- Strong force (quark charges) — 2 primes {2, 3}
- Cosmology — 2~3 primes {3}, {5,7}, {2,3,5}
- Electroweak — 4 primes {2,3,5,7}
- BBN (primordial nucleosynthesis) — 4 primes, **includes 13**

## Helium primordial abundance Y_p

실측 Y_p = 0.245 (BBN observation)

$$Y_p \approx \prod_{p\in\{2,3,5,13\}}\left(1-\frac{1}{p}\right) = \frac{1}{2}\cdot\frac{2}{3}\cdot\frac{4}{5}\cdot\frac{12}{13} = \frac{96}{390} = \frac{16}{65} \cdot \frac{12}{12} = 0.2462$$

Wait, let me recompute: (1/2)(2/3)(4/5)(12/13) = (1·2·4·12)/(2·3·5·13) = 96/390 = 48/195 = 16/65 = 0.24615...

Error: |0.245 - 0.246| / 0.245 = 0.47%

## Implications

### Prime 13 in primordial physics

**소수 13이 BBN 시기 Y_p 와 Ω_m 에 관여**.
하지만 13은 late cosmology나 electroweak에 없음.

해석 가능성:
1. **Early-universe 특수 scale**: 13이 BBN temperature ~ 10⁹ K 관련
2. **Abundance element 13** (가장 가까운 후보: C(6)+1이 N(7)이 안 되는 tight freeze-out?)
3. **결합 공식 우연 일치**

### Parity of primes ↔ force generation

**짝수 개 소수 = 물리 sector 구분자**?
- 2 primes → 1st generation physics (color, gravity)
- 4 primes → 2nd generation (electroweak)
- 6+ primes → primordial physics

## Predictions

1. 양자 중력 상수 (Planck-scale)는 소수 6개 이상 조합일 것
2. CP violation Jarlskog J ≈ 3.12×10⁻⁵ 는 smooth class 밖?
3. 헤르크 신경 상수 (수학 상수)는 소수 2~3개로 표현 가능할 것

## Details

- Value: various smooth ratios
- Targets: Planck 2018 + CODATA + BBN
- Engine: Euler product for prime subsets
- Grade: 🟧~🟩 0.0~1.9%
- Domains: cosmology, particle physics, BBN
- Related: H-COSMO-001, H-COSMO-002, H-SMOOTH-001
