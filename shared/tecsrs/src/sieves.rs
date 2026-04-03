// Phase 1: Arithmetic function sieves — sigma, tau, phi, sopfr, omega, lpf
// 50-200x speedup over per-number Python loops via O(N log N) sieve

use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Smallest prime factor sieve (foundation for all others)
fn build_spf(limit: usize) -> Vec<usize> {
    let mut spf = vec![0usize; limit + 1];
    for i in 2..=limit {
        if spf[i] == 0 {
            // i is prime
            let mut j = i;
            while j <= limit {
                if spf[j] == 0 {
                    spf[j] = i;
                }
                j += i;
            }
        }
    }
    spf
}

/// Sum of divisors: sigma(n) = sum of all divisors of n
fn build_sigma(limit: usize) -> Vec<u64> {
    let mut sigma = vec![0u64; limit + 1];
    for d in 1..=limit {
        let mut multiple = d;
        while multiple <= limit {
            sigma[multiple] += d as u64;
            multiple += d;
        }
    }
    sigma
}

/// Number of divisors: tau(n)
fn build_tau(limit: usize) -> Vec<u64> {
    let mut tau = vec![0u64; limit + 1];
    for d in 1..=limit {
        let mut multiple = d;
        while multiple <= limit {
            tau[multiple] += 1;
            multiple += d;
        }
    }
    tau
}

/// Euler totient function: phi(n)
fn build_phi(limit: usize) -> Vec<u64> {
    let mut phi = vec![0u64; limit + 1];
    for i in 0..=limit {
        phi[i] = i as u64;
    }
    for i in 2..=limit {
        if phi[i] == i as u64 {
            // i is prime
            let mut j = i;
            while j <= limit {
                phi[j] = phi[j] / (i as u64) * ((i as u64) - 1);
                j += i;
            }
        }
    }
    phi
}

/// Sum of prime factors with repetition: sopfr(n)
fn build_sopfr(limit: usize, spf: &[usize]) -> Vec<u64> {
    let mut sopfr = vec![0u64; limit + 1];
    for n in 2..=limit {
        let mut val = n;
        while val > 1 {
            let p = spf[val];
            sopfr[n] += p as u64;
            val /= p;
        }
    }
    sopfr
}

/// Number of distinct prime factors: omega(n)
fn build_omega(limit: usize, spf: &[usize]) -> Vec<u64> {
    let mut omega = vec![0u64; limit + 1];
    for n in 2..=limit {
        let mut val = n;
        while val > 1 {
            let p = spf[val];
            omega[n] += 1;
            while val > 1 && spf[val] == p {
                val /= p;
            }
        }
    }
    omega
}

/// Largest prime factor: lpf(n)
fn build_lpf(limit: usize, spf: &[usize]) -> Vec<u64> {
    let mut lpf = vec![0u64; limit + 1];
    for n in 2..=limit {
        let mut val = n;
        let mut largest = 0usize;
        while val > 1 {
            let p = spf[val];
            if p > largest {
                largest = p;
            }
            while val > 1 && spf[val] == p {
                val /= p;
            }
        }
        lpf[n] = largest as u64;
    }
    lpf
}

/// Full arithmetic tables struct (Rust side)
pub struct ArithTables {
    pub sigma: Vec<u64>,
    pub tau: Vec<u64>,
    pub phi: Vec<u64>,
    pub sopfr: Vec<u64>,
    pub omega: Vec<u64>,
    pub lpf: Vec<u64>,
    pub spf: Vec<usize>,
    pub limit: usize,
}

impl ArithTables {
    pub fn new(limit: usize) -> Self {
        let spf = build_spf(limit);
        ArithTables {
            sigma: build_sigma(limit),
            tau: build_tau(limit),
            phi: build_phi(limit),
            sopfr: build_sopfr(limit, &spf),
            omega: build_omega(limit, &spf),
            lpf: build_lpf(limit, &spf),
            spf,
            limit,
        }
    }
}

// ─── Python bindings ────────────────────────────────────────────

#[pyclass]
pub struct SieveTables {
    inner: ArithTables,
}

#[pymethods]
impl SieveTables {
    #[new]
    fn new(limit: usize) -> Self {
        SieveTables {
            inner: ArithTables::new(limit),
        }
    }

    /// Get sigma(n)
    fn sigma(&self, n: usize) -> PyResult<u64> {
        if n > self.inner.limit {
            return Err(pyo3::exceptions::PyValueError::new_err("n exceeds limit"));
        }
        Ok(self.inner.sigma[n])
    }

    /// Get tau(n)
    fn tau(&self, n: usize) -> PyResult<u64> {
        if n > self.inner.limit {
            return Err(pyo3::exceptions::PyValueError::new_err("n exceeds limit"));
        }
        Ok(self.inner.tau[n])
    }

    /// Get phi(n)
    fn phi(&self, n: usize) -> PyResult<u64> {
        if n > self.inner.limit {
            return Err(pyo3::exceptions::PyValueError::new_err("n exceeds limit"));
        }
        Ok(self.inner.phi[n])
    }

    /// Get sopfr(n)
    fn sopfr(&self, n: usize) -> PyResult<u64> {
        if n > self.inner.limit {
            return Err(pyo3::exceptions::PyValueError::new_err("n exceeds limit"));
        }
        Ok(self.inner.sopfr[n])
    }

    /// Get omega(n)
    fn omega(&self, n: usize) -> PyResult<u64> {
        if n > self.inner.limit {
            return Err(pyo3::exceptions::PyValueError::new_err("n exceeds limit"));
        }
        Ok(self.inner.omega[n])
    }

    /// Get lpf(n) — largest prime factor
    fn lpf(&self, n: usize) -> PyResult<u64> {
        if n > self.inner.limit {
            return Err(pyo3::exceptions::PyValueError::new_err("n exceeds limit"));
        }
        Ok(self.inner.lpf[n])
    }

    /// Return all sigma values as list
    fn sigma_list(&self) -> Vec<u64> {
        self.inner.sigma.clone()
    }

    /// Return all tau values as list
    fn tau_list(&self) -> Vec<u64> {
        self.inner.tau.clone()
    }

    /// Return all phi values as list
    fn phi_list(&self) -> Vec<u64> {
        self.inner.phi.clone()
    }

    /// Return all sopfr values as list
    fn sopfr_list(&self) -> Vec<u64> {
        self.inner.sopfr.clone()
    }

    /// Return all omega values as list
    fn omega_list(&self) -> Vec<u64> {
        self.inner.omega.clone()
    }

    /// Return all lpf values as list
    fn lpf_list(&self) -> Vec<u64> {
        self.inner.lpf.clone()
    }

    /// Get limit
    fn limit(&self) -> usize {
        self.inner.limit
    }

    /// Test identity: find all n in [lo..hi] where lhs(n) == rhs(n)
    /// lhs/rhs are expression strings like "S", "T*P", "n*n", "S+T", "S(T)", etc.
    fn test_identity(&self, lhs: &str, rhs: &str, lo: usize, hi: usize) -> PyResult<Vec<usize>> {
        let limit = hi.min(self.inner.limit);
        let mut hits = Vec::new();
        for n in lo..=limit {
            if n == 0 { continue; }
            let lv = self.eval_expr(lhs, n);
            let rv = self.eval_expr(rhs, n);
            if let (Some(l), Some(r)) = (lv, rv) {
                if l == r {
                    hits.push(n);
                }
            }
        }
        Ok(hits)
    }

    /// Batch uniqueness test: test many (lhs, rhs) pairs, return only those unique to n=6
    fn batch_uniqueness(&self, pairs: Vec<(String, String)>, lo: usize, hi: usize) -> PyResult<Vec<(String, String)>> {
        let limit = hi.min(self.inner.limit);
        let mut unique = Vec::new();
        for (lhs, rhs) in &pairs {
            let mut hits = Vec::new();
            for n in lo..=limit {
                if n == 0 { continue; }
                let lv = self.eval_expr(lhs, n);
                let rv = self.eval_expr(rhs, n);
                if let (Some(l), Some(r)) = (lv, rv) {
                    if l == r {
                        hits.push(n);
                    }
                }
            }
            if hits == vec![6] {
                unique.push((lhs.clone(), rhs.clone()));
            }
        }
        Ok(unique)
    }
}

impl SieveTables {
    /// Evaluate simple expression for a given n
    fn eval_expr(&self, expr: &str, n: usize) -> Option<i64> {
        let t = &self.inner;
        let s = t.sigma[n] as i64;
        let tau = t.tau[n] as i64;
        let phi = t.phi[n] as i64;
        let sp = t.sopfr[n] as i64;
        let om = t.omega[n] as i64;
        let lf = t.lpf[n] as i64;
        let ni = n as i64;

        match expr.trim() {
            // Atomic
            "n" => Some(ni),
            "S" | "sigma" => Some(s),
            "T" | "tau" => Some(tau),
            "P" | "phi" => Some(phi),
            "SP" | "sopfr" => Some(sp),
            "OM" | "omega" => Some(om),
            "LF" | "lpf" => Some(lf),
            // Constants
            "0" => Some(0),
            "1" => Some(1),
            "2" => Some(2),
            "3" => Some(3),
            "4" => Some(4),
            "6" => Some(6),
            "12" => Some(12),
            "720" => Some(720),
            // n operations
            "n*n" | "n^2" => Some(ni * ni),
            "n*n*n" | "n^3" => Some(ni * ni * ni),
            "2*n" => Some(2 * ni),
            "3*n" => Some(3 * ni),
            // Binary: addition
            "S+T" => Some(s + tau),
            "S+P" => Some(s + phi),
            "S+SP" => Some(s + sp),
            "T+P" => Some(tau + phi),
            "T+SP" => Some(tau + sp),
            "P+SP" => Some(phi + sp),
            "n+S" => Some(ni + s),
            "n+T" => Some(ni + tau),
            "n+P" => Some(ni + phi),
            // Binary: subtraction
            "S-T" => Some(s - tau),
            "S-P" => Some(s - phi),
            "S-n" => Some(s - ni),
            "T-P" => Some(tau - phi),
            "n-T" => Some(ni - tau),
            "n-P" => Some(ni - phi),
            // Binary: multiplication
            "S*T" => Some(s * tau),
            "S*P" => Some(s * phi),
            "S*SP" => Some(s * sp),
            "T*P" => Some(tau * phi),
            "T*SP" => Some(tau * sp),
            "P*SP" => Some(phi * sp),
            "n*S" => Some(ni * s),
            "n*T" => Some(ni * tau),
            "n*P" => Some(ni * phi),
            "n*SP" => Some(ni * sp),
            "n*OM" => Some(ni * om),
            "n*S*SP*P" => Some(ni * s * sp * phi),
            // Binary: division (integer only)
            "S/T" => { if tau != 0 && s % tau == 0 { Some(s / tau) } else { None } },
            "S/P" => { if phi != 0 && s % phi == 0 { Some(s / phi) } else { None } },
            "S/n" => { if ni != 0 && s % ni == 0 { Some(s / ni) } else { None } },
            "n/T" => { if tau != 0 && ni % tau == 0 { Some(ni / tau) } else { None } },
            "n*n/T" => { if tau != 0 && (ni*ni) % tau == 0 { Some(ni*ni / tau) } else { None } },
            "T/P" => { if phi != 0 && tau % phi == 0 { Some(tau / phi) } else { None } },
            // Compositions: f(g(n)) — only if g(n) in [1..limit]
            "S(T)" => {
                let v = tau as usize;
                if v >= 1 && v <= t.limit { Some(t.sigma[v] as i64) } else { None }
            },
            "S(P)" => {
                let v = phi as usize;
                if v >= 1 && v <= t.limit { Some(t.sigma[v] as i64) } else { None }
            },
            "T(S)" => {
                let v = s as usize;
                if v >= 1 && v <= t.limit { Some(t.tau[v] as i64) } else { None }
            },
            "T(P)" => {
                let v = phi as usize;
                if v >= 1 && v <= t.limit { Some(t.tau[v] as i64) } else { None }
            },
            "P(S)" => {
                let v = s as usize;
                if v >= 1 && v <= t.limit { Some(t.phi[v] as i64) } else { None }
            },
            "P(T)" => {
                let v = tau as usize;
                if v >= 1 && v <= t.limit { Some(t.phi[v] as i64) } else { None }
            },
            // Combinatorics
            "C(n,2)" => { if ni >= 2 { Some(ni * (ni-1) / 2) } else { None } },
            "C(n,3)" => { if ni >= 3 { Some(ni * (ni-1) * (ni-2) / 6) } else { None } },
            "C(S,2)" => { if s >= 2 { Some(s * (s-1) / 2) } else { None } },
            "n!" => Some(factorial(ni)),
            "(n-1)!" => { if ni >= 1 { Some(factorial(ni-1)) } else { None } },
            "(n-3)!" => { if ni >= 3 { Some(factorial(ni-3)) } else { None } },
            _ => None,
        }
    }
}

fn factorial(n: i64) -> i64 {
    if n <= 1 { return 1; }
    if n > 20 { return i64::MAX; } // overflow guard
    (2..=n).product()
}

/// Standalone function: build all sieve tables and return as dict of lists
#[pyfunction]
pub fn sieve_all(py: Python<'_>, limit: usize) -> PyResult<Py<PyAny>> {
    let tables = ArithTables::new(limit);
    let dict = PyDict::new(py);
    dict.set_item("sigma", tables.sigma)?;
    dict.set_item("tau", tables.tau)?;
    dict.set_item("phi", tables.phi)?;
    dict.set_item("sopfr", tables.sopfr)?;
    dict.set_item("omega", tables.omega)?;
    dict.set_item("lpf", tables.lpf.iter().map(|&x| x as i64).collect::<Vec<_>>())?;
    Ok(dict.into_any().unbind())
}

/// Standalone: sieve sigma only
#[pyfunction]
pub fn sieve_sigma(limit: usize) -> Vec<u64> {
    build_sigma(limit)
}

/// Standalone: sieve tau only
#[pyfunction]
pub fn sieve_tau(limit: usize) -> Vec<u64> {
    build_tau(limit)
}

/// Standalone: sieve phi only
#[pyfunction]
pub fn sieve_phi(limit: usize) -> Vec<u64> {
    build_phi(limit)
}
