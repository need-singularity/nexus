// Phase 2: DFS/BFS expression search engine
// 10-50x speedup over Python nested loops

use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};

/// A constant with name, value, and island classification
#[derive(Clone, Debug)]
struct Constant {
    name: String,
    value: f64,
    island: u8, // 0=A(rational), 1=B(integer), 2=C(log), 3=D(transcendental), 4=E(consciousness)
}

/// Search result
#[pyclass(skip_from_py_object)]
#[derive(Clone, Debug)]
pub struct SearchMatch {
    #[pyo3(get)]
    pub target: String,
    #[pyo3(get)]
    pub target_val: f64,
    #[pyo3(get)]
    pub formula: String,
    #[pyo3(get)]
    pub formula_val: f64,
    #[pyo3(get)]
    pub error: f64,
    #[pyo3(get)]
    pub error_pct: f64,
    #[pyo3(get)]
    pub islands: String,
    #[pyo3(get)]
    pub n_islands: usize,
    #[pyo3(get)]
    pub significance: f64,
    #[pyo3(get)]
    pub is_exact: bool,
}

const EXACT_THRESHOLD: f64 = 1e-12;
const MAX_VALUE: f64 = 1e12;

/// Apply all binary operations to two values
fn binary_ops(av: f64, an: &str, bv: f64, bn: &str) -> Vec<(f64, String)> {
    let mut results = Vec::with_capacity(10);

    // Addition
    let v = av + bv;
    if v.is_finite() && v.abs() < MAX_VALUE {
        results.push((v, format!("({an}+{bn})")));
    }

    // Subtraction both ways
    let v = av - bv;
    if v.is_finite() && v.abs() < MAX_VALUE {
        results.push((v, format!("({an}-{bn})")));
    }
    let v = bv - av;
    if v.is_finite() && v.abs() < MAX_VALUE && (av - bv).abs() > 1e-15 {
        results.push((v, format!("({bn}-{an})")));
    }

    // Multiplication
    let v = av * bv;
    if v.is_finite() && v.abs() < MAX_VALUE {
        results.push((v, format!("({an}*{bn})")));
    }

    // Division both ways
    if bv.abs() > 1e-15 {
        let v = av / bv;
        if v.is_finite() && v.abs() < MAX_VALUE {
            results.push((v, format!("({an}/{bn})")));
        }
    }
    if av.abs() > 1e-15 {
        let v = bv / av;
        if v.is_finite() && v.abs() < MAX_VALUE {
            results.push((v, format!("({bn}/{an})")));
        }
    }

    // Power (with careful overflow checks)
    if av.abs() > 0.0 && bv.abs() < 100.0 {
        let v = av.powf(bv);
        if v.is_finite() && v.abs() < MAX_VALUE {
            results.push((v, format!("({an}^{bn})")));
        }
    }
    if bv.abs() > 0.0 && av.abs() < 100.0 {
        let v = bv.powf(av);
        if v.is_finite() && v.abs() < MAX_VALUE {
            results.push((v, format!("({bn}^{an})")));
        }
    }

    // Logarithm
    if av > 0.0 && av != 1.0 && bv > 0.0 {
        let v = bv.ln() / av.ln();
        if v.is_finite() && v.abs() < MAX_VALUE {
            results.push((v, format!("log_{an}({bn})")));
        }
    }
    if bv > 0.0 && bv != 1.0 && av > 0.0 {
        let v = av.ln() / bv.ln();
        if v.is_finite() && v.abs() < MAX_VALUE {
            results.push((v, format!("log_{bn}({an})")));
        }
    }

    results
}

/// Apply unary operations
fn unary_ops(v: f64, name: &str) -> Vec<(f64, String)> {
    let mut results = Vec::with_capacity(5);
    if v > 0.0 {
        let r = v.ln();
        if r.is_finite() { results.push((r, format!("ln({name})"))); }
        let r = v.sqrt();
        if r.is_finite() { results.push((r, format!("sqrt({name})"))); }
    }
    if v.abs() < 50.0 {
        let r = v.exp();
        if r.is_finite() && r.abs() < MAX_VALUE {
            results.push((r, format!("exp({name})")));
        }
    }
    if v.abs() > 1e-15 {
        let r = 1.0 / v;
        if r.is_finite() && r.abs() < MAX_VALUE {
            results.push((r, format!("1/{name}")));
        }
    }
    results
}

/// Expression with tracked islands
#[derive(Clone)]
struct Expr {
    value: f64,
    name: String,
    islands: u8, // bitmask: bit 0=A, bit 1=B, bit 2=C, bit 3=D, bit 4=E
}

fn island_str(mask: u8) -> String {
    let labels = ['A', 'B', 'C', 'D', 'E'];
    let parts: Vec<String> = (0..5)
        .filter(|&i| mask & (1 << i) != 0)
        .map(|i| labels[i].to_string())
        .collect();
    parts.join("+")
}

fn count_islands(mask: u8) -> usize {
    (0..5).filter(|&i| mask & (1 << i) != 0).count()
}

/// Build expressions up to given depth
fn build_level(constants: &[Constant], depth: usize) -> Vec<Expr> {
    // Level 0: constants + unary ops
    let mut pool: Vec<Expr> = Vec::new();
    let mut seen: HashSet<i64> = HashSet::new(); // dedup by rounded value * 1e8

    for c in constants {
        let key = (c.value * 1e8).round() as i64;
        if seen.insert(key) {
            pool.push(Expr {
                value: c.value,
                name: c.name.clone(),
                islands: 1 << c.island,
            });
        }
        // Unary ops on constants
        for (uv, un) in unary_ops(c.value, &c.name) {
            let key = (uv * 1e8).round() as i64;
            if seen.insert(key) {
                pool.push(Expr {
                    value: uv,
                    name: un,
                    islands: 1 << c.island,
                });
            }
        }
    }

    let base_len = pool.len();

    for _d in 1..=depth {
        let current_len = pool.len();
        let mut new_exprs: Vec<Expr> = Vec::new();

        // Combine pool[0..current_len] x pool[0..base_len] to avoid exponential blowup
        for i in 0..current_len {
            for j in 0..base_len {
                let a = &pool[i];
                let b = &pool[j];
                let merged = a.islands | b.islands;

                for (rv, rn) in binary_ops(a.value, &a.name, b.value, &b.name) {
                    let key = (rv * 1e8).round() as i64;
                    if seen.insert(key) {
                        new_exprs.push(Expr {
                            value: rv,
                            name: rn,
                            islands: merged,
                        });
                    }
                }
            }
        }

        pool.extend(new_exprs);
    }

    pool
}

/// Check expressions against targets
fn check_targets(
    exprs: &[Expr],
    targets: &HashMap<String, f64>,
    threshold: f64,
) -> Vec<SearchMatch> {
    let mut matches = Vec::new();

    for expr in exprs {
        if !expr.value.is_finite() || expr.value.abs() < 1e-15 {
            continue;
        }
        for (tname, &tval) in targets {
            if tval.abs() < 1e-15 { continue; }
            let rel_err = ((expr.value - tval) / tval).abs();
            if rel_err < threshold {
                // Skip trivial: expression is just the target name
                if expr.name == *tname { continue; }
                let n_isl = count_islands(expr.islands);
                let sig = (n_isl as f64) * 10.0 + (-((rel_err + 1e-15).log10()));
                matches.push(SearchMatch {
                    target: tname.clone(),
                    target_val: tval,
                    formula: expr.name.clone(),
                    formula_val: expr.value,
                    error: rel_err,
                    error_pct: rel_err * 100.0,
                    islands: island_str(expr.islands),
                    n_islands: n_isl,
                    significance: sig,
                    is_exact: rel_err < EXACT_THRESHOLD,
                });
            }
        }
    }

    // Sort by significance descending
    matches.sort_by(|a, b| b.significance.partial_cmp(&a.significance).unwrap_or(std::cmp::Ordering::Equal));
    matches
}

// ─── Python bindings ────────────────────────────────────────────

/// DFS expression search engine
#[pyclass]
pub struct DfsEngine {
    constants: Vec<Constant>,
    targets: HashMap<String, f64>,
}

#[pymethods]
impl DfsEngine {
    #[new]
    fn new() -> Self {
        DfsEngine {
            constants: Vec::new(),
            targets: HashMap::new(),
        }
    }

    /// Add a constant: name, value, island (0-4: A=rational, B=integer, C=log, D=transcendental, E=consciousness)
    fn add_constant(&mut self, name: String, value: f64, island: u8) {
        self.constants.push(Constant { name, value, island: island.min(4) });
    }

    /// Add a target: name, value
    fn add_target(&mut self, name: String, value: f64) {
        self.targets.insert(name, value);
    }

    /// Load default TECS-L constants (islands A-D)
    fn load_defaults(&mut self) {
        // Island A: Rational fractions
        let a = vec![
            ("1/2", 0.5), ("1/3", 1.0/3.0), ("1/6", 1.0/6.0),
            ("5/6", 5.0/6.0), ("2/3", 2.0/3.0), ("1/7", 1.0/7.0),
        ];
        for (n, v) in a { self.constants.push(Constant { name: n.to_string(), value: v, island: 0 }); }

        // Island B: Integers / fine-structure
        let b = vec![
            ("6", 6.0), ("12", 12.0), ("4", 4.0), ("8", 8.0),
            ("17", 17.0), ("137", 137.0), ("720", 720.0),
        ];
        for (n, v) in b { self.constants.push(Constant { name: n.to_string(), value: v, island: 1 }); }

        // Island C: Logarithmic / entropy
        let c = vec![
            ("ln(4/3)", (4.0_f64/3.0).ln()), ("ln2", 2.0_f64.ln()),
            ("ln3", 3.0_f64.ln()), ("ln17", 17.0_f64.ln()),
        ];
        for (n, v) in c { self.constants.push(Constant { name: n.to_string(), value: v, island: 2 }); }

        // Island D: Transcendental
        let d = vec![
            ("e", std::f64::consts::E), ("1/e", 1.0/std::f64::consts::E),
            ("pi", std::f64::consts::PI), ("phi", (1.0 + 5.0_f64.sqrt()) / 2.0),
        ];
        for (n, v) in d { self.constants.push(Constant { name: n.to_string(), value: v, island: 3 }); }

        // Island E: Consciousness constants (from anima Laws 63-79)
        let e = vec![
            ("Psi_steps", 3.0 / 2.0_f64.ln()),      // 4.328 evolution number
            ("Psi_coupling", 2.0_f64.ln() / (2.0_f64.powf(5.5))),  // 0.01534
            ("Psi_freedom", 2.0_f64.ln()),            // 0.6931 Law 79
            ("Psi_balance", 0.5),                      // structural equilibrium
            ("conservation", 0.478),                    // H^2+dp^2
            ("dynamics_rate", 0.81),                    // dH/dt coefficient
            ("tanh3_ln2", 3.0_f64.tanh() * 2.0_f64.ln()), // 0.6895 saturation
        ];
        for (n, v) in e { self.constants.push(Constant { name: n.to_string(), value: v, island: 4 }); }
    }

    /// Load default targets (mathematical + physical constants)
    fn load_default_targets(&mut self) {
        let tgts = vec![
            ("euler_gamma", 0.5772156649),
            ("catalan", 0.9159655941),
            ("apery", 1.2020569031),
            ("feigenbaum_delta", 4.6692016091),
            ("feigenbaum_alpha", 2.5029078751),
            ("khinchin", 2.6854520011),
            ("glaisher", 1.2824271291),
            ("twin_prime", 0.6601618158),
            ("landau_ramanujan", 0.7642362350),
            ("sqrt2", std::f64::consts::SQRT_2),
            ("sqrt3", 3.0_f64.sqrt()),
            ("sqrt5", 5.0_f64.sqrt()),
            ("ln10", 10.0_f64.ln()),
            ("alpha_em", 1.0/137.036),
            ("cmb_temp", 2.725),
            ("dark_energy", 0.683),
            ("dark_matter", 0.268),
            ("hubble_reduced", 0.674),
            ("proton_electron_ratio", 1836.15267),
            ("omega_b", 0.0493),
            // Consciousness constants (from anima)
            ("Psi_steps", 3.0 / 2.0_f64.ln()),
            ("Psi_coupling", 2.0_f64.ln() / 2.0_f64.powf(5.5)),
            ("phi_scale_coeff", 0.608),
            ("phi_scale_exp", 1.071),
            ("Psi_emergence", 7.82),
            ("Psi_K", 11.0),
        ];
        for (n, v) in tgts {
            self.targets.insert(n.to_string(), v);
        }
    }

    /// Run DFS search at given depth and threshold
    fn search(&self, depth: usize, threshold: f64) -> Vec<SearchMatch> {
        let exprs = build_level(&self.constants, depth);
        check_targets(&exprs, &self.targets, threshold)
    }

    /// Run search and return only cross-island matches (n_islands >= 2)
    fn search_cross(&self, depth: usize, threshold: f64) -> Vec<SearchMatch> {
        self.search(depth, threshold)
            .into_iter()
            .filter(|m| m.n_islands >= 2)
            .collect()
    }

    /// Return expression count at given depth (for progress estimation)
    fn expression_count(&self, depth: usize) -> usize {
        build_level(&self.constants, depth).len()
    }
}

/// Standalone DFS search with default constants
#[pyfunction]
pub fn dfs_search(depth: usize, threshold: f64) -> Vec<SearchMatch> {
    let mut engine = DfsEngine::new();
    engine.load_defaults();
    engine.load_default_targets();
    engine.search(depth, threshold)
}

/// Reachability: find all integers reachable from operands within max_ops
#[pyfunction]
pub fn reachability(py: Python<'_>, operands: Vec<f64>, max_ops: usize, lo: i64, hi: i64) -> PyResult<Py<PyAny>> {
    let mut pool: HashMap<i64, (f64, String)> = HashMap::new();

    // Layer 0: operands
    for &op in &operands {
        let key = op.round() as i64;
        pool.insert(key, (op, format!("{}", op)));
    }

    for _step in 0..max_ops {
        let items: Vec<(f64, String)> = pool.values().cloned().collect();
        let mut new_entries: Vec<(i64, f64, String)> = Vec::new();

        for (i, (av, an)) in items.iter().enumerate() {
            for (bv, bn) in items.iter().skip(i) {
                // +, -, *, /, ^
                let ops_results = vec![
                    (av + bv, format!("({an}+{bn})")),
                    (av - bv, format!("({an}-{bn})")),
                    (bv - av, format!("({bn}-{an})")),
                    (av * bv, format!("({an}*{bn})")),
                ];
                for (val, expr) in ops_results {
                    if val.is_finite() && val.abs() < 1e15 && (val - val.round()).abs() < 1e-9 {
                        let k = val.round() as i64;
                        if k >= lo && k <= hi && !pool.contains_key(&k) {
                            new_entries.push((k, val, expr));
                        }
                    }
                }
                if bv.abs() > 1e-15 {
                    let val = av / bv;
                    if val.is_finite() && (val - val.round()).abs() < 1e-9 {
                        let k = val.round() as i64;
                        if k >= lo && k <= hi && !pool.contains_key(&k) {
                            new_entries.push((k, val, format!("({an}/{bn})")));
                        }
                    }
                }
                if av.abs() > 1e-15 {
                    let val = bv / av;
                    if val.is_finite() && (val - val.round()).abs() < 1e-9 {
                        let k = val.round() as i64;
                        if k >= lo && k <= hi && !pool.contains_key(&k) {
                            new_entries.push((k, val, format!("({bn}/{an})")));
                        }
                    }
                }
                if bv.abs() < 20.0 && *av > 0.0 {
                    let val = av.powf(*bv);
                    if val.is_finite() && val.abs() < 1e15 && (val - val.round()).abs() < 1e-9 {
                        let k = val.round() as i64;
                        if k >= lo && k <= hi && !pool.contains_key(&k) {
                            new_entries.push((k, val, format!("({an}^{bn})")));
                        }
                    }
                }
            }
        }
        for (k, v, expr) in new_entries {
            pool.entry(k).or_insert((v, expr));
        }
    }

    // Return dict of integer -> expression
    let dict = pyo3::types::PyDict::new(py);
    for (k, (_, expr)) in &pool {
        if *k >= lo && *k <= hi {
            dict.set_item(k, expr)?;
        }
    }
    Ok(dict.into_any().unbind())
}
