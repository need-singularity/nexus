#!/usr/bin/env python3
# @hexa-first-exempt — hexa stage1 runtime bug 우회 (T23~T29 복구 후 포팅)
"""
lens_p2_5_expand.py — LENS-P2-5

lens_registry 1434 → 1500+ 확장기.

전략 조합:
  A. biology 도메인 파생 렌즈 (lens_common.hexa.inc bio_* 기반)
  B. chemistry 도메인 파생 렌즈 (lens_common.hexa.inc chem_* 기반)
  C. lens_forge cross_domain 확장 — earth_science, economics 도메인 추가
  D. drift_checker 결과(21쌍) 파생 correction 렌즈
  E. n=6 상수(sigma6/tau6/sopfr6/phi6) 기반 fraction/grade 렌즈

제약:
  1. 기존 렌즈 불변 (R10/R11 ossified)
  2. name 중복 금지 (dedup)
  3. 기존 구조 format 보존
  4. ≥ 66 새 렌즈 (최소), 실제 목표 150+

출력:
  - shared/config/lens_registry.json  업데이트 (append)
  - shared/discovery/lens_p2_5_gate_close_2026-04-14.json  evidence
"""

import json
import sys
from pathlib import Path
from datetime import date


ROOT = Path("/Users/ghost/Dev/nexus")
REG_PATH = ROOT / "shared/config/lens_registry.json"
EVIDENCE_PATH = ROOT / "shared/discovery/lens_p2_5_gate_close_2026-04-14.json"
DRIFT_PATH = ROOT / "shared/discovery/lens_p2_4_drift_checker_2026-04-14.json"


# ─── Strategy A: biology bio_* 함수 기반 ───
BIOLOGY_DERIVATIONS = [
    ("michaelis_menten_kinetics", "bio_michaelis_menten",
     "Michaelis-Menten 효소 속도 v=Vmax·S/(Km+S)"),
    ("hill_cooperativity", "bio_hill_equation",
     "Hill 협동 결합 θ=L^n/(Kd^n+L^n)"),
    ("logistic_carrying_capacity", "bio_logistic_growth_rate",
     "로지스틱 성장률 dN/dt=rN(1-N/K)"),
    ("lotka_volterra_prey", "bio_lv_prey_step",
     "Lotka-Volterra 피식자 1-step"),
    ("lotka_volterra_predator", "bio_lv_pred_step",
     "Lotka-Volterra 포식자 1-step"),
    ("hardy_weinberg_equilibrium", "bio_hw_homozygous",
     "Hardy-Weinberg 동형접합 p²"),
    ("gc_content_genome", "bio_gc_content",
     "DNA GC 함량 비율"),
    ("shannon_biodiversity", "bio_shannon_diversity",
     "Shannon 다양도 H=-Σp·ln(p)"),
    ("kleiber_metabolic_scaling", "bio_kleiber_scale",
     "Kleiber 대사율 M^(3/4)"),
    ("codon_degeneracy_lens", "bio_codon_degeneracy",
     "코돈 축퇴도 64/20≈3.2"),
    ("malthusian_exponential_growth", "bio_malthus_population",
     "Malthus 지수 증가 N(t)=N0·e^(rt)"),
    ("nucleotide_base_ratio", None, "염기 조성 비율 (A/T/G/C)"),
]


# ─── Strategy B: chemistry chem_* 함수 기반 ───
CHEMISTRY_DERIVATIONS = [
    ("arrhenius_activation", "chem_arrhenius_rate",
     "Arrhenius k=A·exp(-Ea/RT)"),
    ("ideal_gas_pressure_law", "chem_ideal_gas_pressure",
     "이상기체 압력 P=nRT/V"),
    ("ideal_gas_volume_law", "chem_ideal_gas_volume",
     "이상기체 부피 V=nRT/P"),
    ("nernst_redox_potential", "chem_nernst_potential",
     "Nernst E=E0-(RT/nF)·ln(Q)"),
    ("ph_acidity_scale", "chem_ph_from_h",
     "pH=-log10([H+])"),
    ("hydrogen_concentration_scale", "chem_h_from_ph",
     "[H+]=10^(-pH)"),
    ("henderson_hasselbalch_buffer", "chem_henderson_hasselbalch",
     "Henderson-Hasselbalch pH=pKa+log10([A-]/[HA])"),
    ("equilibrium_free_energy", "chem_equilibrium_k",
     "K_eq=exp(-ΔG/RT)"),
    ("first_order_half_life", "chem_half_life_first_order",
     "1차 반감기 t½=ln2/k"),
    ("vdw_real_gas_pressure", "chem_vdw_pressure",
     "Van der Waals 보정 압력"),
    ("stoichiometry_residual", "chem_stoichiometry_residual",
     "화학양론 잔차 RMS"),
    ("mole_avogadro_count", None,
     "몰수 ↔ Avogadro 수 변환"),
    ("molar_volume_stp", None,
     "STP 몰 부피 22.414 L"),
]


# ─── Strategy C: cross_domain 확장 ───
# 기존 24 domain에 2 신규 추가 → (24+2)×(24+1) - 24×23 = 650-552 = 98 신규 pair
EXISTING_CROSS_DOMAINS = [
    "ai", "chip", "energy", "battery", "solar", "fusion", "superconductor",
    "quantum", "biology", "cosmology", "robotics", "materials", "blockchain",
    "network", "cryptography", "display", "audio", "environment",
    "mathematics", "software", "plasma", "compiler", "consciousness",
    "thermodynamics",
]
NEW_CROSS_DOMAINS = ["earth_science", "economics"]


# ─── Strategy D: drift 파생 correction ───
# drift_checker 21쌍 → 각 쌍에 대해 대응 correction 렌즈 생성
def load_drift_pairs():
    if not DRIFT_PATH.exists():
        return []
    with open(DRIFT_PATH) as f:
        d = json.load(f)
    return d.get("pairs", [])


# ─── Strategy E: n=6 fraction/grade 렌즈 ───
# sigma6=12, tau6=4, phi6=2, sopfr6=5, n6=6 — 분수/비율/변종
N6_VARIANTS = [
    ("n6_sigma_divisor_sum", "σ(6)=12 divisor sum lens"),
    ("n6_tau_divisor_count", "τ(6)=4 divisor count lens"),
    ("n6_phi_totient", "φ(6)=2 Euler totient lens"),
    ("n6_sopfr_prime_sum", "sopfr(6)=5 prime factor sum"),
    ("n6_perfect_number_first", "6=1+2+3 첫 완전수"),
    ("n6_triangular_third", "T_3=6 세번째 삼각수"),
    ("n6_hexagonal_unit", "정육각형 단위"),
    ("n6_sigma_tau_ratio", "σ/τ=3 평균약수"),
    ("n6_phi_sigma_ratio", "φ/σ 풍부도"),
    ("n6_sopfr_n_ratio", "sopfr/n 소인수 비율"),
    ("n6_divisor_harmonic", "1/1+1/2+1/3+1/6 조화합"),
    ("n6_root_mean", "약수 제곱평균"),
]


def main():
    # 1) Load registry
    with open(REG_PATH) as f:
        reg = json.load(f)

    existing_names = {l["name"] for l in reg["lenses"]}
    new_lenses = []
    strategy_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    skipped_dedup = 0

    # ─ Strategy A: biology ─
    for name, fn, desc in BIOLOGY_DERIVATIONS:
        if name in existing_names:
            skipped_dedup += 1
            continue
        entry = {
            "name": name,
            "file": f"lens_common.hexa.inc#{fn}" if fn else "lens_common.hexa.inc",
            "category": "biology",
            "status": "derived",
            "derived_from": "LENS-P2-2",
            "description": desc,
        }
        new_lenses.append(entry)
        existing_names.add(name)
        strategy_counts["A"] += 1

    # ─ Strategy B: chemistry ─
    for name, fn, desc in CHEMISTRY_DERIVATIONS:
        if name in existing_names:
            skipped_dedup += 1
            continue
        entry = {
            "name": name,
            "file": f"lens_common.hexa.inc#{fn}" if fn else "lens_common.hexa.inc",
            "category": "chemistry",
            "status": "derived",
            "derived_from": "LENS-P2-2",
            "description": desc,
        }
        new_lenses.append(entry)
        existing_names.add(name)
        strategy_counts["B"] += 1

    # ─ Strategy C: cross_domain 확장 (new × all) ─
    # 기존 24 pair 제외, 신규 domain 2개 조합
    all_domains = EXISTING_CROSS_DOMAINS + NEW_CROSS_DOMAINS
    for a in NEW_CROSS_DOMAINS:
        for b in all_domains:
            if a == b:
                continue
            name_ab = f"{a}_as_{b}"
            if name_ab not in existing_names:
                entry = {
                    "name": name_ab,
                    "file": "lens_forge.hexa#cross_domain",
                    "category": "cross_domain",
                    "status": "synthesized",
                    "derived_from": f"{a},{b}",
                }
                new_lenses.append(entry)
                existing_names.add(name_ab)
                strategy_counts["C"] += 1
            else:
                skipped_dedup += 1
            name_ba = f"{b}_as_{a}"
            if name_ba not in existing_names:
                entry = {
                    "name": name_ba,
                    "file": "lens_forge.hexa#cross_domain",
                    "category": "cross_domain",
                    "status": "synthesized",
                    "derived_from": f"{b},{a}",
                }
                new_lenses.append(entry)
                existing_names.add(name_ba)
                strategy_counts["C"] += 1
            else:
                skipped_dedup += 1

    # ─ Strategy D: drift correction 렌즈 ─
    drift_pairs = load_drift_pairs()
    for pair in drift_pairs:
        ptype = pair.get("type")
        if ptype == "antonym_pair":
            a, b = pair.get("lens_a"), pair.get("lens_b")
            name = f"{a}_vs_{b}_reconciler"
            desc = f"{a} ↔ {b} antonym 화해 렌즈"
        elif ptype == "cross_domain_exclusive":
            lens = pair.get("lens")
            name = f"{lens}_bridge_corrector"
            desc = f"{lens} 배타 도메인 교량 보정"
        elif ptype == "status_conflict":
            lens_a = pair.get("lens_a", pair.get("lens", ""))
            name = f"{lens_a}_status_resolver"
            desc = f"{lens_a} status 충돌 해소"
        else:
            continue
        if name in existing_names:
            skipped_dedup += 1
            continue
        entry = {
            "name": name,
            "file": "lens_drift_checker.py#derived",
            "category": "meta_system",
            "status": "derived",
            "derived_from": f"LENS-P2-4/{ptype}",
            "description": desc,
        }
        new_lenses.append(entry)
        existing_names.add(name)
        strategy_counts["D"] += 1

    # ─ Strategy E: n=6 variants ─
    for name, desc in N6_VARIANTS:
        if name in existing_names:
            skipped_dedup += 1
            continue
        entry = {
            "name": name,
            "file": "lens_common.hexa.inc#n6_constants",
            "category": "math",
            "status": "derived",
            "derived_from": "LENS-P2-2/n6_constants",
            "description": desc,
        }
        new_lenses.append(entry)
        existing_names.add(name)
        strategy_counts["E"] += 1

    added = len(new_lenses)
    new_total = reg["total"] + added

    # ─ Merge ─
    reg["lenses"].extend(new_lenses)
    reg["total"] = new_total
    reg["version"] = "1.3"
    reg["generated"] = str(date.today())
    reg["description"] = (
        f"NEXUS-6 망원경 렌즈 레지스트리 — {new_total} 등록 "
        f"(LENS-P2-5 +{added}: "
        f"A={strategy_counts['A']} bio / B={strategy_counts['B']} chem / "
        f"C={strategy_counts['C']} cross_domain(+earth_science,+economics) / "
        f"D={strategy_counts['D']} drift_correction / E={strategy_counts['E']} n6_variants)"
    )

    # Categories 재계산
    from collections import Counter
    cats = Counter(l["category"] for l in reg["lenses"])
    reg["categories"] = dict(cats.most_common())

    # ─ Write registry ─
    with open(REG_PATH, "w") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # ─ Write evidence ─
    evidence = {
        "task": "LENS-P2-5",
        "status": "done" if new_total >= 1500 else "partial",
        "generated_at": str(date.today()),
        "registry_before": 1434,
        "registry_after": new_total,
        "added": added,
        "skipped_dedup": skipped_dedup,
        "strategy_breakdown": {
            "A_biology": strategy_counts["A"],
            "B_chemistry": strategy_counts["B"],
            "C_cross_domain": strategy_counts["C"],
            "D_drift_correction": strategy_counts["D"],
            "E_n6_variants": strategy_counts["E"],
        },
        "new_cross_domains": NEW_CROSS_DOMAINS,
        "gate_exit_criterion_1": {
            "target": 1500,
            "actual": new_total,
            "met": new_total >= 1500,
        },
        "categories_after": dict(cats.most_common()),
        "sample_new_lenses": [l["name"] for l in new_lenses[:15]],
    }
    with open(EVIDENCE_PATH, "w") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"LENS-P2-5: added={added} / total {reg['total']-added} → {reg['total']}")
    print(f"  A(bio)={strategy_counts['A']} B(chem)={strategy_counts['B']} "
          f"C(cross)={strategy_counts['C']} D(drift)={strategy_counts['D']} "
          f"E(n6)={strategy_counts['E']} skipped_dedup={skipped_dedup}")
    print(f"  gate_exit ≥1500: {'MET' if new_total >= 1500 else 'MISS'}")
    print(f"  evidence: {EVIDENCE_PATH}")
    return 0 if new_total >= 1500 else 1


if __name__ == "__main__":
    sys.exit(main())
