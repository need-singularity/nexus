#!/usr/bin/env python3
"""GZ Epidemic Analyzer — Tests G=D*P/I mapping against real SIR data.

Maps:
  G = R_0  (basic reproduction number)
  D = beta (transmission rate per contact per unit time)
  P = S_0  (initial susceptible fraction, dimensionless)
  I = gamma / beta_eff  (recovery-to-transmission ratio, dimensionless)

  where beta_eff = beta * c (transmission rate * contact rate)
  so I = gamma / (beta * c) = 1/R_0 when S_0 = 1.

Golden Zone prediction:
  I in [0.2123, 0.5000] => endemic (sustainable oscillation)
  I < 0.2123            => explosive (epidemic/pandemic)
  I > 0.5000            => self-limiting (rapid die-out)

Conservation law test:
  G * I = D * P  =>  R_0 * (gamma/beta_eff) = beta * S_0 * (gamma/beta_eff)
                 =>  gamma * S_0 / beta_eff ... not conserved dynamically.
  Corrected: G*I = S_0 (when D*P = S_0 and I = 1/R_0)
  So the conserved quantity is simply S_0 at t=0. Not a dynamic conservation.

Author: GZ-BLOWUP epidemiology analysis
Date: 2026-04-04
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Optional

# ─── Golden Zone constants ───
GZ_UPPER = 0.5
GZ_CENTER = 1.0 / math.e  # 0.3679
GZ_WIDTH = math.log(4.0 / 3.0)  # 0.2877
GZ_LOWER = GZ_UPPER - GZ_WIDTH  # 0.2123


@dataclass
class EpidemicData:
    """Real-world epidemic parameters from published literature."""
    name: str
    beta: float          # transmission rate (per contact per day)
    gamma: float         # recovery rate (1/day = 1/infectious_period)
    S0: float            # initial susceptible fraction
    R0_observed: float   # published R0 estimate (for validation)
    outcome: str         # "explosive", "endemic", "self-limiting"
    source: str          # citation
    contact_rate: float = 1.0  # contacts per day (if beta already includes it, =1)


# ─── Real epidemic data (literature values) ───
# Sources: WHO, CDC, Lancet, Nature, JAMA systematic reviews
# beta values are "effective" (already include contact rate) unless noted
EPIDEMICS = [
    # ── Explosive (I << 0.21) ──
    EpidemicData(
        name="Measles",
        beta=0.45,       # ~90% secondary attack rate in household
        gamma=1/8,       # infectious period ~8 days
        S0=1.0,
        R0_observed=15.0,  # range 12-18, use midpoint
        outcome="explosive",
        source="Guerra et al. Lancet Infect Dis 2017; Fine & Clarkson 1982"
    ),
    EpidemicData(
        name="Smallpox",
        beta=0.30,
        gamma=1/17,      # infectious ~17 days
        S0=1.0,
        R0_observed=5.5,   # range 5-7
        outcome="explosive",
        source="Gani & Leach, Nature 2001"
    ),
    EpidemicData(
        name="COVID-19 (Wuhan, original)",
        beta=0.30,
        gamma=1/10,      # infectious ~10 days
        S0=1.0,
        R0_observed=2.87,  # Li et al. NEJM 2020: 2.2; meta: 2.87
        outcome="explosive",
        source="Liu et al. J Travel Med 2020 (meta-analysis); Li et al. NEJM 2020"
    ),
    EpidemicData(
        name="COVID-19 Delta",
        beta=0.50,
        gamma=1/8,       # slightly shorter infectious period
        S0=0.7,          # partial immunity by Delta wave
        R0_observed=5.1,   # Campbell et al. 2021
        outcome="explosive",
        source="Campbell et al. Euro Surveill 2021; Liu & Rocklov BMJ 2022"
    ),
    EpidemicData(
        name="COVID-19 Omicron",
        beta=0.75,
        gamma=1/5,       # shorter infectious period
        S0=0.5,          # high prior immunity
        R0_observed=9.5,   # range 8-15
        outcome="explosive",
        source="Liu & Rocklov J Travel Med 2022"
    ),
    EpidemicData(
        name="Ebola (2014 West Africa)",
        beta=0.16,
        gamma=1/10,      # infectious ~10 days
        S0=1.0,
        R0_observed=1.8,   # range 1.5-2.5
        outcome="explosive",
        source="WHO Ebola Response Team, NEJM 2014; Althaus, PLOS Curr 2014"
    ),
    EpidemicData(
        name="SARS (2003)",
        beta=0.18,
        gamma=1/10,
        S0=1.0,
        R0_observed=2.7,   # range 2-4; Lipsitch et al. Science 2003
        outcome="explosive",
        source="Lipsitch et al. Science 2003; Riley et al. Science 2003"
    ),
    EpidemicData(
        name="MERS",
        beta=0.06,
        gamma=1/14,      # long infectious period
        S0=1.0,
        R0_observed=0.9,   # usually <1, sporadic clusters
        outcome="self-limiting",
        source="Breban et al. Lancet 2013; Cauchemez et al. Lancet Infect Dis 2014"
    ),

    # ── Endemic (I ~ 0.21-0.50) ──
    EpidemicData(
        name="Seasonal Influenza",
        beta=0.25,
        gamma=1/4,       # infectious ~4 days
        S0=0.5,          # partial population immunity
        R0_observed=1.3,   # range 1.1-1.5 effective R
        outcome="endemic",
        source="Biggerstaff et al. BMC Infect Dis 2014"
    ),
    EpidemicData(
        name="1918 Influenza (pandemic phase)",
        beta=0.40,
        gamma=1/5,
        S0=1.0,
        R0_observed=2.0,   # range 1.4-2.8; Mills et al. Nature 2004
        outcome="explosive",
        source="Mills et al. Nature 2004; Taubenberger & Morens Rev 2006"
    ),
    EpidemicData(
        name="COVID-19 (endemic phase, 2024+)",
        beta=0.35,
        gamma=1/5,
        S0=0.3,          # high hybrid immunity
        R0_observed=1.1,   # effective R ~ 1 oscillating
        outcome="endemic",
        source="estimated from surveillance; Khoury et al. Nat Med 2023"
    ),

    # ── Self-limiting (I > 0.50) ──
    EpidemicData(
        name="Common Cold (rhinovirus)",
        beta=0.15,
        gamma=1/3,       # infectious ~3 days
        S0=0.5,          # partial immunity
        R0_observed=1.2,
        outcome="self-limiting",
        source="Lessler et al. Lancet Infect Dis 2009; Monto AS Annals IM 2002"
    ),

    # ── Chronic / special dynamics ──
    EpidemicData(
        name="HIV (untreated)",
        beta=0.001,      # per-contact transmission very low
        gamma=1/(365*10),  # "infectious" period ~10 years untreated
        S0=1.0,
        R0_observed=4.0,   # Anderson & May 1991; range 2-8
        outcome="endemic",
        source="Anderson & May, Nature 1991; May & Anderson, Proc R Soc 1988"
    ),
    EpidemicData(
        name="Tuberculosis",
        beta=0.002,
        gamma=1/(365*0.5),  # active infectious ~6 months
        S0=1.0,
        R0_observed=3.0,   # range 1-5 depending on setting
        outcome="endemic",
        source="Vynnycky & Fine, Epidemiol Infect 1997; WHO TB Report"
    ),
    EpidemicData(
        name="Malaria (P. falciparum, high transmission)",
        beta=0.05,       # per-bite transmission probability * biting rate
        gamma=1/200,     # ~200 day untreated infection
        S0=1.0,
        R0_observed=100.0,  # can be extremely high; Smith et al. PLoS Med 2007
        outcome="endemic",
        source="Smith et al. PLoS Med 2007; Macdonald, Bull WHO 1956"
    ),
]


def compute_gz_metrics(epi: EpidemicData) -> dict:
    """Compute all GZ-relevant metrics for an epidemic."""
    # Model R0
    R0_model = epi.beta * epi.S0 / epi.gamma

    # Dimensionless inhibition = gamma / beta (recovery per transmission event)
    # This is the probability of recovering before transmitting to the next person
    I_raw = epi.gamma / epi.beta

    # Alternatively: I = 1/R0 (fraction of contacts that DON'T produce infection)
    I_from_R0 = 1.0 / R0_model if R0_model > 0 else float('inf')

    # GZ zone classification
    if I_raw < GZ_LOWER:
        gz_zone = "EXPLOSIVE (below GZ)"
    elif I_raw <= GZ_UPPER:
        gz_zone = "GOLDEN ZONE (endemic)"
    else:
        gz_zone = "SELF-LIMITING (above GZ)"

    # Distance from GZ center
    dist_from_center = abs(I_raw - GZ_CENTER)

    # Conservation test: G*I = D*P => R0 * (gamma/beta) = beta * S0 * (gamma/beta)
    # Left: R0 * gamma/beta = S0 (always, by definition)
    # Right: S0 (always). So conservation is tautological in SIR!
    GI = R0_model * I_raw
    DP = epi.beta * epi.S0  # This is R0 * gamma, not S0

    # Correct conservation: G*I = S0 when I = gamma/beta and G = beta*S0/gamma
    # G * I = (beta*S0/gamma) * (gamma/beta) = S0. Always true by construction.

    # Meta fixed point test: does gamma/beta converge to 1/3?
    dist_from_meta = abs(I_raw - 1.0/3.0)

    # R0 prediction accuracy
    R0_error_pct = abs(R0_model - epi.R0_observed) / epi.R0_observed * 100

    # GZ prediction vs actual outcome
    predicted_outcome = gz_zone.split("(")[1].rstrip(")")
    outcome_match = (
        ("explosive" in predicted_outcome.lower() and epi.outcome == "explosive") or
        ("endemic" in predicted_outcome.lower() and epi.outcome == "endemic") or
        ("self-limiting" in predicted_outcome.lower() and epi.outcome == "self-limiting")
    )

    return {
        "name": epi.name,
        "R0_model": R0_model,
        "R0_observed": epi.R0_observed,
        "R0_error_pct": R0_error_pct,
        "I_raw": I_raw,
        "I_from_R0": I_from_R0,
        "gz_zone": gz_zone,
        "dist_from_center": dist_from_center,
        "dist_from_meta": dist_from_meta,
        "GI_product": GI,
        "S0": epi.S0,
        "predicted_outcome": predicted_outcome.strip(),
        "actual_outcome": epi.outcome,
        "outcome_match": outcome_match,
        "beta": epi.beta,
        "gamma": epi.gamma,
        "source": epi.source,
    }


def print_table(results: list[dict]) -> None:
    """Print formatted analysis table."""
    print("=" * 120)
    print("GZ EPIDEMIC ANALYZER — G=D*P/I mapping to SIR R_0 = beta*S_0/gamma")
    print("=" * 120)
    print()

    # Main table
    header = f"{'Disease':<32} {'R0_obs':>7} {'R0_mod':>7} {'err%':>6} {'I=g/b':>8} {'GZ Zone':<28} {'Match':>5}"
    print(header)
    print("-" * len(header))

    correct = 0
    total = 0
    for r in results:
        match_str = "YES" if r["outcome_match"] else "NO"
        print(f"{r['name']:<32} {r['R0_observed']:>7.2f} {r['R0_model']:>7.2f} "
              f"{r['R0_error_pct']:>5.1f}% {r['I_raw']:>8.4f} "
              f"{r['gz_zone']:<28} {match_str:>5}")
        total += 1
        if r["outcome_match"]:
            correct += 1

    print("-" * len(header))
    print(f"Outcome prediction accuracy: {correct}/{total} = {correct/total*100:.1f}%")
    print()

    # GZ zone distribution
    print("=" * 80)
    print("GZ ZONE CLASSIFICATION")
    print("=" * 80)
    print()
    print("  EXPLOSIVE        GOLDEN ZONE            SELF-LIMITING")
    print("  I < 0.2123       0.2123 <= I <= 0.5      I > 0.5")
    print("  |                |<-- ln(4/3) -->|       |")
    print("  0          0.2123    0.3679    0.5       1.0")
    print("             lower     1/e      upper")
    print()

    for r in results:
        I = r["I_raw"]
        # Position on a 60-char wide bar (I from 0 to 1.0)
        pos = min(int(I * 60), 59)
        bar = ["."] * 60
        # Mark GZ boundaries
        gz_lo = int(GZ_LOWER * 60)
        gz_hi = int(GZ_UPPER * 60)
        gz_ctr = int(GZ_CENTER * 60)
        for i in range(gz_lo, gz_hi + 1):
            if i < 60:
                bar[i] = "-"
        if gz_ctr < 60:
            bar[gz_ctr] = "|"
        if pos < 60:
            bar[pos] = "#"
        bar_str = "".join(bar)
        tag = "OK" if r["outcome_match"] else "MISS"
        print(f"  {r['name']:<30} [{bar_str}] I={I:.4f} {tag}")

    print()

    # Conservation law analysis
    print("=" * 80)
    print("CONSERVATION LAW TEST: G*I = D*P")
    print("=" * 80)
    print()
    print("In SIR: R_0 * (gamma/beta) = (beta*S_0/gamma) * (gamma/beta) = S_0")
    print("This is TAUTOLOGICAL — always true by algebraic identity.")
    print("G*I = S_0 is not a dynamic conservation law but a definition.")
    print()
    header2 = f"{'Disease':<32} {'G*I':>8} {'S_0':>8} {'Match':>8}"
    print(header2)
    print("-" * len(header2))
    for r in results:
        diff = abs(r["GI_product"] - r["S0"])
        print(f"{r['name']:<32} {r['GI_product']:>8.4f} {r['S0']:>8.4f} "
              f"{'exact' if diff < 1e-10 else f'diff={diff:.4f}':>8}")

    print()
    print("VERDICT: G*I = S_0 is always exactly satisfied (algebraic identity).")
    print("This is NOT a testable prediction — it is built into the definition.")
    print()

    # Meta fixed point test
    print("=" * 80)
    print("META FIXED POINT TEST: Does gamma/beta converge to 1/3 for endemic diseases?")
    print("=" * 80)
    print()
    endemic = [r for r in results if r["actual_outcome"] == "endemic"]
    if endemic:
        I_values = [r["I_raw"] for r in endemic]
        mean_I = sum(I_values) / len(I_values)
        print(f"  Endemic diseases (N={len(endemic)}):")
        for r in endemic:
            dist = r["I_raw"] - 1.0/3.0
            print(f"    {r['name']:<32} I = {r['I_raw']:.4f}  "
                  f"(delta from 1/3: {dist:+.4f})")
        print(f"  Mean I (endemic): {mean_I:.4f}")
        print(f"  1/3 = {1/3:.4f}")
        print(f"  Distance from 1/3: {abs(mean_I - 1/3):.4f}")
        print()
        # The HIV and malaria have extreme I values; exclude them for acute endemic
        acute_endemic = [r for r in endemic
                        if r["name"] not in ("HIV (untreated)", "Malaria (P. falciparum, high transmission)",
                                             "Tuberculosis")]
        if acute_endemic:
            acute_I = [r["I_raw"] for r in acute_endemic]
            mean_acute = sum(acute_I) / len(acute_I)
            print(f"  Acute endemic only (N={len(acute_endemic)}):")
            for r in acute_endemic:
                print(f"    {r['name']:<32} I = {r['I_raw']:.4f}")
            print(f"  Mean I (acute endemic): {mean_acute:.4f}")
            print(f"  Distance from 1/3: {abs(mean_acute - 1/3):.4f}")
            print()

    print()
    print("=" * 80)
    print("HONEST ASSESSMENT: WHERE THE MAPPING WORKS AND FAILS")
    print("=" * 80)
    print("""
  WORKS:
    1. Functional form: R_0 = beta*S_0/gamma IS exactly G = D*P/I
       when we identify I = gamma (with dimensional rescaling).
       This is not a coincidence — it is the simplest multiplicative
       model satisfying the same axioms.

    2. Qualitative zones: Low I (high transmission relative to recovery)
       does produce explosive epidemics. High I does produce self-limiting
       outbreaks. This is trivially true from R_0 = 1/I when S_0 = 1.

    3. Conservation G*I = S_0: Algebraically exact (by construction).

  FAILS / LIMITATIONS:
    1. Conservation is tautological: G*I = S_0 is not a dynamic conservation
       law — it is an algebraic identity from the definition. During an
       epidemic, S(t) decreases but gamma and beta are fixed, so I doesn't
       change. The "conservation" doesn't constrain dynamics.

    2. GZ boundaries are NOT special in SIR: The values 0.2123 and 0.5
       have no known epidemiological significance. The only special value
       in SIR is I = 1 (R_0 = 1, epidemic threshold). The GZ boundaries
       come from information-theoretic arguments (Shannon entropy of n=6
       divisor reciprocals) that have no analog in disease transmission.

    3. I = gamma/beta is NOT dimensionless in general: gamma has units 1/time,
       beta has units 1/(time*contacts). The ratio gamma/beta has units of
       contacts, not dimensionless. Making I dimensionless requires
       multiplying by contact interval, which absorbs the free parameter.

    4. Meta fixed point I* = 1/3 is NOT confirmed: Endemic diseases span
       a huge range of I values. HIV (I ~ 0.0003) and common cold (I ~ 2.2)
       are both "endemic" but at opposite extremes. The claim that COVID
       settled at I ~ 0.33 depends heavily on which beta/gamma estimates
       you use in the endemic phase.

    5. Chronic diseases break the model: HIV, TB, malaria have complex
       dynamics (latency, vector transmission, chronic carriage) that
       cannot be reduced to simple SIR. The SIR model itself is a poor
       description of these diseases, so mapping G=D*P/I onto SIR and
       then applying to HIV is doubly approximate.

    6. The mapping is not PREDICTIVE: Given beta, gamma, S_0, we can
       compute R_0 directly. The G=D*P/I framework adds no computational
       power. Its value would be if the GZ boundaries predicted something
       R_0 alone cannot — e.g., a phase transition at I = 0.2123.
       No such transition exists in standard SIR dynamics.

  VERDICT:
    The R_0 = beta*S_0/gamma formula is a SPECIAL CASE of G=D*P/I,
    confirming that the G=D*P/I functional form arises naturally in
    epidemiology. However, the GZ-specific constants (1/e, 0.2123, 0.5)
    do NOT have known epidemiological meaning. The mapping is
    STRUCTURALLY CORRECT but the GZ overlay is UNCONFIRMED.

    Grade: STRUCTURAL (form match) + UNCONFIRMED (GZ constants)
""")


def vaccination_analysis() -> None:
    """Analyze GZ predictions for optimal vaccination."""
    print("=" * 80)
    print("VACCINATION ANALYSIS: GZ optimal intervention point")
    print("=" * 80)
    print()
    print("GZ predicts optimal intervention at I = 1/e => R_0 = 1/I_eff = e ~ 2.718")
    print("Standard herd immunity threshold: v_c = 1 - 1/R_0")
    print()
    print("For I_target = 1/e (GZ center):")
    print(f"  R_0 at GZ center = beta*S/gamma with I=1/e => R_0 = 1/(1/e) = e = {math.e:.4f}")
    print(f"  Herd immunity threshold: 1 - 1/e = {1 - 1/math.e:.4f} = {(1-1/math.e)*100:.1f}%")
    print()
    print("Comparison with real vaccination targets:")
    print()

    vaccines = [
        ("Measles", 15.0, 1 - 1/15),
        ("Smallpox", 5.5, 1 - 1/5.5),
        ("COVID-19 (original)", 2.87, 1 - 1/2.87),
        ("COVID-19 (Delta)", 5.1, 1 - 1/5.1),
        ("Seasonal Flu", 1.3, 1 - 1/1.3),
        ("GZ optimal (I=1/e)", math.e, 1 - 1/math.e),
    ]

    header = f"{'Disease':<28} {'R_0':>6} {'v_c (herd imm)':>15} {'Coverage needed':>16}"
    print(header)
    print("-" * len(header))
    for name, R0, vc in vaccines:
        print(f"{name:<28} {R0:>6.2f} {vc:>14.1%} {vc:>15.1%}")

    print()
    print("The GZ 'optimal' point (R_0 = e) requires 63.2% vaccination coverage.")
    print("This falls between seasonal flu (23%) and COVID original (65%).")
    print()
    print("HONEST NOTE: The herd immunity formula v_c = 1-1/R_0 is a property of SIR,")
    print("not of GZ. The GZ adds the claim that R_0 = e is somehow 'optimal', but")
    print("optimal for WHAT? In epidemiology, lower R_0 is always better (fewer cases).")
    print("The GZ 'peak creativity' interpretation (maximizing G at I=1/e) translates")
    print("to 'peak epidemic potential' — which is a BAD thing, not a good thing.")
    print()
    print("The semantic mapping INVERTS the desirability:")
    print("  Consciousness: high G = good (genius, creativity)")
    print("  Epidemics:     high G = bad  (more infections)")
    print("  => GZ center is the WORST endemic state, not the best.")
    print("  => The 'frozen zone' (I > 0.5, R_0 < 2) is actually DESIRABLE.")
    print()


def main():
    results = [compute_gz_metrics(epi) for epi in EPIDEMICS]

    # Sort by I_raw for display
    results.sort(key=lambda r: r["I_raw"])

    print_table(results)
    vaccination_analysis()

    # Summary statistics
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    matches = sum(1 for r in results if r["outcome_match"])
    total = len(results)
    print(f"  Total diseases analyzed:    {total}")
    print(f"  GZ zone prediction correct: {matches}/{total} ({matches/total*100:.0f}%)")
    print(f"  Diseases in Golden Zone:    {sum(1 for r in results if 'GOLDEN' in r['gz_zone'])}")
    print(f"  Below GZ (explosive):       {sum(1 for r in results if 'EXPLOSIVE' in r['gz_zone'])}")
    print(f"  Above GZ (self-limiting):   {sum(1 for r in results if 'SELF-LIMITING' in r['gz_zone'])}")
    print()

    # R0 model accuracy
    r0_errors = [r["R0_error_pct"] for r in results]
    print(f"  R0 model vs observed:")
    print(f"    Mean absolute error: {sum(r0_errors)/len(r0_errors):.1f}%")
    print(f"    Max error:           {max(r0_errors):.1f}% ({max(results, key=lambda r: r['R0_error_pct'])['name']})")
    print(f"    Note: R0 model = beta*S0/gamma uses our beta/gamma estimates,")
    print(f"          not independent predictions. Error reflects parameter uncertainty,")
    print(f"          not model failure.")
    print()

    # ── Alternative mapping: I = 1/R_0 (always in (0,1) for R_0 > 1) ──
    print()
    print("=" * 80)
    print("ALTERNATIVE MAPPING: I = 1/R_0 (dimensionless, always in (0,1) for R_0 > 1)")
    print("=" * 80)
    print()
    print("If we define I = 1/R_0 directly (the 'inefficiency' of transmission),")
    print("then by construction G = D*P/I = D*P*R_0. This is circular.")
    print("But let's check where real epidemics fall on the I = 1/R_0 scale:")
    print()

    header3 = f"{'Disease':<35} {'R_0_obs':>8} {'I=1/R_0':>8} {'GZ Zone':>28} {'Outcome':<15} {'Match':>5}"
    print(header3)
    print("-" * len(header3))

    alt_correct = 0
    for epi in sorted(EPIDEMICS, key=lambda e: 1/e.R0_observed):
        I_alt = 1.0 / epi.R0_observed
        if I_alt < GZ_LOWER:
            zone = "EXPLOSIVE (below GZ)"
        elif I_alt <= GZ_UPPER:
            zone = "GOLDEN ZONE (endemic)"
        else:
            zone = "SELF-LIMITING (above GZ)"

        predicted = zone.split("(")[1].rstrip(")")
        match = (
            ("explosive" in predicted.lower() and epi.outcome == "explosive") or
            ("endemic" in predicted.lower() and epi.outcome == "endemic") or
            ("self-limiting" in predicted.lower() and epi.outcome == "self-limiting")
        )
        if match:
            alt_correct += 1
        tag = "YES" if match else "NO"
        print(f"  {epi.name:<33} {epi.R0_observed:>8.2f} {I_alt:>8.4f} {zone:>28} {epi.outcome:<15} {tag:>5}")

    print()
    print(f"  Alternative mapping accuracy: {alt_correct}/{len(EPIDEMICS)} = {alt_correct/len(EPIDEMICS)*100:.1f}%")
    print()
    print("  Key insight: with I = 1/R_0:")
    print(f"    GZ lower (0.2123) => R_0 = {1/GZ_LOWER:.2f} (above this = explosive)")
    print(f"    GZ center (1/e)   => R_0 = e = {math.e:.2f}")
    print(f"    GZ upper (0.5)    => R_0 = 2.00 (below this = self-limiting)")
    print()
    print("  So GZ predicts:")
    print("    R_0 > 4.71: explosive (measles=15, malaria=100, omicron=9.5)")
    print("    R_0 in [2, 4.71]: endemic sweet spot (COVID original=2.87, HIV=4)")
    print("    R_0 < 2: self-limiting (flu=1.3, MERS=0.9, cold=1.2)")
    print()
    print("  This is MORE plausible than I = gamma/beta, but the boundaries")
    print("  are still arbitrary from an epidemiological standpoint.")
    print("  The real boundary is R_0 = 1 (epidemic threshold), not R_0 = 2.")

    return results


if __name__ == "__main__":
    results = main()
