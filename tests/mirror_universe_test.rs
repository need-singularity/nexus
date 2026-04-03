/// 거울 우주 통합 실험
/// — 모든 렌즈가 거울이자 관찰자, 서로를 비추면 모두가 연결됨
use nexus6::telescope::Telescope;
use nexus6::telescope::mirror_scan::{CorridorBehavior, mirror_delta};

fn sin_data(n: usize, d: usize) -> Vec<f64> {
    (0..n * d).map(|i| ((i as f64) * std::f64::consts::TAU / 10.0).sin()).collect()
}

fn mixed_data(n: usize, d: usize) -> Vec<f64> {
    (0..n * d).map(|i| {
        let x = i as f64;
        (x * 0.1).sin() + (x * 0.37).cos() + (x % 7.0) * 0.1
    }).collect()
}

// ─── 1. 거울 우주 통합 (6 렌즈) ─────────────────────────────────

#[test]
fn test_mirror_universe_6_lenses() {
    let t = Telescope::new();
    let data = sin_data(50, 4);
    let r = t.mirror_universe(&data, 50, 4, None, Some(6));

    println!("=== 거울 우주 (6 렌즈) ===");
    println!("렌즈: {:?}", r.lens_names);
    println!("조화도: {:.4}", r.harmony);

    let c = &r.connection;
    println!("\n--- 연결 증명 ---");
    println!("직접 연결: {:.1}%", c.direct_connectivity * 100.0);
    println!("간접 연결 (M²): {:.1}%", c.indirect_connectivity * 100.0);
    println!("완전 연결 깊이: {}", c.full_connection_depth);
    println!("비대칭도: {:.4}", c.asymmetry);
    println!("자기작용: {:.4}", c.self_action_strength);
    println!("상호작용: {:.4}", c.mutual_action_strength);
    println!("모두 연결됨: {}", c.all_connected);

    println!("\n--- 공명 캐스케이드 ---");
    for (k, e) in &r.cascade.energy_by_depth {
        println!("M^{}: energy = {:.4}", k, e);
    }
    println!("지배 고유값: {:.4}", r.cascade.dominant_eigenvalue);
    println!("스펙트럼 갭: {:.4}", r.cascade.spectral_gap);
    println!("수렴: {}", r.cascade.converges);
    println!("지배 고유벡터:");
    for (name, val) in &r.cascade.dominant_eigenvector {
        println!("  {}: {:.4}", name, val);
    }

    println!("\n--- 반사 엔트로피 ---");
    println!("시스템 엔트로피: {:.4}", r.entropy.system_entropy);
    for (name, e) in &r.entropy.emission_entropy {
        println!("  방출 {}: {:.4}", name, e);
    }

    println!("\n--- 거울 지문 ---");
    println!("시그니처: {:?}", r.fingerprint.signature.iter().map(|v| format!("{:.3}", v)).collect::<Vec<_>>());
    println!("지문 엔트로피: {:.4}", r.fingerprint.entropy);
    println!("연결 깊이: {}", r.fingerprint.connection_depth);

    println!("\n--- 상위 공명 쌍 ---");
    for (a, b, v) in r.top_resonances.iter().take(10) {
        println!("  {} → {}: {:.4}", a, b, v);
    }

    println!("\n--- 자기 반사 (대각선) ---");
    for (name, v) in &r.self_reflection_strengths {
        println!("  {}: {:.4}", name, v);
    }

    println!("\n--- 방출력 Top ---");
    for (name, v) in r.mirror_power.iter().take(6) {
        println!("  {}: {:.4}", name, v);
    }
    println!("--- 수신력 Top ---");
    for (name, v) in r.mirror_sensitivity.iter().take(6) {
        println!("  {}: {:.4}", name, v);
    }

    assert_eq!(r.lens_count, 6);
    assert!(r.harmony >= 0.0);
}

// ─── 2. 선택 렌즈 미러볼 ────────────────────────────────────────

#[test]
fn test_mirror_universe_selected() {
    let t = Telescope::new();
    let data = mixed_data(40, 5);
    let selected = &[
        "ConsciousnessLens", "TopologyLens", "EntropyLens",
        "MirrorLens", "WaveLens", "GravityLens",
    ];
    let r = t.mirror_universe(&data, 40, 5, Some(selected), None);

    println!("=== 선택 6렌즈 미러볼 ===");
    println!("렌즈: {:?}", r.lens_names);
    println!("직접 연결: {:.1}%", r.connection.direct_connectivity * 100.0);
    println!("조화도: {:.4}", r.harmony);

    for (a, b, v) in r.top_resonances.iter().take(6) {
        println!("  {} → {}: {:.4}", a, b, v);
    }

    assert_eq!(r.lens_count, selected.len());
}

// ─── 3. 무한 거울 복도 ──────────────────────────────────────────

#[test]
fn test_infinite_corridor_experiments() {
    let t = Telescope::new();
    let data = mixed_data(40, 6);

    let pairs = [
        ("EntropyLens", "DensityLens"),
        ("ConsciousnessLens", "WaveLens"),
        ("TopologyLens", "MirrorLens"),
        ("GravityLens", "CausalLens"),
        ("SpectralLens", "FractalLens"),
        ("ChaosLens", "StabilityLens"),
    ];

    println!("=== 무한 거울 복도 실험 ===");
    for (a, b) in &pairs {
        if let Some(r) = t.infinite_corridor(&data, 40, 6, a, b, 20) {
            let behavior = match &r.behavior {
                CorridorBehavior::Converge => "수렴".to_string(),
                CorridorBehavior::Diverge => "발산".to_string(),
                CorridorBehavior::Cycle(p) => format!("주기({})", p),
                CorridorBehavior::Chaotic => "카오스".to_string(),
            };
            println!("{} ↔ {}: {} | 반복={} | 최종크기={:.4}",
                a, b, behavior, r.trajectory.len(), r.fixed_point_magnitude);
            if r.trajectory.len() <= 10 {
                println!("  궤적: {:?}", r.trajectory.iter().map(|v| format!("{:.3}", v)).collect::<Vec<_>>());
            }
        } else {
            println!("{} ↔ {}: 실행 불가", a, b);
        }
    }
}

// ─── 4. 자기 반사 (나르키소스) ───────────────────────────────────

#[test]
fn test_self_reflection_experiments() {
    let t = Telescope::new();
    let data = mixed_data(40, 6);

    let lens_names = [
        "EntropyLens", "ConsciousnessLens", "TopologyLens",
        "MirrorLens", "ChaosLens", "VoidLens",
        "GravityLens", "WaveLens", "DensityLens",
    ];

    println!("=== 자기 반사 (나르키소스) 실험 ===");
    for name in &lens_names {
        if let Some(r) = t.self_reflect(&data, 40, 6, name, 15) {
            let fp = if r.has_fixed_point { "고정점 O" } else { "고정점 X" };
            let last_sim = r.self_similarity_curve.last().map(|v| format!("{:.4}", v)).unwrap_or_default();
            println!("{:25} | {} | 반복={} | 최종유사도={}",
                name, fp, r.trajectory.len(), last_sim);
            if r.trajectory.len() <= 8 {
                println!("  궤적: {:?}", r.trajectory.iter().map(|v| format!("{:.3}", v)).collect::<Vec<_>>());
            }
        } else {
            println!("{}: 실행 불가", name);
        }
    }
}

// ─── 5. 하위 호환 검증 ──────────────────────────────────────────

#[test]
fn test_backward_compat() {
    let t = Telescope::new();
    let data = sin_data(30, 3);

    let ball = t.mirror_ball(&data, 30, 3, Some(6));
    println!("=== 하위 호환: mirror_ball ===");
    println!("렌즈: {}, 조화: {:.4}", ball.lens_count, ball.harmony);
    assert_eq!(ball.lens_count, 6);

    if let Some(r) = t.mirror_reflect(&data, 30, 3, "EntropyLens", "DensityLens") {
        println!("=== 하위 호환: mirror_reflect ===");
        println!("{} ↔ {}", r.lens_a, r.lens_b);
    }
}

// ─── 6. 대규모 미러볼 (20 렌즈) ─────────────────────────────────

#[test]
fn test_mirror_universe_20_lenses() {
    let t = Telescope::new();
    let data = mixed_data(50, 5);
    let r = t.mirror_universe(&data, 50, 5, None, Some(20));

    println!("=== 대규모 미러볼 (20 렌즈) ===");
    println!("렌즈 수: {}", r.lens_count);
    println!("반사 셀: {}", r.reflections.len());
    println!("조화도: {:.4}", r.harmony);
    println!("직접 연결: {:.1}%", r.connection.direct_connectivity * 100.0);
    println!("간접 연결: {:.1}%", r.connection.indirect_connectivity * 100.0);
    println!("완전 연결 깊이: {}", r.connection.full_connection_depth);
    println!("모두 연결됨: {}", r.connection.all_connected);
    println!("지배 고유값: {:.4}", r.cascade.dominant_eigenvalue);
    println!("스펙트럼 갭: {:.4}", r.cascade.spectral_gap);

    println!("\n--- 방출력 Top 5 ---");
    for (name, v) in r.mirror_power.iter().take(5) {
        println!("  {}: {:.4}", name, v);
    }
    println!("--- 수신력 Top 5 ---");
    for (name, v) in r.mirror_sensitivity.iter().take(5) {
        println!("  {}: {:.4}", name, v);
    }
    println!("--- 상위 공명 쌍 ---");
    for (a, b, v) in r.top_resonances.iter().take(10) {
        println!("  {} → {}: {:.4}", a, b, v);
    }

    assert_eq!(r.lens_count, 20);
    assert_eq!(r.reflections.len(), 400);
}

// ─── 7. 실시간 변형 감지 ────────────────────────────────────────

#[test]
fn test_mirror_delta_detection() {
    let t = Telescope::new();
    let data1 = sin_data(40, 4);
    let data2 = mixed_data(40, 4);

    let r1 = t.mirror_universe(&data1, 40, 4, None, Some(10));
    let r2 = t.mirror_universe(&data2, 40, 4, None, Some(10));
    let delta = mirror_delta(&r1, &r2);

    println!("=== 실시간 변형 감지 ===");
    println!("공명 이동량: {:.4}", delta.resonance_shift);
    println!("조화도 변화: {:.4}", delta.harmony_delta);
    println!("연결도 변화: {:.4}", delta.connectivity_delta);
    println!("고유값 변화: {:.4}", delta.eigenvalue_delta);
    println!("상전이: {}", delta.phase_transition);

    println!("\n새로운 공명 쌍:");
    for (a, b, v) in &delta.new_resonances {
        println!("  + {} → {}: {:.4}", a, b, v);
    }
    println!("사라진 공명 쌍:");
    for (a, b, v) in &delta.lost_resonances {
        println!("  - {} → {}: {:.4}", a, b, v);
    }
    println!("가장 크게 변한 렌즈:");
    for (name, d) in &delta.most_changed_lenses {
        println!("  {}: Δ{:.4}", name, d);
    }
}

// ─── 8. 자율 렌즈 조합 발견 ─────────────────────────────────────

#[test]
fn test_auto_lens_combinations() {
    let t = Telescope::new();
    let data = mixed_data(50, 5);
    let r = t.mirror_universe(&data, 50, 5, None, Some(20));
    let combos = t.discover_combinations(&r, 6);

    println!("=== 자율 렌즈 조합 발견 (20렌즈 → 6개 조합) ===");
    for c in &combos {
        println!("\n[{}] score={:.4}", c.name, c.score);
        println!("  이유: {}", c.reason);
        println!("  렌즈: {:?}", c.lenses);
    }

    assert!(!combos.is_empty());
}

// ─── 9. 규칙 없는 자유 탐색 ─────────────────────────────────────

#[test]
fn test_free_explore_evolution() {
    let t = Telescope::new();
    let data = mixed_data(40, 5);
    let r = t.free_explore(&data, 40, 5, Some(10), 8);

    println!("=== 규칙 없는 자유 탐색 ===");
    println!("세대 수: {}", r.generations);
    println!("상전이: {:?}", r.phase_transitions);

    println!("\n조화도 궤적:");
    for (i, h) in r.harmony_trajectory.iter().enumerate() {
        println!("  Gen {}: harmony={:.6}", i, h);
    }
    println!("\n연결도 궤적:");
    for (i, c) in r.connectivity_trajectory.iter().enumerate() {
        println!("  Gen {}: connectivity={:.4}", i, c);
    }
    println!("\n고유값 궤적:");
    for (i, e) in r.eigenvalue_trajectory.iter().enumerate() {
        println!("  Gen {}: eigenvalue={:.4}", i, e);
    }

    println!("\n최적 렌즈 조합:");
    for c in &r.best_combinations {
        println!("  [{}] score={:.4} — {:?}", c.name, c.score, c.lenses);
    }

    println!("\n최종 상태:");
    println!("  조화도: {:.4}", r.final_state.harmony);
    println!("  연결: {:.1}%", r.final_state.connection.direct_connectivity * 100.0);
    println!("  고유값: {:.4}", r.final_state.cascade.dominant_eigenvalue);
}
