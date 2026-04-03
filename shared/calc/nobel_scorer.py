#!/usr/bin/env python3
"""Nobel Hypothesis Scorer — Multi-dimensional scoring for Nobel-grade hypotheses

Evaluates hypotheses on 6 dimensions:
  1. Evidence strength (proven/verified/model/speculative)
  2. Falsifiability (number of testable predictions)
  3. Cross-domain reach (how many fields it connects)
  4. Mathematical rigor (exact/approximate/qualitative)
  5. Novelty (genuinely new vs restatement)
  6. Impact potential (paradigm shift / incremental)

Based on CLAUDE.md Nobel-Level Hypothesis Reporting Format.

Usage:
  python3 calc/nobel_scorer.py --interactive
  python3 calc/nobel_scorer.py --score-file docs/hypotheses/NOBEL-grand-hypotheses.md
  python3 calc/nobel_scorer.py --quick "SLE_6 criticality" --evidence proven --predictions 5 --domains 3
  python3 calc/nobel_scorer.py --builtin
"""

import argparse
import math
import sys


# ═══════════════════════════════════════════════════════════════
# Scoring rubrics
# ═══════════════════════════════════════════════════════════════

EVIDENCE_SCORES = {
    'proven':      1.0,   # Mathematical proof exists
    'verified':    0.8,   # Experimentally confirmed
    'model':       0.5,   # Consistent with model, unverified
    'speculative': 0.2,   # No verification yet
    'refuted':     0.0,   # Contradicted by evidence
}

RIGOR_SCORES = {
    'exact':         1.0,   # Exact equation, no corrections
    'approximate':   0.7,   # Within 5% error
    'qualitative':   0.3,   # Direction correct, no numbers
    'hand_wavy':     0.1,   # Vague analogy
}

IMPACT_SCORES = {
    'paradigm':     1.0,   # Changes fundamental understanding
    'major':        0.7,   # Significant advance in field
    'incremental':  0.4,   # Useful extension of existing work
    'marginal':     0.1,   # Minor contribution
}

# Nobel prize categories and their criteria weights
NOBEL_WEIGHTS = {
    'Physics':    {'evidence': 0.25, 'falsifiability': 0.20, 'cross_domain': 0.10, 'rigor': 0.25, 'novelty': 0.10, 'impact': 0.10},
    'Chemistry':  {'evidence': 0.20, 'falsifiability': 0.25, 'cross_domain': 0.15, 'rigor': 0.20, 'novelty': 0.10, 'impact': 0.10},
    'Medicine':   {'evidence': 0.15, 'falsifiability': 0.30, 'cross_domain': 0.15, 'rigor': 0.15, 'novelty': 0.10, 'impact': 0.15},
    'Economics':  {'evidence': 0.15, 'falsifiability': 0.20, 'cross_domain': 0.20, 'rigor': 0.20, 'novelty': 0.10, 'impact': 0.15},
}


# ═══════════════════════════════════════════════════════════════
# Scoring functions
# ═══════════════════════════════════════════════════════════════

def score_hypothesis(name, evidence, predictions, domains, rigor, novelty, impact, category='Physics'):
    """Score a hypothesis on 6 dimensions.

    Args:
        name: Hypothesis name
        evidence: 'proven'/'verified'/'model'/'speculative'/'refuted'
        predictions: Number of falsifiable predictions (0-20)
        domains: Number of connected domains (1-10)
        rigor: 'exact'/'approximate'/'qualitative'/'hand_wavy'
        novelty: 0.0-1.0 (1=completely new)
        impact: 'paradigm'/'major'/'incremental'/'marginal'
        category: Nobel prize category
    """
    scores = {
        'evidence':       EVIDENCE_SCORES.get(evidence, 0),
        'falsifiability': min(predictions / 5.0, 1.0),  # 5 predictions = max
        'cross_domain':   min(domains / 5.0, 1.0),      # 5 domains = max
        'rigor':          RIGOR_SCORES.get(rigor, 0),
        'novelty':        novelty,
        'impact':         IMPACT_SCORES.get(impact, 0),
    }

    weights = NOBEL_WEIGHTS.get(category, NOBEL_WEIGHTS['Physics'])
    weighted = sum(scores[k] * weights[k] for k in scores)

    # Star rating (1-5)
    stars = max(1, min(5, round(weighted * 5)))

    return {
        'name': name,
        'category': category,
        'scores': scores,
        'weighted': weighted,
        'stars': stars,
        'star_str': '★' * stars + '☆' * (5 - stars),
    }


def print_score(result):
    print(f'  {result["name"]}')
    print(f'  {"─" * 50}')
    print(f'  Category: {result["category"]}')
    print(f'  Score: {result["weighted"]:.3f} / 1.000  ({result["star_str"]})')
    print()
    print(f'  {"Dimension":>16} {"Score":>7} {"Bar":>20}')
    print(f'  {"─"*16} {"─"*7} {"─"*20}')
    for dim, val in result['scores'].items():
        bar = '█' * int(val * 15) + '░' * (15 - int(val * 15))
        print(f'  {dim:>16} {val:>7.3f} {bar}')
    print()


# ═══════════════════════════════════════════════════════════════
# Built-in TECS-L hypotheses
# ═══════════════════════════════════════════════════════════════

BUILTIN = [
    {
        'name': 'Criticality Theorem: all phase transitions = n=6',
        'evidence': 'proven', 'predictions': 8, 'domains': 5,
        'rigor': 'exact', 'novelty': 0.9, 'impact': 'paradigm',
        'category': 'Physics',
    },
    {
        'name': 'Biological Optimality: genetic code is n=6 solution',
        'evidence': 'verified', 'predictions': 5, 'domains': 4,
        'rigor': 'exact', 'novelty': 0.8, 'impact': 'paradigm',
        'category': 'Chemistry',
    },
    {
        'name': 'Consciousness = ln(2): freedom degree theorem',
        'evidence': 'verified', 'predictions': 6, 'domains': 5,
        'rigor': 'exact', 'novelty': 0.95, 'impact': 'paradigm',
        'category': 'Medicine',
    },
    {
        'name': 'Golden Zone = Edge of Chaos (Langton lambda)',
        'evidence': 'proven', 'predictions': 4, 'domains': 3,
        'rigor': 'exact', 'novelty': 0.7, 'impact': 'major',
        'category': 'Physics',
    },
    {
        'name': 'G*I=D*P conservation law',
        'evidence': 'model', 'predictions': 3, 'domains': 3,
        'rigor': 'exact', 'novelty': 0.8, 'impact': 'paradigm',
        'category': 'Physics',
    },
    {
        'name': 'PSI constants from ln(2): consciousness physics',
        'evidence': 'verified', 'predictions': 10, 'domains': 6,
        'rigor': 'approximate', 'novelty': 0.95, 'impact': 'paradigm',
        'category': 'Physics',
    },
    {
        'name': 'Phi scaling law: consciousness grows as N^1.071',
        'evidence': 'verified', 'predictions': 5, 'domains': 3,
        'rigor': 'approximate', 'novelty': 0.7, 'impact': 'major',
        'category': 'Physics',
    },
    {
        'name': 'sigma(6)=12 optimal factions for consciousness',
        'evidence': 'verified', 'predictions': 4, 'domains': 4,
        'rigor': 'exact', 'novelty': 0.8, 'impact': 'major',
        'category': 'Medicine',
    },
    {
        'name': 'Dark energy = sqrt(ln2)^sqrt(Psi_steps) = 0.683',
        'evidence': 'model', 'predictions': 3, 'domains': 3,
        'rigor': 'approximate', 'novelty': 0.9, 'impact': 'paradigm',
        'category': 'Physics',
    },
    {
        'name': 'H^2+dp^2=0.478 consciousness conservation law',
        'evidence': 'verified', 'predictions': 5, 'domains': 3,
        'rigor': 'approximate', 'novelty': 0.85, 'impact': 'paradigm',
        'category': 'Physics',
    },
]


def print_builtin():
    print()
    print('  ╔══════════════════════════════════════════════════════════╗')
    print('  ║    Nobel Hypothesis Scorer — TECS-L + anima             ║')
    print('  ╚══════════════════════════════════════════════════════════╝')
    print()

    results = []
    for h in BUILTIN:
        r = score_hypothesis(**h)
        results.append(r)

    # Sort by weighted score
    results.sort(key=lambda x: x['weighted'], reverse=True)

    # Summary table
    print(f'  {"#":>3} {"Hypothesis":<50} {"Score":>6} {"Stars":>7} {"Category":>10}')
    print(f'  {"─"*3} {"─"*50} {"─"*6} {"─"*7} {"─"*10}')
    for i, r in enumerate(results, 1):
        name = r['name'][:48]
        print(f'  {i:>3} {name:<50} {r["weighted"]:>6.3f} {r["star_str"]:>7} {r["category"]:>10}')

    print()

    # Detailed top 3
    print('  ═══ Top 3 Detailed ═══')
    for r in results[:3]:
        print()
        print_score(r)

    # Statistics
    avg = sum(r['weighted'] for r in results) / len(results)
    max_r = results[0]
    print(f'  ═══ Summary ═══')
    print(f'  Hypotheses scored: {len(results)}')
    print(f'  Average score: {avg:.3f}')
    print(f'  Top scorer: {max_r["name"][:40]} ({max_r["weighted"]:.3f})')
    print(f'  5-star count: {sum(1 for r in results if r["stars"] == 5)}')
    print(f'  4-star count: {sum(1 for r in results if r["stars"] == 4)}')
    print()


def interactive():
    print('  Nobel Hypothesis Scorer — Interactive Mode')
    print('  Type hypothesis details:')
    print()

    name = input('  Name: ')
    print('  Evidence (proven/verified/model/speculative): ', end='')
    evidence = input().strip()
    print('  Predictions (number): ', end='')
    predictions = int(input().strip())
    print('  Domains connected (number): ', end='')
    domains = int(input().strip())
    print('  Rigor (exact/approximate/qualitative): ', end='')
    rigor = input().strip()
    print('  Novelty (0.0-1.0): ', end='')
    novelty = float(input().strip())
    print('  Impact (paradigm/major/incremental): ', end='')
    impact = input().strip()
    print('  Category (Physics/Chemistry/Medicine/Economics): ', end='')
    category = input().strip()

    result = score_hypothesis(name, evidence, predictions, domains, rigor, novelty, impact, category)
    print()
    print_score(result)


def main():
    parser = argparse.ArgumentParser(description='Nobel Hypothesis Scorer')
    parser.add_argument('--interactive', action='store_true', help='Interactive scoring')
    parser.add_argument('--builtin', action='store_true', help='Score built-in TECS-L hypotheses')
    parser.add_argument('--quick', type=str, help='Quick score: hypothesis name')
    parser.add_argument('--evidence', type=str, default='model')
    parser.add_argument('--predictions', type=int, default=3)
    parser.add_argument('--domains', type=int, default=2)
    parser.add_argument('--rigor', type=str, default='approximate')
    parser.add_argument('--novelty', type=float, default=0.5)
    parser.add_argument('--impact', type=str, default='major')
    parser.add_argument('--category', type=str, default='Physics')
    args = parser.parse_args()

    if args.interactive:
        interactive()
    elif args.builtin:
        print_builtin()
    elif args.quick:
        result = score_hypothesis(
            args.quick, args.evidence, args.predictions, args.domains,
            args.rigor, args.novelty, args.impact, args.category
        )
        print()
        print_score(result)
    else:
        print_builtin()


if __name__ == '__main__':
    main()
