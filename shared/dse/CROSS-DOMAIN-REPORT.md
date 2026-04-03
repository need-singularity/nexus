# DSE Cross-Domain 전수조사 리포트

**날짜**: 2026-04-01
**대상**: 30개 도메인 × 30C2 = 435 쌍 전수 스캔
**바이너리**: universal-dse (Rust)

---

## 글로벌 통계

```
  Score: min=0.7783  max=0.9081  avg=0.8381  median=0.8358
  n6%:   min=78.5    max=100.0   avg=95.3    median=96.5
  n6=100% 쌍: 66개 (15.2%)
```

**Score 분포:**
```
  [0.90-0.95)    4 ████
  [0.85-0.90)  135 ███████████████████████████████████████████
  [0.80-0.85)  280 ████████████████████████████████████████████████████████████████████████████████████████
  [0.75-0.80)   17 █████
```

---

## TOP-50 (Pareto Score 순)

| Rank | Domain A | Domain B | n6% | Perf | Power | Cost | Score |
|------|----------|----------|-----|------|-------|------|-------|
| 1 | **cryptography** | **chip** | 97.0 | 0.945 | 0.853 | 0.660 | **0.9081** |
| 2 | **cryptography** | **grid** | 97.0 | 0.930 | 0.885 | 0.625 | **0.9065** |
| 3 | **cryptography** | **compiler-os** | 97.0 | 0.930 | 0.810 | 0.750 | **0.9040** |
| 4 | chip | grid | 100.0 | 0.945 | 0.858 | 0.465 | 0.9016 |
| 5 | chip | compiler-os | 100.0 | 0.945 | 0.783 | 0.590 | 0.8991 |
| 6 | compiler-os | grid | 100.0 | 0.930 | 0.815 | 0.555 | 0.8975 |
| 7 | cosmology-particle | cryptography | 94.0 | 0.930 | 0.765 | 0.855 | 0.8935 |
| 8 | cryptography | material | 96.0 | 0.919 | 0.815 | 0.670 | 0.8897 |
| 9 | chip | cosmology-particle | 96.5 | 0.940 | 0.763 | 0.680 | 0.8886 |
| 10 | cryptography | medical | 97.0 | 0.894 | 0.795 | 0.720 | 0.8872 |
| 11 | cosmology-particle | grid | 96.5 | 0.925 | 0.795 | 0.645 | 0.8870 |
| 12 | crypto | cryptography | 95.3 | 0.912 | 0.785 | 0.735 | 0.8853 |
| 13 | chip | material | 99.0 | 0.934 | 0.788 | 0.510 | 0.8848 |
| 14 | compiler-os | cosmology-particle | 96.5 | 0.925 | 0.720 | 0.770 | 0.8845 |
| 15 | grid | material | 99.0 | 0.919 | 0.820 | 0.475 | 0.8832 |
| 16 | cryptography | pure-mathematics | 92.5 | 0.855 | 0.860 | 0.840 | 0.8825 |
| 17 | cryptography | solar | 92.0 | 0.943 | 0.863 | 0.590 | 0.8825 |
| 18 | chip | medical | 100.0 | 0.909 | 0.768 | 0.560 | 0.8823 |
| 19 | cryptography | learning-algorithm | 95.0 | 0.905 | 0.795 | 0.715 | 0.8820 |
| 20 | compiler-os | material | 99.0 | 0.919 | 0.745 | 0.600 | 0.8807 |
| 21 | grid | medical | 100.0 | 0.894 | 0.800 | 0.525 | 0.8807 |
| 22 | chip | crypto | 98.3 | 0.927 | 0.758 | 0.575 | 0.8804 |
| 23 | crypto | grid | 98.3 | 0.912 | 0.790 | 0.540 | 0.8788 |
| 24 | cryptography | display-audio | 97.0 | 0.910 | 0.760 | 0.655 | 0.8785 |
| 25 | cryptography | thermal | 97.0 | 0.920 | 0.745 | 0.655 | 0.8785 |
| 26 | cryptography | network | 95.3 | 0.879 | 0.805 | 0.725 | 0.8784 |
| 27 | compiler-os | medical | 100.0 | 0.894 | 0.725 | 0.650 | 0.8782 |
| 28 | chip | pure-mathematics | 96.5 | 0.860 | 0.823 | 0.690 | 0.8776 |
| 29 | chip | solar | 95.0 | 0.958 | 0.836 | 0.430 | 0.8776 |
| 30 | chip | learning-algorithm | 98.0 | 0.920 | 0.768 | 0.555 | 0.8771 |
| 31 | blockchain | cryptography | 93.6 | 0.888 | 0.815 | 0.730 | 0.8768 |
| 32 | compiler-os | crypto | 98.3 | 0.912 | 0.715 | 0.665 | 0.8763 |
| 33 | grid | pure-mathematics | 95.5 | 0.855 | 0.865 | 0.645 | 0.8760 |
| 34 | grid | solar | 95.0 | 0.943 | 0.868 | 0.395 | 0.8760 |
| 35 | grid | learning-algorithm | 98.0 | 0.905 | 0.800 | 0.520 | 0.8755 |
| 36 | chip | display-audio | 100.0 | 0.925 | 0.733 | 0.495 | 0.8736 |
| 37 | chip | thermal | 100.0 | 0.935 | 0.718 | 0.495 | 0.8736 |
| 38 | chip | network | 98.3 | 0.894 | 0.778 | 0.565 | 0.8735 |
| 39 | compiler-os | pure-mathematics | 95.5 | 0.855 | 0.790 | 0.770 | 0.8735 |
| 40 | compiler-os | solar | 95.0 | 0.943 | 0.793 | 0.520 | 0.8735 |
| 41 | compiler-os | learning-algorithm | 98.0 | 0.905 | 0.725 | 0.645 | 0.8730 |
| 42 | display-audio | grid | 100.0 | 0.910 | 0.765 | 0.460 | 0.8720 |
| 43 | grid | thermal | 100.0 | 0.920 | 0.750 | 0.460 | 0.8720 |
| 44 | blockchain | chip | 96.6 | 0.903 | 0.788 | 0.570 | 0.8719 |
| 45 | grid | network | 98.3 | 0.879 | 0.810 | 0.530 | 0.8719 |
| 46 | autonomous | cryptography | 97.0 | 0.911 | 0.730 | 0.640 | 0.8713 |
| 47 | biology | cryptography | 97.0 | 0.907 | 0.735 | 0.640 | 0.8711 |
| 48 | blockchain | grid | 96.6 | 0.888 | 0.820 | 0.535 | 0.8703 |
| 49 | cryptography | programming-language | 95.0 | 0.940 | 0.731 | 0.621 | 0.8703 |
| 50 | cosmology-particle | material | 95.5 | 0.914 | 0.725 | 0.690 | 0.8702 |

---

## 도메인 평균 점수 랭킹 (파트너 능력)

| Rank | Domain | Avg Score | Avg n6% | 등급 |
|------|--------|-----------|---------|------|
| 1 | **cryptography** | **0.8742** | 94.7 | S |
| 2 | **chip** | **0.8695** | 97.6 | S |
| 3 | **grid** | **0.8680** | 97.5 | S |
| 4 | **compiler-os** | **0.8656** | 97.5 | A |
| 5 | cosmology-particle | 0.8554 | 94.3 | A |
| 6 | material | 0.8518 | 96.6 | B+ |
| 7 | medical | 0.8493 | 97.6 | B+ |
| 8 | crypto | 0.8475 | 95.9 | B |
| 9 | pure-mathematics | 0.8448 | 93.7 | B |
| 10 | solar | 0.8448 | 92.7 | B |
| 11 | learning-algorithm | 0.8443 | 95.6 | B |
| 12 | display-audio | 0.8409 | 97.5 | B |
| 13 | thermal | 0.8409 | 97.6 | B |
| 14 | network | 0.8408 | 95.9 | B |
| 15 | blockchain | 0.8393 | 94.3 | B |
| 16 | autonomous | 0.8340 | 97.6 | C |
| 17 | biology | 0.8338 | 97.5 | C |
| 18 | programming-language | 0.8330 | 95.6 | C |
| 19 | energy_gen | 0.8322 | 97.6 | C |
| 20 | agriculture | 0.8287 | 97.6 | C |
| 21 | fusion | 0.8279 | 90.3 | C |
| 22 | robotics | 0.8257 | 95.9 | C |
| 23 | space | 0.8255 | 97.6 | C |
| 24 | software-design | 0.8232 | 92.7 | D |
| 25 | neuroscience | 0.8229 | 95.9 | D |
| 26 | battery | 0.8227 | 94.4 | D |
| 27 | plasma-physics | 0.8187 | 90.8 | D |
| 28 | linguistics | 0.8184 | 94.3 | D |
| 29 | quantum | 0.8178 | 97.6 | D |
| 30 | **sc** | **0.8007** | 84.1 | **F** |

---

## Synergy Heatmap (Top-15 도메인)

```
              crypto  chip   grid  compil cosmo  mater  medic  crypt  pure-m solar  learn  displ  therm  netwo  block
cryptography    --   .9081  .9065  .9040  .8935  .8897  .8872  .8853  .8825  .8825  .8820  .8785  .8785  .8784  .8768
chip          .9081    --   .9016  .8991  .8886  .8848  .8823  .8804  .8776  .8776  .8771  .8736  .8736  .8735  .8719
grid          .9065  .9016    --   .8975  .8870  .8832  .8807  .8788  .8760  .8760  .8755  .8720  .8720  .8719  .8703
compiler-os   .9040  .8991  .8975    --   .8845  .8807  .8782  .8763  .8735  .8735  .8730  .8695  .8695  .8694  .8678
cosmol-part   .8935  .8886  .8870  .8845    --   .8702  .8677  .8658  .8630  .8630  .8625  .8590  .8590  .8590  .8573
material      .8897  .8848  .8832  .8807  .8702    --   .8635  .8616  .8592  .8592  .8587  .8552  .8552  .8552  .8535
medical       .8872  .8823  .8807  .8782  .8677  .8635    --   .8598  .8566  .8566  .8565  .8527  .8527  .8527  .8510
```
(등급: S >= 0.88 / A >= 0.86 / B >= 0.84 / C >= 0.82 / D >= 0.80)

---

## n6=100% 달성 쌍 (66개)

n6=100%를 달성한 쌍 중 Score 상위:

| Rank | Domain A | Domain B | Score | Perf |
|------|----------|----------|-------|------|
| 1 | chip | grid | 0.9016 | 0.945 |
| 2 | chip | compiler-os | 0.8991 | 0.945 |
| 3 | compiler-os | grid | 0.8975 | 0.930 |
| 4 | chip | medical | 0.8823 | 0.909 |
| 5 | grid | medical | 0.8807 | 0.894 |
| 6 | compiler-os | medical | 0.8782 | 0.894 |
| 7 | chip | display-audio | 0.8736 | 0.925 |
| 8 | chip | thermal | 0.8736 | 0.935 |
| 9 | display-audio | grid | 0.8720 | 0.910 |
| 10 | grid | thermal | 0.8720 | 0.920 |

n6=100%인 쌍은 대부분 agriculture/autonomous/biology/chip/compiler-os/display-audio/energy_gen/grid/medical/quantum/space/thermal 12개 도메인 간의 조합.

---

## 핵심 발견

### 1. Global Optimum: cryptography x chip (Score 0.9081)
- 435쌍 중 압도적 1위
- cryptography가 Top-3를 모두 차지 (chip/grid/compiler-os와 조합)
- n6=97.0%, Perf=0.945, Power=0.853으로 모든 지표가 높음

### 2. "Cryptography Effect" -- 가장 강력한 시너지 파트너
- cryptography는 29개 파트너와의 평균 Score 0.8742로 30개 도메인 중 1위
- Top-20 Score 쌍 중 10개(50%)에 cryptography가 포함
- 특이점: n6% 평균은 94.7로 최상위가 아님에도 Score가 압도적 --> Power/Cost 보너스가 큼
- 이는 암호학의 수학적 구조가 cross-domain synergy에서 범용적 증폭기 역할을 함을 시사

### 3. "Big 4" 시너지 허브: cryptography, chip, grid, compiler-os
- 이 4개 도메인 간의 6쌍이 모두 Top-6에 진입
- 평균 Score 0.900 이상의 "S-tier" 조합은 이 4개 도메인에서만 발생
- 핵심 클러스터: 정보보안 + 하드웨어 + 에너지그리드 + OS 설계

### 4. n6% vs Score 디커플링
- agriculture/autonomous/biology 그룹은 n6=100% 달성 빈도가 가장 높지만 Score는 중위권
- cryptography는 n6=94.7%로 낮지만 Perf/Power/Cost에서 보상받아 Score 1위
- 순수 n6% 최적화와 종합 Pareto 최적화는 다른 결과를 냄

### 5. 최약 도메인: sc (superconductor)
- 29개 파트너와의 평균 Score 0.8007로 유일한 F등급
- 최하위 10쌍 중 8쌍에 sc가 포함
- n6% 평균 84.1로도 최하위 --> 호환성 개선 필요

### 6. 이종 도메인 교차 시너지 (가장 의외의 발견)
- cosmology-particle x cryptography (0.8935) -- 우주론과 암호학의 시너지
- chip x cosmology-particle (0.8886) -- 반도체와 입자물리학
- grid x pure-mathematics (0.8760) -- 전력망과 순수수학
- cryptography x solar (0.8825) -- 암호학과 태양광

---

## 결론

435쌍 전수조사 결과, **cryptography x chip** (Score 0.9081)이 글로벌 최적 조합이다.
cryptography는 "범용 시너지 증폭기"로, 어떤 도메인과 조합해도 높은 점수를 보인다.
Big 4 (cryptography, chip, grid, compiler-os) 클러스터가 전체 Top-6을 독점하며,
이 4개 도메인의 교차점은 **정보-하드웨어-에너지-시스템** 통합 아키텍처를 시사한다.
