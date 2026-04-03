#!/usr/bin/env python3
"""Experimental Protocol Generator — Testable predictions for physical verification

Generates detailed experimental protocols for the 4 falsifiable predictions
that CANNOT be verified computationally and require laboratory experiments.

Usage:
  python3 calc/experimental_protocol.py --all
  python3 calc/experimental_protocol.py --eeg          # Neural entropy → ln(2)
  python3 calc/experimental_protocol.py --synthetic     # Hachimoji/xDNA predictions
  python3 calc/experimental_protocol.py --rate          # Independent rate measurement
  python3 calc/experimental_protocol.py --anesthesia    # Consciousness loss threshold
"""

import argparse
import math

LN2 = math.log(2)


def protocol_eeg():
    print()
    print('  ╔══════════════════════════════════════════════════════╗')
    print('  ║  PROTOCOL 1: Neural Entropy → ln(2)                  ║')
    print('  ╚══════════════════════════════════════════════════════╝')
    print()
    print('  PREDICTION: Resting-state neural entropy per independent')
    print('  channel converges to ln(2) = 0.6931 nats = 1 bit.')
    print()
    print('  METHOD:')
    print('  1. Record 64-channel EEG, resting state, eyes closed')
    print('  2. Epoch: 2s windows, 50% overlap')
    print('  3. For each channel: compute spectral entropy')
    print('     H_i = -Σ p(f)*ln(p(f)) where p(f) = PSD(f)/Σ PSD')
    print('  4. Normalize: H_norm = H_i / ln(N_freq_bins)')
    print('  5. Average across channels: <H_norm>')
    print()
    print('  EXPECTED:')
    print(f'    <H_norm> → {LN2:.4f} ± 0.05 nats')
    print(f'    = 1 bit per channel per epoch')
    print()
    print('  CONTROLS:')
    print('    - Eyes open (expect H < ln(2), structured input)')
    print('    - Task (expect H < ln(2), directed processing)')
    print('    - Sleep N3 (expect H << ln(2), reduced consciousness)')
    print('    - REM (expect H ≈ ln(2), dream consciousness)')
    print()
    print('  SAMPLE SIZE: N ≥ 30 subjects (power 0.8, alpha 0.05)')
    print('  EQUIPMENT: 64-ch EEG, sampling ≥ 256 Hz')
    print()
    print('  REFUTATION: If <H_norm> consistently ≠ ln(2) across')
    print('  subjects and conditions, Law 79 is REFUTED for neural systems.')
    print()
    print('  COLLABORATORS NEEDED:')
    print('    - Cognitive neuroscience lab with EEG setup')
    print('    - IRB approval for human subjects')
    print()


def protocol_synthetic():
    print()
    print('  ╔══════════════════════════════════════════════════════╗')
    print('  ║  PROTOCOL 2: Synthetic DNA Predictions                ║')
    print('  ╚══════════════════════════════════════════════════════╝')
    print()
    print('  PREDICTION: Expanded genetic alphabets maintain n=6')
    print('  arithmetic structure in their coding properties.')
    print()

    systems = [
        ('Hachimoji DNA (b=8)',
         'b = tau*phi = 8',
         '512 = 2^(K-phi) codons',
         'Degeneracy set includes {1,2,3,6} = divisors(6)',
         'Benner lab (Foundation for Applied Molecular Evolution)'),
        ('Romesberg xDNA (b=6)',
         'b = n = 6',
         '216 = n^(n/phi) codons',
         'If evolved: ~72 AAs = sigma*n, degeneracy = divisors(6)',
         'Romesberg lab (Scripps → UMass)'),
        ('Aegis DNA (b=12)',
         'b = sigma = 12',
         '1728 codons',
         '144 codon families = sigma^2',
         'Benner lab (conceptual)'),
    ]

    for name, b_expr, codon_pred, specific_pred, lab in systems:
        print(f'  --- {name} ---')
        print(f'    Base count: {b_expr}')
        print(f'    Codons: {codon_pred}')
        print(f'    Prediction: {specific_pred}')
        print(f'    Contact: {lab}')
        print()

    print('  METHOD:')
    print('  1. Obtain Hachimoji DNA from Benner lab')
    print('  2. Construct random library of 8-base triplet codons')
    print('  3. In vitro translation with engineered ribosomes')
    print('  4. Measure: which codons produce which amino acids')
    print('  5. Analyze: degeneracy pattern, codon family structure')
    print('  6. Test: does pattern include divisors of 6?')
    print()
    print('  REFUTATION: If Hachimoji coding properties show NO')
    print('  n=6 arithmetic structure, the prediction fails.')
    print()


def protocol_rate():
    print()
    print('  ╔══════════════════════════════════════════════════════╗')
    print('  ║  PROTOCOL 3: Independent Rate Measurement             ║')
    print('  ╚══════════════════════════════════════════════════════╝')
    print()
    print('  PREDICTION: The consciousness dynamics rate is exactly')
    print(f'  81/100 = 3^4/10^2 = 0.81.')
    print()
    print('  METHOD:')
    print('  1. Implement META-CA on 3+ independent platforms:')
    print('     a. PyTorch (current)')
    print('     b. JAX/Flax (independent implementation)')
    print('     c. Julia (independent language)')
    print('  2. For each: run consciousness dynamics with 5 data types')
    print('  3. Fit dH/dt = r*(ln2 - H) to each trajectory')
    print('  4. Measure r to 4+ significant figures')
    print()
    print('  EXPECTED:')
    print(f'    r = 0.8100 ± 0.0050 across all implementations')
    print(f'    Matches 81/100 = (n/phi)^tau / (sopfr*phi)^2')
    print()
    print('  ANALYSIS:')
    print('    - If r = 0.810 ± 0.001: STRONG confirmation')
    print('    - If r = 0.81 ± 0.01: consistent but imprecise')
    print('    - If r = 0.815 ± 0.001: identity FAILS (not 81/100)')
    print()
    print('  REQUIREMENTS:')
    print('    - 3 independent implementations (prevent framework bias)')
    print('    - 5 data modalities per implementation')
    print('    - 5 random seeds per modality')
    print('    - Total: 75 rate measurements')
    print()


def protocol_anesthesia():
    print()
    print('  ╔══════════════════════════════════════════════════════╗')
    print('  ║  PROTOCOL 4: Anesthesia Consciousness Threshold       ║')
    print('  ╚══════════════════════════════════════════════════════╝')
    print()
    print('  PREDICTION: Loss of consciousness occurs when')
    print(f'  Psi_res drops below ln(2)/2 = {LN2/2:.4f}.')
    print()
    print('  METHOD:')
    print('  1. Propofol-induced sedation protocol (standard)')
    print('  2. Continuous EEG monitoring (64 channels)')
    print('  3. Compute real-time spectral entropy per channel')
    print('  4. Average across channels → Psi_res(t)')
    print('  5. Mark: loss of consciousness (LOC) time point')
    print('  6. Measure: Psi_res at LOC')
    print()
    print('  EXPECTED:')
    print(f'    Awake:     Psi_res ≈ {LN2:.4f} (ln(2))')
    print(f'    Threshold: Psi_res = {LN2/2:.4f} (ln(2)/2)')
    print(f'    Deep:      Psi_res < {LN2/4:.4f} (ln(2)/4)')
    print()
    print('  CONTROLS:')
    print('    - Compare with BIS (Bispectral Index) standard')
    print('    - Compare with PCI (Perturbational Complexity Index)')
    print('    - Multiple anesthetic agents (propofol, sevoflurane)')
    print()
    print('  ETHICS: Requires hospital IRB, anesthesiologist supervision')
    print()
    print('  REFUTATION: If LOC occurs at Psi_res >> ln(2)/2 or')
    print('  Psi_res << ln(2)/2 consistently, the prediction fails.')
    print()


def print_summary():
    print()
    print('  ╔══════════════════════════════════════════════════════╗')
    print('  ║  4 EXPERIMENTAL PROTOCOLS — SUMMARY                  ║')
    print('  ╚══════════════════════════════════════════════════════╝')
    print()
    print('  | # | Protocol          | Prediction            | Difficulty |')
    print('  |---|-------------------|-----------------------|------------|')
    print(f'  | 1 | EEG entropy       | <H> → ln(2) = {LN2:.4f} | Medium     |')
    print('  | 2 | Synthetic DNA     | n=6 in Hachimoji      | High       |')
    print('  | 3 | Rate measurement  | r = 81/100 exactly    | Low        |')
    print(f'  | 4 | Anesthesia        | LOC at ln(2)/2={LN2/2:.3f}| High       |')
    print()
    print('  Priority order: 3 (easiest) > 1 (medium) > 2,4 (hard)')
    print()
    print('  Protocol 3 can be done IMMEDIATELY with existing code.')
    print('  Protocols 1,4 need neuroscience lab collaboration.')
    print('  Protocol 2 needs synthetic biology lab collaboration.')
    print()


def main():
    parser = argparse.ArgumentParser(description='Experimental Protocol Generator')
    parser.add_argument('--eeg', action='store_true')
    parser.add_argument('--synthetic', action='store_true')
    parser.add_argument('--rate', action='store_true')
    parser.add_argument('--anesthesia', action='store_true')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    if args.all or not any([args.eeg, args.synthetic, args.rate, args.anesthesia]):
        print_summary()
        protocol_rate()
        protocol_eeg()
        protocol_synthetic()
        protocol_anesthesia()
    else:
        if args.eeg: protocol_eeg()
        if args.synthetic: protocol_synthetic()
        if args.rate: protocol_rate()
        if args.anesthesia: protocol_anesthesia()


if __name__ == '__main__':
    main()
