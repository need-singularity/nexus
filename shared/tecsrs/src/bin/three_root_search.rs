/// 3-Root Uniqueness Theorem: σ(n)φ(n) = nτ(n) search
///
/// Verifies that σ(n)*φ(n) = n*τ(n) has NO solution except n=1 and n=6
/// among all positive integers up to the given limit.
///
/// Uses a segmented sieve with rayon parallelism to push verification
/// as far as possible (target: 10^10).
///
/// Usage:
///   cargo run --release --bin three_root_search -- --limit 1000000000000
///   cargo run --release --bin three_root_search  (default: 10^12)

use rayon::prelude::*;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Instant;

const DEFAULT_LIMIT: u64 = 1_000_000_000_000; // 10^12
const CHUNK_SIZE: u64 = 4_000_000;            // 4M per chunk — good cache/parallelism balance

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let limit = parse_limit(&args);

    let t0 = Instant::now();

    println!("=====================================================================");
    println!("  3-ROOT UNIQUENESS THEOREM VERIFICATION");
    println!("  σ(n)φ(n) = nτ(n)  →  solutions only at n=1 and n=6");
    println!("  Range: [1, {}]  ({:.2e})", limit, limit as f64);
    println!("  Chunk size: {}  Threads: {}", CHUNK_SIZE, rayon::current_num_threads());
    println!("=====================================================================");
    println!();

    // Primes up to sqrt(limit) for segmented sieve
    let sqrt_limit = (limit as f64).sqrt() as usize + 2;
    let primes = sieve_primes(sqrt_limit);
    println!("  Primes up to sqrt(N)={}: {} primes", sqrt_limit, primes.len());

    // Progress counter
    let progress = AtomicU64::new(0);

    // Divide range into chunks, process in parallel
    let num_chunks = ((limit - 1) / CHUNK_SIZE + 1) as usize;
    let chunk_indices: Vec<usize> = (0..num_chunks).collect();

    let all_solutions: Vec<Vec<u64>> = chunk_indices
        .par_iter()
        .map(|&chunk_idx| {
            let lo = (chunk_idx as u64) * CHUNK_SIZE + 1;
            let hi = std::cmp::min(lo + CHUNK_SIZE - 1, limit);
            let size = (hi - lo + 1) as usize;

            let (sigma, tau, phi) = build_chunk_fast(lo, hi, size, &primes);

            let mut solutions = Vec::new();
            for i in 0..size {
                let n = lo + i as u64;
                if n == 0 { continue; }

                let s = sigma[i];
                let t = tau[i];
                let p = phi[i];

                // σ(n)*φ(n) == n*τ(n)  — use u128 to prevent overflow
                if (s as u128) * (p as u128) == (n as u128) * (t as u128) {
                    solutions.push(n);
                }
            }

            // Update progress
            let prev = progress.fetch_add(hi - lo + 1, Ordering::Relaxed);
            let new_total = prev + (hi - lo + 1);
            // Print progress every 10^9 (1000 lines for 10^12 run)
            if new_total / 1_000_000_000 > prev / 1_000_000_000 {
                let pct = (new_total as f64 / limit as f64) * 100.0;
                let elapsed_s = t0.elapsed().as_secs_f64();
                let rate = new_total as f64 / elapsed_s;
                let eta_s = (limit - new_total) as f64 / rate;
                eprintln!("  Progress: {:.2e} / {:.2e} ({:.1}%) — {:.1?} elapsed, ETA {:.0}s ({:.1}min)",
                         new_total as f64, limit as f64, pct, t0.elapsed(), eta_s, eta_s / 60.0);
            }

            solutions
        })
        .collect();

    let elapsed = t0.elapsed();

    // Collect all solutions
    let mut solutions: Vec<u64> = all_solutions.into_iter().flatten().collect();
    solutions.sort();

    // Report
    println!();
    println!("=====================================================================");
    println!("  RESULTS");
    println!("=====================================================================");
    println!();
    println!("  Equation:   σ(n)·φ(n) = n·τ(n)");
    println!("  Range:      [1, {}]  ({:.2e})", limit, limit as f64);
    println!("  Solutions:  {:?}", solutions);
    println!("  Expected:   [1, 6]");
    println!();

    let pass = solutions == vec![1, 6];
    if pass {
        println!("  STATUS: CONFIRMED — n=1 and n=6 are the ONLY solutions");
        println!("  in [1, {:.2e}]", limit as f64);
    } else {
        println!("  STATUS: *** UNEXPECTED SOLUTIONS FOUND ***");
        println!("  Additional solutions beyond {{1, 6}}: {:?}",
                 solutions.iter().filter(|&&n| n != 1 && n != 6).collect::<Vec<_>>());
    }

    println!();
    println!("  Time:       {:.2?}", elapsed);
    println!("  Rate:       {:.2e} integers/second", limit as f64 / elapsed.as_secs_f64());
    println!("=====================================================================");

    // Estimate time for next milestone
    if limit < 1_000_000_000_000 {
        let est = elapsed.as_secs_f64() * (1_000_000_000_000.0 / limit as f64);
        println!();
        println!("  Estimated time for 10^12: {:.0}s ({:.1} minutes, {:.1} hours)",
                 est, est / 60.0, est / 3600.0);
    } else if limit < 10_000_000_000_000 {
        let est = elapsed.as_secs_f64() * (10_000_000_000_000.0 / limit as f64);
        println!();
        println!("  Estimated time for 10^13: {:.0}s ({:.1} hours)",
                 est, est / 3600.0);
    }
}

fn parse_limit(args: &[String]) -> u64 {
    for i in 0..args.len() {
        if args[i] == "--limit" && i + 1 < args.len() {
            return args[i + 1].replace('_', "").parse().unwrap_or(DEFAULT_LIMIT);
        }
    }
    DEFAULT_LIMIT
}

/// Build σ, τ, φ arrays for [lo, hi] via segmented multiplicative sieve.
/// Each n is factored by sieving with primes up to sqrt(limit).
fn build_chunk_fast(lo: u64, hi: u64, size: usize, primes: &[usize]) -> (Vec<u64>, Vec<u64>, Vec<u64>) {
    // Multiplicative accumulators
    let mut sigma_mult = vec![1u64; size];
    let mut tau_mult = vec![1u64; size];
    let mut phi_mult = vec![1u64; size];
    let mut remaining = vec![0u64; size];

    // Initialize remaining[i] = lo + i
    for i in 0..size {
        remaining[i] = lo + i as u64;
    }

    // Sieve with each prime p
    for &p in primes {
        let p64 = p as u64;

        // Find first multiple of p in [lo, hi]
        let first = if lo % p64 == 0 { lo } else { lo + (p64 - lo % p64) };
        if first > hi { continue; }

        let mut idx = (first - lo) as usize;
        while idx < size {
            if remaining[idx] % p64 == 0 {
                let mut a: u32 = 0;
                let mut pk: u64 = 1; // will be p^a
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
                let phi_pa = (pk / p64) * (p64 - 1);
                phi_mult[idx] *= phi_pa;
            }
            idx += p as usize;
        }
    }

    // Remaining cofactor > 1 means it is a prime (larger than sqrt(limit))
    let mut sigma = vec![0u64; size];
    let mut tau = vec![0u64; size];
    let mut phi = vec![0u64; size];

    for i in 0..size {
        let n = lo + i as u64;
        if n <= 1 {
            sigma[i] = n;
            tau[i] = if n == 0 { 0 } else { 1 };
            phi[i] = n;
            continue;
        }

        let r = remaining[i];
        if r > 1 {
            // r is prime, exponent 1
            sigma[i] = sigma_mult[i] * (r + 1);
            tau[i] = tau_mult[i] * 2;
            phi[i] = phi_mult[i] * (r - 1);
        } else {
            sigma[i] = sigma_mult[i];
            tau[i] = tau_mult[i];
            phi[i] = phi_mult[i];
        }
    }

    (sigma, tau, phi)
}

/// Sieve of Eratosthenes returning sorted list of primes up to limit.
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
