#!/usr/bin/env python3
"""
FTL Tribunal -- 15 FTL mechanisms judged by 3 physics axes
============================================================
Axes: General Relativity (GR), Quantum Mechanics (QM), Causality
Verdicts: ALLOWED / CONDITIONAL / ILLUSORY / FORBIDDEN / SPECULATIVE

Usage:
    python3 .shared/calc/ftl_tribunal.py                    # all 15
    python3 .shared/calc/ftl_tribunal.py --mechanism 2      # single
    python3 .shared/calc/ftl_tribunal.py --summary           # table only
    python3 .shared/calc/ftl_tribunal.py --category allowed  # filter
"""

import argparse
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# ── Verdict constants ──────────────────────────────────────────────
ALLOWED     = "ALLOWED"
CONDITIONAL = "CONDITIONAL"
ILLUSORY    = "ILLUSORY"
FORBIDDEN   = "FORBIDDEN"
SPECULATIVE = "SPECULATIVE"

VERDICT_ORDER = [ALLOWED, CONDITIONAL, ILLUSORY, FORBIDDEN, SPECULATIVE]
VERDICT_EMOJI = {
    ALLOWED:     "\u2705",  # green check
    CONDITIONAL: "\u26A0\uFE0F",   # warning
    ILLUSORY:    "\U0001F47B",      # ghost
    FORBIDDEN:   "\u274C",  # red X
    SPECULATIVE: "\U0001F52E",      # crystal ball
}


@dataclass
class Verdict:
    axis: str          # GR / QM / Causality
    ruling: str        # short label
    explanation: str   # 1-3 sentences


@dataclass
class FTLMechanism:
    number: int
    name: str
    description: str
    gr: Verdict
    qm: Verdict
    causality: Verdict
    overall: str       # one of VERDICT constants
    references: List[str] = field(default_factory=list)


# ── Database of 15 mechanisms ─────────────────────────────────────

MECHANISMS: List[FTLMechanism] = [

    # 1 ── Tachyons
    FTLMechanism(
        number=1,
        name="Tachyons",
        description=(
            "Hypothetical particles with imaginary rest mass (m^2 < 0) that "
            "always travel faster than light. In special relativity, the energy-"
            "momentum relation E^2 = p^2 c^2 + m^2 c^4 permits real energy for "
            "imaginary m when v > c. The Feinberg reinterpretation (1967) treats "
            "them as a consistent extension of SR kinematics. However, tachyonic "
            "fields in QFT signal vacuum instability rather than real superluminal "
            "particles: the field rolls to a true vacuum via tachyon condensation "
            "(as in open string field theory)."
        ),
        gr=Verdict("GR", "Permitted kinematics",
                   "Special relativity allows v > c solutions with imaginary mass. "
                   "The Lorentz group has spacelike representations. No GR inconsistency "
                   "at the kinematic level."),
        qm=Verdict("QM", "Vacuum unstable",
                   "Tachyonic fields (m^2 < 0) produce exponentially growing modes, "
                   "signaling vacuum instability. The 'tachyon' is not a particle but "
                   "a signal that the vacuum is at a local maximum. Tachyon condensation "
                   "rolls to the true vacuum (Sen 1999, Zwiebach 2000)."),
        causality=Verdict("Causality", "Violated",
                          "A tachyon emitted in one frame can be received before emission "
                          "in a boosted frame (Tolman antitelephone, 1917). If tachyons "
                          "carry information, closed timelike signal paths exist."),
        overall=FORBIDDEN,
        references=["Feinberg (1967) Phys Rev 159:1089", "Sen (1999) JHEP 9912:027"],
    ),

    # 2 ── Alcubierre warp drive
    FTLMechanism(
        number=2,
        name="Alcubierre Warp Drive",
        description=(
            "A spacetime geometry proposed by Alcubierre (1994) that contracts space "
            "ahead of a 'warp bubble' and expands it behind, allowing the bubble to "
            "effectively travel at arbitrary velocity while the interior remains locally "
            "flat. The passenger experiences no acceleration or time dilation. The metric "
            "is an exact solution to Einstein's field equations, but the required stress-"
            "energy tensor has negative energy density everywhere on the bubble wall, "
            "violating all classical energy conditions."
        ),
        gr=Verdict("GR", "Valid metric solution",
                   "The Alcubierre metric is an exact solution of Einstein's field "
                   "equations. GR imposes no speed limit on how fast coordinates can "
                   "shift -- the constraint is on the matter content, not the geometry."),
        qm=Verdict("QM", "Requires exotic matter",
                   "The stress-energy tensor violates the weak energy condition (WEC). "
                   "Quantum fields can violate WEC locally (Casimir effect), but quantum "
                   "energy inequalities (Ford-Roman 1995) severely constrain the magnitude "
                   "and duration. Van Den Broeck (1999) reduced the energy from ~10^64 J "
                   "to ~solar-mass, still far beyond any known source of negative energy."),
        causality=Verdict("Causality", "CTC risk",
                          "Finazzi, Liberati & Barcelo (2009) showed that two warp bubbles "
                          "passing each other can form closed timelike curves. Krasnikov "
                          "argued that any two-way FTL scheme generically permits CTCs. "
                          "Whether a 'chronology protection' mechanism intervenes is open."),
        overall=CONDITIONAL,
        references=[
            "Alcubierre (1994) Class Quantum Grav 11:L73",
            "Finazzi, Liberati & Barcelo (2009) Phys Rev D 79:124017",
        ],
    ),

    # 3 ── Wormholes
    FTLMechanism(
        number=3,
        name="Wormholes (Einstein-Rosen Bridge)",
        description=(
            "Topological shortcuts connecting distant regions of spacetime (or different "
            "universes). Einstein and Rosen (1935) found bridge solutions in Schwarzschild "
            "geometry, but these pinch off too fast to traverse. Morris and Thorne (1988) "
            "showed that a traversable wormhole requires matter violating the averaged null "
            "energy condition (ANEC). The throat must be threaded with exotic matter to "
            "keep it open. Visser (1995) analyzed thin-shell constructions and the amount "
            "of exotic matter needed."
        ),
        gr=Verdict("GR", "Solutions exist",
                   "Morris-Thorne (1988) constructed traversable wormhole metrics as valid "
                   "GR solutions. The topology is allowed; Einstein's equations constrain "
                   "the required stress-energy but do not forbid the geometry per se."),
        qm=Verdict("QM", "Needs negative energy",
                   "Traversability requires ANEC violation. Quantum fields can violate "
                   "pointwise energy conditions (Casimir effect), but quantum energy "
                   "inequalities limit the available negative energy. Casimir-scale "
                   "negative energy (~10^-4 N/m) is many orders of magnitude too small "
                   "for macroscopic traversability."),
        causality=Verdict("Causality", "CTC possible",
                          "If one wormhole mouth is accelerated or placed in a gravitational "
                          "potential (differential aging), a traversable wormhole becomes a "
                          "time machine (Morris, Thorne & Yurtsever 1988). Hawking's "
                          "chronology protection conjecture (1992) suggests quantum back-"
                          "reaction destroys the wormhole before CTCs form, but this is "
                          "unproven."),
        overall=CONDITIONAL,
        references=[
            "Morris & Thorne (1988) Am J Phys 56:395",
            "Visser (1995) Lorentzian Wormholes, Springer",
        ],
    ),

    # 4 ── Quantum Entanglement
    FTLMechanism(
        number=4,
        name="Quantum Entanglement (EPR)",
        description=(
            "Entangled particles exhibit correlations that cannot be explained by local "
            "hidden variables (Bell 1964, experimentally confirmed by Aspect 1982, "
            "Hensen+ 2015). Measuring one particle instantaneously constrains the other's "
            "state regardless of distance. However, the outcomes are random -- no "
            "information is encoded in any single measurement. The no-signaling theorem "
            "(Ghirardi+ 1980) proves that reduced density matrices of the distant particle "
            "are independent of local measurement choices, making FTL communication "
            "impossible within standard QM."
        ),
        gr=Verdict("GR", "Not applicable",
                   "Entanglement is a quantum phenomenon with no direct GR analog. "
                   "Relativistic QFT (algebraic QFT) rigorously incorporates entanglement "
                   "while preserving Lorentz covariance and microcausality."),
        qm=Verdict("QM", "Real nonlocality",
                   "Bell inequality violations are experimentally confirmed to >100 sigma "
                   "(Hensen+ 2015 loophole-free). The correlations are genuinely nonlocal "
                   "in the Bell sense. But this is 'passion at a distance' (Shimony), "
                   "not signaling."),
        causality=Verdict("Causality", "No-signaling theorem",
                          "The no-signaling theorem guarantees that no superluminal "
                          "information transfer is possible via entanglement alone. "
                          "The marginal statistics at each detector are independent of "
                          "distant measurement settings. Any apparent FTL scheme requires "
                          "a classical side-channel at v <= c."),
        overall=FORBIDDEN,
        references=[
            "Bell (1964) Physics 1:195",
            "Hensen et al. (2015) Nature 526:682 (loophole-free Bell test)",
        ],
    ),

    # 5 ── Quantum Tunneling (Hartman effect)
    FTLMechanism(
        number=5,
        name="Quantum Tunneling (Hartman Effect)",
        description=(
            "The Hartman effect (1962) shows that the group delay for a particle "
            "tunneling through a barrier becomes independent of barrier width for "
            "thick barriers, implying arbitrarily large 'tunneling velocities.' "
            "Experiments (Steinberg+ 1993, Nimtz 1994) measured apparently superluminal "
            "microwave transmission through evanescent barriers. However, Winful (2006) "
            "showed that the group delay measures dwell time (energy storage), not a "
            "propagation velocity. The signal front -- the earliest detectable disturbance "
            "-- always propagates at v <= c."
        ),
        gr=Verdict("GR", "Not applicable",
                   "Tunneling is a non-relativistic QM phenomenon. In relativistic QFT, "
                   "the Kramers-Kronig relations and microcausality ensure the retarded "
                   "Green's function vanishes outside the lightcone."),
        qm=Verdict("QM", "Hartman effect real",
                   "The barrier-width-independent group delay is a genuine QM prediction, "
                   "experimentally confirmed. But 'group delay' for evanescent waves does "
                   "not correspond to the transit time of a localizable particle or signal."),
        causality=Verdict("Causality", "Signal velocity <= c",
                          "Winful (2006) demonstrated that the group delay reflects energy "
                          "storage time in the barrier, not superluminal propagation. The "
                          "signal front velocity (Brillouin, Sommerfeld) is always <= c. "
                          "No information is transmitted faster than light."),
        overall=ILLUSORY,
        references=[
            "Hartman (1962) J Appl Phys 33:3427",
            "Winful (2006) Phys Rep 436:1",
        ],
    ),

    # 6 ── Cherenkov radiation
    FTLMechanism(
        number=6,
        name="Cherenkov Radiation",
        description=(
            "When a charged particle moves through a dielectric medium faster than the "
            "phase velocity of light in that medium (v > c/n, where n is the refractive "
            "index), it emits electromagnetic radiation in a cone -- Cherenkov radiation. "
            "This is the optical analog of a sonic boom. Discovered by Cherenkov (1934) "
            "and explained by Frank & Tamm (1937, Nobel 1958). The particle exceeds "
            "c_medium = c/n but never exceeds c_vacuum. It is widely used in particle "
            "physics detectors (Super-Kamiokande, IceCube)."
        ),
        gr=Verdict("GR", "Not applicable",
                   "This is an electromagnetic phenomenon in a medium. The vacuum speed "
                   "of light c is never exceeded. GR's lightcone structure is unaffected."),
        qm=Verdict("QM", "Well understood",
                   "Cherenkov radiation is fully described by classical electrodynamics in "
                   "media and QED. The emission rate is given by the Frank-Tamm formula. "
                   "No exotic quantum effects are involved."),
        causality=Verdict("Causality", "No violation",
                          "The particle velocity exceeds c/n, not c. Since the fundamental "
                          "causal speed limit is c (not c/n), no causal paradox arises. "
                          "Information still propagates at v <= c."),
        overall=ALLOWED,
        references=[
            "Cherenkov (1934) Dokl Akad Nauk SSSR 2:451",
            "Frank & Tamm (1937) Dokl Akad Nauk SSSR 14:109",
        ],
    ),

    # 7 ── Phase velocity > c
    FTLMechanism(
        number=7,
        name="Phase Velocity > c",
        description=(
            "The phase velocity v_ph = omega/k of a wave can exceed c in many physical "
            "situations: inside waveguides, in plasma (where v_ph = c/sqrt(1-(omega_p/"
            "omega)^2)), near absorption resonances, and in quantum-mechanical de Broglie "
            "waves (v_ph = c^2/v_group > c always for massive particles). This was "
            "understood since Sommerfeld and Brillouin (1914), who showed that phase "
            "velocity does not carry information or energy. The signal velocity (front "
            "velocity) is always <= c."
        ),
        gr=Verdict("GR", "Not applicable",
                   "Phase velocity is a property of wave kinematics, not spacetime "
                   "structure. GR constrains the propagation of causal signals (null "
                   "geodesics), not the mathematical speed of phase fronts."),
        qm=Verdict("QM", "Standard wave mechanics",
                   "Superluminal phase velocities are standard in dispersive media and "
                   "quantum mechanics. The de Broglie phase velocity of any massive "
                   "particle exceeds c. This carries no physical content beyond the "
                   "dispersion relation."),
        causality=Verdict("Causality", "No information carried",
                          "A monochromatic wave with v_ph > c carries no information "
                          "(it has existed for all time by definition). Modulating it to "
                          "encode information creates a wave packet whose group and front "
                          "velocities obey v <= c. Brillouin (1960) proved this rigorously."),
        overall=ILLUSORY,
        references=[
            "Sommerfeld (1914) Ann Phys 44:177",
            "Brillouin (1960) Wave Propagation and Group Velocity, Academic Press",
        ],
    ),

    # 8 ── Superluminal group velocity
    FTLMechanism(
        number=8,
        name="Superluminal Group Velocity",
        description=(
            "In regions of anomalous dispersion (dn/d_omega < 0, typically near absorption "
            "lines), the group velocity v_g = d_omega/dk can exceed c or even become "
            "negative. Wang, Kuzmich & Dogariu (2000) demonstrated a pulse peak exiting "
            "a cesium gas cell before entering it (v_g ~ -c/310). This does not violate "
            "causality because the pulse is analytic: the leading edge contains all "
            "information about the peak, which is merely reshaped (not advanced) by the "
            "medium. The signal front velocity remains <= c."
        ),
        gr=Verdict("GR", "Not applicable",
                   "Group velocity anomalies occur in dispersive media and do not "
                   "involve spacetime curvature or modifications to the metric."),
        qm=Verdict("QM", "Experimentally demonstrated",
                   "Wang et al. (2000) measured superluminal group velocity in gain-"
                   "assisted anomalous dispersion. The effect is well-described by "
                   "classical electrodynamics and semiclassical QM."),
        causality=Verdict("Causality", "Signal front <= c",
                          "Brillouin's theorem: the front velocity (onset of the signal) "
                          "always equals c in vacuum and <= c in media. The superluminal "
                          "'peak advance' results from pulse reshaping of an analytic "
                          "waveform, not from superluminal information transfer. Stenner+ "
                          "(2003) confirmed this with information-bearing pulses."),
        overall=ILLUSORY,
        references=[
            "Wang, Kuzmich & Dogariu (2000) Nature 406:277",
            "Stenner, Gauthier & Neifeld (2003) Nature 425:695",
        ],
    ),

    # 9 ── Casimir effect
    FTLMechanism(
        number=9,
        name="Casimir Effect (Negative Energy)",
        description=(
            "The Casimir effect (1948) arises from the difference in zero-point energy of "
            "the quantum vacuum between two closely-spaced conducting plates and the "
            "exterior. The energy density between the plates is negative relative to the "
            "unbounded vacuum, producing an attractive force ~ hbar c pi^2 / (240 d^4). "
            "Lamoreaux (1997) confirmed it to ~5% accuracy. This is the only experimentally "
            "verified source of negative energy density, which is the key ingredient "
            "required by warp drives and traversable wormholes. However, quantum energy "
            "inequalities (Ford & Roman 1995) constrain the magnitude and duration of "
            "negative energy, making macroscopic spacetime engineering implausible."
        ),
        gr=Verdict("GR", "Local WEC violation",
                   "The Casimir effect produces stress-energy that violates the weak "
                   "energy condition locally. This demonstrates that classical energy "
                   "conditions are not absolute -- quantum effects can violate them. "
                   "However, the averaged null energy condition (ANEC) may still hold."),
        qm=Verdict("QM", "Experimentally confirmed",
                   "The Casimir force is measured to high precision (Lamoreaux 1997, "
                   "Mohideen & Roy 1998). It is a direct consequence of quantum field "
                   "theory in bounded domains. No controversy about the physics."),
        causality=Verdict("Causality", "Insufficient for FTL",
                          "The negative energy density achievable is ~10^-4 N/m at "
                          "micrometer separations. Ford-Roman quantum inequalities "
                          "constrain: (negative energy) x (duration)^4 <= constant. "
                          "Scaling to macroscopic spacetime engineering (warp bubbles, "
                          "wormhole throats) requires energy densities many orders of "
                          "magnitude beyond what Casimir provides."),
        overall=CONDITIONAL,
        references=[
            "Casimir (1948) Proc K Ned Akad Wet 51:793",
            "Lamoreaux (1997) Phys Rev Lett 78:5",
        ],
    ),

    # 10 ── String T-duality
    FTLMechanism(
        number=10,
        name="String Theory T-Duality",
        description=(
            "T-duality is an exact symmetry of string theory: a string on a compact "
            "dimension of radius R is physically equivalent to a string on radius "
            "l_s^2/R, where l_s is the string length. When R < l_s, the dual description "
            "has R' > l_s, implying a minimum observable length ~ l_s (Planck scale). "
            "This suggests that sub-Planckian distances are 'mapped' to super-Planckian "
            "ones, potentially altering the notion of locality and causality at the "
            "smallest scales. However, T-duality is a duality of descriptions, not a "
            "mechanism for FTL signal transmission."
        ),
        gr=Verdict("GR", "Modifies Planck-scale geometry",
                   "T-duality implies that classical GR geometry breaks down below the "
                   "string scale. The minimum length l_s replaces the point-particle "
                   "notion. At macroscopic scales, GR is recovered as a low-energy limit."),
        qm=Verdict("QM", "Consistent within string theory",
                   "T-duality is an exact perturbative symmetry (proven for bosonic and "
                   "type II strings). It is part of the larger U-duality web. No internal "
                   "inconsistency."),
        causality=Verdict("Causality", "Unclear implications",
                          "T-duality reshuffles winding and momentum modes but does not "
                          "provide a mechanism to send signals faster than light. The "
                          "implications for macroscopic causality are indirect at best. "
                          "String field theory preserves target-space causality in known "
                          "formulations."),
        overall=SPECULATIVE,
        references=[
            "Polchinski (1998) String Theory, Cambridge Univ Press",
            "Giveon, Porrati & Rabinovici (1994) Phys Rep 244:77",
        ],
    ),

    # 11 ── Cosmic inflation / metric expansion
    FTLMechanism(
        number=11,
        name="Cosmic Inflation / Metric Expansion",
        description=(
            "In standard FLRW cosmology, the metric expansion of space causes distant "
            "galaxies to recede at velocities v_rec = H_0 d that exceed c beyond the "
            "Hubble radius (d > c/H_0 ~ 14.4 Gly). During inflation, space expanded "
            "exponentially, with points separating at >> c. This is not 'motion through "
            "space' but expansion of the metric itself. The CMB photons we observe were "
            "emitted from regions now receding at ~3.2c. No local Lorentz violation occurs, "
            "and no information is transmitted between causally disconnected regions."
        ),
        gr=Verdict("GR", "Standard cosmology",
                   "Metric expansion at v > c is a generic feature of FLRW solutions. "
                   "It is a coordinate statement about comoving observers, not a violation "
                   "of SR. The Milne and de Sitter solutions illustrate this clearly."),
        qm=Verdict("QM", "Consistent",
                   "Inflationary cosmology (Guth 1981, Linde 1982) is driven by a scalar "
                   "field (inflaton) with standard QFT dynamics. Quantum fluctuations during "
                   "inflation seed the CMB anisotropy spectrum, confirmed by Planck."),
        causality=Verdict("Causality", "No local violation",
                          "Superluminal recession does not enable FTL communication. "
                          "Causally disconnected regions cannot exchange signals -- the "
                          "particle horizon defines the causal boundary. The expansion "
                          "rate is not a signal velocity."),
        overall=ALLOWED,
        references=[
            "Guth (1981) Phys Rev D 23:347",
            "Davis & Lineweaver (2004) PASA 21:97",
        ],
    ),

    # 12 ── Krasnikov tube
    FTLMechanism(
        number=12,
        name="Krasnikov Tube",
        description=(
            "The Krasnikov tube (1995) is a modification of the spacetime metric along "
            "the worldline of an outbound traveler, creating a 'tube' through which the "
            "return trip can be made in arbitrarily short time. Unlike the Alcubierre "
            "drive, the tube is created by the outbound trip (at v <= c) and only used "
            "for the return. It requires exotic matter (negative energy) to maintain, "
            "similar to wormholes. Krasnikov specifically designed it to be causally "
            "safe: a single tube cannot create CTCs because it is one-directional."
        ),
        gr=Verdict("GR", "Valid solution",
                   "The Krasnikov metric is an exact solution of Einstein's field equations "
                   "with an exotic stress-energy source. The spacetime is globally "
                   "hyperbolic, which is a stronger causality condition than many "
                   "alternatives."),
        qm=Verdict("QM", "Requires exotic matter",
                   "Like all known traversable FTL solutions, the stress-energy tensor "
                   "violates energy conditions. The same quantum inequality constraints "
                   "that limit the Casimir effect apply. The required negative energy is "
                   "large (though less characterized than for warp drives)."),
        causality=Verdict("Causality", "One-way safe, two-tube risk",
                          "A single Krasnikov tube preserves causality by construction "
                          "(it is unidirectional). However, Everett & Roman (1997) showed "
                          "that two overlapping tubes in opposite directions can create "
                          "CTCs, reducing it to the same causality problem as other FTL "
                          "proposals."),
        overall=CONDITIONAL,
        references=[
            "Krasnikov (1995) Phys Rev D 57:4760",
            "Everett & Roman (1997) Phys Rev D 56:2100",
        ],
    ),

    # 13 ── Variable speed of light
    FTLMechanism(
        number=13,
        name="Variable Speed of Light (VSL)",
        description=(
            "VSL theories propose that the speed of light was significantly higher in "
            "the early universe, offering an alternative to cosmic inflation for solving "
            "the horizon and flatness problems. Moffat (1993) proposed spontaneous "
            "Lorentz violation in the early universe; Magueijo (2000) formulated a "
            "bimetric theory with a dynamical c. These theories modify the foundations "
            "of both GR and QFT, since c enters as a structural constant in the Lorentz "
            "group. The observational status is inconclusive: some VSL models predict "
            "different CMB spectra from inflation, but current data does not distinguish "
            "them."
        ),
        gr=Verdict("GR", "Requires modified GR",
                   "VSL theories replace standard GR with bimetric or scalar-tensor "
                   "theories where c is promoted to a dynamical field. This breaks "
                   "local Lorentz invariance (at least in the early universe). The "
                   "Einstein equivalence principle is modified."),
        qm=Verdict("QM", "Modified dispersion",
                   "A varying c changes the dispersion relation E^2 = p^2 c(t)^2 + m^2 "
                   "c(t)^4, affecting particle physics, vacuum structure, and potentially "
                   "the fine-structure constant. Constraints from quasar absorption spectra "
                   "(Webb+ 1999) on Delta_alpha/alpha are at the 10^-5 level."),
        causality=Verdict("Causality", "Redefines the barrier",
                          "If c itself varies, the 'speed limit' is no longer a fixed "
                          "constant but a dynamical field. Causality must be reformulated "
                          "in terms of the local value of c(t,x). Whether this enables "
                          "effective FTL (relative to the current c) depends on the specific "
                          "model and is not well-defined in general."),
        overall=SPECULATIVE,
        references=[
            "Moffat (1993) Int J Mod Phys D 2:351",
            "Magueijo (2003) Rep Prog Phys 66:2025",
        ],
    ),

    # 14 ── Noncommutative geometry
    FTLMechanism(
        number=14,
        name="Noncommutative Geometry Spacetime",
        description=(
            "In noncommutative geometry (NCG), spacetime coordinates satisfy [x^mu, x^nu] "
            "= i theta^{mu nu}, introducing a fundamental length scale sqrt(theta) ~ l_P. "
            "This 'fuzziness' modifies the UV structure of field theories, replacing point-"
            "like interactions with smeared ones. NCG naturally arises in certain limits of "
            "string theory (Seiberg-Witten 1999). Modified dispersion relations in NCG "
            "field theories can yield energy-dependent propagation speeds, potentially "
            "allowing high-energy photons to travel slightly faster (or slower) than the "
            "low-energy speed of light."
        ),
        gr=Verdict("GR", "Modified at Planck scale",
                   "NCG replaces the smooth manifold with a noncommutative algebra at "
                   "short distances. Classical GR is recovered in the commutative limit "
                   "(theta -> 0). The modification is suppressed by (E/E_P)^2."),
        qm=Verdict("QM", "Modified dispersion relations",
                   "NCG field theories produce energy-dependent speed of light: "
                   "v(E) ~ c(1 + xi (E/E_P)^n) where xi and n are model-dependent. "
                   "This is testable via gamma-ray burst time delays (Fermi LAT data "
                   "constrains E_QG > 10^19 GeV for linear modifications)."),
        causality=Verdict("Causality", "Unclear",
                          "Energy-dependent speed of light could in principle allow "
                          "high-energy signals to arrive 'before' low-energy ones over "
                          "cosmological distances. Whether this constitutes a true "
                          "causality violation depends on whether a preferred frame exists "
                          "and on the precise form of the modified dispersion relation."),
        overall=SPECULATIVE,
        references=[
            "Seiberg & Witten (1999) JHEP 9909:032",
            "Amelino-Camelia (2013) Living Rev Relativity 16:5",
        ],
    ),

    # 15 ── Loop quantum gravity
    FTLMechanism(
        number=15,
        name="Loop Quantum Gravity (LQG)",
        description=(
            "LQG quantizes spacetime itself: area and volume are discrete, with "
            "eigenvalues proportional to l_P^2 and l_P^3 (Rovelli & Smolin 1995). "
            "The continuum is replaced by spin networks (Penrose) evolving via spin "
            "foams. A major prediction is modified dispersion relations at high energies: "
            "E^2 = p^2 c^2 + m^2 c^4 + eta p^2 (pc/E_P)^n, which could make the "
            "effective speed of light energy-dependent. This has been constrained (but "
            "not excluded) by gamma-ray burst observations (Amelino-Camelia 1998, "
            "Abdo+ 2009)."
        ),
        gr=Verdict("GR", "Replaced by spin foams",
                   "LQG does not modify GR but replaces it at the Planck scale with "
                   "a fundamentally quantum geometry. Classical GR emerges as the "
                   "semiclassical limit. The theory resolves singularities (big bounce "
                   "replacing big bang, Ashtekar+ 2006)."),
        qm=Verdict("QM", "Modified dispersion predicted",
                   "Discrete spacetime structure at the Planck scale generically "
                   "modifies the dispersion relation. The leading correction is "
                   "proportional to (E/E_P)^n with n=1 or n=2 depending on the model. "
                   "Fermi LAT constrains n=1 models severely (Abdo+ 2009)."),
        causality=Verdict("Causality", "Possible Lorentz violation",
                          "If the dispersion relation is modified, Lorentz invariance is "
                          "broken (or deformed, in DSR approaches). This could in "
                          "principle allow superluminal propagation for ultra-high-energy "
                          "particles. Current constraints push any effect to very high "
                          "energies (E > 10^17 GeV for quadratic modifications)."),
        overall=SPECULATIVE,
        references=[
            "Rovelli & Smolin (1995) Nucl Phys B 442:593",
            "Amelino-Camelia (1998) Nature 393:763",
        ],
    ),
]


# ── Display helpers ────────────────────────────────────────────────

SEP    = "=" * 72
SUBSEP = "-" * 72


def print_mechanism(m: FTLMechanism) -> None:
    """Print full details for one mechanism."""
    emoji = VERDICT_EMOJI.get(m.overall, "")
    print(f"\n{SEP}")
    print(f"  [{m.number:2d}] {m.name}  {emoji} {m.overall}")
    print(SEP)
    print()

    # Description
    for line in _wrap(m.description, width=72):
        print(f"  {line}")
    print()

    # Three axes
    for v in [m.gr, m.qm, m.causality]:
        print(f"  {SUBSEP}")
        print(f"  {v.axis}: {v.ruling}")
        print(f"  {SUBSEP}")
        for line in _wrap(v.explanation, width=68):
            print(f"    {line}")
        print()

    # References
    print(f"  References:")
    for ref in m.references:
        print(f"    - {ref}")
    print()


def _wrap(text: str, width: int = 72) -> List[str]:
    """Simple word-wrap."""
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        if current and len(current) + 1 + len(w) > width:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}" if current else w
    if current:
        lines.append(current)
    return lines


def print_summary_table(mechanisms: List[FTLMechanism]) -> None:
    """Print compact verdict table."""
    print(f"\n{SEP}")
    print("  FTL TRIBUNAL — SUMMARY TABLE")
    print(SEP)
    print()
    hdr = f"  {'#':>2}  {'Mechanism':<35} {'GR':<22} {'QM':<22} {'Causality':<22} {'VERDICT':<13}"
    print(hdr)
    print(f"  {'--':>2}  {'---':<35} {'--':<22} {'--':<22} {'---------':<22} {'-------':<13}")
    for m in mechanisms:
        emoji = VERDICT_EMOJI.get(m.overall, "")
        print(
            f"  {m.number:>2}  {m.name:<35} "
            f"{m.gr.ruling:<22} "
            f"{m.qm.ruling:<22} "
            f"{m.causality.ruling:<22} "
            f"{emoji} {m.overall}"
        )
    print()


def print_statistics(mechanisms: List[FTLMechanism]) -> None:
    """Print verdict breakdown."""
    print(f"  {SUBSEP}")
    print("  STATISTICS")
    print(f"  {SUBSEP}")
    counts = {}
    for v in VERDICT_ORDER:
        counts[v] = sum(1 for m in mechanisms if m.overall == v)
    total = len(mechanisms)
    for v in VERDICT_ORDER:
        bar = "#" * (counts[v] * 4)
        emoji = VERDICT_EMOJI.get(v, "")
        print(f"    {emoji} {v:<13} {counts[v]:>2}/{total}  {bar}")
    print()

    # Percentages
    print(f"    Genuine FTL possible:       "
          f"{counts[ALLOWED]}/{total} "
          f"({100*counts[ALLOWED]/total:.0f}%) -- but these are not 'real' FTL")
    print(f"    Conditionally possible:     "
          f"{counts[CONDITIONAL]}/{total} "
          f"({100*counts[CONDITIONAL]/total:.0f}%) -- require exotic matter / unknown physics")
    print(f"    Illusory (not real FTL):     "
          f"{counts[ILLUSORY]}/{total} "
          f"({100*counts[ILLUSORY]/total:.0f}%)")
    print(f"    Forbidden by physics:       "
          f"{counts[FORBIDDEN]}/{total} "
          f"({100*counts[FORBIDDEN]/total:.0f}%)")
    print(f"    Speculative (unknown):      "
          f"{counts[SPECULATIVE]}/{total} "
          f"({100*counts[SPECULATIVE]/total:.0f}%)")
    print()


def print_what_would_it_take(mechanisms: List[FTLMechanism]) -> None:
    """Common requirements for CONDITIONAL mechanisms."""
    cond = [m for m in mechanisms if m.overall == CONDITIONAL]
    if not cond:
        return

    print(f"  {SEP}")
    print("  WHAT WOULD IT TAKE?  (Requirements for CONDITIONAL mechanisms)")
    print(f"  {SEP}")
    print()
    print("  The following mechanisms are valid GR solutions but require physics")
    print("  beyond the Standard Model to be realized:")
    print()
    for m in cond:
        print(f"    [{m.number}] {m.name}")
    print()
    print("  Common requirements:")
    print()
    print("    1. EXOTIC MATTER (negative energy density)")
    print("       - All CONDITIONAL mechanisms require stress-energy violating")
    print("         the weak or averaged null energy condition.")
    print("       - The Casimir effect proves negative energy exists in QFT,")
    print("         but quantum energy inequalities (Ford-Roman) severely limit")
    print("         the magnitude x duration product.")
    print("       - Required: a macroscopic, sustained source of negative energy")
    print("         far beyond Casimir scales.")
    print()
    print("    2. CHRONOLOGY PROTECTION RESOLUTION")
    print("       - Any two-way FTL scheme generically permits CTCs.")
    print("       - Hawking's chronology protection conjecture (1992) suggests")
    print("         quantum backreaction prevents CTC formation, but no proof.")
    print("       - Required: either prove chronology protection (forbidding all")
    print("         FTL), or find a consistent QG theory with CTCs.")
    print()
    print("    3. QUANTUM GRAVITY THEORY")
    print("       - Semiclassical analysis (QFT on curved spacetime) is")
    print("         insufficient: the exotic matter required pushes into the")
    print("         quantum gravity regime.")
    print("       - Required: a complete theory of quantum gravity to determine")
    print("         whether these solutions survive beyond the classical limit.")
    print()
    print("    4. ENGINEERING SCALE-UP")
    print("       - Even if negative energy is available, engineering a")
    print("         macroscopic warp bubble or wormhole throat requires")
    print("         energy densities comparable to stellar masses.")
    print("       - Lentz (2021) proposed a 'positive energy' warp solution,")
    print("         but Fell & Heisenberg (2021) showed it still needs")
    print("         superluminal matter sources.")
    print()
    print("  Bottom line: CONDITIONAL means 'not forbidden by known physics,")
    print("  but requiring physics we do not currently possess.'")
    print()


# ── Main ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="FTL Tribunal: 15 mechanisms judged by GR, QM, and Causality"
    )
    parser.add_argument(
        "--mechanism", "-m", type=int,
        help="Show single mechanism by number (1-15)"
    )
    parser.add_argument(
        "--summary", "-s", action="store_true",
        help="Show verdict summary table only"
    )
    parser.add_argument(
        "--category", "-c", type=str,
        help="Filter by verdict category (allowed/conditional/illusory/forbidden/speculative)"
    )
    args = parser.parse_args()

    # Determine which mechanisms to show
    selected = MECHANISMS

    if args.mechanism is not None:
        idx = args.mechanism
        if idx < 1 or idx > len(MECHANISMS):
            print(f"Error: mechanism number must be 1-{len(MECHANISMS)}, got {idx}")
            sys.exit(1)
        selected = [MECHANISMS[idx - 1]]

    if args.category:
        cat = args.category.upper()
        if cat not in VERDICT_ORDER:
            print(f"Error: category must be one of {VERDICT_ORDER}, got '{cat}'")
            sys.exit(1)
        selected = [m for m in selected if m.overall == cat]
        if not selected:
            print(f"No mechanisms with verdict '{cat}'.")
            sys.exit(0)

    # Print header
    print()
    print(f"  {'=' * 56}")
    print(f"  FTL TRIBUNAL")
    print(f"  15 Faster-Than-Light Mechanisms x 3 Physics Axes")
    print(f"  Axes: General Relativity | Quantum Mechanics | Causality")
    print(f"  {'=' * 56}")

    if args.summary:
        print_summary_table(selected)
        print_statistics(selected)
        return

    # Full output
    for m in selected:
        print_mechanism(m)

    # Summary + stats + what-would-it-take (only for full runs)
    if len(selected) > 1:
        print_summary_table(selected)
        print_statistics(selected)
        print_what_would_it_take(selected)


if __name__ == "__main__":
    main()
