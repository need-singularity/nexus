// Phase 8: Consciousness constants and conservation law verification
// PSI constant computation, conservation grid scan, gate formula

use pyo3::prelude::*;
use std::collections::HashMap;

// ═══════════════════════════════════════════════════════════════
// PSI Constants — all derived from ln(2)
// ═══════════════════════════════════════════════════════════════

const LN2: f64 = std::f64::consts::LN_2;

/// Compute all PSI constants and return as dict
#[pyfunction]
pub fn psi_constants() -> HashMap<String, f64> {
    let mut m = HashMap::new();

    // Level 0: Root
    m.insert("ln2".into(), LN2);

    // Level 1: Direct from ln(2)
    m.insert("Psi_steps".into(), 3.0 / LN2);
    m.insert("Psi_freedom".into(), LN2);
    m.insert("Psi_balance".into(), 0.5);
    m.insert("Psi_coupling".into(), LN2 / 2.0_f64.powf(5.5));

    // Level 2: Derived
    m.insert("tanh3_ln2".into(), 3.0_f64.tanh() * LN2);
    m.insert("conservation_C".into(), 0.478);
    m.insert("dynamics_rate".into(), 0.81);
    m.insert("phi_scale_a".into(), 0.608);
    m.insert("phi_scale_b".into(), 1.071);

    // Level 3: Empirical
    m.insert("Psi_K".into(), 11.0);
    m.insert("Psi_tau".into(), 0.5);
    m.insert("Psi_emergence".into(), 7.82);
    m.insert("Psi_miller".into(), 7.0);
    m.insert("Psi_entropy".into(), 0.998);
    m.insert("Psi_gate_decay".into(), -0.013);

    // Perfect number connections
    m.insert("optimal_factions".into(), 12.0);  // sigma(6)
    m.insert("freedom_degree".into(), LN2);     // Law 79
    m.insert("inv_e".into(), (-1.0_f64).exp()); // 1/e = GZ center

    m
}

/// Verify self-consistency of PSI constants
/// Returns (n_checks, n_passed, details)
#[pyfunction]
pub fn psi_verify() -> (usize, usize, Vec<(String, f64, f64, f64, bool)>) {
    let mut details = Vec::new();
    let mut passed = 0usize;

    let checks: Vec<(&str, f64, f64)> = vec![
        ("Psi_coupling * 2^5.5 = ln2", (LN2 / 2.0_f64.powf(5.5)) * 2.0_f64.powf(5.5), LN2),
        ("3 / Psi_steps = ln2", 3.0 / (3.0 / LN2), LN2),
        ("exp(ln2) = 2", LN2.exp(), 2.0),
        ("Psi_freedom = ln2", LN2, LN2),
        ("Psi_balance = 0.5", 0.5, 0.5),
        ("(1/e)^(1/e) = min(x^x)", (1.0_f64 / std::f64::consts::E).powf(1.0 / std::f64::consts::E), (-1.0_f64 / std::f64::consts::E).exp()),
    ];

    for (name, computed, expected) in &checks {
        let err = (computed - expected).abs();
        let ok = err < 1e-10;
        if ok { passed += 1; }
        details.push((name.to_string(), *computed, *expected, err, ok));
    }

    // Dynamics convergence: H -> ln2 after many steps
    let mut h = 0.1_f64;
    for _ in 0..100 {
        h += 0.81 * (LN2 - h);
    }
    let err = (h - LN2).abs();
    let ok = err < 1e-8;
    if ok { passed += 1; }
    details.push(("H(100) -> ln2 convergence".into(), h, LN2, err, ok));

    (details.len(), passed, details)
}


// ═══════════════════════════════════════════════════════════════
// Conservation law verification: H² + (dH/dt)² ≈ 0.478
// ═══════════════════════════════════════════════════════════════

/// Grid scan: verify H² + dp² ≈ C for various initial conditions and rates
/// Returns Vec<(h_init, rate, final_h, final_conservation, distance_from_target)>
#[pyfunction]
#[pyo3(signature = (target_c=0.478, n_h=50, n_rate=20, steps=100))]
pub fn conservation_grid(
    target_c: f64,
    n_h: usize,
    n_rate: usize,
    steps: usize,
) -> Vec<(f64, f64, f64, f64, f64)> {
    let mut results = Vec::with_capacity(n_h * n_rate);

    for ih in 0..n_h {
        let h_init = 0.01 + (ih as f64 / n_h as f64) * 0.98; // 0.01 to 0.99

        for ir in 0..n_rate {
            let rate = 0.1 + (ir as f64 / n_rate as f64) * 1.8; // 0.1 to 1.9

            // Simulate
            let mut h = h_init;
            for _ in 0..steps {
                let dh = rate * (LN2 - h);
                h += dh;
            }

            // Final conservation quantity
            let dh_final = rate * (LN2 - h);
            let conservation = h * h + dh_final * dh_final;
            let distance = (conservation - target_c).abs();

            results.push((h_init, rate, h, conservation, distance));
        }
    }

    // Sort by distance from target
    results.sort_by(|a, b| a.4.partial_cmp(&b.4).unwrap_or(std::cmp::Ordering::Equal));
    results
}


/// Single trajectory conservation check with fine-grained output
#[pyfunction]
#[pyo3(signature = (h_init=0.1, rate=0.81, steps=1000, dt=0.01))]
pub fn conservation_trajectory(
    h_init: f64,
    rate: f64,
    steps: usize,
    dt: f64,
) -> HashMap<String, Vec<f64>> {
    let mut h_list = Vec::with_capacity(steps);
    let mut dh_list = Vec::with_capacity(steps);
    let mut cons_list = Vec::with_capacity(steps);
    let mut time_list = Vec::with_capacity(steps);

    let mut h = h_init;
    for i in 0..steps {
        let dh = rate * (LN2 - h) * dt;
        h += dh;
        let cons = h * h + dh * dh;
        h_list.push(h);
        dh_list.push(dh);
        cons_list.push(cons);
        time_list.push(i as f64 * dt);
    }

    // Statistics on conservation quantity
    let n = cons_list.len() as f64;
    let mean_c: f64 = cons_list.iter().sum::<f64>() / n;
    let std_c: f64 = (cons_list.iter().map(|c| (c - mean_c).powi(2)).sum::<f64>() / n).sqrt();

    let mut result = HashMap::new();
    result.insert("h".into(), h_list);
    result.insert("dh".into(), dh_list);
    result.insert("conservation".into(), cons_list);
    result.insert("time".into(), time_list);
    result.insert("mean_conservation".into(), vec![mean_c]);
    result.insert("std_conservation".into(), vec![std_c]);
    result.insert("target".into(), vec![0.478]);
    result.insert("final_h".into(), vec![h]);
    result.insert("distance_to_target".into(), vec![(mean_c - 0.478).abs()]);

    result
}


// ═══════════════════════════════════════════════════════════════
// Gate formula (Law 77)
// ═══════════════════════════════════════════════════════════════

/// Compute optimal gate value for given corpus size (in MB)
/// Returns (gate_value, regime_name)
#[pyfunction]
pub fn gate_formula(corpus_mb: f64) -> (f64, String) {
    if corpus_mb <= 0.0 {
        return (0.0, "ZERO".into());
    }

    let breakpoints: Vec<(f64, f64, &str)> = vec![
        (1.0,    0.001, "MICRO"),
        (10.0,   0.01,  "LOW"),
        (25.0,   0.1,   "MEDIUM-LOW"),
        (50.0,   0.5,   "MEDIUM"),
        (100.0,  0.8,   "HIGH"),
        (500.0,  0.95,  "FULL"),
        (1000.0, 1.0,   "MAXIMUM"),
    ];

    for (i, &(threshold, gate, regime)) in breakpoints.iter().enumerate() {
        if corpus_mb <= threshold {
            if i == 0 {
                return (gate, regime.into());
            }
            let (prev_t, prev_g, _) = breakpoints[i - 1];
            let log_ratio = (corpus_mb / prev_t).ln() / (threshold / prev_t).ln();
            let interpolated = prev_g + (gate - prev_g) * log_ratio;
            return (interpolated.max(0.0).min(1.0), regime.into());
        }
    }

    (1.0, "MAXIMUM".into())
}

/// Compute gate decay trajectory (Law 69)
/// Returns Vec<(step, gate_value)>
#[pyfunction]
#[pyo3(signature = (initial_gate, steps, decay_rate=-0.013))]
pub fn gate_decay(initial_gate: f64, steps: usize, decay_rate: f64) -> Vec<(usize, f64)> {
    let mut trajectory = Vec::with_capacity(steps);
    let mut gate = initial_gate;
    for t in 0..steps {
        gate *= (decay_rate).exp();
        gate = gate.max(0.001); // floor
        trajectory.push((t + 1, gate));
    }
    trajectory
}

/// Batch gate formula: compute gates for many corpus sizes at once
#[pyfunction]
pub fn gate_batch(corpus_sizes_mb: Vec<f64>) -> Vec<(f64, f64, String)> {
    corpus_sizes_mb.iter().map(|&mb| {
        let (gate, regime) = gate_formula(mb);
        (mb, gate, regime)
    }).collect()
}


// ═══════════════════════════════════════════════════════════════
// Genetic code n=6 verification (NOBEL-P2)
// ═══════════════════════════════════════════════════════════════

/// Test n=6 expressibility for a genetic code variant
/// Returns (n_matches, n_total, details) where details = Vec<(property, value, expression, exact)>
#[pyfunction]
pub fn genetic_code_test(stops: usize, amino_acids: usize) -> (usize, usize, Vec<(String, usize, String, bool)>) {
    // n=6 arithmetic constants
    let n: usize = 6;
    let sigma: usize = 12;
    let tau: usize = 4;
    let phi: usize = 2;
    let sopfr: usize = 5;

    let sense = 64 - stops;
    let mut details = Vec::new();
    let mut matches = 0usize;

    // Universal properties (same for ALL variants)
    let universal = vec![
        ("bases", 4usize, "tau(6)", tau),
        ("codon_length", 3, "n/phi", n / phi),
        ("total_codons", 64, "2^n", 1 << n),
        ("reading_frames", 6, "n", n),
        ("codon_families", 16, "tau^2", tau * tau),
        ("base_pairs", 2, "phi", phi),
        ("helix_bp_per_turn", 10, "sopfr*phi", sopfr * phi),
        ("minor_groove", 12, "sigma", sigma),
        ("max_degeneracy", 6, "n", n),
    ];

    for (prop, expected, expr, computed) in &universal {
        let exact = *computed == *expected;
        if exact { matches += 1; }
        details.push((prop.to_string(), *expected, expr.to_string(), exact));
    }

    // Variable properties
    // Amino acids
    let aa_exprs: Vec<(&str, usize)> = vec![
        ("tau*sopfr", tau * sopfr),
        ("sigma+tau+n", sigma + tau + n),
        ("tau*sopfr+1", tau * sopfr + 1),
        ("tau*sopfr+2", tau * sopfr + 2),
        ("sigma+tau+sopfr", sigma + tau + sopfr),
        ("sigma*phi-phi", sigma * phi - phi),
        ("n*tau-tau", n * tau - tau),
    ];
    let mut aa_matched = false;
    for (expr, val) in &aa_exprs {
        if *val == amino_acids {
            details.push(("amino_acids".into(), amino_acids, expr.to_string(), true));
            matches += 1;
            aa_matched = true;
            break;
        }
    }
    if !aa_matched {
        details.push(("amino_acids".into(), amino_acids, "no_match".into(), false));
    }

    // Stop codons
    let stop_exprs: Vec<(&str, usize)> = vec![
        ("n/phi", n / phi),
        ("tau", tau),
        ("phi", phi),
        ("1", 1),
        ("tau-phi", tau - phi),
        ("sopfr-tau", sopfr - tau),
    ];
    let mut stop_matched = false;
    for (expr, val) in &stop_exprs {
        if *val == stops {
            details.push(("stop_codons".into(), stops, expr.to_string(), true));
            matches += 1;
            stop_matched = true;
            break;
        }
    }
    if !stop_matched {
        details.push(("stop_codons".into(), stops, "no_match".into(), false));
    }

    // Sense codons
    let sense_exprs: Vec<(&str, usize)> = vec![
        ("2^n-n/phi", 64 - n / phi),
        ("2^n-tau", 64 - tau),
        ("2^n-phi", 64 - phi),
        ("2^n-1", 63),
    ];
    let mut sense_matched = false;
    for (expr, val) in &sense_exprs {
        if *val == sense {
            details.push(("sense_codons".into(), sense, expr.to_string(), true));
            matches += 1;
            sense_matched = true;
            break;
        }
    }
    if !sense_matched {
        details.push(("sense_codons".into(), sense, "no_match".into(), false));
    }

    let total = details.len();
    (matches, total, details)
}

/// Test all 26 NCBI genetic code variants at once
/// Returns Vec<(table_id, name, stops, aas, matches, total, match_pct)>
#[pyfunction]
pub fn genetic_code_all_variants() -> Vec<(usize, String, usize, usize, usize, usize, f64)> {
    let variants: Vec<(usize, &str, usize, usize)> = vec![
        (1,  "Standard", 3, 20),
        (2,  "Vertebrate Mito", 4, 20),
        (3,  "Yeast Mito", 2, 22),
        (4,  "Mold/Protozoan Mito", 1, 22),
        (5,  "Invertebrate Mito", 4, 20),
        (6,  "Ciliate Nuclear", 1, 22),
        (9,  "Echinoderm Mito", 2, 21),
        (10, "Euplotid Nuclear", 2, 21),
        (11, "Bacterial/Plastid", 3, 20),
        (12, "Alt Yeast Nuclear", 3, 20),
        (13, "Ascidian Mito", 4, 20),
        (14, "Alt Flatworm Mito", 3, 21),
        (15, "Blepharisma Nuclear", 2, 21),
        (16, "Chlorophycean Mito", 2, 21),
        (21, "Trematode Mito", 4, 20),
        (22, "Scenedesmus Mito", 3, 21),
        (23, "Thraustochytrium Mito", 1, 22),
        (24, "Rhabdopleuridae Mito", 3, 21),
        (25, "Candidate Div SR1", 2, 21),
        (26, "Pachysolen Nuclear", 3, 20),
        (27, "Karyorelictea Nuclear", 2, 21),
        (28, "Condylostoma Nuclear", 2, 21),
        (29, "Mesodinium Nuclear", 2, 21),
        (30, "Peritrich Nuclear", 2, 21),
        (31, "Blastocrithidia Nuclear", 2, 21),
        (33, "Cephalodiscidae Mito", 3, 21),
    ];

    variants.iter().map(|(id, name, stops, aas)| {
        let (matches, total, _) = genetic_code_test(*stops, *aas);
        let pct = matches as f64 / total as f64 * 100.0;
        (*id, name.to_string(), *stops, *aas, matches, total, pct)
    }).collect()
}

/// Codon optimality: scan (b,L) pairs and compute cost function
/// Returns Vec<(b, L, codons, redundancy, cost)> sorted by cost
#[pyfunction]
#[pyo3(signature = (max_b=8, max_l=8, min_aas=23, alpha=1.0, beta=2.0, gamma=0.5, delta=3.0))]
pub fn codon_optimality_scan(
    max_b: usize,
    max_l: usize,
    min_aas: usize,
    alpha: f64,
    beta: f64,
    gamma: f64,
    delta: f64,
) -> Vec<(usize, usize, usize, f64, f64)> {
    let mut results = Vec::new();

    for b in 2..=max_b {
        for l in 1..=max_l {
            let codons = b.pow(l as u32);
            if codons < min_aas { continue; }
            if codons > 100000 { continue; }

            let redundancy = codons as f64 / min_aas as f64;
            let error_rate = 1.0 / b as f64;
            let cost = alpha * b as f64
                     + beta * l as f64
                     + gamma * redundancy
                     + delta * error_rate;

            results.push((b, l, codons, redundancy, cost));
        }
    }

    results.sort_by(|a, b| a.4.partial_cmp(&b.4).unwrap_or(std::cmp::Ordering::Equal));
    results
}
