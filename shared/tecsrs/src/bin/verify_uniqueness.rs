/// H-PH-9 Extended Uniqueness Verification
/// Sieve-based bulk computation for large-range searches.
///
/// Tests:
///   1. S(n)=0 search up to 10^6
///   2. Self-decomposition sigma(n)(n+phi(n)) = n*tau(n)^2 up to 10^6
///   3. sigma*phi = n*tau up to 10^7
///   4. Additional uniqueness conditions up to 10^6
///   5. Statistics: S(n) distribution, growth rate
///
/// Usage: cargo run --release --bin verify_uniqueness

use std::time::Instant;

// ─── Sieve functions (duplicated from sieves.rs to avoid PyO3 dep) ───

fn build_sigma(limit: usize) -> Vec<u64> {
    let mut sigma = vec![0u64; limit + 1];
    for d in 1..=limit {
        let mut m = d;
        while m <= limit {
            sigma[m] += d as u64;
            m += d;
        }
    }
    sigma
}

fn build_tau(limit: usize) -> Vec<u64> {
    let mut tau = vec![0u64; limit + 1];
    for d in 1..=limit {
        let mut m = d;
        while m <= limit {
            tau[m] += 1;
            m += d;
        }
    }
    tau
}

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

fn main() {
    let t0 = Instant::now();

    println!("=================================================================");
    println!("  H-PH-9 EXTENDED UNIQUENESS VERIFICATION");
    println!("  Sieve-based bulk computation");
    println!("=================================================================");
    println!();

    // ─── Phase 1: Build sieves ───────────────────────────────────────
    let limit_1m: usize = 1_000_000;
    let limit_10m: usize = 10_000_000;

    println!("[Phase 1] Building arithmetic sieves...");
    let t1 = Instant::now();

    // Build 10^7 sieves for the extended sigma*phi=n*tau test
    let sigma_10m = build_sigma(limit_10m);
    let tau_10m = build_tau(limit_10m);
    let phi_10m = build_phi(limit_10m);
    println!("  Sieves built to {} in {:.2?}", limit_10m, t1.elapsed());
    println!();

    // Aliases for 10^6 range (just slice references)
    let sigma = &sigma_10m[..=limit_1m];
    let tau = &tau_10m[..=limit_1m];
    let phi = &phi_10m[..=limit_1m];

    // ─── Test 1: S(n) = 0 search up to 10^6 ─────────────────────────
    println!("=================================================================");
    println!("  TEST 1: S(n) = 0 search  [n = 1..{}]", limit_1m);
    println!("  S(n) = [sigma*phi - n*tau]^2 + [sigma*(n+phi) - n*tau^2]^2");
    println!("=================================================================");
    let t2 = Instant::now();

    let mut s_zero_solutions: Vec<usize> = Vec::new();
    let mut near_misses: Vec<(usize, u128)> = Vec::new(); // (n, S(n))

    // For statistics: accumulate S(n) by range
    let ranges: [(usize, usize); 5] = [
        (1, 100),
        (101, 1_000),
        (1_001, 10_000),
        (10_001, 100_000),
        (100_001, 1_000_000),
    ];
    let mut range_sum: [f64; 5] = [0.0; 5];
    let mut range_count: [u64; 5] = [0; 5];
    let mut range_min: [u128; 5] = [u128::MAX; 5];
    let mut range_max: [u128; 5] = [0; 5];

    // Histogram buckets: log10(S(n)) in [0, 1), [1, 2), ..., [30+, inf)
    let mut histogram = [0u64; 32];

    for n in 1..=limit_1m {
        let s = sigma[n] as i128;
        let t = tau[n] as i128;
        let p = phi[n] as i128;
        let ni = n as i128;

        let term1 = s * p - ni * t;
        let term2 = s * (ni + p) - ni * t * t;
        let sn = (term1 * term1 + term2 * term2) as u128;

        if sn == 0 {
            s_zero_solutions.push(n);
        } else if sn < 100 {
            near_misses.push((n, sn));
        }

        // Statistics
        for (idx, &(lo, hi)) in ranges.iter().enumerate() {
            if n >= lo && n <= hi {
                let log_s = if sn == 0 { 0.0 } else { (sn as f64).log10() };
                range_sum[idx] += log_s;
                range_count[idx] += 1;
                if sn < range_min[idx] { range_min[idx] = sn; }
                if sn > range_max[idx] { range_max[idx] = sn; }
                break;
            }
        }

        // Histogram
        if sn == 0 {
            histogram[0] += 1;
        } else {
            let bucket = (sn as f64).log10().floor() as usize;
            let bucket = bucket.min(31);
            histogram[bucket] += 1;
        }
    }

    println!("  S(n) = 0 solutions: {:?}", s_zero_solutions);
    if near_misses.is_empty() {
        println!("  Near-misses (S < 100): NONE");
    } else {
        println!("  Near-misses (S < 100):");
        for (n, sn) in &near_misses {
            println!("    n = {}: S(n) = {}", n, sn);
        }
    }
    println!("  Time: {:.2?}", t2.elapsed());
    println!();

    // ─── Test 2: Self-decomposition up to 10^6 ──────────────────────
    println!("=================================================================");
    println!("  TEST 2: Self-decomposition  [n = 1..{}]", limit_1m);
    println!("  sigma(n) * (n + phi(n)) = n * tau(n)^2");
    println!("=================================================================");
    let t3 = Instant::now();

    let mut self_decomp_solutions: Vec<usize> = Vec::new();

    for n in 1..=limit_1m {
        let s = sigma[n] as u128;
        let t = tau[n] as u128;
        let p = phi[n] as u128;
        let ni = n as u128;

        let lhs = s * (ni + p);
        let rhs = ni * t * t;
        if lhs == rhs {
            self_decomp_solutions.push(n);
        }
    }

    println!("  Solutions: {:?}", self_decomp_solutions);
    println!("  Time: {:.2?}", t3.elapsed());
    println!();

    // ─── Test 3: sigma*phi = n*tau up to 10^7 ───────────────────────
    println!("=================================================================");
    println!("  TEST 3: sigma*phi = n*tau  [n = 1..{}]", limit_10m);
    println!("  (R(n) = sigma*phi / (n*tau) = 1)");
    println!("=================================================================");
    let t4 = Instant::now();

    let mut sigma_phi_eq_n_tau: Vec<usize> = Vec::new();

    for n in 1..=limit_10m {
        let s = sigma_10m[n] as u128;
        let t = tau_10m[n] as u128;
        let p = phi_10m[n] as u128;
        let ni = n as u128;

        if s * p == ni * t {
            sigma_phi_eq_n_tau.push(n);
        }
    }

    println!("  Solutions: {:?}", sigma_phi_eq_n_tau);
    println!("  Time: {:.2?}", t4.elapsed());
    println!();

    // ─── Test 4a: sigma/phi = n ─────────────────────────────────────
    println!("=================================================================");
    println!("  TEST 4a: sigma(n) / phi(n) = n  [n = 1..{}]", limit_1m);
    println!("=================================================================");
    let t5 = Instant::now();

    let mut sigma_div_phi_eq_n: Vec<usize> = Vec::new();

    for n in 1..=limit_1m {
        // sigma(n) = n * phi(n) iff sigma(n)/phi(n) = n
        let s = sigma[n] as u128;
        let p = phi[n] as u128;
        let ni = n as u128;

        if p > 0 && s == ni * p {
            sigma_div_phi_eq_n.push(n);
        }
    }

    println!("  Solutions: {:?}", sigma_div_phi_eq_n);
    println!("  Time: {:.2?}", t5.elapsed());
    println!();

    // ─── Test 4b: sigma*phi = n*tau (same as Test 3 but explicit) ───
    // Already done in Test 3. Print confirmation.
    println!("=================================================================");
    println!("  TEST 4b: sigma*phi = n*tau (R(n) = 1)  [n = 1..{}]", limit_1m);
    println!("=================================================================");
    let mut r_eq_1: Vec<usize> = Vec::new();
    for n in 1..=limit_1m {
        let s = sigma[n] as u128;
        let t = tau[n] as u128;
        let p = phi[n] as u128;
        let ni = n as u128;
        if s * p == ni * t {
            r_eq_1.push(n);
        }
    }
    println!("  Solutions: {:?}", r_eq_1);
    println!();

    // ─── Test 4c: Gauge self-decomposition ──────────────────────────
    println!("=================================================================");
    println!("  TEST 4c: Gauge self-decomposition  [n = 1..{}]", limit_1m);
    println!("  (sigma - tau) + (sigma / tau) + R = sigma");
    println!("  where R = sigma*phi / (n*tau)");
    println!("  At n=6: (12-4) + (12/4) + 1 = 8 + 3 + 1 = 12 = sigma");
    println!("=================================================================");
    let t6 = Instant::now();

    let mut gauge_solutions: Vec<usize> = Vec::new();

    for n in 1..=limit_1m {
        let s = sigma[n] as i128;
        let t = tau[n] as i128;
        let p = phi[n] as i128;
        let ni = n as i128;

        // Need sigma/tau to be integer, and R = sigma*phi/(n*tau) to be integer
        if t == 0 || ni == 0 { continue; }
        if s % t != 0 { continue; }
        if (s * p) % (ni * t) != 0 { continue; }

        let s_over_t = s / t;
        let r = (s * p) / (ni * t);
        let lhs = (s - t) + s_over_t + r;

        if lhs == s {
            gauge_solutions.push(n);
        }
    }

    println!("  Solutions: {:?}", gauge_solutions);
    // Verify the n=6 case explicitly
    {
        let s6 = sigma[6] as i128;
        let t6 = tau[6] as i128;
        let p6 = phi[6] as i128;
        println!("  n=6 check: sigma={}, tau={}, phi={}", s6, t6, p6);
        println!("    (sigma-tau) = {}", s6 - t6);
        println!("    (sigma/tau) = {}", s6 / t6);
        println!("    R = sigma*phi/(n*tau) = {}", s6 * p6 / (6 * t6));
        println!("    Sum = {} (should be {} = sigma)", (s6 - t6) + s6 / t6 + s6 * p6 / (6 * t6), s6);
    }
    println!("  Time: {:.2?}", t6.elapsed());
    println!();

    // ─── Test 5: Statistics ─────────────────────────────────────────
    println!("=================================================================");
    println!("  TEST 5: S(n) Distribution Statistics");
    println!("=================================================================");
    println!();

    println!("  Average log10(S(n)) by range:");
    println!("  {:>20}  {:>12}  {:>12}  {:>12}", "Range", "Avg log10(S)", "Min S", "Max S");
    println!("  {:->20}  {:->12}  {:->12}  {:->12}", "", "", "", "");
    for (idx, &(lo, hi)) in ranges.iter().enumerate() {
        let avg = if range_count[idx] > 0 { range_sum[idx] / range_count[idx] as f64 } else { 0.0 };
        let min_str = if range_min[idx] == u128::MAX { "N/A".to_string() } else { format!("{}", range_min[idx]) };
        // Max can be huge, use scientific notation
        let max_str = if range_max[idx] == 0 { "0".to_string() } else { format!("{:.2e}", range_max[idx] as f64) };
        println!("  {:>10}-{:<9}  {:>12.2}  {:>12}  {:>12}", lo, hi, avg, min_str, max_str);
    }
    println!();

    println!("  Histogram of log10(S(n)):");
    let max_bar = histogram.iter().copied().max().unwrap_or(1);
    let bar_scale = 60.0 / max_bar as f64;
    for (i, &count) in histogram.iter().enumerate() {
        if count == 0 { continue; }
        let bar_len = (count as f64 * bar_scale).ceil() as usize;
        let bar: String = "#".repeat(bar_len.max(1));
        if i == 0 {
            println!("    S=0     : {:>8}  {}", count, bar);
        } else if i == 31 {
            println!("    [30,inf): {:>8}  {}", count, bar);
        } else {
            println!("    [{:>2},{:>2}) : {:>8}  {}", i, i + 1, count, bar);
        }
    }
    println!();

    // Growth rate: sample S(n) at powers of 10
    println!("  S(n) growth rate at sample points:");
    println!("  {:>10}  {:>20}  {:>12}", "n", "S(n)", "log10(S)");
    println!("  {:->10}  {:->20}  {:->12}", "", "", "");
    let sample_points = [6, 10, 100, 1000, 10000, 100000, 1000000];
    for &n in &sample_points {
        if n > limit_1m { break; }
        let s_val = sigma[n] as i128;
        let t_val = tau[n] as i128;
        let p_val = phi[n] as i128;
        let ni = n as i128;
        let term1 = s_val * p_val - ni * t_val;
        let term2 = s_val * (ni + p_val) - ni * t_val * t_val;
        let sn = (term1 * term1 + term2 * term2) as u128;
        let log_s = if sn == 0 { f64::NEG_INFINITY } else { (sn as f64).log10() };
        if sn == 0 {
            println!("  {:>10}  {:>20}  {:>12}", n, 0, "-inf");
        } else {
            println!("  {:>10}  {:>20.0}  {:>12.2}", n, sn as f64, log_s);
        }
    }
    println!();

    // ─── Final Summary ──────────────────────────────────────────────
    let elapsed = t0.elapsed();
    println!("=================================================================");
    println!("  FINAL SUMMARY");
    println!("=================================================================");
    println!();
    println!("  Test 1: S(n) = 0");
    println!("    Range: [1, {}]", limit_1m);
    println!("    Solutions: {:?}", s_zero_solutions);
    let s0_status = if s_zero_solutions == vec![6] { "CONFIRMED: only n=6 (n=1 gives S=1)" } else { "UNEXPECTED RESULT" };
    println!("    Status: {}", s0_status);
    println!();

    println!("  Test 2: Self-decomposition sigma(n)(n+phi(n)) = n*tau(n)^2");
    println!("    Range: [1, {}]", limit_1m);
    println!("    Solutions: {:?}", self_decomp_solutions);
    let sd_status = if self_decomp_solutions == vec![6] { "CONFIRMED: only n=6" } else { "UNEXPECTED RESULT" };
    println!("    Status: {}", sd_status);
    println!();

    println!("  Test 3: sigma*phi = n*tau  (R = 1)");
    println!("    Range: [1, {}]", limit_10m);
    println!("    Solutions: {:?}", sigma_phi_eq_n_tau);
    let sp_status = if sigma_phi_eq_n_tau == vec![1, 6] { "CONFIRMED: only n=1,6" } else { "UNEXPECTED RESULT" };
    println!("    Status: {}", sp_status);
    println!();

    println!("  Test 4a: sigma/phi = n");
    println!("    Range: [1, {}]", limit_1m);
    println!("    Solutions: {:?}", sigma_div_phi_eq_n);
    let sdn_status = if sigma_div_phi_eq_n == vec![1, 6] { "CONFIRMED: only n=1,6" } else { "UNEXPECTED RESULT" };
    println!("    Status: {}", sdn_status);
    println!();

    println!("  Test 4c: Gauge self-decomposition");
    println!("    Range: [1, {}]", limit_1m);
    println!("    Solutions: {:?}", gauge_solutions);
    println!();

    println!("  Near-misses for S(n) < 100: {}", near_misses.len());
    if !near_misses.is_empty() {
        for (n, sn) in &near_misses {
            println!("    n={}: S={}", n, sn);
        }
    }
    println!();

    println!("  Total time: {:.2?}", elapsed);
    println!("=================================================================");
}
