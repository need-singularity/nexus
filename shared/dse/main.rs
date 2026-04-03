// Universal DSE Explorer — n6-architecture
// Rust single-file, no crate dependencies
// Usage: universal-dse <domain.toml> [domain2.toml ...] [--top N]
//   Single domain:  universal-dse domains/chip.toml
//   Cross-DSE:      universal-dse domains/chip.toml domains/battery.toml
//   Batch:          universal-dse --all domains/
//   Cross-all:      universal-dse --cross-all domains/ [--top N]
//   CSV export:     universal-dse domains/chip.toml --csv
//   Validate:       universal-dse --validate domains/chip.toml
//   Random test:    universal-dse --random-baseline 10000 domains/chip.toml

use std::env;
use std::fs;
use std::fmt;
use std::path::Path;

// ── N6 Constants ──
const N: f64 = 6.0;
const PHI: f64 = 2.0;
const TAU: f64 = 4.0;
const SIGMA: f64 = 12.0;
const SOPFR: f64 = 5.0;
const MU: f64 = 1.0;
const J2: f64 = 24.0;

// ── Data Structures ──

#[derive(Clone, Debug)]
struct Candidate {
    id: String,
    label: String,
    n6: f64,
    perf: f64,
    power: f64,
    cost: f64,
}

#[derive(Clone, Debug)]
struct Level {
    name: String,
    candidates: Vec<Candidate>,
}

#[derive(Clone, Debug)]
struct Rule {
    rule_type: String, // "require" or "exclude"
    if_level: usize,
    if_id: String,
    then_level: usize,
    then_ids: Vec<String>,
}

#[derive(Clone, Debug)]
struct Weights {
    n6: f64,
    perf: f64,
    power: f64,
    cost: f64,
}

#[derive(Clone, Debug)]
struct Domain {
    name: String,
    desc: String,
    weights: Weights,
    levels: Vec<Level>,
    rules: Vec<Rule>,
}

#[derive(Clone)]
struct Combo {
    indices: Vec<usize>,
    n6_avg: f64,
    perf_avg: f64,
    power_avg: f64,
    cost_avg: f64,
    pareto_score: f64,
}

// ── TOML Subset Parser ──
// Supports: [section], [[array]], key = "str", key = 0.5, # comments
// [[level]] starts a new level; [[candidate]] adds to last level; [[rule]] adds a rule

fn parse_toml(content: &str) -> Domain {
    let mut name = String::new();
    let mut desc = String::new();
    let mut weights = Weights { n6: 0.40, perf: 0.30, power: 0.20, cost: 0.10 };
    let mut levels: Vec<Level> = Vec::new();
    let mut rules: Vec<Rule> = Vec::new();

    #[derive(PartialEq)]
    enum Section { Meta, Scoring, Level, Candidate, Rule, None }
    let mut section = Section::None;

    // Temp buffers for building candidates and rules
    let mut cur_cand = Candidate {
        id: String::new(), label: String::new(),
        n6: 0.0, perf: 0.0, power: 0.0, cost: 0.0,
    };
    let mut cur_rule = Rule {
        rule_type: String::new(), if_level: 0, if_id: String::new(),
        then_level: 0, then_ids: Vec::new(),
    };
    let mut has_cand = false;
    let mut has_rule = false;

    for raw_line in content.lines() {
        let line = raw_line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        // Section headers
        if line == "[[level]]" {
            // Flush pending candidate
            if has_cand && !levels.is_empty() {
                levels.last_mut().unwrap().candidates.push(cur_cand.clone());
                has_cand = false;
            }
            if has_rule {
                rules.push(cur_rule.clone());
                has_rule = false;
            }
            levels.push(Level { name: String::new(), candidates: Vec::new() });
            section = Section::Level;
            continue;
        }
        if line == "[[candidate]]" {
            if has_cand && !levels.is_empty() {
                levels.last_mut().unwrap().candidates.push(cur_cand.clone());
            }
            cur_cand = Candidate {
                id: String::new(), label: String::new(),
                n6: 0.0, perf: 0.0, power: 0.0, cost: 0.0,
            };
            has_cand = true;
            section = Section::Candidate;
            continue;
        }
        if line == "[[rule]]" {
            if has_cand && !levels.is_empty() {
                levels.last_mut().unwrap().candidates.push(cur_cand.clone());
                has_cand = false;
            }
            if has_rule {
                rules.push(cur_rule.clone());
            }
            cur_rule = Rule {
                rule_type: String::new(), if_level: 0, if_id: String::new(),
                then_level: 0, then_ids: Vec::new(),
            };
            has_rule = true;
            section = Section::Rule;
            continue;
        }
        if line == "[meta]" { section = Section::Meta; continue; }
        if line == "[scoring]" { section = Section::Scoring; continue; }

        // Key = Value
        if let Some(eq_pos) = line.find('=') {
            let key = line[..eq_pos].trim();
            let val = line[eq_pos + 1..].trim();
            let val_str = val.trim_matches('"');

            match section {
                Section::Meta => match key {
                    "name" => name = val_str.to_string(),
                    "desc" => desc = val_str.to_string(),
                    _ => {}
                },
                Section::Scoring => {
                    let v: f64 = val.parse().unwrap_or(0.0);
                    match key {
                        "n6" => weights.n6 = v,
                        "perf" => weights.perf = v,
                        "power" => weights.power = v,
                        "cost" => weights.cost = v,
                        _ => {}
                    }
                },
                Section::Level => {
                    if key == "name" {
                        if let Some(l) = levels.last_mut() {
                            l.name = val_str.to_string();
                        }
                    }
                },
                Section::Candidate => match key {
                    "id" => cur_cand.id = val_str.to_string(),
                    "label" => cur_cand.label = val_str.to_string(),
                    "n6" => cur_cand.n6 = val.parse().unwrap_or(0.0),
                    "perf" => cur_cand.perf = val.parse().unwrap_or(0.0),
                    "power" => cur_cand.power = val.parse().unwrap_or(0.0),
                    "cost" => cur_cand.cost = val.parse().unwrap_or(0.0),
                    _ => {}
                },
                Section::Rule => match key {
                    "type" => cur_rule.rule_type = val_str.to_string(),
                    "if_level" => cur_rule.if_level = val.parse().unwrap_or(0),
                    "if_id" => cur_rule.if_id = val_str.to_string(),
                    "then_level" => cur_rule.then_level = val.parse().unwrap_or(0),
                    "then_ids" => {
                        cur_rule.then_ids = val_str.split(',')
                            .map(|s| s.trim().to_string())
                            .collect();
                    }
                    _ => {}
                },
                Section::None => {}
            }
        }
    }

    // Flush remaining
    if has_cand && !levels.is_empty() {
        levels.last_mut().unwrap().candidates.push(cur_cand);
    }
    if has_rule {
        rules.push(cur_rule);
    }

    Domain { name, desc, weights, levels, rules }
}

// ── Compatibility Check ──

fn is_compatible(rules: &[Rule], levels: &[Level], indices: &[usize]) -> bool {
    for rule in rules {
        if rule.if_level >= levels.len() || rule.then_level >= levels.len() {
            continue;
        }
        let if_cand = &levels[rule.if_level].candidates[indices[rule.if_level]];
        if if_cand.id == rule.if_id {
            let then_cand = &levels[rule.then_level].candidates[indices[rule.then_level]];
            match rule.rule_type.as_str() {
                "require" => {
                    if !rule.then_ids.iter().any(|id| id == &then_cand.id) {
                        return false;
                    }
                }
                "exclude" => {
                    if rule.then_ids.iter().any(|id| id == &then_cand.id) {
                        return false;
                    }
                }
                _ => {}
            }
        }
    }
    true
}

// ── Scoring ──

fn score(domain: &Domain, indices: &[usize]) -> Combo {
    let n = domain.levels.len() as f64;
    let mut n6_sum = 0.0;
    let mut perf_sum = 0.0;
    let mut power_sum = 0.0;
    let mut cost_sum = 0.0;

    for (i, level) in domain.levels.iter().enumerate() {
        let c = &level.candidates[indices[i]];
        n6_sum += c.n6;
        perf_sum += c.perf;
        power_sum += c.power;
        cost_sum += c.cost;
    }

    let n6_avg = n6_sum / n;
    let perf_avg = perf_sum / n;
    let power_avg = power_sum / n;
    let cost_avg = cost_sum / n;

    let w = &domain.weights;
    let pareto_score = w.n6 * n6_avg + w.perf * perf_avg
                     + w.power * power_avg + w.cost * cost_avg;

    Combo {
        indices: indices.to_vec(),
        n6_avg, perf_avg, power_avg, cost_avg, pareto_score,
    }
}

// ── Enumeration (variable number of levels) ──

fn enumerate(domain: &Domain) -> Vec<Combo> {
    let num_levels = domain.levels.len();
    if num_levels == 0 { return Vec::new(); }

    let sizes: Vec<usize> = domain.levels.iter().map(|l| l.candidates.len()).collect();
    let total: usize = sizes.iter().product();

    let mut results = Vec::with_capacity(total);
    let mut indices = vec![0usize; num_levels];

    for _ in 0..total {
        if is_compatible(&domain.rules, &domain.levels, &indices) {
            results.push(score(domain, &indices));
        }
        // Odometer increment
        let mut carry = true;
        for i in (0..num_levels).rev() {
            if carry {
                indices[i] += 1;
                if indices[i] >= sizes[i] {
                    indices[i] = 0;
                } else {
                    carry = false;
                }
            }
        }
    }

    results.sort_by(|a, b| b.pareto_score.partial_cmp(&a.pareto_score).unwrap());
    results
}

// ── Pareto Frontier (dominance-based) ──

fn pareto_frontier(combos: &[Combo]) -> Vec<usize> {
    let mut frontier: Vec<usize> = Vec::new();
    for i in 0..combos.len() {
        let mut dominated = false;
        for j in 0..combos.len() {
            if i == j { continue; }
            if dominates(&combos[j], &combos[i]) {
                dominated = true;
                break;
            }
        }
        if !dominated {
            frontier.push(i);
        }
    }
    frontier
}

fn dominates(a: &Combo, b: &Combo) -> bool {
    let a_vals = [a.n6_avg, a.perf_avg, a.power_avg, a.cost_avg];
    let b_vals = [b.n6_avg, b.perf_avg, b.power_avg, b.cost_avg];
    let all_geq = a_vals.iter().zip(b_vals.iter()).all(|(av, bv)| av >= bv);
    let any_gt = a_vals.iter().zip(b_vals.iter()).any(|(av, bv)| av > bv);
    all_geq && any_gt
}

// ── Output ──

fn combo_path(domain: &Domain, combo: &Combo) -> String {
    combo.indices.iter().enumerate()
        .map(|(i, &idx)| domain.levels[i].candidates[idx].id.clone())
        .collect::<Vec<_>>()
        .join(" + ")
}

fn combo_labels(domain: &Domain, combo: &Combo) -> String {
    combo.indices.iter().enumerate()
        .map(|(i, &idx)| domain.levels[i].candidates[idx].label.clone())
        .collect::<Vec<_>>()
        .join(" -> ")
}

fn print_header(domain: &Domain, total: usize, compatible: usize) {
    let bar = "=".repeat(66);
    println!("\n{}", bar);
    println!("  Universal DSE -- {}", domain.name);
    if !domain.desc.is_empty() {
        println!("  {}", domain.desc);
    }
    println!("  {} total combinations -> {} compatible", total, compatible);
    println!("  Weights: n6={:.0}% perf={:.0}% power={:.0}% cost={:.0}%",
        domain.weights.n6 * 100.0, domain.weights.perf * 100.0,
        domain.weights.power * 100.0, domain.weights.cost * 100.0);
    println!("{}\n", bar);
}

fn print_candidates(domain: &Domain) {
    println!("=== CANDIDATES ===\n");
    for (i, level) in domain.levels.iter().enumerate() {
        print!("  L{}: {} ({})  ", i + 1, level.name, level.candidates.len());
        let ids: Vec<&str> = level.candidates.iter().map(|c| c.id.as_str()).collect();
        println!("{}", ids.join(", "));
    }
    println!();
}

fn print_top(domain: &Domain, combos: &[Combo], top_n: usize) {
    let show = std::cmp::min(top_n, combos.len());
    println!("=== TOP {} ===\n", show);

    // Header
    let level_names: Vec<String> = domain.levels.iter()
        .map(|l| {
            let n = &l.name;
            if n.len() > 10 { n[..10].to_string() } else { n.clone() }
        })
        .collect();

    print!("  {:>4} |", "Rank");
    for n in &level_names {
        print!(" {:>10} |", n);
    }
    println!("  n6%  | Perf  | Power | Cost  | Pareto");

    let sep_w = 7 + (level_names.len() * 13) + 45;
    println!("  {}", "-".repeat(sep_w));

    for (rank, combo) in combos[..show].iter().enumerate() {
        print!("  {:>4} |", rank + 1);
        for (i, &idx) in combo.indices.iter().enumerate() {
            let id = &domain.levels[i].candidates[idx].id;
            let short = if id.len() > 10 { &id[..10] } else { id.as_str() };
            print!(" {:>10} |", short);
        }
        println!(" {:5.1} | {:.3} | {:.3} | {:.3} | {:.4}",
            combo.n6_avg * 100.0, combo.perf_avg, combo.power_avg,
            combo.cost_avg, combo.pareto_score);
    }
    println!();
}

fn print_best_by_category(domain: &Domain, combos: &[Combo]) {
    if combos.is_empty() { return; }
    println!("=== BEST BY CATEGORY ===\n");

    // Best n6
    let best_n6 = combos.iter().max_by(|a, b|
        a.n6_avg.partial_cmp(&b.n6_avg).unwrap()).unwrap();
    println!("  Best n6:    {} ({:.1}%)", combo_path(domain, best_n6), best_n6.n6_avg * 100.0);

    // Best perf
    let best_perf = combos.iter().max_by(|a, b|
        a.perf_avg.partial_cmp(&b.perf_avg).unwrap()).unwrap();
    println!("  Best Perf:  {} (perf={:.3})", combo_path(domain, best_perf), best_perf.perf_avg);

    // Best power
    let best_pow = combos.iter().max_by(|a, b|
        a.power_avg.partial_cmp(&b.power_avg).unwrap()).unwrap();
    println!("  Best Power: {} (power={:.3})", combo_path(domain, best_pow), best_pow.power_avg);

    // Best cost
    let best_cost = combos.iter().max_by(|a, b|
        a.cost_avg.partial_cmp(&b.cost_avg).unwrap()).unwrap();
    println!("  Best Cost:  {} (cost={:.3})", combo_path(domain, best_cost), best_cost.cost_avg);

    println!();
}

fn print_pareto(domain: &Domain, combos: &[Combo], frontier: &[usize]) {
    println!("=== PARETO FRONTIER ({} non-dominated solutions) ===\n", frontier.len());

    let show = std::cmp::min(10, frontier.len());
    for (i, &idx) in frontier[..show].iter().enumerate() {
        let c = &combos[idx];
        println!("  {:>2}. {} | n6={:.1}% perf={:.3} pow={:.3} cost={:.3}",
            i + 1, combo_path(domain, c),
            c.n6_avg * 100.0, c.perf_avg, c.power_avg, c.cost_avg);
    }
    if frontier.len() > show {
        println!("  ... +{} more", frontier.len() - show);
    }
    println!();
}

fn print_stats(combos: &[Combo]) {
    if combos.is_empty() { return; }
    println!("=== STATISTICS ===\n");

    let n6_vals: Vec<f64> = combos.iter().map(|c| c.n6_avg * 100.0).collect();
    let perf_vals: Vec<f64> = combos.iter().map(|c| c.perf_avg).collect();

    let n6_max = n6_vals.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let n6_min = n6_vals.iter().cloned().fold(f64::INFINITY, f64::min);
    let n6_avg = n6_vals.iter().sum::<f64>() / n6_vals.len() as f64;

    let perf_max = perf_vals.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let perf_avg = perf_vals.iter().sum::<f64>() / perf_vals.len() as f64;

    // Percentiles
    let mut sorted_n6 = n6_vals.clone();
    sorted_n6.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let p50 = sorted_n6[sorted_n6.len() / 2];
    let p75 = sorted_n6[sorted_n6.len() * 3 / 4];
    let p90 = sorted_n6[sorted_n6.len() * 9 / 10];

    println!("  n6%:  max={:.1}  min={:.1}  avg={:.1}  p50={:.1}  p75={:.1}  p90={:.1}",
        n6_max, n6_min, n6_avg, p50, p75, p90);
    println!("  perf: max={:.3}  avg={:.3}", perf_max, perf_avg);
    println!("  combos: {}", combos.len());
    println!();
}

fn print_ascii_path(domain: &Domain, combo: &Combo) {
    println!("=== OPTIMAL PATH ===\n");
    let n = domain.levels.len();
    for (i, &idx) in combo.indices.iter().enumerate() {
        let c = &domain.levels[i].candidates[idx];
        let bar_len = (c.n6 * 20.0) as usize;
        let bar: String = "█".repeat(bar_len);
        let empty: String = "░".repeat(20 - bar_len);
        println!("  L{} {:>10}: [{}{}] n6={:.0}%  {}",
            i + 1, domain.levels[i].name,
            bar, empty, c.n6 * 100.0, c.label);
        if i < n - 1 {
            println!("        |");
            println!("        v");
        }
    }
    println!();
}

// ── Cross-DSE ──

fn cross_dse(domains: &[Domain], top_k: usize) {
    println!("\n{}", "=".repeat(66));
    println!("  Cross-DSE: {} domains", domains.len());
    for d in domains {
        println!("    - {}", d.name);
    }
    println!("{}\n", "=".repeat(66));

    // Run each domain, take top-K
    let mut domain_tops: Vec<(String, Vec<Combo>)> = Vec::new();
    for domain in domains {
        let combos = enumerate(domain);
        let take = std::cmp::min(top_k, combos.len());
        domain_tops.push((domain.name.clone(), combos[..take].to_vec()));
    }

    // Pairwise cross-combination
    if domain_tops.len() >= 2 {
        for i in 0..domain_tops.len() {
            for j in (i + 1)..domain_tops.len() {
                let (ref name_a, ref tops_a) = domain_tops[i];
                let (ref name_b, ref tops_b) = domain_tops[j];

                println!("--- Cross: {} x {} ---\n", name_a, name_b);

                let mut cross_results: Vec<(usize, usize, f64, f64, f64, f64, f64)> = Vec::new();

                for (ai, a) in tops_a.iter().enumerate() {
                    for (bi, b) in tops_b.iter().enumerate() {
                        let cn6 = (a.n6_avg + b.n6_avg) / 2.0;
                        let cperf = (a.perf_avg + b.perf_avg) / 2.0;
                        let cpow = (a.power_avg + b.power_avg) / 2.0;
                        let ccost = (a.cost_avg + b.cost_avg) / 2.0;
                        let cscore = 0.40 * cn6 + 0.30 * cperf + 0.20 * cpow + 0.10 * ccost;
                        cross_results.push((ai, bi, cn6, cperf, cpow, ccost, cscore));
                    }
                }

                cross_results.sort_by(|a, b| b.6.partial_cmp(&a.6).unwrap());

                let show = std::cmp::min(10, cross_results.len());
                println!("  {:>4} | {:>6} | {:>6} | {:>5} | {:>5} | {:>5} | {:>5} | {:>6}",
                    "Rank", name_a, name_b, "n6%", "Perf", "Power", "Cost", "Score");
                let sep = "-".repeat(70);
                println!("  {}", sep);

                for (r, &(ai, bi, cn6, cp, cpw, cc, cs)) in cross_results[..show].iter().enumerate() {
                    let pa = combo_short(&domains[i], &tops_a[ai]);
                    let pb = combo_short(&domains[j], &tops_b[bi]);
                    println!("  {:>4} | {:>6} | {:>6} | {:4.1} | {:.3} | {:.3} | {:.3} | {:.4}",
                        r + 1, pa, pb, cn6 * 100.0, cp, cpw, cc, cs);
                }
                println!();
            }
        }
    }
}

fn combo_short(domain: &Domain, combo: &Combo) -> String {
    if combo.indices.is_empty() { return String::from("-"); }
    let first = &domain.levels[0].candidates[combo.indices[0]].id;
    if first.len() > 6 { first[..6].to_string() } else { first.clone() }
}

// ── CSV Output ──

fn print_csv(domain: &Domain, combos: &[Combo]) {
    // Header
    let level_names: Vec<&str> = domain.levels.iter().map(|l| l.name.as_str()).collect();
    print!("rank");
    for n in &level_names {
        print!(",{}", n);
    }
    println!(",n6_pct,perf,power,cost,pareto");

    for (rank, combo) in combos.iter().enumerate() {
        print!("{}", rank + 1);
        for (i, &idx) in combo.indices.iter().enumerate() {
            print!(",{}", domain.levels[i].candidates[idx].id);
        }
        println!(",{:.1},{:.3},{:.3},{:.3},{:.4}",
            combo.n6_avg * 100.0, combo.perf_avg, combo.power_avg,
            combo.cost_avg, combo.pareto_score);
    }
}

// ── Batch All Domains ──

fn load_all_domains(dir: &str) -> Vec<(String, Domain)> {
    let mut domains = Vec::new();
    let dir_path = Path::new(dir);
    if !dir_path.is_dir() {
        eprintln!("Error: {} is not a directory", dir);
        return domains;
    }
    let mut entries: Vec<_> = fs::read_dir(dir_path)
        .unwrap()
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().map_or(false, |ext| ext == "toml"))
        .collect();
    entries.sort_by_key(|e| e.file_name());

    for entry in entries {
        let path = entry.path();
        let name = path.file_stem().unwrap().to_string_lossy().to_string();
        let content = fs::read_to_string(&path).unwrap_or_default();
        let domain = parse_toml(&content);
        if !domain.levels.is_empty() {
            domains.push((name, domain));
        }
    }
    domains
}

fn run_batch_all(dir: &str) {
    let domains = load_all_domains(dir);
    if domains.is_empty() {
        eprintln!("No valid domains found in {}", dir);
        return;
    }

    println!("\n{}", "=".repeat(90));
    println!("  Universal DSE — Batch All ({} domains)", domains.len());
    println!("{}\n", "=".repeat(90));

    println!("  {:>20} | {:>8} | {:>8} | {:>6} | {:>6} | {:>6} | {:>6} | {:>7}",
        "Domain", "Combos", "Compat", "n6%", "Perf", "Power", "Cost", "Pareto");
    println!("  {}", "-".repeat(85));

    let mut total_combos: usize = 0;
    let mut total_compat: usize = 0;
    let mut pareto_sum = 0.0;
    let mut n6_sum = 0.0;

    for (name, domain) in &domains {
        let sizes: Vec<usize> = domain.levels.iter().map(|l| l.candidates.len()).collect();
        let total: usize = sizes.iter().product();
        let combos = enumerate(domain);
        let compat = combos.len();
        total_combos += total;
        total_compat += compat;

        if let Some(best) = combos.first() {
            pareto_sum += best.pareto_score;
            n6_sum += best.n6_avg;
            println!("  {:>20} | {:>8} | {:>8} | {:>5.1} | {:>.3} | {:>.3} | {:>.3} | {:>.4}",
                name, total, compat,
                best.n6_avg * 100.0, best.perf_avg, best.power_avg,
                best.cost_avg, best.pareto_score);
        }
    }

    let n = domains.len() as f64;
    println!("  {}", "-".repeat(85));
    println!("  {:>20} | {:>8} | {:>8} | {:>5.1} | {:>6} | {:>6} | {:>6} | {:>.4}",
        "TOTAL/AVG", total_combos, total_compat,
        n6_sum / n * 100.0, "", "", "", pareto_sum / n);
    println!();
}

// ── Cross-All (NxN) ──

fn run_cross_all(dir: &str, top_n: usize) {
    let domains = load_all_domains(dir);
    let n = domains.len();
    if n < 2 {
        eprintln!("Need at least 2 domains for cross-all");
        return;
    }

    println!("\n{}", "=".repeat(90));
    println!("  Cross-DSE All Pairs: {}C2 = {} pairs", n, n * (n - 1) / 2);
    println!("{}\n", "=".repeat(90));

    // Pre-compute top combos for each domain
    let mut domain_tops: Vec<Vec<Combo>> = Vec::new();
    for (_, domain) in &domains {
        let combos = enumerate(domain);
        let take = std::cmp::min(5, combos.len());
        domain_tops.push(combos[..take].to_vec());
    }

    // All pairs
    struct CrossResult {
        a_name: String,
        b_name: String,
        n6: f64,
        perf: f64,
        power: f64,
        cost: f64,
        score: f64,
    }
    let mut all_results: Vec<CrossResult> = Vec::new();

    for i in 0..n {
        for j in (i + 1)..n {
            let mut best_score: f64 = 0.0;
            let mut best = (0.0, 0.0, 0.0, 0.0, 0.0);
            for a in &domain_tops[i] {
                for b in &domain_tops[j] {
                    let cn6 = (a.n6_avg + b.n6_avg) / 2.0;
                    let cp = (a.perf_avg + b.perf_avg) / 2.0;
                    let cpw = (a.power_avg + b.power_avg) / 2.0;
                    let cc = (a.cost_avg + b.cost_avg) / 2.0;
                    let cs = 0.40 * cn6 + 0.30 * cp + 0.20 * cpw + 0.10 * cc;
                    if cs > best_score {
                        best_score = cs;
                        best = (cn6, cp, cpw, cc, cs);
                    }
                }
            }
            all_results.push(CrossResult {
                a_name: domains[i].0.clone(),
                b_name: domains[j].0.clone(),
                n6: best.0, perf: best.1, power: best.2, cost: best.3, score: best.4,
            });
        }
    }

    // Sort by score
    all_results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());

    let show = std::cmp::min(top_n, all_results.len());
    println!("  {:>4} | {:>18} | {:>18} | {:>5} | {:>5} | {:>5} | {:>5} | {:>6}",
        "Rank", "Domain A", "Domain B", "n6%", "Perf", "Power", "Cost", "Score");
    println!("  {}", "-".repeat(90));

    for (r, cr) in all_results[..show].iter().enumerate() {
        println!("  {:>4} | {:>18} | {:>18} | {:4.1} | {:.3} | {:.3} | {:.3} | {:.4}",
            r + 1, cr.a_name, cr.b_name,
            cr.n6 * 100.0, cr.perf, cr.power, cr.cost, cr.score);
    }

    // Domain frequency in top-20
    let freq_n = std::cmp::min(20, all_results.len());
    let mut freq: std::collections::HashMap<String, usize> = std::collections::HashMap::new();
    for cr in &all_results[..freq_n] {
        *freq.entry(cr.a_name.clone()).or_insert(0) += 1;
        *freq.entry(cr.b_name.clone()).or_insert(0) += 1;
    }
    let mut freq_vec: Vec<_> = freq.into_iter().collect();
    freq_vec.sort_by(|a, b| b.1.cmp(&a.1));

    println!("\n  === Domain Frequency in Top-{} ===\n", freq_n);
    for (name, count) in &freq_vec {
        let bar = "█".repeat(*count * 3);
        println!("  {:>18} {:>2} {}", name, count, bar);
    }

    println!("\n  Total pairs: {}", all_results.len());
    println!("  Avg score: {:.4}", all_results.iter().map(|r| r.score).sum::<f64>() / all_results.len() as f64);
    println!();
}

// ── Validate ──

fn validate_domain(path: &str) {
    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(e) => { eprintln!("Error: {}: {}", path, e); return; }
    };
    let domain = parse_toml(&content);
    let name = Path::new(path).file_stem().unwrap().to_string_lossy();

    println!("\n=== Validation: {} ===\n", name);

    let mut warnings = 0;
    let mut errors = 0;

    // Check levels
    if domain.levels.is_empty() {
        println!("  ERROR: No levels defined");
        errors += 1;
    } else if domain.levels.len() != 5 {
        println!("  WARN: {} levels (standard is 5)", domain.levels.len());
        warnings += 1;
    }

    // Check scoring weights
    let w_sum = domain.weights.n6 + domain.weights.perf + domain.weights.power + domain.weights.cost;
    if (w_sum - 1.0).abs() > 0.05 {
        println!("  WARN: Scoring weights sum to {:.2} (should be ~1.0)", w_sum);
        warnings += 1;
    }

    // Check candidates
    for (i, level) in domain.levels.iter().enumerate() {
        if level.candidates.is_empty() {
            println!("  ERROR: Level {} '{}' has no candidates", i, level.name);
            errors += 1;
            continue;
        }
        for c in &level.candidates {
            if c.id.is_empty() {
                println!("  ERROR: L{} candidate missing id", i);
                errors += 1;
            }
            if c.n6 < 0.0 || c.n6 > 1.0 {
                println!("  ERROR: L{} '{}' n6={:.2} out of range [0,1]", i, c.id, c.n6);
                errors += 1;
            }
            if c.perf < 0.0 || c.perf > 1.0 {
                println!("  WARN: L{} '{}' perf={:.2} out of range", i, c.id, c.perf);
                warnings += 1;
            }
            // Check if n6 is high but has no justification (label is short)
            if c.n6 >= 0.9 && c.label.len() < 10 {
                println!("  WARN: L{} '{}' n6={:.2} but label is minimal — add notes?", i, c.id, c.n6);
                warnings += 1;
            }
        }
    }

    // Check rules reference valid levels
    for (ri, rule) in domain.rules.iter().enumerate() {
        if rule.if_level >= domain.levels.len() {
            println!("  ERROR: Rule {} if_level={} exceeds level count", ri, rule.if_level);
            errors += 1;
        }
        if rule.then_level >= domain.levels.len() {
            println!("  ERROR: Rule {} then_level={} exceeds level count", ri, rule.then_level);
            errors += 1;
        }
    }

    // Summary
    let combos = enumerate(&domain);
    let sizes: Vec<usize> = domain.levels.iter().map(|l| l.candidates.len()).collect();
    let total: usize = sizes.iter().product();
    let filter_pct = if total > 0 { (total - combos.len()) as f64 / total as f64 * 100.0 } else { 0.0 };

    println!("\n  Summary:");
    println!("    Levels: {}", domain.levels.len());
    println!("    Candidates per level: {:?}", sizes);
    println!("    Total combos: {} -> {} compatible ({:.1}% filtered)",
        total, combos.len(), filter_pct);
    println!("    Rules: {}", domain.rules.len());
    println!("    Errors: {}, Warnings: {}", errors, warnings);

    if errors == 0 && warnings == 0 {
        println!("    Status: PASS ✓");
    } else if errors == 0 {
        println!("    Status: PASS with {} warnings", warnings);
    } else {
        println!("    Status: FAIL ({} errors)", errors);
    }
    println!();
}

// ── Random Baseline (Monte Carlo significance test) ──

fn run_random_baseline(n_trials: usize, path: &str) {
    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(e) => { eprintln!("Error: {}: {}", path, e); return; }
    };
    let domain = parse_toml(&content);
    let name = Path::new(path).file_stem().unwrap().to_string_lossy();

    let combos = enumerate(&domain);
    if combos.is_empty() {
        eprintln!("No compatible combinations");
        return;
    }

    let actual_best_n6 = combos[0].n6_avg;
    let actual_best_pareto = combos[0].pareto_score;

    // Simple LCG PRNG (no external deps)
    let mut seed: u64 = 42;
    let lcg_next = |s: &mut u64| -> u64 {
        *s = s.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        *s >> 33
    };

    // Monte Carlo: shuffle n6 scores and recompute
    let mut n6_scores: Vec<f64> = Vec::new();
    for level in &domain.levels {
        for c in &level.candidates {
            n6_scores.push(c.n6);
        }
    }
    let total_candidates = n6_scores.len();

    let mut random_beat_n6 = 0usize;
    let mut random_beat_pareto = 0usize;
    let mut random_n6_sum = 0.0f64;
    let mut random_pareto_sum = 0.0f64;

    println!("\n{}", "=".repeat(66));
    println!("  Random Baseline Test — {}", name);
    println!("  {} trials, shuffling n6 scores across candidates", n_trials);
    println!("{}\n", "=".repeat(66));

    for _ in 0..n_trials {
        // Fisher-Yates shuffle of n6_scores
        let mut shuffled = n6_scores.clone();
        for i in (1..shuffled.len()).rev() {
            let j = (lcg_next(&mut seed) as usize) % (i + 1);
            shuffled.swap(i, j);
        }

        // Assign shuffled n6 scores back to candidates and find best
        // We approximate: pick random n6 for each level's best candidate
        let n_levels = domain.levels.len();
        let mut best_n6 = 0.0f64;
        let mut idx = 0;
        for level in &domain.levels {
            let mut level_max_n6 = 0.0f64;
            for _ in &level.candidates {
                if idx < shuffled.len() {
                    level_max_n6 = level_max_n6.max(shuffled[idx]);
                    idx += 1;
                }
            }
            best_n6 += level_max_n6;
        }
        best_n6 /= n_levels as f64;

        // Approximate Pareto with shuffled n6, keeping perf/power/cost
        let w = &domain.weights;
        let approx_pareto = w.n6 * best_n6 + w.perf * combos[0].perf_avg
            + w.power * combos[0].power_avg + w.cost * combos[0].cost_avg;

        random_n6_sum += best_n6;
        random_pareto_sum += approx_pareto;

        if best_n6 >= actual_best_n6 { random_beat_n6 += 1; }
        if approx_pareto >= actual_best_pareto { random_beat_pareto += 1; }
    }

    let avg_random_n6 = random_n6_sum / n_trials as f64;
    let avg_random_pareto = random_pareto_sum / n_trials as f64;
    let p_n6 = random_beat_n6 as f64 / n_trials as f64;
    let p_pareto = random_beat_pareto as f64 / n_trials as f64;

    println!("  Actual best n6:    {:.1}%", actual_best_n6 * 100.0);
    println!("  Random avg n6:     {:.1}%", avg_random_n6 * 100.0);
    println!("  p-value (n6):      {:.6} ({}/{} trials beat actual)",
        p_n6, random_beat_n6, n_trials);
    println!();
    println!("  Actual Pareto:     {:.4}", actual_best_pareto);
    println!("  Random avg Pareto: {:.4}", avg_random_pareto);
    println!("  p-value (Pareto):  {:.6} ({}/{} trials beat actual)",
        p_pareto, random_beat_pareto, n_trials);
    println!();

    let delta_n6 = (actual_best_n6 - avg_random_n6) * 100.0;
    println!("  n6 advantage:      +{:.1}% over random", delta_n6);

    if p_n6 < 0.01 {
        println!("  Significance:      p < 0.01 — HIGHLY SIGNIFICANT");
    } else if p_n6 < 0.05 {
        println!("  Significance:      p < 0.05 — SIGNIFICANT");
    } else {
        println!("  Significance:      p >= 0.05 — NOT SIGNIFICANT");
    }
    println!();
}

// ── Main ──

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("Universal DSE Explorer — n6-architecture");
        eprintln!();
        eprintln!("Usage:");
        eprintln!("  {} <domain.toml>                   Single domain DSE", args[0]);
        eprintln!("  {} <d1.toml> <d2.toml> [...]       Cross-DSE", args[0]);
        eprintln!("  {} <domain.toml> --top 30           Custom top-N", args[0]);
        eprintln!("  {} <domain.toml> --csv              CSV output", args[0]);
        eprintln!("  {} --all <domains_dir/>             Batch all domains", args[0]);
        eprintln!("  {} --cross-all <domains_dir/> [--top N]  All pairs", args[0]);
        eprintln!("  {} --validate <domain.toml>         Validate TOML", args[0]);
        eprintln!("  {} --random-baseline N <domain.toml>  Monte Carlo test", args[0]);
        eprintln!();
        eprintln!("TOML Format:");
        eprintln!("  [meta]           name, desc");
        eprintln!("  [scoring]        n6, perf, power, cost weights (sum=1.0)");
        eprintln!("  [[level]]        name of each level");
        eprintln!("  [[candidate]]    id, label, n6, perf, power, cost (0.0-1.0)");
        eprintln!("  [[rule]]         type=require|exclude, if_level, if_id, then_level, then_ids");
        std::process::exit(1);
    }

    // Parse args
    let mut toml_files: Vec<String> = Vec::new();
    let mut top_n: usize = 20;
    let mut csv_mode = false;
    let mut batch_all_dir: Option<String> = None;
    let mut cross_all_dir: Option<String> = None;
    let mut validate_file: Option<String> = None;
    let mut random_baseline: Option<(usize, String)> = None;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--top" if i + 1 < args.len() => {
                top_n = args[i + 1].parse().unwrap_or(20);
                i += 2;
            }
            "--csv" => {
                csv_mode = true;
                i += 1;
            }
            "--all" if i + 1 < args.len() => {
                batch_all_dir = Some(args[i + 1].clone());
                i += 2;
            }
            "--cross-all" if i + 1 < args.len() => {
                cross_all_dir = Some(args[i + 1].clone());
                i += 2;
            }
            "--validate" if i + 1 < args.len() => {
                validate_file = Some(args[i + 1].clone());
                i += 2;
            }
            "--random-baseline" if i + 2 < args.len() => {
                let n: usize = args[i + 1].parse().unwrap_or(10000);
                random_baseline = Some((n, args[i + 2].clone()));
                i += 3;
            }
            _ => {
                toml_files.push(args[i].clone());
                i += 1;
            }
        }
    }

    // Dispatch special modes
    if let Some(dir) = batch_all_dir {
        run_batch_all(&dir);
        return;
    }
    if let Some(dir) = cross_all_dir {
        run_cross_all(&dir, top_n);
        return;
    }
    if let Some(path) = validate_file {
        validate_domain(&path);
        return;
    }
    if let Some((n, path)) = random_baseline {
        run_random_baseline(n, &path);
        return;
    }

    if toml_files.is_empty() {
        eprintln!("Error: no TOML files specified");
        std::process::exit(1);
    }

    // Load domains
    let mut domains: Vec<Domain> = Vec::new();
    for path in &toml_files {
        let content = match fs::read_to_string(path) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("Error reading {}: {}", path, e);
                std::process::exit(1);
            }
        };
        let domain = parse_toml(&content);
        if domain.levels.is_empty() {
            eprintln!("Warning: {} has no levels defined", path);
            continue;
        }
        domains.push(domain);
    }

    if domains.is_empty() {
        eprintln!("Error: no valid domains loaded");
        std::process::exit(1);
    }

    // Cross-DSE mode
    if domains.len() > 1 {
        // First run each individually
        for domain in &domains {
            run_single(domain, top_n);
        }
        // Then cross-DSE
        cross_dse(&domains, 5);
        return;
    }

    // Single domain mode
    if csv_mode {
        let combos = enumerate(&domains[0]);
        print_csv(&domains[0], &combos);
    } else {
        run_single(&domains[0], top_n);
    }
}

fn run_single(domain: &Domain, top_n: usize) {
    let sizes: Vec<usize> = domain.levels.iter().map(|l| l.candidates.len()).collect();
    let total: usize = sizes.iter().product();

    let combos = enumerate(domain);
    let compatible = combos.len();

    print_header(domain, total, compatible);
    print_candidates(domain);
    print_top(domain, &combos, top_n);
    print_best_by_category(domain, &combos);

    // Pareto frontier (limit to top 200 for O(n^2) dominance check)
    let pareto_set = if combos.len() <= 500 {
        pareto_frontier(&combos)
    } else {
        pareto_frontier(&combos[..500])
    };
    print_pareto(domain, &combos, &pareto_set);

    print_stats(&combos);

    if !combos.is_empty() {
        print_ascii_path(domain, &combos[0]);
    }
}
