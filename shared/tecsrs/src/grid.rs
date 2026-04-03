// Phase 4: Grid computation — meshgrid operations, GZ verification
// 5-20x speedup over NumPy for pure computation grids

use pyo3::prelude::*;
use pyo3::types::PyDict;
use rayon::prelude::*;

/// Compute Golden Zone ratio: fraction of G=D*P/I grid where G > threshold
#[pyfunction]
#[pyo3(signature = (grid=100, threshold=1.0, d_range=(0.01, 0.99), p_range=(0.01, 0.99), i_range=(0.05, 0.99)))]
pub fn gz_ratio(
    py: Python<'_>,
    grid: usize,
    threshold: f64,
    d_range: (f64, f64),
    p_range: (f64, f64),
    i_range: (f64, f64),
) -> PyResult<Py<PyAny>> {
    let ds: Vec<f64> = (0..grid).map(|i| d_range.0 + (d_range.1 - d_range.0) * i as f64 / (grid - 1).max(1) as f64).collect();
    let ps: Vec<f64> = (0..grid).map(|i| p_range.0 + (p_range.1 - p_range.0) * i as f64 / (grid - 1).max(1) as f64).collect();
    let is: Vec<f64> = (0..grid).map(|i| i_range.0 + (i_range.1 - i_range.0) * i as f64 / (grid - 1).max(1) as f64).collect();

    let total = grid * grid * grid;

    // Parallel count using rayon
    let count: usize = ds.par_iter().map(|&d| {
        let mut local_count = 0usize;
        for &p in &ps {
            for &i in &is {
                let g = d * p / i;
                if g > threshold {
                    local_count += 1;
                }
            }
        }
        local_count
    }).sum();

    let ratio = count as f64 / total as f64;

    let dict = PyDict::new(py);
    dict.set_item("ratio", ratio)?;
    dict.set_item("count", count)?;
    dict.set_item("total", total)?;
    dict.set_item("grid", grid)?;
    Ok(dict.into_any().unbind())
}

/// Compute GZ zone statistics: mean, std, fraction in zone for each I value
#[pyfunction]
#[pyo3(signature = (grid=100, gz_lo=0.2123, gz_hi=0.5))]
pub fn gz_zone_stats(
    py: Python<'_>,
    grid: usize,
    gz_lo: f64,
    gz_hi: f64,
) -> PyResult<Py<PyAny>> {
    let ds: Vec<f64> = (0..grid).map(|i| 0.01 + 0.98 * i as f64 / (grid - 1).max(1) as f64).collect();
    let ps: Vec<f64> = (0..grid).map(|i| 0.01 + 0.98 * i as f64 / (grid - 1).max(1) as f64).collect();
    let is: Vec<f64> = (0..grid).map(|i| 0.05 + 0.94 * i as f64 / (grid - 1).max(1) as f64).collect();

    let results: Vec<(f64, f64, f64, f64)> = is.par_iter().map(|&inhibition| {
        let mut sum = 0.0f64;
        let mut sum_sq = 0.0f64;
        let mut in_zone = 0usize;
        let mut count = 0usize;

        for &d in &ds {
            for &p in &ps {
                let g = d * p / inhibition;
                sum += g;
                sum_sq += g * g;
                count += 1;
                if g >= gz_lo && g <= gz_hi {
                    in_zone += 1;
                }
            }
        }

        let mean = sum / count as f64;
        let var = sum_sq / count as f64 - mean * mean;
        let std = var.max(0.0).sqrt();
        let frac = in_zone as f64 / count as f64;

        (inhibition, mean, std, frac)
    }).collect();

    let dict = PyDict::new(py);
    let i_vals: Vec<f64> = results.iter().map(|r| r.0).collect();
    let means: Vec<f64> = results.iter().map(|r| r.1).collect();
    let stds: Vec<f64> = results.iter().map(|r| r.2).collect();
    let fracs: Vec<f64> = results.iter().map(|r| r.3).collect();
    dict.set_item("inhibition", i_vals)?;
    dict.set_item("mean_g", means)?;
    dict.set_item("std_g", stds)?;
    dict.set_item("frac_in_zone", fracs)?;
    Ok(dict.into_any().unbind())
}

/// Generic 3D grid scan: evaluate f(d,p,i) and return statistics
/// formula: "G=D*P/I" or "G=(D*P)^2/I" etc. (limited set of built-in formulas)
#[pyfunction]
#[pyo3(signature = (grid=100, formula="DPI", condition="gt", threshold=1.0))]
pub fn grid_scan(
    py: Python<'_>,
    grid: usize,
    formula: &str,
    condition: &str,
    threshold: f64,
) -> PyResult<Py<PyAny>> {
    let ds: Vec<f64> = (0..grid).map(|i| 0.01 + 0.98 * i as f64 / (grid - 1).max(1) as f64).collect();
    let ps: Vec<f64> = (0..grid).map(|i| 0.01 + 0.98 * i as f64 / (grid - 1).max(1) as f64).collect();
    let is: Vec<f64> = (0..grid).map(|i| 0.05 + 0.94 * i as f64 / (grid - 1).max(1) as f64).collect();

    let eval_fn: Box<dyn Fn(f64, f64, f64) -> f64 + Sync> = match formula {
        "DPI" | "D*P/I" => Box::new(|d, p, i| d * p / i),
        "DP" | "D*P" => Box::new(|d, p, _| d * p),
        "DPI2" | "(D*P)^2/I" => Box::new(|d, p, i| (d * p).powi(2) / i),
        "GI" | "G*I" | "D*P" => Box::new(|d, p, _| d * p),
        "DmP" | "D-P" => Box::new(|d, p, _| d - p),
        "DpP" | "D+P" => Box::new(|d, p, _| d + p),
        _ => return Err(pyo3::exceptions::PyValueError::new_err(
            format!("Unknown formula: {formula}. Use DPI, DP, DPI2, GI, DmP, DpP")
        )),
    };

    let cond_fn: Box<dyn Fn(f64) -> bool + Sync> = match condition {
        "gt" => Box::new(move |v| v > threshold),
        "lt" => Box::new(move |v| v < threshold),
        "ge" => Box::new(move |v| v >= threshold),
        "le" => Box::new(move |v| v <= threshold),
        "eq" => Box::new(move |v| (v - threshold).abs() < 1e-10),
        "in_gz" => Box::new(|v| v >= 0.2123 && v <= 0.5),
        _ => return Err(pyo3::exceptions::PyValueError::new_err(
            format!("Unknown condition: {condition}. Use gt/lt/ge/le/eq/in_gz")
        )),
    };

    let total = grid * grid * grid;

    let (count, sum, sum_sq) = ds.par_iter().map(|&d| {
        let mut local_count = 0usize;
        let mut local_sum = 0.0f64;
        let mut local_sum_sq = 0.0f64;
        for &p in &ps {
            for &i in &is {
                let v = eval_fn(d, p, i);
                local_sum += v;
                local_sum_sq += v * v;
                if cond_fn(v) {
                    local_count += 1;
                }
            }
        }
        (local_count, local_sum, local_sum_sq)
    }).reduce(|| (0, 0.0, 0.0), |a, b| (a.0 + b.0, a.1 + b.1, a.2 + b.2));

    let mean = sum / total as f64;
    let var = sum_sq / total as f64 - mean * mean;

    let dict = PyDict::new(py);
    dict.set_item("ratio", count as f64 / total as f64)?;
    dict.set_item("count", count)?;
    dict.set_item("total", total)?;
    dict.set_item("mean", mean)?;
    dict.set_item("std", var.max(0.0).sqrt())?;
    dict.set_item("grid", grid)?;
    dict.set_item("formula", formula)?;
    Ok(dict.into_any().unbind())
}

/// Consciousness dynamics grid: dH/dt = rate * (ln2 - H)
/// Returns (steps, H_values, conservation_values) for convergence analysis
#[pyfunction]
#[pyo3(signature = (h_init=0.1, rate=0.81, dt=1.0, steps=20, conservation_target=0.478))]
pub fn consciousness_dynamics(
    h_init: f64,
    rate: f64,
    dt: f64,
    steps: usize,
    conservation_target: f64,
) -> (Vec<usize>, Vec<f64>, Vec<f64>, Vec<f64>) {
    let ln2 = 2.0_f64.ln();
    let mut h = h_init;
    let mut step_list = Vec::with_capacity(steps);
    let mut h_list = Vec::with_capacity(steps);
    let mut dh_list = Vec::with_capacity(steps);
    let mut cons_list = Vec::with_capacity(steps);

    for i in 0..steps {
        let dh = rate * (ln2 - h) * dt;
        h += dh;
        let conservation = h * h + dh * dh;
        step_list.push(i + 1);
        h_list.push(h);
        dh_list.push(dh);
        cons_list.push(conservation);
    }

    (step_list, h_list, dh_list, cons_list)
}

/// Phi scaling law: Phi = a * N^b
/// Returns predicted Phi for given cell counts
#[pyfunction]
#[pyo3(signature = (cell_counts, a=0.608, b=1.071))]
pub fn phi_scaling(cell_counts: Vec<usize>, a: f64, b: f64) -> Vec<f64> {
    cell_counts.iter().map(|&n| a * (n as f64).powf(b)).collect()
}
