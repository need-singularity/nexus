/// H-PH-9 Extreme Uniqueness Verification up to 10^8
///
/// Verifies ALL six conditions:
///   1. S(n) = [σφ - nτ]² + [σ(n+φ) - nτ²]² = 0  → only n=6
///   2. σφ = nτ  (R=1)  → only n=1, n=6
///   3. σ/φ = n  → only n=1, n=6
///   4. σ(n+φ) = nτ²  → only n=6
///   5. τ+2 = n  → only n=6 among perfect numbers (check all n)
///   6. Gauge: (σ-τ) + (σ/τ) + R = σ where R=σφ/(nτ) → only n=6 (n>1)
///
/// Uses a segmented sieve approach:
///   - Sieve smallest prime factor (SPF) up to sqrt(N)
///   - Process in chunks of ~10^6, computing σ,τ,φ from prime factorization
///   - Memory: ~O(chunk_size + sqrt(N)) instead of O(N)
///
/// Usage: cargo run --release --bin verify_uniqueness_extreme

use std::time::Instant;

const LIMIT: u64 = 1_000_000_000; // 10^9 (verified in 66s on M3)
const CHUNK: usize = 1_000_000; // process 10^6 at a time

fn main() {
    let t0 = Instant::now();

    println!("=================================================================");
    println!("  H-PH-9 EXTREME UNIQUENESS VERIFICATION");
    println!("  Range: [1, {}]  ({:.0e})", LIMIT, LIMIT as f64);
    println!("  Chunk size: {}", CHUNK);
    println!("=================================================================");
    println!();

    // Results collectors
    let mut sol_s_zero: Vec<u64> = Vec::new();       // Test 1: S(n)=0
    let mut sol_r_eq_1: Vec<u64> = Vec::new();       // Test 2: σφ=nτ
    let mut sol_sigma_div_phi: Vec<u64> = Vec::new(); // Test 3: σ/φ=n
    let mut sol_self_decomp: Vec<u64> = Vec::new();   // Test 4: σ(n+φ)=nτ²
    let mut sol_tau_plus_2: Vec<u64> = Vec::new();    // Test 5: τ+2=n
    let mut sol_gauge: Vec<u64> = Vec::new();         // Test 6: gauge self-decomposition
    let mut near_misses_s: Vec<(u64, u128)> = Vec::new(); // S(n) < 1000

    // Process in chunks using segmented sieve for σ, τ, φ
    let num_chunks = ((LIMIT as usize) + CHUNK - 1) / CHUNK;
    let mut last_report = Instant::now();

    for chunk_idx in 0..num_chunks {
        let lo = (chunk_idx as u64) * (CHUNK as u64) + 1;
        let hi = std::cmp::min(lo + (CHUNK as u64) - 1, LIMIT);
        let size = (hi - lo + 1) as usize;

        // Build σ, τ, φ for [lo..hi] using divisor sieve within chunk
        let (sigma_arr, tau_arr, phi_arr) = build_chunk(lo, hi, size);

        // Test all conditions
        for i in 0..size {
            let n = lo + i as u64;
            if n == 0 { continue; }

            let s = sigma_arr[i];
            let t = tau_arr[i];
            let p = phi_arr[i];

            // Test 2: σφ = nτ
            if (s as u128) * (p as u128) == (n as u128) * (t as u128) {
                sol_r_eq_1.push(n);
            }

            // Test 3: σ/φ = n  (i.e., σ = n*φ)
            if p > 0 && s == n * p {
                sol_sigma_div_phi.push(n);
            }

            // Test 4: σ(n+φ) = nτ²
            let lhs4 = (s as u128) * ((n + p) as u128);
            let rhs4 = (n as u128) * (t as u128) * (t as u128);
            if lhs4 == rhs4 {
                sol_self_decomp.push(n);
            }

            // Test 1: S(n) = [σφ - nτ]² + [σ(n+φ) - nτ²]² = 0
            // Both terms must be zero, so this is intersection of Test 2 and Test 4
            // But compute anyway for near-miss detection
            let term1 = (s as i128) * (p as i128) - (n as i128) * (t as i128);
            let term2 = (s as i128) * ((n + p) as i128) - (n as i128) * (t as i128) * (t as i128);
            let sn = (term1 as i128).unsigned_abs() * (term1 as i128).unsigned_abs()
                   + (term2 as i128).unsigned_abs() * (term2 as i128).unsigned_abs();
            if sn == 0 {
                sol_s_zero.push(n);
            } else if sn < 1000 && n > 1 {
                near_misses_s.push((n, sn));
            }

            // Test 5: τ+2 = n
            if t + 2 == n {
                sol_tau_plus_2.push(n);
            }

            // Test 6: Gauge self-decomposition
            // (σ-τ) + (σ/τ) + R = σ  where R = σφ/(nτ)
            // Requires σ%τ==0 and (σφ)%(nτ)==0
            if n > 1 && t > 0 && s % t == 0 {
                let sp = (s as u128) * (p as u128);
                let nt = (n as u128) * (t as u128);
                if sp % nt == 0 {
                    let s_over_t = s / t;
                    let r = (sp / nt) as u64;
                    let lhs_gauge = (s - t) + s_over_t + r;
                    if lhs_gauge == s {
                        sol_gauge.push(n);
                    }
                }
            }
        }

        // Progress report every 5 seconds
        if last_report.elapsed().as_secs() >= 5 || chunk_idx == num_chunks - 1 {
            let pct = (hi as f64 / LIMIT as f64) * 100.0;
            println!("  Progress: {}/{} ({:.1}%) — {:.1?} elapsed",
                     hi, LIMIT, pct, t0.elapsed());
            last_report = Instant::now();
        }
    }

    let elapsed = t0.elapsed();

    // ─── Results ─────────────────────────────────────────────────────
    println!();
    println!("=================================================================");
    println!("  RESULTS — All 6 conditions verified to N = {}", LIMIT);
    println!("  Total time: {:.2?}", elapsed);
    println!("=================================================================");
    println!();

    print_result("Test 1: S(n) = [σφ-nτ]² + [σ(n+φ)-nτ²]² = 0",
                 &sol_s_zero, &[6], LIMIT);
    print_result("Test 2: σ(n)φ(n) = nτ(n)  (R=1)",
                 &sol_r_eq_1, &[1, 6], LIMIT);
    print_result("Test 3: σ(n)/φ(n) = n",
                 &sol_sigma_div_phi, &[1, 6], LIMIT);
    print_result("Test 4: σ(n)(n+φ(n)) = nτ(n)²",
                 &sol_self_decomp, &[6], LIMIT);

    println!("  Test 5: τ(n)+2 = n");
    println!("    Range: [1, {}]", LIMIT);
    println!("    Solutions: {:?}", sol_tau_plus_2);
    // Check which are perfect numbers
    let perfect_in_sol5: Vec<u64> = sol_tau_plus_2.iter()
        .copied()
        .filter(|&n| is_perfect(n))
        .collect();
    println!("    Perfect number solutions: {:?}", perfect_in_sol5);
    let status5 = if perfect_in_sol5 == vec![6] { "CONFIRMED" } else { "UNEXPECTED" };
    println!("    Status: {} — only n=6 among perfect numbers", status5);
    println!();

    print_result("Test 6: Gauge (σ-τ)+(σ/τ)+R = σ  [n>1]",
                 &sol_gauge, &[6], LIMIT);

    // Near misses
    println!("  Near-misses for S(n) < 1000 (n>1): {}", near_misses_s.len());
    if !near_misses_s.is_empty() {
        for (n, sn) in near_misses_s.iter().take(20) {
            println!("    n={}: S={}", n, sn);
        }
        if near_misses_s.len() > 20 {
            println!("    ... and {} more", near_misses_s.len() - 20);
        }
    }
    println!();

    // Final verdict
    println!("=================================================================");
    println!("  VERDICT");
    println!("=================================================================");
    let all_pass = sol_s_zero == vec![6]
        && sol_r_eq_1 == vec![1, 6]
        && sol_sigma_div_phi == vec![1, 6]
        && sol_self_decomp == vec![6]
        && perfect_in_sol5 == vec![6]
        && sol_gauge == vec![6];
    if all_pass {
        println!("  ALL 6 CONDITIONS CONFIRMED up to N = {}", LIMIT);
        println!("  n=6 uniqueness holds with ZERO counterexamples.");
    } else {
        println!("  SOME CONDITIONS HAD UNEXPECTED RESULTS — review above.");
    }
    println!("  Time: {:.2?}", elapsed);
    println!("=================================================================");
}

/// Build σ, τ, φ arrays for the range [lo, hi] using a segmented divisor sieve.
fn build_chunk(lo: u64, hi: u64, size: usize) -> (Vec<u64>, Vec<u64>, Vec<u64>) {
    let mut sigma = vec![0u64; size];
    let mut tau = vec![0u64; size];
    let mut phi = vec![0u64; size]; // will be computed separately

    // Divisor sieve for σ and τ: iterate over all d from 1..=hi,
    // but only those d that have a multiple in [lo, hi].
    // For d up to hi, first multiple >= lo is ceil(lo/d)*d.
    // This is O(hi * ln(hi)) total across all d — too slow for hi=10^8 in one pass.
    //
    // Instead: use multiplicative property.
    // Factor each n via trial division / SPF sieve approach.
    // We sieve the smallest prime factor for [lo..hi].

    // Step 1: Initialize phi[i] = lo+i, then sieve with primes
    // Step 2: For σ and τ, we track the remaining cofactor after dividing out primes

    // We need primes up to sqrt(hi)
    let sqrt_hi = (hi as f64).sqrt() as u64 + 1;
    let primes = sieve_primes(sqrt_hi as usize);

    // For each n in [lo..hi], we need to factorize it.
    // We'll do a segmented sieve approach:
    //   - For each prime p <= sqrt(hi), mark multiples in [lo..hi]
    //   - Track the remaining cofactor

    // Arrays for factorization-based computation
    // remaining[i] = n / (all prime factors processed so far)
    let mut remaining = vec![0u64; size];
    // sigma accumulator (multiplicative: product of σ(p^a) for each prime power)
    let mut sigma_mult = vec![1u64; size];
    // tau accumulator (multiplicative: product of (a+1) for each prime power)
    let mut tau_mult = vec![1u64; size];
    // phi accumulator (multiplicative: product of p^(a-1)*(p-1))
    let mut phi_mult = vec![1u64; size];

    // Initialize remaining
    for i in 0..size {
        remaining[i] = lo + i as u64;
    }

    // Sieve with each prime
    for &p in &primes {
        if (p as u64) * (p as u64) > hi {
            // Remaining primes are too large to appear as p^2 in range,
            // but they can still appear as single factors. We handle the
            // remaining cofactor at the end.
            break;
        }
        let p64 = p as u64;

        // Find first multiple of p in [lo..hi]
        let first = if lo % p64 == 0 { lo } else { lo + (p64 - lo % p64) };

        let mut idx = (first - lo) as usize;
        while idx < size {
            if remaining[idx] % p64 == 0 {
                // Count the exponent of p in remaining[idx]
                let mut a: u32 = 0;
                let mut pk: u64 = 1; // p^a
                while remaining[idx] % p64 == 0 {
                    remaining[idx] /= p64;
                    a += 1;
                    pk *= p64;
                }
                // σ(p^a) = (p^(a+1) - 1) / (p - 1)
                let sigma_pa = (pk * p64 - 1) / (p64 - 1);
                sigma_mult[idx] *= sigma_pa;
                // τ(p^a) = a + 1
                tau_mult[idx] *= (a + 1) as u64;
                // φ(p^a) = p^(a-1) * (p-1)
                let phi_pa = (pk / p64) * (p64 - 1); // pk = p^a, so pk/p = p^(a-1)
                // Wait, pk was multiplied a times but we divided remaining.
                // pk = p^a already (since we multiplied pk *= p64 a times starting from 1)
                // Correction: pk after loop = p^a
                phi_mult[idx] *= phi_pa;
            }
            idx += p64 as usize;
        }
    }

    // Handle remaining cofactor > 1 (it must be a prime)
    for i in 0..size {
        let r = remaining[i];
        if r > 1 {
            // r is a prime factor with exponent 1
            sigma_mult[i] *= r + 1; // σ(r) = 1 + r
            tau_mult[i] *= 2u64;    // τ(r) = 2
            phi_mult[i] *= r - 1;   // φ(r) = r - 1
        }
        // Handle n=1 special case
        let n = lo + i as u64;
        if n <= 1 {
            sigma[i] = n;
            tau[i] = if n == 0 { 0 } else { 1 };
            phi[i] = n; // φ(1)=1, φ(0)=0
        } else {
            sigma[i] = sigma_mult[i];
            tau[i] = tau_mult[i] as u64;
            phi[i] = phi_mult[i];
        }
    }

    (sigma, tau, phi)
}

/// Simple sieve of Eratosthenes returning list of primes up to limit
fn sieve_primes(limit: usize) -> Vec<usize> {
    let mut is_prime = vec![true; limit + 1];
    is_prime[0] = false;
    if limit >= 1 { is_prime[1] = false; }
    let mut i = 2;
    while i * i <= limit {
        if is_prime[i] {
            let mut j = i * i;
            while j <= limit {
                is_prime[j] = false;
                j += i;
            }
        }
        i += 1;
    }
    (2..=limit).filter(|&x| is_prime[x]).collect()
}

/// Check if n is a perfect number (σ(n) = 2n)
fn is_perfect(n: u64) -> bool {
    if n < 2 { return false; }
    let mut sum: u64 = 1;
    let mut d: u64 = 2;
    while d * d <= n {
        if n % d == 0 {
            sum += d;
            if d != n / d {
                sum += n / d;
            }
        }
        d += 1;
    }
    sum == n
}

fn print_result(label: &str, solutions: &[u64], expected: &[u64], limit: u64) {
    println!("  {}", label);
    println!("    Range: [1, {}]", limit);
    println!("    Solutions: {:?}", solutions);
    let status = if solutions == expected { "CONFIRMED" } else { "UNEXPECTED" };
    println!("    Expected:  {:?}", expected);
    println!("    Status: {}", status);
    println!();
}
