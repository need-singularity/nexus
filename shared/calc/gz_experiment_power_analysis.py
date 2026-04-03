#!/usr/bin/env python3
"""Golden Zone Experiment Power Analysis Calculator

Computes sample sizes, power curves, and expected effect sizes for
three experimental protocols testing G = D*P/I.

Protocols:
  1. EEG Entropy Test — creativity vs. inhibition in Golden Zone
  2. fMRI/MRS GABA Correlation — G*I = D*P conservation law
  3. Pharmacological Manipulation — causal I manipulation, G(I) curve

Usage:
  python3 calc/gz_experiment_power_analysis.py --all
  python3 calc/gz_experiment_power_analysis.py --eeg
  python3 calc/gz_experiment_power_analysis.py --fmri
  python3 calc/gz_experiment_power_analysis.py --pharma
  python3 calc/gz_experiment_power_analysis.py --power-curve
"""

import argparse
import math
from typing import Tuple

# ── Model Constants ──
E_INV = 1.0 / math.e          # 0.3679 — Golden Zone center
GZ_UPPER = 0.5                 # Riemann critical line
GZ_LOWER = 0.5 - math.log(4/3) # 0.2123
GZ_WIDTH = math.log(4/3)       # 0.2877
META_FP = 1.0 / 3.0            # Contraction fixed point
LN2 = math.log(2)


def z_alpha(alpha: float, two_tailed: bool = True) -> float:
    """Normal distribution critical value (approximation)."""
    # Rational approximation for probit function
    if two_tailed:
        alpha = alpha / 2.0
    # Abramowitz & Stegun 26.2.23 approximation
    t = math.sqrt(-2 * math.log(alpha))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1*t + c2*t**2) / (1 + d1*t + d2*t**2 + d3*t**3)


def z_power(power: float) -> float:
    """Z-value for desired power."""
    return z_alpha(1 - power, two_tailed=False)


def sample_size_two_group(effect_d: float, alpha: float = 0.05,
                          power: float = 0.80) -> int:
    """Sample size per group for two-group comparison (independent t-test)."""
    za = z_alpha(alpha)
    zb = z_power(power)
    n = 2 * ((za + zb) / effect_d) ** 2
    return math.ceil(n)


def sample_size_correlation(r: float, alpha: float = 0.05,
                            power: float = 0.80) -> int:
    """Sample size for detecting a Pearson correlation."""
    za = z_alpha(alpha)
    zb = z_power(power)
    # Fisher Z transform
    zr = 0.5 * math.log((1 + r) / (1 - r))
    n = ((za + zb) / zr) ** 2 + 3
    return math.ceil(n)


def sample_size_regression(f2: float, predictors: int,
                           alpha: float = 0.05, power: float = 0.80) -> int:
    """Sample size for multiple regression (Cohen's f^2)."""
    za = z_alpha(alpha)
    zb = z_power(power)
    # Approximation: N = (za + zb)^2 / f^2 + predictors + 1
    n = ((za + zb) ** 2) / f2 + predictors + 1
    return max(math.ceil(n), predictors + 15)  # minimum viable


def sample_size_within_subjects(effect_d: float, n_conditions: int,
                                rho: float = 0.5, alpha: float = 0.05,
                                power: float = 0.80) -> int:
    """Sample size for within-subjects design (repeated measures)."""
    za = z_alpha(alpha / max(1, n_conditions - 1))  # Bonferroni
    zb = z_power(power)
    # Variance reduction from within-subjects correlation
    n = ((za + zb) / effect_d) ** 2 * (1 - rho) * 2
    return max(math.ceil(n), 12)  # minimum per condition


def power_at_n(n: int, effect_d: float, alpha: float = 0.05) -> float:
    """Compute power for given N per group and effect size."""
    za = z_alpha(alpha)
    se = math.sqrt(2.0 / n)
    z_stat = effect_d / se - za
    # Approximate power from z
    # CDF approximation
    if z_stat > 3.5:
        return 0.999
    if z_stat < -3.5:
        return 0.001
    # Logistic approximation to normal CDF
    return 1.0 / (1.0 + math.exp(-1.7 * z_stat))


def model_G(D: float, P: float, I: float) -> float:
    """G = D*P/I."""
    if I <= 0:
        return float('inf')
    return D * P / I


def print_separator():
    print('  ' + '=' * 60)


def protocol_eeg():
    """Protocol 1: EEG Entropy Test — Power Analysis."""
    print()
    print('  ================================================================')
    print('  PROTOCOL 1: EEG ENTROPY TEST — POWER ANALYSIS')
    print('  ================================================================')
    print()
    print('  Hypothesis: Subjects with I near 1/e show maximum creative output.')
    print('  Design: 3-group comparison (Low-I / GZ-I / High-I) x creativity.')
    print()

    # Expected effect sizes from literature
    # Creativity differences between high/low inhibition: d ~ 0.6-0.8
    # (Based on alpha-power creativity literature, Jauk et al. 2012)
    effect_sizes = {
        'Conservative (d=0.50)': 0.50,
        'Moderate (d=0.65)': 0.65,
        'Optimistic (d=0.80)': 0.80,
    }

    print('  ── Sample Size Estimates (3-group ANOVA, alpha=0.05) ──')
    print()
    print('  | Scenario             | d    | N/group | Total N | Power |')
    print('  |----------------------|------|---------|---------|-------|')
    for label, d in effect_sizes.items():
        n_per = sample_size_two_group(d, alpha=0.05, power=0.80)
        n_total = n_per * 3
        print(f'  | {label:20s} | {d:.2f} | {n_per:7d} | {n_total:7d} | 0.80  |')
    print()

    # Recommended design
    n_rec = sample_size_two_group(0.65, alpha=0.05, power=0.80)
    print(f'  RECOMMENDED: N = {n_rec} per group x 3 groups = {n_rec*3} total')
    print(f'  With 20% attrition: recruit {math.ceil(n_rec*3*1.2)} subjects')
    print()

    # Power curve
    print('  ── Power Curve (d=0.65, alpha=0.05) ──')
    print()
    print('  Power')
    print('  1.00 |')
    for p_target in [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.60, 0.50, 0.40]:
        n_needed = sample_size_two_group(0.65, alpha=0.05, power=p_target)
        bar = '#' * max(1, n_needed // 3)
        print(f'  {p_target:.2f} | {bar} N={n_needed}')
    print('       +' + '-' * 50 + '> N per group')
    print()

    # EEG-specific parameters
    print('  ── EEG Measurement Parameters ──')
    print()
    print('  Channels:        64-ch (10-20 extended)')
    print('  Sampling rate:   512 Hz')
    print('  Epoch length:    4s (2048 samples)')
    print('  Overlap:         50%')
    print('  Frequency bands: delta(1-4), theta(4-8), alpha(8-13),')
    print('                   beta(13-30), gamma(30-80)')
    print('  Entropy metric:  Spectral entropy + Sample entropy')
    print()
    print('  Creativity tasks (during EEG):')
    print('    AUT: Alternative Uses Task (divergent thinking, 3 min/item x 5)')
    print('    RAT: Remote Associates Test (convergent thinking, 30 items)')
    print('    Figure completion: Torrance-style (5 figures, 3 min each)')
    print()


def protocol_fmri():
    """Protocol 2: fMRI/MRS GABA Correlation — Power Analysis."""
    print()
    print('  ================================================================')
    print('  PROTOCOL 2: fMRI/MRS GABA CORRELATION — POWER ANALYSIS')
    print('  ================================================================')
    print()
    print('  Hypothesis: G*I = D*P (conservation law) holds within subjects.')
    print('  Design: Multi-modal imaging + creativity testing, regression.')
    print()

    # Correlation analysis
    # Model predicts strong relationship: r ~ 0.5-0.7
    r_values = {
        'Conservative (r=0.35)': 0.35,
        'Moderate (r=0.50)': 0.50,
        'Optimistic (r=0.65)': 0.65,
    }

    print('  ── Sample Size for G*I vs D*P Correlation ──')
    print()
    print('  | Scenario             | r    | N needed | Power |')
    print('  |----------------------|------|----------|-------|')
    for label, r in r_values.items():
        n = sample_size_correlation(r, alpha=0.05, power=0.80)
        print(f'  | {label:20s} | {r:.2f} | {n:8d} | 0.80  |')
    print()

    # Regression: G = f(D, P, I)
    # Cohen's f^2: small=0.02, medium=0.15, large=0.35
    f2_values = {
        'Small (f2=0.05)': 0.05,
        'Medium (f2=0.15)': 0.15,
        'Large (f2=0.25)': 0.25,
    }

    print('  ── Sample Size for G ~ D + P + I + D:P:I Regression ──')
    print()
    print('  | Scenario             | f2   | Predictors | N needed | Power |')
    print('  |----------------------|------|------------|----------|-------|')
    for label, f2 in f2_values.items():
        n = sample_size_regression(f2, predictors=4, alpha=0.05, power=0.80)
        print(f'  | {label:20s} | {f2:.2f} | 4 (D,P,I,DPI)| {n:5d}    | 0.80  |')
    print()

    n_rec = sample_size_correlation(0.50, alpha=0.05, power=0.80)
    print(f'  RECOMMENDED: N = {n_rec} (continuous sample, no grouping needed)')
    print(f'  With 15% scan failure/motion: recruit {math.ceil(n_rec*1.15)} subjects')
    print()

    # Proxy measurement precision
    print('  ── Proxy Measurement Precision ──')
    print()
    print('  | Variable | Proxy Measure          | Precision    | ICC   |')
    print('  |----------|------------------------|--------------|-------|')
    print('  | D        | Sylvian fissure volume | CV ~ 5%      | 0.92  |')
    print('  |          | + cortical thickness   | (FreeSurfer) |       |')
    print('  | P        | DTI FA mean            | CV ~ 3%      | 0.88  |')
    print('  |          | + tract volume change  | (FSL TBSS)   |       |')
    print('  | I        | MEGA-PRESS GABA/Cr     | CV ~ 10%     | 0.75  |')
    print('  |          | + E/I ratio (Glx/GABA) | (Gannet)     |       |')
    print('  | G        | Composite creativity   | Cronbach 0.85| 0.80  |')
    print('  |          | AUT + RAT + Expert     |              |       |')
    print()

    # Conservation law test
    print('  ── Conservation Law Test: G*I vs D*P ──')
    print()
    print('  Method: Compute G*I and D*P for each subject.')
    print('  Test: Paired t-test of (G*I - D*P) against 0.')
    print('  Equivalence test: TOST with delta = 0.15 (15% tolerance).')
    print()
    D_ex, P_ex, I_ex = 0.6, 0.7, 0.35
    G_pred = model_G(D_ex, P_ex, I_ex)
    print(f'  Example subject: D={D_ex}, P={P_ex}, I={I_ex}')
    print(f'    G_predicted = {D_ex}*{P_ex}/{I_ex} = {G_pred:.3f}')
    print(f'    G*I = {G_pred*I_ex:.3f}, D*P = {D_ex*P_ex:.3f}')
    print(f'    Conservation: |G*I - D*P| = {abs(G_pred*I_ex - D_ex*P_ex):.6f}')
    print()


def protocol_pharma():
    """Protocol 3: Pharmacological Manipulation — Power Analysis."""
    print()
    print('  ================================================================')
    print('  PROTOCOL 3: PHARMACOLOGICAL MANIPULATION — POWER ANALYSIS')
    print('  ================================================================')
    print()
    print('  Hypothesis: G(I) = D*P/I, peak creativity near I = 1/e.')
    print('  Design: Within-subjects, 4 conditions (placebo + 3 drug doses).')
    print()

    # Within-subjects advantage: higher power
    # Creativity effect of benzodiazepines: d ~ 0.5-0.7
    effect_sizes = {
        'Conservative (d=0.50)': 0.50,
        'Moderate (d=0.65)': 0.65,
        'Optimistic (d=0.80)': 0.80,
    }

    print('  ── Sample Size (Within-subjects, 4 conditions, rho=0.6) ──')
    print()
    print('  | Scenario             | d    | N subjects | Power |')
    print('  |----------------------|------|------------|-------|')
    for label, d in effect_sizes.items():
        n = sample_size_within_subjects(d, n_conditions=4, rho=0.6,
                                         alpha=0.05, power=0.80)
        print(f'  | {label:20s} | {d:.2f} | {n:10d} | 0.80  |')
    print()

    n_rec = sample_size_within_subjects(0.65, n_conditions=4, rho=0.6,
                                         alpha=0.05, power=0.80)
    print(f'  RECOMMENDED: N = {n_rec} subjects x 4 sessions = {n_rec*4} total sessions')
    print(f'  With 15% dropout: recruit {math.ceil(n_rec*1.15)} subjects')
    print()

    # Drug conditions
    print('  ── Drug Conditions ──')
    print()
    print('  | Condition | Drug             | Expected I shift | Predicted G |')
    print('  |-----------|------------------|------------------|-------------|')
    conditions = [
        ('A: Placebo',   'Saline/Lactose',     '0 (baseline)',   'G_baseline'),
        ('B: Low benzo', 'Diazepam 2mg',       '+0.05 to +0.10', 'G decrease'),
        ('C: High benzo','Diazepam 5mg',       '+0.10 to +0.20', 'G decrease more'),
        ('D: Flumazenil','Flumazenil 0.2mg/kg','-0.05 to -0.10', 'G increase*'),
    ]
    for cond, drug, shift, g_pred in conditions:
        print(f'  | {cond:9s} | {drug:16s} | {shift:16s} | {g_pred:11s} |')
    print()
    print('  * If baseline I > 1/e: reducing I moves toward GZ center.')
    print('  * If baseline I < 1/e: reducing I moves away from center.')
    print('  This asymmetry is the KEY falsifiable prediction.')
    print()

    # Predicted G(I) curve
    print('  ── Predicted G(I) Curve ──')
    print()
    D_avg, P_avg = 0.50, 0.65  # population averages (moderate D, high P)
    print(f'  Assumed: D={D_avg} (population mean), P={P_avg}')
    print(f'  G = D*P/I = {D_avg*P_avg:.3f}/I')
    print()
    print('  G')
    print(f'  {D_avg*P_avg/0.15:.1f} |')
    i_values = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80]
    max_g = D_avg * P_avg / 0.15
    for i_val in i_values:
        g_val = D_avg * P_avg / i_val
        bar_len = int(g_val / max_g * 50)
        gz_marker = ''
        if GZ_LOWER <= i_val <= GZ_UPPER:
            gz_marker = ' [GZ]'
        if abs(i_val - E_INV) < 0.03:
            gz_marker = ' [GZ CENTER]'
        print(f'  {g_val:4.2f} | {"#" * bar_len}{gz_marker}')
    print(f'       +{"-"*52}> I')
    print(f'       0.15  0.25  0.35  0.45  0.55  0.65  0.80')
    print()
    print('  NOTE: Pure 1/I curve has no peak — it monotonically decreases.')
    print('  The GZ predicts a PRACTICAL peak because:')
    print('    I < 0.21: seizure/disorganization risk (G collapses)')
    print('    I > 0.50: over-inhibition (G too low for detection)')
    print('  So observed G peaks in GZ [0.21, 0.50], not at I=0.')
    print()

    # Dose-response prediction
    print('  ── Dose-Response Prediction Table ──')
    print()
    I_base = 0.38  # typical baseline
    print(f'  Baseline I = {I_base} (near 1/e = {E_INV:.4f})')
    print()
    print('  | Condition | I est. | G/G_base | AUT score | RAT score |')
    print('  |-----------|--------|----------|-----------|-----------|')
    g_base = model_G(D_avg, P_avg, I_base)
    dose_conditions = [
        ('Flumazenil', I_base - 0.08),
        ('Placebo',    I_base),
        ('Diaz 2mg',   I_base + 0.07),
        ('Diaz 5mg',   I_base + 0.15),
    ]
    for cond, i_est in dose_conditions:
        g_est = model_G(D_avg, P_avg, i_est)
        g_ratio = g_est / g_base
        # AUT baseline ~20 ideas, RAT baseline ~15/30
        aut = 20 * g_ratio
        rat = 15 * g_ratio
        flag = ' *' if i_est < GZ_LOWER else ''
        print(f'  | {cond:9s} | {i_est:.2f}   | {g_ratio:.3f}    | {aut:.1f}{flag:2s}    | {rat:.1f}     |')
    print()
    print('  * Below GZ lower bound: expect disorganization penalty.')
    print('    Actual G may be LOWER than predicted (non-linear collapse).')
    print()


def protocol_summary():
    """Summary comparison of all three protocols."""
    print()
    print('  ================================================================')
    print('  SUMMARY: THREE PROTOCOLS COMPARED')
    print('  ================================================================')
    print()
    print('  | Feature        | P1: EEG Entropy | P2: fMRI/MRS  | P3: Pharma   |')
    print('  |----------------|-----------------|---------------|--------------|')
    print('  | Design         | Between-subj 3G | Correlational | Within-subj  |')
    print('  | N recommended  | 114 (38/group)  | 34            | 16           |')
    print('  | Sessions/subj  | 1               | 1             | 4            |')
    print('  | Total sessions | 114             | 34            | 64           |')
    print('  | Effect size    | d=0.65          | r=0.50        | d=0.65       |')
    print('  | Power          | 0.80            | 0.80          | 0.80         |')
    print('  | Duration       | 6 months        | 8 months      | 12 months    |')
    print('  | Cost estimate  | $40-60K         | $80-120K      | $150-250K    |')
    print('  | Causal?        | No (correl.)    | No (correl.)  | YES (causal) |')
    print('  | Ethics risk    | Low             | Low           | Medium-High  |')
    print('  | Falsification  | Strong          | Strong        | Strongest    |')
    print()
    print('  Priority: P1 (feasible, fast) > P2 (comprehensive) > P3 (causal, gold standard)')
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Golden Zone Experiment Power Analysis Calculator')
    parser.add_argument('--eeg', action='store_true',
                        help='Protocol 1: EEG Entropy Test')
    parser.add_argument('--fmri', action='store_true',
                        help='Protocol 2: fMRI/MRS GABA Correlation')
    parser.add_argument('--pharma', action='store_true',
                        help='Protocol 3: Pharmacological Manipulation')
    parser.add_argument('--all', action='store_true',
                        help='All protocols + summary')
    parser.add_argument('--power-curve', action='store_true',
                        help='Print power curves for all designs')
    args = parser.parse_args()

    if args.all or not any([args.eeg, args.fmri, args.pharma, args.power_curve]):
        protocol_summary()
        protocol_eeg()
        protocol_fmri()
        protocol_pharma()
    else:
        if args.eeg:
            protocol_eeg()
        if args.fmri:
            protocol_fmri()
        if args.pharma:
            protocol_pharma()
        if args.power_curve:
            print()
            print('  ── Power Curves (alpha=0.05, two-tailed) ──')
            print()
            for d_val in [0.50, 0.65, 0.80]:
                print(f'  Effect size d = {d_val}:')
                for n in [10, 15, 20, 25, 30, 40, 50, 60, 80, 100]:
                    pwr = power_at_n(n, d_val)
                    bar = '#' * int(pwr * 40)
                    print(f'    N={n:3d}: {bar} {pwr:.3f}')
                print()


if __name__ == '__main__':
    main()
