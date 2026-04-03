// Phase 3: Monte Carlo simulation — Texas Sharpshooter, bootstrap CI
// 5-15x speedup over Python loops

use pyo3::prelude::*;
use pyo3::types::PyDict;
use rand::prelude::*;
use rand_chacha::ChaCha8Rng;

/// Texas Sharpshooter test result
#[pyclass(skip_from_py_object)]
#[derive(Clone, Debug)]
pub struct TexasResult {
    #[pyo3(get)]
    pub real_hits: usize,
    #[pyo3(get)]
    pub random_mean: f64,
    #[pyo3(get)]
    pub random_std: f64,
    #[pyo3(get)]
    pub p_value: f64,
    #[pyo3(get)]
    pub z_score: f64,
    #[pyo3(get)]
    pub histogram: Vec<usize>,
    #[pyo3(get)]
    pub n_trials: usize,
}

/// Claim structure for Texas Sharpshooter
struct Claim {
    target: f64,
    tolerance: f64,
}

/// Check if any combination of random constants matches target within tolerance
fn count_random_hits(constants: &[f64], claims: &[Claim]) -> usize {
    let mut hits = 0;
    for claim in claims {
        let target = claim.target;
        let tol = claim.tolerance;
        let mut found = false;

        // Single constant match
        for &c in constants {
            if ((c - target) / target).abs() < tol {
                found = true;
                break;
            }
        }

        if !found {
            // Binary ops between pairs
            'outer: for i in 0..constants.len() {
                for j in 0..constants.len() {
                    if i == j { continue; }
                    let a = constants[i];
                    let b = constants[j];
                    let candidates = [
                        a + b,
                        a - b,
                        if b.abs() > 1e-15 { a / b } else { f64::NAN },
                        a * b,
                    ];
                    for &v in &candidates {
                        if v.is_finite() && target.abs() > 1e-15 && ((v - target) / target).abs() < tol {
                            found = true;
                            break 'outer;
                        }
                    }
                }
            }
        }

        if found { hits += 1; }
    }
    hits
}

/// Run Texas Sharpshooter test
#[pyfunction]
#[pyo3(signature = (real_hits, targets, tolerances, n_constants=14, n_trials=5000, seed=42))]
pub fn texas_sharpshooter(
    real_hits: usize,
    targets: Vec<f64>,
    tolerances: Vec<f64>,
    n_constants: usize,
    n_trials: usize,
    seed: u64,
) -> TexasResult {
    let claims: Vec<Claim> = targets.iter().zip(tolerances.iter())
        .map(|(&t, &tol)| Claim { target: t, tolerance: tol })
        .collect();

    let scales = [0.01, 0.1, 1.0, 10.0, 100.0];
    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    let mut random_hits_vec = vec![0usize; n_trials];

    for trial in 0..n_trials {
        // Generate random constants
        let mut constants = Vec::with_capacity(n_constants);
        for _ in 0..n_constants {
            let scale_idx = rng.gen_range(0..scales.len());
            let val: f64 = rng.gen::<f64>() * scales[scale_idx] * 2.0;
            constants.push(val);
        }
        random_hits_vec[trial] = count_random_hits(&constants, &claims);
    }

    // Statistics
    let sum: f64 = random_hits_vec.iter().map(|&x| x as f64).sum();
    let mean = sum / n_trials as f64;
    let var: f64 = random_hits_vec.iter().map(|&x| {
        let d = x as f64 - mean;
        d * d
    }).sum::<f64>() / n_trials as f64;
    let std = var.sqrt();

    let p_value = random_hits_vec.iter().filter(|&&x| x >= real_hits).count() as f64 / n_trials as f64;
    let z_score = if std > 0.0 { (real_hits as f64 - mean) / std } else { f64::INFINITY };

    // Histogram (0..max_hits+1)
    let max_h = *random_hits_vec.iter().max().unwrap_or(&0);
    let mut histogram = vec![0usize; max_h + 1];
    for &h in &random_hits_vec {
        histogram[h] += 1;
    }

    TexasResult {
        real_hits,
        random_mean: mean,
        random_std: std,
        p_value,
        z_score,
        histogram,
        n_trials,
    }
}

/// Bootstrap confidence interval
#[pyfunction]
#[pyo3(signature = (data, n_boot=10000, ci=0.95, seed=42))]
pub fn bootstrap_ci(
    py: Python<'_>,
    data: Vec<f64>,
    n_boot: usize,
    ci: f64,
    seed: u64,
) -> PyResult<Py<PyAny>> {
    let n = data.len();
    if n == 0 {
        return Err(pyo3::exceptions::PyValueError::new_err("empty data"));
    }

    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    let mut boot_means = Vec::with_capacity(n_boot);

    for _ in 0..n_boot {
        let mut sum = 0.0;
        for _ in 0..n {
            let idx = rng.gen_range(0..n);
            sum += data[idx];
        }
        boot_means.push(sum / n as f64);
    }

    boot_means.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

    let alpha = 1.0 - ci;
    let lo_idx = ((alpha / 2.0) * n_boot as f64) as usize;
    let hi_idx = ((1.0 - alpha / 2.0) * n_boot as f64).min((n_boot - 1) as f64) as usize;

    let estimate: f64 = data.iter().sum::<f64>() / n as f64;

    let dict = PyDict::new(py);
    dict.set_item("estimate", estimate)?;
    dict.set_item("ci_lo", boot_means[lo_idx])?;
    dict.set_item("ci_hi", boot_means[hi_idx])?;
    dict.set_item("ci_level", ci)?;
    dict.set_item("n_boot", n_boot)?;
    Ok(dict.into_any().unbind())
}

/// Bootstrap for arbitrary statistic function (median, variance, etc.)
#[pyfunction]
#[pyo3(signature = (data, stat="mean", n_boot=10000, ci=0.95, seed=42))]
pub fn bootstrap_stat(
    py: Python<'_>,
    data: Vec<f64>,
    stat: &str,
    n_boot: usize,
    ci: f64,
    seed: u64,
) -> PyResult<Py<PyAny>> {
    let n = data.len();
    if n == 0 {
        return Err(pyo3::exceptions::PyValueError::new_err("empty data"));
    }

    let stat_fn: Box<dyn Fn(&[f64]) -> f64> = match stat {
        "mean" => Box::new(|s: &[f64]| s.iter().sum::<f64>() / s.len() as f64),
        "median" => Box::new(|s: &[f64]| {
            let mut sorted = s.to_vec();
            sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
            let mid = sorted.len() / 2;
            if sorted.len() % 2 == 0 { (sorted[mid-1] + sorted[mid]) / 2.0 } else { sorted[mid] }
        }),
        "std" => Box::new(|s: &[f64]| {
            let mean = s.iter().sum::<f64>() / s.len() as f64;
            let var = s.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / s.len() as f64;
            var.sqrt()
        }),
        "var" => Box::new(|s: &[f64]| {
            let mean = s.iter().sum::<f64>() / s.len() as f64;
            s.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / s.len() as f64
        }),
        _ => return Err(pyo3::exceptions::PyValueError::new_err(
            format!("Unknown stat: {stat}. Use mean/median/std/var")
        )),
    };

    let estimate = stat_fn(&data);
    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    let mut boot_vals = Vec::with_capacity(n_boot);

    for _ in 0..n_boot {
        let mut sample = Vec::with_capacity(n);
        for _ in 0..n {
            sample.push(data[rng.gen_range(0..n)]);
        }
        boot_vals.push(stat_fn(&sample));
    }

    boot_vals.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

    let alpha = 1.0 - ci;
    let lo_idx = ((alpha / 2.0) * n_boot as f64) as usize;
    let hi_idx = ((1.0 - alpha / 2.0) * n_boot as f64).min((n_boot - 1) as f64) as usize;

    let dict = PyDict::new(py);
    dict.set_item("estimate", estimate)?;
    dict.set_item("ci_lo", boot_vals[lo_idx])?;
    dict.set_item("ci_hi", boot_vals[hi_idx])?;
    dict.set_item("ci_level", ci)?;
    dict.set_item("n_boot", n_boot)?;
    dict.set_item("stat", stat)?;
    Ok(dict.into_any().unbind())
}

/// Permutation test: test if two groups differ significantly
#[pyfunction]
#[pyo3(signature = (group1, group2, n_perms=10000, seed=42))]
pub fn permutation_test(
    py: Python<'_>,
    group1: Vec<f64>,
    group2: Vec<f64>,
    n_perms: usize,
    seed: u64,
) -> PyResult<Py<PyAny>> {
    let n1 = group1.len();
    let n_total = n1 + group2.len();

    let mean1: f64 = group1.iter().sum::<f64>() / n1 as f64;
    let mean2: f64 = group2.iter().sum::<f64>() / group2.len() as f64;
    let observed_diff = (mean1 - mean2).abs();

    let mut combined: Vec<f64> = Vec::with_capacity(n_total);
    combined.extend_from_slice(&group1);
    combined.extend_from_slice(&group2);

    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    let mut count_ge = 0usize;

    for _ in 0..n_perms {
        // Fisher-Yates partial shuffle for first n1 elements
        let mut shuffled = combined.clone();
        for i in 0..n1 {
            let j = rng.gen_range(i..n_total);
            shuffled.swap(i, j);
        }
        let perm_mean1: f64 = shuffled[..n1].iter().sum::<f64>() / n1 as f64;
        let perm_mean2: f64 = shuffled[n1..].iter().sum::<f64>() / (n_total - n1) as f64;
        if (perm_mean1 - perm_mean2).abs() >= observed_diff {
            count_ge += 1;
        }
    }

    let p_value = count_ge as f64 / n_perms as f64;

    // Cohen's d
    let var1: f64 = group1.iter().map(|x| (x - mean1).powi(2)).sum::<f64>() / (n1 as f64 - 1.0).max(1.0);
    let var2: f64 = group2.iter().map(|x| (x - mean2).powi(2)).sum::<f64>() / (group2.len() as f64 - 1.0).max(1.0);
    let pooled_sd = ((var1 + var2) / 2.0).sqrt();
    let cohens_d = if pooled_sd > 0.0 { (mean1 - mean2).abs() / pooled_sd } else { 0.0 };

    let dict = PyDict::new(py);
    dict.set_item("observed_diff", observed_diff)?;
    dict.set_item("p_value", p_value)?;
    dict.set_item("n_perms", n_perms)?;
    dict.set_item("cohens_d", cohens_d)?;
    dict.set_item("mean1", mean1)?;
    dict.set_item("mean2", mean2)?;
    dict.set_item("significant", p_value < 0.05)?;
    Ok(dict.into_any().unbind())
}
