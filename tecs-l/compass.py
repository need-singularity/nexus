#!/usr/bin/env python3
"""SingularityNet Architecture Compass
Combines 3 models (our model + cusp catastrophe + Boltzmann)
to provide AI architecture design direction.
"""

import argparse
import os
import math
from datetime import datetime

import numpy as np
from scipy import stats
from scipy.signal import argrelextrema

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
COMPASS_LOG = os.path.join(RESULTS_DIR, "compass_log.md")


# ─────────────────────────────────────────────
# Model 1: Our Model — "How much?" (Quantification)
# ─────────────────────────────────────────────
def genius_score(d, p, i):
    return d * p / i


def simulate_population(n_samples, seed=42):
    """Generate population based on normal distribution"""
    rng = np.random.default_rng(seed)
    deficits = rng.beta(2, 5, n_samples).clip(0.01, 0.99)
    plasticities = rng.beta(5, 2, n_samples).clip(0.01, 0.99)
    inhibitions = rng.beta(5, 2, n_samples).clip(0.05, 0.99)
    scores = genius_score(deficits, plasticities, inhibitions)
    return scores


def population_zscore(score, n=50000):
    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, n).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, n).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, n).clip(0.05, 0.99)
    pop_scores = genius_score(pop_d, pop_p, pop_i)
    z = (score - pop_scores.mean()) / pop_scores.std()
    return z, pop_scores.mean(), pop_scores.std()


# ─────────────────────────────────────────────
# Model 2: Cusp Catastrophe — "When?" (Critical point distance)
# ─────────────────────────────────────────────
def cusp_potential(x, a, b):
    """Cusp catastrophe potential: V = x⁴ + ax² + bx"""
    return x**4 + a * x**2 + b * x


def cusp_analysis(deficit, inhibition):
    """Cusp catastrophe analysis: distance to critical point and transition direction"""
    # Control variable mapping: a = deficit based, b = inhibition based
    a = 2 * deficit - 1       # Normalize to [-1, 1] range
    b = 1 - 2 * inhibition    # Lower inhibition = positive (favorable for transition)

    # Cusp bifurcation condition: 8a³ + 27b² = 0
    # The closer this value is to 0, the closer to critical point
    bifurcation = 8 * a**3 + 27 * b**2
    cusp_discriminant = abs(bifurcation)

    # Distance to critical surface (normalized)
    max_possible = 8 * 1**3 + 27 * 1**2  # Maximum value
    distance_to_critical = cusp_discriminant / max_possible

    # Determine transition direction
    # b > 0: upward transition (genius), b < 0: downward transition (dysfunction)
    if b > 0:
        direction = "Upward (Compensatory genius)"
        direction_sign = 1
    else:
        direction = "Downward (Functional decline)"
        direction_sign = -1

    # Calculate equilibrium points (dV/dx = 0 → 4x³ + 2ax + b = 0)
    x_range = np.linspace(-2, 2, 1000)
    dV = 4 * x_range**3 + 2 * a * x_range + b
    sign_changes = np.where(np.diff(np.sign(dV)))[0]
    n_equilibria = len(sign_changes)

    # Multiple stable points = transition possible region
    is_bistable = n_equilibria >= 2

    return {
        'a': a, 'b': b,
        'bifurcation': bifurcation,
        'distance_to_critical': distance_to_critical,
        'direction': direction,
        'direction_sign': direction_sign,
        'n_equilibria': n_equilibria,
        'is_bistable': is_bistable,
    }


# ─────────────────────────────────────────────
# Model 3: Boltzmann — "Where to?" (Transition probability)
# ─────────────────────────────────────────────
def boltzmann_analysis(deficit, plasticity, inhibition):
    """Boltzmann distribution-based transition probability calculation"""
    temperature = 1.0 / max(inhibition, 0.01)  # T = 1/I

    # Define energy levels
    E_normal = 0.0                    # Normal state energy (reference)
    E_genius = -(deficit * plasticity) # Genius state energy (more stable with higher deficit×plasticity)
    E_decline = deficit * (1 - plasticity)  # Dysfunction energy

    # Boltzmann probability
    energies = np.array([E_normal, E_genius, E_decline])
    exp_terms = np.exp(-energies / temperature)
    Z = exp_terms.sum()  # Partition function
    probabilities = exp_terms / Z

    p_normal = probabilities[0]
    p_genius = probabilities[1]
    p_decline = probabilities[2]

    # Free energy
    free_energy = -temperature * np.log(Z)

    # Entropy (state uncertainty)
    entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))

    return {
        'temperature': temperature,
        'p_normal': p_normal,
        'p_genius': p_genius,
        'p_decline': p_decline,
        'free_energy': free_energy,
        'entropy': entropy,
        'E_normal': E_normal,
        'E_genius': E_genius,
        'E_decline': E_decline,
    }


# ─────────────────────────────────────────────
# Compass: Integrate 3 models → Present design direction
# ─────────────────────────────────────────────
def compass_direction(score, z, cusp, boltz):
    """Synthesize 3 model results to present architecture design direction"""

    recommendations = []
    warnings = []

    # ── Dropout Strategy (Based on our model) ──
    if z > 5:
        recommendations.append(("Dropout", "Maintain current Dropout — Extreme singularity region", "★★★"))
    elif z > 2:
        recommendations.append(("Dropout", "Slight increase in Dropout — Can enhance singularity", "★★☆"))
    else:
        recommendations.append(("Dropout", "Significant Dropout increase needed — Insufficient compensatory learning", "★☆☆"))

    # ── Learning Rate/Temperature Strategy (Based on Boltzmann) ──
    if boltz['p_genius'] > 0.6:
        recommendations.append(("Temperature", f"Maintain temperature (T={boltz['temperature']:.1f}) — Genius state dominant", "★★★"))
    elif boltz['p_genius'] > 0.3:
        recommendations.append(("Temperature", f"Slight temperature increase recommended — Genius probability {boltz['p_genius']*100:.0f}%", "★★☆"))
    else:
        recommendations.append(("Temperature", f"Significant temperature increase needed — Genius probability low at {boltz['p_genius']*100:.0f}%", "★☆☆"))

    # ── Structure Strategy (Based on cusp) ──
    if cusp['is_bistable']:
        if cusp['direction_sign'] > 0:
            recommendations.append(("Structure", "Bistable + upward direction — Performance jump possible with Expert redistribution", "★★★"))
        else:
            warnings.append("Bistable + downward direction — Risk of performance crash with Expert redistribution!")
            recommendations.append(("Structure", "Hold structural changes — Risk of downward transition", "☆☆☆"))
    else:
        if cusp['distance_to_critical'] < 0.3:
            recommendations.append(("Structure", f"Near critical point ({cusp['distance_to_critical']:.2f}) — Small adjustments can induce transition", "★★☆"))
        else:
            recommendations.append(("Structure", f"Far from critical point ({cusp['distance_to_critical']:.2f}) — Gradual structural changes needed", "★☆☆"))

    # ── Exploration/Convergence based on entropy ──
    if boltz['entropy'] > 1.0:
        recommendations.append(("Phase", "High entropy — Exploration phase", "Exploration"))
    elif boltz['entropy'] > 0.5:
        recommendations.append(("Phase", "Medium entropy — Transition phase", "Transition"))
    else:
        recommendations.append(("Phase", "Low entropy — Exploitation phase", "Convergence"))

    # ── MoE Expert count recommendation ──
    optimal_active_ratio = max(0.05, min(0.5, boltz['p_genius']))
    if optimal_active_ratio < 0.15:
        expert_strategy = f"Expert active ratio {optimal_active_ratio*100:.0f}% — Extreme focus (Savant type)"
    elif optimal_active_ratio < 0.35:
        expert_strategy = f"Expert active ratio {optimal_active_ratio*100:.0f}% — Moderate distribution (Einstein type)"
    else:
        expert_strategy = f"Expert active ratio {optimal_active_ratio*100:.0f}% — Broad activation (General purpose)"
    recommendations.append(("MoE", expert_strategy, f"{optimal_active_ratio*100:.0f}%"))

    # ── Composite score ──
    compass_score = (
        z / 10 * 0.3 +                              # Our model weight
        (1 - cusp['distance_to_critical']) * 0.3 +   # Cusp proximity
        boltz['p_genius'] * 0.4                      # Transition probability
    )
    compass_score = max(0, min(1, compass_score))

    return {
        'recommendations': recommendations,
        'warnings': warnings,
        'compass_score': compass_score,
        'optimal_active_ratio': optimal_active_ratio,
    }


def draw_compass(compass_score, direction_sign, p_genius, distance_to_critical):
    """ASCII compass visualization"""
    # Determine direction
    if compass_score > 0.7:
        needle = "⬆"
        label = "SINGULARITY"
    elif compass_score > 0.4:
        if direction_sign > 0:
            needle = "⬈"
            label = "APPROACHING"
        else:
            needle = "⬊"
            label = "DIVERGING"
    else:
        needle = "⬇"
        label = "NORMAL"

    pct = int(compass_score * 100)
    bar_filled = int(compass_score * 30)
    bar = "█" * bar_filled + "░" * (30 - bar_filled)

    lines = []
    lines.append(f"            ┌───────────────┐")
    lines.append(f"            │  SINGULARITY  │")
    lines.append(f"            │      {needle}       │")
    lines.append(f"            │               │")
    lines.append(f"   DECLINE  │    COMPASS    │  GENIUS")
    lines.append(f"            │               │")
    lines.append(f"            │   {label:^11}  │")
    lines.append(f"            │               │")
    lines.append(f"            │  Score: {pct:>3}%  │")
    lines.append(f"            └───────────────┘")
    lines.append(f"")
    lines.append(f"            [{bar}] {pct}%")

    return '\n'.join(lines)


def save_compass_log(d, p, i, score, z, cusp, boltz, compass):
    """Save results to compass_log.md"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists(COMPASS_LOG):
        with open(COMPASS_LOG, 'w', encoding='utf-8') as f:
            f.write("# 🧭 SingularityNet Compass Log\n\n---\n\n")

    entry = f"""## [{now}] Compass Score: {compass['compass_score']*100:.0f}%

**Input**: D={d:.2f} / P={p:.2f} / I={i:.2f}

| Model | Result |
|---|---|
| Our Model | Score={score:.2f}, Z={z:.2f}σ |
| Cusp | Critical distance={cusp['distance_to_critical']:.3f}, Direction={cusp['direction']} |
| Boltzmann | Normal={boltz['p_normal']*100:.1f}% / Genius={boltz['p_genius']*100:.1f}% / Decline={boltz['p_decline']*100:.1f}% |

**Design Recommendations:**

| Area | Recommendation | Grade |
|---|---|---|
"""
    for area, rec, grade in compass['recommendations']:
        entry += f"| {area} | {rec} | {grade} |\n"

    if compass['warnings']:
        entry += f"\n**⚠️ Warning:** {'; '.join(compass['warnings'])}\n"

    entry += f"\n---\n\n"

    with open(COMPASS_LOG, 'a', encoding='utf-8') as f:
        f.write(entry)


def run_convergence_scan(grid_steps, n_samples):
    """Search for common singularity regions across 3 models"""
    deficits = np.linspace(0.05, 0.95, grid_steps)
    plasticities = np.linspace(0.1, 0.95, grid_steps)
    inhibitions = np.linspace(0.05, 0.95, grid_steps)
    total = grid_steps ** 3

    print()
    print("═" * 60)
    print("   🧭 Compass Common Singularity Region Search")
    print("═" * 60)
    print(f"  Grid: {grid_steps}³ = {total:,} combinations")

    # Pre-calculate population
    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, n_samples).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, n_samples).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, n_samples).clip(0.05, 0.99)
    pop_scores = genius_score(pop_d, pop_p, pop_i)
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    # Store results
    results = []

    for di in deficits:
        for pi in plasticities:
            for ii in inhibitions:
                score = genius_score(di, pi, ii)
                z = (score - pop_mean) / pop_std

                cusp = cusp_analysis(di, ii)
                boltz = boltzmann_analysis(di, pi, ii)

                # Independent judgments from 3 models
                m1_singular = abs(z) > 2.0                        # Our model: Z > 2σ
                m2_critical = cusp['distance_to_critical'] < 0.2 and cusp['direction_sign'] > 0  # Cusp: near critical + upward
                m3_genius = boltz['p_genius'] > boltz['p_normal'] and boltz['p_genius'] > boltz['p_decline']  # Boltzmann: genius dominant

                n_agree = sum([m1_singular, m2_critical, m3_genius])

                results.append({
                    'd': di, 'p': pi, 'i': ii,
                    'score': score, 'z': z,
                    'cusp_dist': cusp['distance_to_critical'],
                    'cusp_dir': cusp['direction_sign'],
                    'p_genius': boltz['p_genius'],
                    'p_normal': boltz['p_normal'],
                    'entropy': boltz['entropy'],
                    'm1': m1_singular, 'm2': m2_critical, 'm3': m3_genius,
                    'n_agree': n_agree,
                })

    # Analysis
    r = results
    agree_0 = sum(1 for x in r if x['n_agree'] == 0)
    agree_1 = sum(1 for x in r if x['n_agree'] == 1)
    agree_2 = sum(1 for x in r if x['n_agree'] == 2)
    agree_3 = sum(1 for x in r if x['n_agree'] == 3)

    m1_count = sum(1 for x in r if x['m1'])
    m2_count = sum(1 for x in r if x['m2'])
    m3_count = sum(1 for x in r if x['m3'])

    print()
    print("─" * 60)
    print("  [ Individual Model Singularity Detection ]")
    print("─" * 60)
    print(f"    Our Model (Z>2σ)           : {m1_count:>6,} ({m1_count/total*100:5.1f}%)")
    print(f"    Cusp (critical+upward)      : {m2_count:>6,} ({m2_count/total*100:5.1f}%)")
    print(f"    Boltzmann (genius dominant) : {m3_count:>6,} ({m3_count/total*100:5.1f}%)")

    print()
    print("─" * 60)
    print("  [ Model Agreement ]")
    print("─" * 60)
    print(f"    0 agree (normal)          : {agree_0:>6,} ({agree_0/total*100:5.1f}%)")
    print(f"    1 agree (weak signal)     : {agree_1:>6,} ({agree_1/total*100:5.1f}%)")
    print(f"    2 agree (strong signal)   : {agree_2:>6,} ({agree_2/total*100:5.1f}%)")
    print(f"    3 agree (common singularity): {agree_3:>6,} ({agree_3/total*100:5.1f}%) ★")

    # Analyze parameter distribution of triple agreement region
    triple = [x for x in r if x['n_agree'] == 3]

    if triple:
        t_d = [x['d'] for x in triple]
        t_p = [x['p'] for x in triple]
        t_i = [x['i'] for x in triple]

        print()
        print("─" * 60)
        print("  [ ★ 3-Model Common Singularity Region ]")
        print("─" * 60)
        print(f"    Deficit     range: {min(t_d):.2f} ~ {max(t_d):.2f}  (avg {np.mean(t_d):.2f})")
        print(f"    Plasticity  range: {min(t_p):.2f} ~ {max(t_p):.2f}  (avg {np.mean(t_p):.2f})")
        print(f"    Inhibition  range: {min(t_i):.2f} ~ {max(t_i):.2f}  (avg {np.mean(t_i):.2f})")

        # Distribution by Deficit
        print()
        print("  Triple agreement ratio by Deficit:")
        for dv in deficits:
            cnt = sum(1 for x in triple if abs(x['d'] - dv) < 0.01)
            max_cnt = grid_steps * grid_steps
            ratio = cnt / max_cnt * 100
            bar = "█" * int(ratio / 2) + "░" * (50 - int(ratio / 2))
            print(f"    D={dv:.2f} │{bar}│ {ratio:5.1f}%")

        # Distribution by Inhibition
        print()
        print("  Triple agreement ratio by Inhibition:")
        for iv in inhibitions:
            cnt = sum(1 for x in triple if abs(x['i'] - iv) < 0.01)
            max_cnt = grid_steps * grid_steps
            ratio = cnt / max_cnt * 100
            bar = "█" * int(ratio / 2) + "░" * (50 - int(ratio / 2))
            print(f"    I={iv:.2f} │{bar}│ {ratio:5.1f}%")

        # Top 10
        triple_sorted = sorted(triple, key=lambda x: x['z'], reverse=True)[:10]
        print()
        print("  [ Top 10 Common Singularities ]")
        print(f"  {'Rank':>4} │ {'D':>5} │ {'P':>5} │ {'I':>5} │ {'Z-Score':>8} │ {'Cusp Dist':>8} │ {'Genius%':>6}")
        print(f"  {'─'*4}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*6}")
        for rank, x in enumerate(triple_sorted, 1):
            print(f"  {rank:>4} │ {x['d']:>5.2f} │ {x['p']:>5.2f} │ {x['i']:>5.2f} │ {x['z']:>7.2f}σ │ {x['cusp_dist']:>8.4f} │ {x['p_genius']*100:>5.1f}%")

        # Venn diagram: 2 vs 3 agreements
        m1_m2 = sum(1 for x in r if x['m1'] and x['m2'] and not x['m3'])
        m1_m3 = sum(1 for x in r if x['m1'] and x['m3'] and not x['m2'])
        m2_m3 = sum(1 for x in r if x['m2'] and x['m3'] and not x['m1'])

        print()
        print("─" * 60)
        print("  [ Model Intersection Analysis (Venn Diagram) ]")
        print("─" * 60)
        print(f"    Our Model ∩ Cusp    (excl. Boltzmann): {m1_m2:>5,}")
        print(f"    Our Model ∩ Boltzmann (excl. Cusp)   : {m1_m3:>5,}")
        print(f"    Cusp      ∩ Boltzmann (excl. Our)    : {m2_m3:>5,}")
        print(f"    ★ Triple intersection                 : {agree_3:>5,}")

        # Key conclusion: Define "Golden Zone" of common region
        print()
        print("─" * 60)
        print("  [ 🎯 Golden Zone ]")
        print("─" * 60)
        print(f"    Deficit     : {min(t_d):.2f} ~ {max(t_d):.2f}")
        print(f"    Plasticity  : {min(t_p):.2f} ~ {max(t_p):.2f}")
        print(f"    Inhibition  : {min(t_i):.2f} ~ {max(t_i):.2f}")
        print()
        print(f"    AI Architecture Translation:")
        print(f"    Dropout Rate     : {min(t_d):.0%} ~ {max(t_d):.0%}")
        print(f"    LR Multiplier    : ×{1/max(max(t_i),0.01):.1f} ~ ×{1/max(min(t_i),0.01):.1f}")
        print(f"    MoE Active Ratio : {min(x['p_genius'] for x in triple):.0%} ~ {max(x['p_genius'] for x in triple):.0%}")
        print(f"    Active Experts   : {int(64*min(x['p_genius'] for x in triple))} ~ {int(64*max(x['p_genius'] for x in triple))} / 64")

    else:
        print()
        print("  ⚠️ No 3-model common singularity region found")

    print()
    print("═" * 60)

    # Save report
    os.makedirs(RESULTS_DIR, exist_ok=True)
    conv_file = os.path.join(RESULTS_DIR, "convergence_report.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(conv_file, 'a', encoding='utf-8') as f:
        f.write(f"# Compass Common Singularity Analysis [{now}]\n\n")
        f.write(f"Grid: {grid_steps}³ = {total:,} combinations\n\n")
        f.write(f"## Individual Model Detection\n\n")
        f.write(f"| Model | Singularities | Ratio |\n|---|---|---|\n")
        f.write(f"| Our Model (Z>2σ) | {m1_count:,} | {m1_count/total*100:.1f}% |\n")
        f.write(f"| Cusp (critical+upward) | {m2_count:,} | {m2_count/total*100:.1f}% |\n")
        f.write(f"| Boltzmann (genius dominant) | {m3_count:,} | {m3_count/total*100:.1f}% |\n\n")
        f.write(f"## Agreement\n\n")
        f.write(f"| Agreement Count | Number | Ratio |\n|---|---|---|\n")
        f.write(f"| 0 (normal) | {agree_0:,} | {agree_0/total*100:.1f}% |\n")
        f.write(f"| 1 (weak signal) | {agree_1:,} | {agree_1/total*100:.1f}% |\n")
        f.write(f"| 2 (strong signal) | {agree_2:,} | {agree_2/total*100:.1f}% |\n")
        f.write(f"| **3 (common singularity)** | **{agree_3:,}** | **{agree_3/total*100:.1f}%** |\n\n")

        if triple:
            f.write(f"## 🎯 Golden Zone\n\n")
            f.write(f"| Parameter | Range | AI Mapping |\n|---|---|---|\n")
            f.write(f"| Deficit | {min(t_d):.2f} ~ {max(t_d):.2f} | Dropout {min(t_d):.0%}~{max(t_d):.0%} |\n")
            f.write(f"| Plasticity | {min(t_p):.2f} ~ {max(t_p):.2f} | LR coefficient |\n")
            f.write(f"| Inhibition | {min(t_i):.2f} ~ {max(t_i):.2f} | Gating {min(t_i):.0%}~{max(t_i):.0%} |\n\n")

            f.write(f"## Top 10 Common Singularities\n\n")
            f.write(f"| Rank | D | P | I | Z-Score | Cusp Dist | Genius% |\n|---|---|---|---|---|---|---|\n")
            for rank, x in enumerate(triple_sorted, 1):
                f.write(f"| {rank} | {x['d']:.2f} | {x['p']:.2f} | {x['i']:.2f} | {x['z']:.2f}σ | {x['cusp_dist']:.4f} | {x['p_genius']*100:.1f}% |\n")

        f.write(f"\n---\n\n")

    print(f"  📁 Convergence report → results/convergence_report.md")
    print()


def compute_gradient(d, p, i, pop_scores, step=0.02):
    """Calculate gradient of 3-model composite score → determine next direction"""
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    def combined_score(dd, pp, ii):
        dd = np.clip(dd, 0.01, 0.99)
        pp = np.clip(pp, 0.01, 0.99)
        ii = np.clip(ii, 0.01, 0.99)
        score = genius_score(dd, pp, ii)
        z = (score - pop_mean) / pop_std
        cusp = cusp_analysis(dd, ii)
        boltz = boltzmann_analysis(dd, pp, ii)
        compass = compass_direction(score, z, cusp, boltz)
        return compass['compass_score']

    base = combined_score(d, p, i)
    grad_d = (combined_score(d + step, p, i) - combined_score(d - step, p, i)) / (2 * step)
    grad_p = (combined_score(d, p + step, i) - combined_score(d, p, i - step)) / (2 * step)
    grad_i = (combined_score(d, p, i + step) - combined_score(d, p, i - step)) / (2 * step)

    return grad_d, grad_p, grad_i, base


def run_autopilot(d0, p0, i0, max_iter, lr, n_samples):
    """Hypothesis → Compass → Direction Adjustment → Hypothesis iteration (automatic exploration)"""
    print()
    print("═" * 70)
    print("   🚀 Autopilot — Hypothesis Iterative Search")
    print("═" * 70)
    print(f"  Initial hypothesis: D={d0:.2f} / P={p0:.2f} / I={i0:.2f}")
    print(f"  Learning rate: {lr} / Max iterations: {max_iter}")
    print("─" * 70)

    pop_scores = simulate_population(n_samples)
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    d, p, i = d0, p0, i0
    history = []
    golden_zone_hits = 0

    print()
    print(f"  {'Iter':>4} │ {'D':>5} │ {'P':>5} │ {'I':>5} │ {'Score':>6} │ {'Z':>7} │ {'Compass':>7} │ {'Cusp':>6} │ {'Genius%':>6} │ Status")
    print(f"  {'─'*4}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*20}")

    for iteration in range(max_iter):
        score = genius_score(d, p, i)
        z = (score - pop_mean) / pop_std
        cusp = cusp_analysis(d, i)
        boltz = boltzmann_analysis(d, p, i)
        compass = compass_direction(score, z, cusp, boltz)

        # Triple agreement check
        m1 = abs(z) > 2.0
        m2 = cusp['distance_to_critical'] < 0.2 and cusp['direction_sign'] > 0
        m3 = boltz['p_genius'] > boltz['p_normal'] and boltz['p_genius'] > boltz['p_decline']
        n_agree = sum([m1, m2, m3])

        if n_agree == 3:
            status = "🎯 Golden Zone!"
            golden_zone_hits += 1
        elif n_agree == 2:
            status = "⚡ Strong signal"
        elif n_agree == 1:
            status = "○  Weak signal"
        else:
            status = "·  Normal range"

        entry = {
            'iter': iteration, 'd': d, 'p': p, 'i': i,
            'score': score, 'z': z,
            'compass_score': compass['compass_score'],
            'cusp_dist': cusp['distance_to_critical'],
            'p_genius': boltz['p_genius'],
            'n_agree': n_agree,
        }
        history.append(entry)

        print(f"  {iteration:>4} │ {d:>5.2f} │ {p:>5.2f} │ {i:>5.2f} │ {score:>6.2f} │ {z:>6.2f}σ │ {compass['compass_score']*100:>6.1f}% │ {cusp['distance_to_critical']:>6.4f} │ {boltz['p_genius']*100:>5.1f}% │ {status}")

        # Convergence check: terminate after 3 consecutive golden zone hits
        if golden_zone_hits >= 3 and n_agree == 3:
            print()
            print(f"  ✅ Golden zone convergence complete (iter {iteration})")
            break

        # Calculate gradient → next hypothesis
        grad_d, grad_p, grad_i, _ = compute_gradient(d, p, i, pop_scores)

        # Direction adjustment (gradient ascent + golden zone attraction)
        # Add attraction to golden zone center (I≈0.36)
        golden_i_center = 0.36
        i_attraction = (golden_i_center - i) * 0.1

        d_new = d + lr * grad_d
        p_new = p + lr * grad_p
        i_new = i + lr * grad_i + lr * i_attraction

        d = np.clip(d_new, 0.05, 0.95)
        p = np.clip(p_new, 0.10, 0.95)
        i = np.clip(i_new, 0.05, 0.95)

    # Trajectory visualization
    print()
    print("─" * 70)
    print("  [ Search Trajectory ]")
    print("─" * 70)

    # Inhibition trajectory
    print()
    print("  Inhibition trajectory (Golden Zone = 0.24~0.48):")
    for h in history:
        pos = int(h['i'] / 1.0 * 60)
        golden_lo = int(0.24 * 60)
        golden_hi = int(0.48 * 60)
        line = list("·" * 61)
        for gi in range(golden_lo, golden_hi + 1):
            line[gi] = "░"
        marker = "🎯" if h['n_agree'] == 3 else ("⚡" if h['n_agree'] == 2 else "○")
        if pos < len(line):
            line[pos] = "●"
        print(f"    {h['iter']:>3} │{''.join(line)}│ I={h['i']:.2f} {marker}")
    print(f"        {'':>1}{'0.0':.<20}{'0.24':.<14}{'0.48':.<14}{'1.0'}")
    print(f"        {'':>1}{'':>20}└─ Golden Zone ─┘")

    # Compass Score trajectory
    print()
    print("  Compass Score trajectory:")
    for h in history:
        bar_len = int(h['compass_score'] * 50)
        bar = "█" * bar_len + "░" * (50 - bar_len)
        marker = "🎯" if h['n_agree'] == 3 else ""
        print(f"    {h['iter']:>3} │{bar}│ {h['compass_score']*100:5.1f}% {marker}")

    # Summary report
    print()
    print("─" * 70)
    print("  [ Summary Report ]")
    print("─" * 70)
    print(f"    Total iterations      : {len(history)}")
    print(f"    Golden Zone hits      : {golden_zone_hits}")
    print(f"    Final parameters      : D={d:.2f} / P={p:.2f} / I={i:.2f}")

    if history:
        best = max(history, key=lambda x: x['compass_score'])
        print(f"    Best Compass Score    : {best['compass_score']*100:.1f}% (iter {best['iter']})")
        print(f"    Best parameters       : D={best['d']:.2f} / P={best['p']:.2f} / I={best['i']:.2f}")

    first = history[0]
    last = history[-1]
    print()
    print(f"    Start → End:")
    print(f"      D: {first['d']:.2f} → {last['d']:.2f}  ({'+' if last['d']>first['d'] else ''}{last['d']-first['d']:.2f})")
    print(f"      P: {first['p']:.2f} → {last['p']:.2f}  ({'+' if last['p']>first['p'] else ''}{last['p']-first['p']:.2f})")
    print(f"      I: {first['i']:.2f} → {last['i']:.2f}  ({'+' if last['i']>first['i'] else ''}{last['i']-first['i']:.2f})")
    print(f"      Compass: {first['compass_score']*100:.1f}% → {last['compass_score']*100:.1f}%")

    print()
    print("═" * 70)

    # Save log
    os.makedirs(RESULTS_DIR, exist_ok=True)
    pilot_file = os.path.join(RESULTS_DIR, "autopilot_log.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(pilot_file, 'a', encoding='utf-8') as f:
        f.write(f"# 🚀 Autopilot Search [{now}]\n\n")
        f.write(f"Initial: D={d0:.2f} / P={p0:.2f} / I={i0:.2f} → Final: D={d:.2f} / P={p:.2f} / I={i:.2f}\n\n")
        f.write(f"| Iter | D | P | I | Z-Score | Compass | Agreement |\n|---|---|---|---|---|---|---|\n")
        for h in history:
            agree_label = "🎯" if h['n_agree'] == 3 else ("⚡" if h['n_agree'] == 2 else "○")
            f.write(f"| {h['iter']} | {h['d']:.2f} | {h['p']:.2f} | {h['i']:.2f} | {h['z']:.2f}σ | {h['compass_score']*100:.1f}% | {agree_label} |\n")
        f.write(f"\nGolden Zone hits: {golden_zone_hits} times\n\n---\n\n")

    print(f"  📁 Search log → results/autopilot_log.md")
    print()


def main():
    parser = argparse.ArgumentParser(description="SingularityNet Architecture Compass")
    parser.add_argument('--deficit', type=float, default=0.7, help="Structural deficit (Dropout Rate)")
    parser.add_argument('--plasticity', type=float, default=0.8, help="Neuroplasticity (Learning Rate coefficient)")
    parser.add_argument('--inhibition', type=float, default=0.15, help="Inhibition level (Gating strength)")
    parser.add_argument('--convergence', action='store_true', help="Search for 3-model common singularity regions")
    parser.add_argument('--autopilot', action='store_true', help="Automatic iterative hypothesis search")
    parser.add_argument('--iterations', type=int, default=30, help="Autopilot maximum iterations")
    parser.add_argument('--lr', type=float, default=0.15, help="Autopilot learning rate")
    parser.add_argument('--grid', type=int, default=20, help="Grid resolution")
    parser.add_argument('--samples', type=int, default=50000, help="Population sample count")
    args = parser.parse_args()

    if args.convergence:
        run_convergence_scan(args.grid, args.samples)
        return

    if args.autopilot:
        run_autopilot(args.deficit, args.plasticity, args.inhibition,
                      args.iterations, args.lr, args.samples)
        return

    d = np.clip(args.deficit, 0.01, 0.99)
    p = np.clip(args.plasticity, 0.01, 0.99)
    i = np.clip(args.inhibition, 0.01, 0.99)

    # ── Run 3 models ──
    score = genius_score(d, p, i)
    z, pop_mean, pop_std = population_zscore(score)
    cusp = cusp_analysis(d, i)
    boltz = boltzmann_analysis(d, p, i)
    compass = compass_direction(score, z, cusp, boltz)

    # ── Output ──
    print()
    print("═" * 60)
    print("   🧭 SingularityNet Architecture Compass")
    print("═" * 60)

    # Input
    print()
    print(f"  Input (AI Architecture Mapping):")
    print(f"    Deficit     = {d:.2f}  → Dropout Rate")
    print(f"    Plasticity  = {p:.2f}  → Learning Rate coefficient")
    print(f"    Inhibition  = {i:.2f}  → Gating strength")

    # Model 1: Our model
    print()
    print("─" * 60)
    print("  📊 Model 1: Current Score (Our Model)")
    print("─" * 60)
    print(f"    Genius Score = {score:.2f}")
    print(f"    Z-Score      = {z:.2f}σ  {'⚡ Singularity!' if abs(z) > 2 else '○ Normal'}")
    print(f"    Percentile   = Top {(1-stats.norm.cdf(z))*100:.4f}%")

    # Model 2: Cusp catastrophe
    print()
    print("─" * 60)
    print("  📐 Model 2: Critical Point Analysis (Cusp Catastrophe)")
    print("─" * 60)
    print(f"    Control variables  a={cusp['a']:.2f}, b={cusp['b']:.2f}")
    print(f"    Bifurcation disc.  = {cusp['bifurcation']:.4f}")
    print(f"    Critical distance  = {cusp['distance_to_critical']:.4f}")
    print(f"    Equilibrium count  = {cusp['n_equilibria']} {'(Bistable → Transition possible!)' if cusp['is_bistable'] else '(Single stable)'}")
    print(f"    Transition direction = {cusp['direction']}")

    # Model 3: Boltzmann
    print()
    print("─" * 60)
    print("  🌡️ Model 3: Transition Probability (Boltzmann Distribution)")
    print("─" * 60)
    print(f"    Temperature T  = {boltz['temperature']:.2f} (= 1/Inhibition)")
    print(f"    ────────────────────────────────────")
    print(f"    Normal state   = {boltz['p_normal']*100:5.1f}%  E={boltz['E_normal']:.2f}")
    print(f"    Genius state   = {boltz['p_genius']*100:5.1f}%  E={boltz['E_genius']:.2f}")
    print(f"    Decline state  = {boltz['p_decline']*100:5.1f}%  E={boltz['E_decline']:.2f}")
    print(f"    ────────────────────────────────────")
    print(f"    Free energy    = {boltz['free_energy']:.4f}")
    print(f"    Entropy        = {boltz['entropy']:.4f}")

    # Compass
    print()
    print("─" * 60)
    print("  🧭 Compass — Integrated Design Direction")
    print("─" * 60)
    print()
    print(draw_compass(
        compass['compass_score'],
        cusp['direction_sign'],
        boltz['p_genius'],
        cusp['distance_to_critical'],
    ))

    # Recommendations
    print()
    print("─" * 60)
    print("  📋 Architecture Design Recommendations")
    print("─" * 60)
    for area, rec, grade in compass['recommendations']:
        print(f"    [{grade:^5}] {area:12} │ {rec}")

    if compass['warnings']:
        print()
        for w in compass['warnings']:
            print(f"    ⚠️  {w}")

    # AI architecture mapping summary
    print()
    print("─" * 60)
    print("  🔧 Specific Design Parameters")
    print("─" * 60)
    print(f"    Dropout Rate      = {d:.0%}")
    print(f"    Learning Rate     × {boltz['temperature']:.1f} (Boltzmann temperature)")
    print(f"    MoE Active Ratio  = {compass['optimal_active_ratio']:.0%}")
    print(f"    64 experts → Active {int(64*compass['optimal_active_ratio'])} experts")
    print(f"    Structure trigger = Loss 2nd derivative > {1/max(cusp['distance_to_critical'],0.01):.1f}")

    print()
    print("═" * 60)

    # Log
    save_compass_log(d, p, i, score, z, cusp, boltz, compass)
    print(f"  📁 Compass log → results/compass_log.md")
    print()


if __name__ == '__main__':
    main()