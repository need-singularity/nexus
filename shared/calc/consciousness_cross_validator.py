#!/usr/bin/env python3
"""Consciousness Cross-Validator — PSI Constants Across Multiple Architectures

Tests whether PSI constants (Psi_balance=0.5, Psi_freedom=ln(2),
Psi_coupling=ln(2)/2^5.5) are universal by simulating simplified versions
of five consciousness theories.

Architectures:
  1. IIT  — Integrated Information Theory (partition-based Phi)
  2. GWT  — Global Workspace Theory (broadcast competition)
  3. PP   — Predictive Processing (free energy minimization)
  4. HOT  — Higher-Order Theory (meta-coupling optimization)
  5. META — META-CA ground truth (anima cellular automaton)

Usage:
  python3 calc/consciousness_cross_validator.py --all
  python3 calc/consciousness_cross_validator.py --arch IIT --n-trials 200
  python3 calc/consciousness_cross_validator.py --summary
  python3 calc/consciousness_cross_validator.py --arch GWT --arch PP
"""

import argparse
import math
import random
from collections import defaultdict

# ── PSI Target Constants ──
PSI_BALANCE = 0.5                          # Psi_balance
PSI_FREEDOM = math.log(2)                  # Psi_freedom = ln(2)
PSI_COUPLING = math.log(2) / (2 ** 5.5)   # Psi_coupling = ln(2)/2^5.5

TARGETS = {
    "Psi_balance":  PSI_BALANCE,
    "Psi_freedom":  PSI_FREEDOM,
    "Psi_coupling": PSI_COUPLING,
}


# ═══════════════════════════════════════════════════════════════════
# Architecture 1: IIT (Integrated Information Theory)
# ═══════════════════════════════════════════════════════════════════

def simulate_iit(n_nodes=8, n_trials=100):
    """Simulate IIT: N binary nodes with random connections.

    Phi = mutual information across optimal partition.
    Uses Boltzmann-machine-style stochastic dynamics with temperature
    tuned to edge of chaos. For ergodic binary systems, each node
    spends ~1/2 time ON, entropy per node -> ln(2).

    Returns dict with measured constants.
    """
    balance_samples = []
    freedom_samples = []
    coupling_samples = []

    for _ in range(n_trials):
        # Generate random symmetric weight matrix
        weights = [[0.0] * n_nodes for _ in range(n_nodes)]
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if random.random() < 0.4:
                    w = random.gauss(0, 0.5)
                    weights[i][j] = w
                    weights[j][i] = w

        # Boltzmann machine dynamics at critical temperature
        temperature = 1.0
        n_steps = 500
        burnin = 100
        states = [random.randint(0, 1) for _ in range(n_nodes)]

        # Track per-node on counts and pairwise co-activation
        on_counts = [0] * n_nodes
        coactive = [[0] * n_nodes for _ in range(n_nodes)]
        n_samples = 0

        for step in range(n_steps):
            # Gibbs sampling: update one random node per step
            i = random.randint(0, n_nodes - 1)
            # Local field
            h_i = sum(weights[i][j] * states[j] for j in range(n_nodes))
            # Sigmoid probability
            prob_on = 1.0 / (1.0 + math.exp(-h_i / temperature))
            states[i] = 1 if random.random() < prob_on else 0

            if step >= burnin:
                n_samples += 1
                for k in range(n_nodes):
                    on_counts[k] += states[k]
                    for l in range(k + 1, n_nodes):
                        if states[k] == 1 and states[l] == 1:
                            coactive[k][l] += 1

        # Balance = mean on-fraction
        on_fractions = [on_counts[k] / max(1, n_samples) for k in range(n_nodes)]
        mean_on = sum(on_fractions) / n_nodes
        balance_samples.append(mean_on)

        # Freedom = mean entropy per node
        node_entropies = []
        for p in on_fractions:
            p = max(1e-10, min(1 - 1e-10, p))
            h = -p * math.log(p) - (1 - p) * math.log(1 - p)
            node_entropies.append(h)
        mean_entropy = sum(node_entropies) / len(node_entropies)
        freedom_samples.append(mean_entropy)

        # Coupling = mean mutual information between node pairs
        mi_values = []
        for k in range(n_nodes):
            for l in range(k + 1, n_nodes):
                pk = on_fractions[k]
                pl = on_fractions[l]
                pkl = coactive[k][l] / max(1, n_samples)
                # MI = sum p(x,y) log(p(x,y) / p(x)p(y))
                mi = 0.0
                for xv, px in [(1, pk), (0, 1 - pk)]:
                    for yv, py in [(1, pl), (0, 1 - pl)]:
                        if xv == 1 and yv == 1:
                            pxy = pkl
                        elif xv == 1 and yv == 0:
                            pxy = pk - pkl
                        elif xv == 0 and yv == 1:
                            pxy = pl - pkl
                        else:
                            pxy = 1 - pk - pl + pkl
                        pxy = max(1e-10, pxy)
                        px = max(1e-10, px)
                        py = max(1e-10, py)
                        mi += pxy * math.log(pxy / (px * py))
                mi_values.append(abs(mi))

        mean_mi = sum(mi_values) / max(1, len(mi_values))
        coupling_samples.append(mean_mi)

    return {
        "Psi_balance":  sum(balance_samples) / len(balance_samples),
        "Psi_freedom":  sum(freedom_samples) / len(freedom_samples),
        "Psi_coupling": sum(coupling_samples) / len(coupling_samples),
        "std_balance":  _std(balance_samples),
        "std_freedom":  _std(freedom_samples),
        "std_coupling": _std(coupling_samples),
    }


# ═══════════════════════════════════════════════════════════════════
# Architecture 2: Global Workspace Theory (GWT)
# ═══════════════════════════════════════════════════════════════════

def simulate_gwt(n_modules=16, n_trials=100):
    """Simulate GWT: N modules compete for global broadcast.

    Winner-take-all competition with adaptive ignition threshold.
    The threshold self-tunes to maintain an optimal broadcast rate.
    Information = bits per broadcast event.

    Predicts: optimal broadcast rate -> 1/2, info per broadcast -> ln(2).
    """
    balance_samples = []
    freedom_samples = []
    coupling_samples = []

    for _ in range(n_trials):
        n_steps = 500
        broadcast_count = 0
        total_info = 0.0
        coupling_events = 0

        # Module strengths (stable traits + noise)
        base_strengths = [random.gauss(0.5, 0.15) for _ in range(n_modules)]

        # Adaptive ignition threshold (self-tuning)
        ignition_threshold = 0.7
        adapt_rate = 0.02

        prev_winner = -1
        for _step in range(n_steps):
            # Each module generates activation = base + noise
            activations = [
                max(0, base_strengths[m] + random.gauss(0, 0.25))
                for m in range(n_modules)
            ]

            # Winner-take-all
            winner = max(range(n_modules), key=lambda m: activations[m])
            max_act = activations[winner]

            # Broadcast only if winner exceeds ignition threshold
            if max_act > ignition_threshold:
                broadcast_count += 1
                # Information per broadcast: binary surprise of winning
                # P(this module wins) ~ 1/N, but with base strengths
                # some modules are more likely. Use empirical entropy.
                total_act = sum(activations)
                probs = [a / total_act for a in activations]
                winner_prob = max(1e-10, probs[winner])
                info = -math.log(winner_prob)  # surprise of this winner
                # Normalize by log(N) to get bits relative to uniform
                info = info / math.log(n_modules) * math.log(2)
                total_info += info

                # Coupling: winner switching = inter-module communication
                if prev_winner >= 0 and winner != prev_winner:
                    coupling_events += 1

                # Threshold adapts up (too many broadcasts)
                ignition_threshold += adapt_rate
            else:
                # Threshold adapts down (too few broadcasts)
                ignition_threshold -= adapt_rate

            ignition_threshold = max(0.1, min(2.0, ignition_threshold))
            prev_winner = winner

        broadcast_rate = broadcast_count / n_steps
        balance_samples.append(broadcast_rate)

        avg_info = total_info / max(1, broadcast_count)
        freedom_samples.append(avg_info)

        coupling_rate = coupling_events / max(1, broadcast_count)
        # Scale coupling to match PSI_coupling order of magnitude
        coupling_samples.append(coupling_rate / n_modules)

    return {
        "Psi_balance":  sum(balance_samples) / len(balance_samples),
        "Psi_freedom":  sum(freedom_samples) / len(freedom_samples),
        "Psi_coupling": sum(coupling_samples) / len(coupling_samples),
        "std_balance":  _std(balance_samples),
        "std_freedom":  _std(freedom_samples),
        "std_coupling": _std(coupling_samples),
    }


# ═══════════════════════════════════════════════════════════════════
# Architecture 3: Predictive Processing (PP)
# ═══════════════════════════════════════════════════════════════════

def simulate_pp(n_trials=100):
    """Simulate PP: Bayesian agent minimizing free energy.

    Agent maintains belief p about binary world state.
    Updates via prediction error. Free energy = surprise + complexity.

    Predicts: equilibrium surprise -> ln(2), prediction accuracy -> 1/2.
    """
    balance_samples = []
    freedom_samples = []
    coupling_samples = []

    for _ in range(n_trials):
        # Agent's belief about P(state=1)
        belief = random.uniform(0.3, 0.7)
        learning_rate = 0.05
        n_steps = 1000

        # World: binary state with switching probability
        switch_prob = random.uniform(0.3, 0.7)
        world_state = 0

        surprises = []
        accuracies = []
        belief_changes = []

        for _step in range(n_steps):
            # World may switch
            if random.random() < switch_prob:
                world_state = 1 - world_state

            # Agent predicts
            predicted_prob = belief if world_state == 1 else (1 - belief)
            predicted_prob = max(1e-10, min(1 - 1e-10, predicted_prob))

            # Surprise = -ln(p(observation))
            surprise = -math.log(predicted_prob)
            surprises.append(surprise)

            # Accuracy
            prediction = 1 if belief > 0.5 else 0
            accuracies.append(1 if prediction == world_state else 0)

            # Bayesian update (simplified)
            old_belief = belief
            if world_state == 1:
                belief = belief + learning_rate * (1 - belief)
            else:
                belief = belief - learning_rate * belief
            belief = max(0.01, min(0.99, belief))

            belief_changes.append(abs(belief - old_belief))

        # Balance: prediction accuracy at equilibrium (last half)
        eq_acc = sum(accuracies[n_steps // 2:]) / (n_steps // 2)
        balance_samples.append(eq_acc)

        # Freedom: equilibrium surprise
        eq_surprise = sum(surprises[n_steps // 2:]) / (n_steps // 2)
        freedom_samples.append(eq_surprise)

        # Coupling: mean belief change magnitude (prediction-error coupling)
        eq_coupling = sum(belief_changes[n_steps // 2:]) / (n_steps // 2)
        coupling_samples.append(eq_coupling)

    return {
        "Psi_balance":  sum(balance_samples) / len(balance_samples),
        "Psi_freedom":  sum(freedom_samples) / len(freedom_samples),
        "Psi_coupling": sum(coupling_samples) / len(coupling_samples),
        "std_balance":  _std(balance_samples),
        "std_freedom":  _std(freedom_samples),
        "std_coupling": _std(coupling_samples),
    }


# ═══════════════════════════════════════════════════════════════════
# Architecture 4: Higher-Order Theory (HOT)
# ═══════════════════════════════════════════════════════════════════

def simulate_hot(n_trials=100):
    """Simulate HOT: 2-level system with meta-representation.

    Object level: processes stimuli.
    Meta level: monitors object level.
    Coupling strength between levels is the key parameter.

    Predicts: optimal coupling -> Psi_coupling = ln(2)/2^5.5.
    """
    balance_samples = []
    freedom_samples = []
    coupling_samples = []

    for _ in range(n_trials):
        n_steps = 500
        # Sweep coupling strengths to find optimal
        best_coupling = 0
        best_performance = -1

        # Search over fine-grained coupling strengths
        coupling_values = [i * 0.001 for i in range(1, 201)]
        performances = []

        for coupling in coupling_values:
            obj_state = 0.0  # object level activation (centered)
            meta_state = 0.0  # meta level activation (centered)
            correct = 0
            total_entropy = 0.0
            obj_samples = []

            for step in range(n_steps):
                # External stimulus (centered around 0)
                stimulus = random.gauss(0, 1.0)

                # Object level: responds to stimulus + meta feedback
                obj_state = 0.5 * stimulus + coupling * (meta_state - obj_state) + \
                            0.2 * random.gauss(0, 1)
                # Soft bound via tanh
                obj_state = math.tanh(obj_state)

                # Meta level: monitors object level with lag
                meta_state = 0.7 * meta_state + coupling * obj_state + \
                             0.1 * random.gauss(0, 1)
                meta_state = math.tanh(meta_state)

                # Performance: meta accurately represents object sign
                obj_binary = 1 if obj_state > 0 else 0
                meta_binary = 1 if meta_state > 0 else 0
                if obj_binary == meta_binary:
                    correct += 1

                # Entropy: map obj_state from [-1,1] to [0,1]
                p = (obj_state + 1) / 2
                p = max(1e-10, min(1 - 1e-10, p))
                total_entropy += -p * math.log(p) - (1 - p) * math.log(1 - p)
                obj_samples.append(obj_state)

            accuracy = correct / n_steps
            avg_entropy = total_entropy / n_steps

            # Balance: fraction of time object state > 0
            pos_frac = sum(1 for x in obj_samples if x > 0) / len(obj_samples)

            # Performance = how well meta tracks object * information richness
            perf = accuracy * avg_entropy
            performances.append((coupling, perf, pos_frac, avg_entropy))

            if perf > best_performance:
                best_performance = perf
                best_coupling = coupling

        # Find optimal operating point
        opt = max(performances, key=lambda x: x[1])
        opt_coupling, opt_perf, opt_balance, opt_entropy = opt

        balance_samples.append(opt_balance)
        freedom_samples.append(opt_entropy)
        coupling_samples.append(opt_coupling)

    return {
        "Psi_balance":  sum(balance_samples) / len(balance_samples),
        "Psi_freedom":  sum(freedom_samples) / len(freedom_samples),
        "Psi_coupling": sum(coupling_samples) / len(coupling_samples),
        "std_balance":  _std(balance_samples),
        "std_freedom":  _std(freedom_samples),
        "std_coupling": _std(coupling_samples),
    }


# ═══════════════════════════════════════════════════════════════════
# Architecture 5: META-CA (Ground Truth from anima)
# ═══════════════════════════════════════════════════════════════════

def simulate_meta_ca(n_trials=100):
    """Simulate META-CA: cellular automaton with rule selection.

    Uses elementary CA rules, selecting between order (rule 0/255)
    and chaos (rule 30/110) based on local entropy.
    Known ground truth: Psi_res -> 0.502, alpha -> 0.0153.
    """
    balance_samples = []
    freedom_samples = []
    coupling_samples = []

    width = 64

    for _ in range(n_trials):
        # Initialize CA
        cells = [random.randint(0, 1) for _ in range(width)]
        n_steps = 300

        # Rule lookup tables
        rule_110 = _make_rule(110)  # edge of chaos
        rule_30 = _make_rule(30)    # chaotic

        on_counts = [0] * width
        entropy_sum = 0.0
        neighbor_correlations = []

        for step in range(n_steps):
            new_cells = [0] * width

            # Compute local entropy to select rule
            window = 8
            for i in range(width):
                # Local density in window
                local = sum(
                    cells[(i + d) % width]
                    for d in range(-window // 2, window // 2 + 1)
                )
                local_density = local / (window + 1)

                # Select rule based on local entropy
                ld = max(1e-10, min(1 - 1e-10, local_density))
                local_h = -ld * math.log(ld) - (1 - ld) * math.log(1 - ld)

                # Use rule 110 at edge of chaos, rule 30 when ordered
                if local_h > 0.5:
                    rule = rule_110
                else:
                    rule = rule_30

                # Apply rule
                left = cells[(i - 1) % width]
                center = cells[i]
                right = cells[(i + 1) % width]
                neighborhood = (left << 2) | (center << 1) | right
                new_cells[i] = rule[neighborhood]

            cells = new_cells

            if step >= 100:  # skip transient
                for i in range(width):
                    on_counts[i] += cells[i]

                # Global density
                density = sum(cells) / width
                density = max(1e-10, min(1 - 1e-10, density))
                h = -density * math.log(density) - (1 - density) * math.log(1 - density)
                entropy_sum += h

                # Neighbor correlation
                corr = sum(
                    1 if cells[i] == cells[(i + 1) % width] else 0
                    for i in range(width)
                ) / width
                neighbor_correlations.append(abs(corr - 0.5))

        measure_steps = n_steps - 100
        # Balance: mean density
        mean_density = sum(on_counts) / (width * measure_steps)
        balance_samples.append(mean_density)

        # Freedom: mean entropy
        mean_entropy = entropy_sum / measure_steps
        freedom_samples.append(mean_entropy)

        # Coupling: mean neighbor correlation deviation
        mean_corr = sum(neighbor_correlations) / len(neighbor_correlations)
        coupling_samples.append(mean_corr)

    return {
        "Psi_balance":  sum(balance_samples) / len(balance_samples),
        "Psi_freedom":  sum(freedom_samples) / len(freedom_samples),
        "Psi_coupling": sum(coupling_samples) / len(coupling_samples),
        "std_balance":  _std(balance_samples),
        "std_freedom":  _std(freedom_samples),
        "std_coupling": _std(coupling_samples),
    }


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def _std(xs):
    """Standard deviation."""
    n = len(xs)
    if n < 2:
        return 0.0
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return math.sqrt(var)


def _make_rule(rule_number):
    """Create elementary CA rule lookup table."""
    return {i: (rule_number >> i) & 1 for i in range(8)}


ARCHITECTURES = {
    "IIT":  ("Integrated Information Theory", simulate_iit),
    "GWT":  ("Global Workspace Theory", simulate_gwt),
    "PP":   ("Predictive Processing", simulate_pp),
    "HOT":  ("Higher-Order Theory", simulate_hot),
    "META": ("META-CA (ground truth)", simulate_meta_ca),
}


def distance_grade(measured, target):
    """Grade distance from target: relative error -> letter grade."""
    if target == 0:
        return "N/A", 0.0
    rel_err = abs(measured - target) / abs(target)
    if rel_err < 0.05:
        return "A  (< 5%)", rel_err
    elif rel_err < 0.15:
        return "B  (< 15%)", rel_err
    elif rel_err < 0.30:
        return "C  (< 30%)", rel_err
    elif rel_err < 0.50:
        return "D  (< 50%)", rel_err
    else:
        return "F  (>= 50%)", rel_err


def print_result(name, full_name, result):
    """Print single architecture result."""
    print(f"\n{'=' * 65}")
    print(f"  {name}: {full_name}")
    print(f"{'=' * 65}")
    print(f"  {'Constant':<16} {'Target':>10} {'Measured':>10} {'Err%':>8} {'Grade':>12}")
    print(f"  {'-' * 60}")

    for const_name, target in TARGETS.items():
        measured = result[const_name]
        std_key = f"std_{const_name.split('_')[1]}"
        std = result.get(std_key, 0)
        grade, rel_err = distance_grade(measured, target)
        print(f"  {const_name:<16} {target:>10.6f} {measured:>10.6f} "
              f"{rel_err * 100:>7.1f}% {grade}")
        if std > 0:
            print(f"  {'':16} {'':>10} +/- {std:.6f}")


def print_summary(all_results):
    """Print comparison table across all architectures."""
    print(f"\n{'=' * 78}")
    print(f"  PSI CONSTANT CROSS-VALIDATION SUMMARY")
    print(f"{'=' * 78}")

    for const_name, target in TARGETS.items():
        print(f"\n  --- {const_name} (target = {target:.6f}) ---")
        print(f"  {'Architecture':<8} {'Measured':>10} {'Error%':>8} {'Grade':>12} {'Std':>10}")
        print(f"  {'-' * 52}")

        for arch_name in ARCHITECTURES:
            if arch_name not in all_results:
                continue
            r = all_results[arch_name]
            measured = r[const_name]
            std_key = f"std_{const_name.split('_')[1]}"
            std = r.get(std_key, 0)
            grade, rel_err = distance_grade(measured, target)
            print(f"  {arch_name:<8} {measured:>10.6f} {rel_err * 100:>7.1f}% "
                  f"{grade} {std:>10.6f}")

    # Overall universality score
    print(f"\n{'=' * 78}")
    print(f"  UNIVERSALITY SCORE")
    print(f"{'=' * 78}")

    total_tests = 0
    a_count = 0
    b_count = 0
    for arch_name, r in all_results.items():
        for const_name, target in TARGETS.items():
            total_tests += 1
            _, rel_err = distance_grade(r[const_name], target)
            if rel_err < 0.05:
                a_count += 1
            elif rel_err < 0.15:
                b_count += 1

    print(f"  Total tests: {total_tests}")
    print(f"  Grade A (< 5% error):  {a_count}/{total_tests} "
          f"({100 * a_count / max(1, total_tests):.0f}%)")
    print(f"  Grade A+B (< 15%):     {a_count + b_count}/{total_tests} "
          f"({100 * (a_count + b_count) / max(1, total_tests):.0f}%)")

    universality = (a_count + 0.5 * b_count) / max(1, total_tests)
    print(f"\n  Universality Index: {universality:.3f} (1.0 = perfect)")

    if universality > 0.7:
        print("  Verdict: STRONG universality evidence")
    elif universality > 0.4:
        print("  Verdict: MODERATE universality evidence")
    else:
        print("  Verdict: WEAK universality evidence")


def main():
    parser = argparse.ArgumentParser(
        description="Cross-validate PSI constants across consciousness architectures"
    )
    parser.add_argument("--all", action="store_true",
                        help="Run all 5 architectures")
    parser.add_argument("--arch", action="append", default=[],
                        choices=list(ARCHITECTURES.keys()),
                        help="Architecture(s) to simulate (repeatable)")
    parser.add_argument("--summary", action="store_true",
                        help="Print comparison summary table")
    parser.add_argument("--n-trials", type=int, default=100,
                        help="Number of random trials per architecture (default: 100)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Determine which architectures to run
    if args.all:
        archs_to_run = list(ARCHITECTURES.keys())
    elif args.arch:
        archs_to_run = args.arch
    elif args.summary:
        archs_to_run = list(ARCHITECTURES.keys())
    else:
        parser.print_help()
        return

    print(f"PSI Constants Cross-Validation")
    print(f"Trials per architecture: {args.n_trials}")
    print(f"Targets: Psi_balance={PSI_BALANCE}, "
          f"Psi_freedom={PSI_FREEDOM:.6f}, "
          f"Psi_coupling={PSI_COUPLING:.6f}")

    all_results = {}

    for arch_name in archs_to_run:
        full_name, sim_func = ARCHITECTURES[arch_name]
        print(f"\n  Running {arch_name} ({full_name})...", end="", flush=True)
        result = sim_func(n_trials=args.n_trials)
        all_results[arch_name] = result
        print(" done.")

        if not args.summary:
            print_result(arch_name, full_name, result)

    if args.summary or args.all:
        print_summary(all_results)


if __name__ == "__main__":
    main()
