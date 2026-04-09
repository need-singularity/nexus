#!/usr/bin/env python3
"""
L-1_quark 레벨 노드 생성 스크립트
PDG 2024 데이터 기반 표준모형 61입자 + 상호작용
카테고리: 쿼크(18) + 렙톤(12) + 게이지보손(12) + 표준모형상수(20) + 대칭군(10) + 상호작용(10) + 쿼크혼합(10)
"""

import json
import shutil
from datetime import datetime

SRC = "/Users/ghost/Dev/nexus/shared/reality_map.json"
PDG_URL = "https://pdg.lbl.gov/"
PDG_SOURCE = "Particle Data Group (PDG) 2024"

def make_node(
    node_id, claim, measured, unit, detail,
    n6_expr, n6_value, verify, grade, causal,
    uncertainty=0, thread=None, origin="natural",
    bt_refs=None, siblings=None, children=None,
    cause=""
):
    return {
        "id": node_id,
        "level": "L-1_quark",
        "claim": claim,
        "measured": measured,
        "unit": unit,
        "detail": detail,
        "source": PDG_SOURCE,
        "source_url": PDG_URL,
        "uncertainty": uncertainty,
        "n6_expr": n6_expr,
        "n6_value": n6_value,
        "verify": verify,
        "grade": grade,
        "causal": causal,
        "cause": cause,
        "children": children or [],
        "siblings": siblings or [],
        "thread": thread or "misc",
        "origin": origin,
        "bt_refs": bt_refs or ["BT-137", "BT-165", "BT-208"]
    }


# ==============================================================
# 카테고리 1: 쿼크 18노드 (6맛 × 질량/전하/스핀)
# ==============================================================
quark_nodes = [
    # --- UP 쿼크 ---
    make_node(
        "L-1-quark-up-mass",
        "업 쿼크 질량 (MS-bar, 2 GeV)",
        2.16, "MeV", "PDG 2024 권장값 u 쿼크 MS-bar 질량 μ=2 GeV",
        "misc", 2.16, "2.16 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.49,
        cause="쿼크 질량은 힉스 메커니즘 유카와 결합에서 발생, 6맛 = n=6"
    ),
    make_node(
        "L-1-quark-up-charge",
        "업 쿼크 전하",
        2/3, "e", "u/c/t 업형 쿼크 전하 +2/3e",
        "misc", 2/3, "2/3 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="SU(2)_L 아이소스핀 +1/2, 약한 하이퍼전하 +1/6 → Q = +2/3"
    ),
    make_node(
        "L-1-quark-up-spin",
        "업 쿼크 스핀",
        0.5, "ħ", "모든 쿼크 스핀 1/2 (페르미온)",
        "misc", 0.5, "1/2 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        thread="misc",
        cause="쿼크는 페르미온 → 스핀 1/2 (파울리 원리)"
    ),
    # --- DOWN 쿼크 ---
    make_node(
        "L-1-quark-down-mass",
        "다운 쿼크 질량 (MS-bar, 2 GeV)",
        4.67, "MeV", "PDG 2024 권장값 d 쿼크 MS-bar 질량",
        "misc", 4.67, "4.67 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.48,
        cause="힉스 메커니즘 유카와 결합, u+d = 업형+다운형 한 세대"
    ),
    make_node(
        "L-1-quark-down-charge",
        "다운 쿼크 전하",
        -1/3, "e", "d/s/b 다운형 쿼크 전하 -1/3e",
        "misc", -1/3, "-1/3 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="SU(2)_L 아이소스핀 -1/2, 약한 하이퍼전하 +1/6 → Q = -1/3"
    ),
    make_node(
        "L-1-quark-down-spin",
        "다운 쿼크 스핀",
        0.5, "ħ", "모든 쿼크 스핀 1/2 (페르미온)",
        "misc", 0.5, "1/2 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    # --- CHARM 쿼크 ---
    make_node(
        "L-1-quark-charm-mass",
        "참 쿼크 질량 (MS-bar, mc)",
        1270.0, "MeV", "PDG 2024 c 쿼크 MS-bar 질량 μ=mc",
        "misc", 1270.0, "1270 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=20.0,
        cause="2세대 업형 쿼크, 참 하드로닉 스펙트럼으로 결정"
    ),
    make_node(
        "L-1-quark-charm-charge",
        "참 쿼크 전하",
        2/3, "e", "업형 쿼크 전하 +2/3e (u/c/t 동일)",
        "misc", 2/3, "+2/3 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    make_node(
        "L-1-quark-charm-spin",
        "참 쿼크 스핀",
        0.5, "ħ", "페르미온 스핀 1/2",
        "misc", 0.5, "1/2 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    # --- STRANGE 쿼크 ---
    make_node(
        "L-1-quark-strange-mass",
        "스트레인지 쿼크 질량 (MS-bar, 2 GeV)",
        93.4, "MeV", "PDG 2024 s 쿼크 MS-bar 질량",
        "misc", 93.4, "93.4 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=8.6,
        cause="2세대 다운형 쿼크, 기묘성(strangeness) 보존 강상호작용"
    ),
    make_node(
        "L-1-quark-strange-charge",
        "스트레인지 쿼크 전하",
        -1/3, "e", "다운형 쿼크 전하 -1/3e",
        "misc", -1/3, "-1/3 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    make_node(
        "L-1-quark-strange-spin",
        "스트레인지 쿼크 스핀",
        0.5, "ħ", "페르미온 스핀 1/2",
        "misc", 0.5, "1/2 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    # --- TOP 쿼크 ---
    make_node(
        "L-1-quark-top-mass",
        "탑 쿼크 극점 질량 (pole mass)",
        172690.0, "MeV", "PDG 2024 t 쿼크 극점 질량 172.69±0.30 GeV",
        "misc", 172690.0, "172690 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=300.0,
        cause="3세대 업형 쿼크, 가장 무거운 기본입자, 수명 < 하드론화 시간"
    ),
    make_node(
        "L-1-quark-top-charge",
        "탑 쿼크 전하",
        2/3, "e", "업형 쿼크 전하 +2/3e",
        "misc", 2/3, "+2/3 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    make_node(
        "L-1-quark-top-spin",
        "탑 쿼크 스핀",
        0.5, "ħ", "페르미온 스핀 1/2",
        "misc", 0.5, "1/2 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    # --- BOTTOM 쿼크 ---
    make_node(
        "L-1-quark-bottom-mass",
        "보텀 쿼크 MS-bar 질량 (mb)",
        4180.0, "MeV", "PDG 2024 b 쿼크 MS-bar 질량 4.18±0.03 GeV",
        "misc", 4180.0, "4180 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=30.0,
        cause="3세대 다운형 쿼크, b-물리(CP위반) 연구 핵심"
    ),
    make_node(
        "L-1-quark-bottom-charge",
        "보텀 쿼크 전하",
        -1/3, "e", "다운형 쿼크 전하 -1/3e",
        "misc", -1/3, "-1/3 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    make_node(
        "L-1-quark-bottom-spin",
        "보텀 쿼크 스핀",
        0.5, "ħ", "페르미온 스핀 1/2",
        "misc", 0.5, "1/2 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
]

# ==============================================================
# 카테고리 2: 렙톤 12노드 (6종 × 질량/전하)
# ==============================================================
lepton_nodes = [
    # 하전 렙톤 질량
    make_node(
        "L-1-lepton-electron-mass",
        "전자 질량",
        0.51099895, "MeV", "PDG 2024 전자 질량 0.51099895 MeV",
        "misc", 0.51099895, "0.51099895 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=1.5e-8,
        cause="가장 가벼운 하전 렙톤, 원자 전자껍질 구조 결정"
    ),
    make_node(
        "L-1-lepton-electron-charge",
        "전자 전하",
        -1.0, "e", "전자 기본 전하 -1e = -1.602176634×10⁻¹⁹ C",
        "misc", -1.0, "-1 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="U(1)_EM 게이지 대칭 기본 전하 단위"
    ),
    make_node(
        "L-1-lepton-muon-mass",
        "뮤온 질량",
        105.6583755, "MeV", "PDG 2024 μ 질량 105.658 MeV",
        "misc", 105.6583755, "105.658 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.0000023,
        cause="2세대 하전 렙톤, 수명 2.197μs (약력 붕괴)"
    ),
    make_node(
        "L-1-lepton-muon-charge",
        "뮤온 전하",
        -1.0, "e", "하전 렙톤 전하 -1e",
        "misc", -1.0, "-1 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    make_node(
        "L-1-lepton-tau-mass",
        "타우 질량",
        1776.86, "MeV", "PDG 2024 τ 질량 1776.86±0.12 MeV",
        "misc", 1776.86, "1776.86 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.12,
        cause="3세대 하전 렙톤, 수명 290.3fs, 하드론/렙톤 붕괴"
    ),
    make_node(
        "L-1-lepton-tau-charge",
        "타우 전하",
        -1.0, "e", "하전 렙톤 전하 -1e",
        "misc", -1.0, "-1 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    # 중성미자 질량 상한
    make_node(
        "L-1-lepton-nu-e-mass-upper",
        "전자 중성미자 질량 상한",
        0.0000008, "MeV", "PDG 2024 ν_e 질량 상한 < 0.8 eV (직접 측정, KATRIN)",
        "misc", 0.0000008, "< 8×10⁻⁷ MeV (KATRIN 2022)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="베타붕괴 운동학에서 트리튬 엔드포인트 스펙트럼, KATRIN 직접 측정"
    ),
    make_node(
        "L-1-lepton-nu-e-charge",
        "전자 중성미자 전하",
        0.0, "e", "중성미자 전하 0 (전기적 중성)",
        "misc", 0.0, "0 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="중성미자는 U(1)_EM 게이지 전하 없음"
    ),
    make_node(
        "L-1-lepton-nu-mu-mass-upper",
        "뮤 중성미자 질량 상한",
        0.19, "MeV", "PDG 2024 ν_μ 질량 상한 < 190 keV (파이온 붕괴)",
        "misc", 0.19, "< 0.19 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="π→μν 붕괴 운동학에서 뮤온 운동량 측정으로 제한"
    ),
    make_node(
        "L-1-lepton-nu-tau-mass-upper",
        "타우 중성미자 질량 상한",
        18.2, "MeV", "PDG 2024 ν_τ 질량 상한 < 18.2 MeV (타우 붕괴)",
        "misc", 18.2, "< 18.2 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="τ→5π+ν 붕괴 운동학 분석"
    ),
    make_node(
        "L-1-lepton-flavor-count",
        "렙톤 맛 총 수 = 6 = n",
        6, "종", "e/μ/τ + ν_e/ν_μ/ν_τ = 6종, 3세대 × 2",
        "n", 6, "6 == n",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="n",
        cause="쿼크-렙톤 대칭 (anomaly cancellation): 렙톤 6 = 쿼크 6 = n",
        bt_refs=["BT-137", "BT-165", "BT-208", "BT-101"]
    ),
    make_node(
        "L-1-lepton-charged-count",
        "하전 렙톤 수 = 3 = tau/2",
        3, "종", "e/μ/τ 하전 렙톤 3종 = τ/2 = 4/2",
        "misc", 3, "3 (tau/2 = 2)",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="3세대 SM 구조, 4번째 세대 LEP Z→ν 측정에서 배제"
    ),
]

# ==============================================================
# 카테고리 3: 게이지 보손 12노드
# ==============================================================
gauge_nodes = [
    # 광자
    make_node(
        "L-1-boson-photon-mass",
        "광자 질량 (상한)",
        0.0, "MeV", "PDG 2024 광자 질량 < 10⁻¹⁸ eV, 실용상 0",
        "misc", 0.0, "0 MeV (이론값, U(1)_EM 게이지 불변)",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="U(1)_EM 게이지 대칭 → 광자 질량 = 0 (Goldstone 정리 반전)"
    ),
    make_node(
        "L-1-boson-photon-spin",
        "광자 스핀",
        1, "ħ", "벡터 보손 스핀 1",
        "misc", 1, "1 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="게이지 보손은 벡터장 → 스핀 1"
    ),
    # W 보손
    make_node(
        "L-1-boson-W-mass",
        "W 보손 질량",
        80369.0, "MeV", "PDG 2024 W 질량 80.369±0.013 GeV (LEP/Tevatron/LHC 평균)",
        "misc", 80369.0, "80369 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=13.0,
        cause="힉스 메커니즘 SU(2)_L 자발 대칭 깨짐, mW = g·v/2"
    ),
    make_node(
        "L-1-boson-W-charge",
        "W 보손 전하 (W+/W-)",
        1.0, "e", "W± 전하 ±1e, 약력 전하 변환 매개",
        "misc", 1.0, "±1 e",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="SU(2)_L 사다리 연산자 T± → 전하 변환"
    ),
    make_node(
        "L-1-boson-W-spin",
        "W 보손 스핀",
        1, "ħ", "벡터 보손 스핀 1",
        "misc", 1, "1 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    # Z 보손
    make_node(
        "L-1-boson-Z-mass",
        "Z 보손 질량",
        91187.6, "MeV", "PDG 2024 Z 질량 91.1876±0.0021 GeV (LEP 정밀 측정)",
        "misc", 91187.6, "91187.6 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=2.1,
        cause="약한 혼합각 sin²θ_W ≈ 0.231로 mZ = mW/cosθ_W"
    ),
    make_node(
        "L-1-boson-Z-spin",
        "Z 보손 스핀",
        1, "ħ", "벡터 보손 스핀 1",
        "misc", 1, "1 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
    # 힉스 보손
    make_node(
        "L-1-boson-higgs-mass",
        "힉스 보손 질량",
        125250.0, "MeV", "PDG 2024 힉스 질량 125.20±0.11 GeV (LHC ATLAS+CMS)",
        "misc", 125250.0, "125250 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=110.0,
        cause="힉스 포텐셜 V(φ) 최솟값에서 VEV v=246 GeV → mH 결정"
    ),
    make_node(
        "L-1-boson-higgs-spin",
        "힉스 보손 스핀",
        0, "ħ", "스칼라 보손 스핀 0",
        "misc", 0, "0 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="힉스 장은 스칼라 필드 → J=0 (CP 짝 측정 확인)"
    ),
    # 글루온
    make_node(
        "L-1-boson-gluon-count",
        "글루온 수 = 8 = sigma-4",
        8, "종", "SU(3)_C 생성원 수 = 3²-1 = 8",
        "misc", 8, "8 = SU(3) generators",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="misc",
        cause="SU(3) 군의 차원 = N²-1 = 9-1 = 8 (색팔중도)"
    ),
    make_node(
        "L-1-boson-gluon-mass",
        "글루온 질량 (이론값)",
        0.0, "MeV", "글루온 질량 = 0 (SU(3)_C 게이지 불변성)",
        "misc", 0.0, "0 MeV",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="색(color) 게이지 대칭 보존 → 글루온은 질량 없음"
    ),
    make_node(
        "L-1-boson-gluon-spin",
        "글루온 스핀",
        1, "ħ", "벡터 보손 스핀 1",
        "misc", 1, "1 ħ",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0
    ),
]

# ==============================================================
# 카테고리 4: 표준모형 상수 20노드
# ==============================================================
sm_const_nodes = [
    make_node(
        "L-1-const-alpha-EM",
        "미세구조상수 α_EM ≈ 1/137.036",
        1/137.035999084, "dimensionless",
        "PDG 2024 α = 7.2973525693×10⁻³ = 1/137.035999084",
        "misc", 1/137.035999084, "1/137.036 (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=1.5e-11,
        cause="U(1)_EM 결합상수, 재규격화로 에너지에 따라 변화 (running)"
    ),
    make_node(
        "L-1-const-alpha-s-mZ",
        "강력 결합상수 α_s(m_Z)",
        0.1179, "dimensionless",
        "PDG 2024 α_s(m_Z) = 0.1179±0.0010 (world average)",
        "misc", 0.1179, "0.1179 (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.001,
        cause="SU(3)_C 결합상수, m_Z 스케일에서 세계평균 (점근적 자유성)"
    ),
    make_node(
        "L-1-const-sin2-theta-W",
        "약한 혼합각 sin²θ_W (MS-bar, m_Z)",
        0.23122, "dimensionless",
        "PDG 2024 sin²θ̂_W(m_Z) = 0.23122±0.00003",
        "misc", 0.23122, "0.23122 (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.00003,
        cause="약전자기 통일에서 SU(2)_L와 U(1)_Y 결합상수 비율 tan θ_W = g'/g"
    ),
    make_node(
        "L-1-const-higgs-vev",
        "힉스 진공기댓값 v",
        246220.0, "MeV", "v = (√2 G_F)^(-1/2) = 246.22 GeV",
        "misc", 246220.0, "246220 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="전기약력 자발 대칭 깨짐 스케일, mW = g·v/2, mZ = mW/cosθ_W"
    ),
    make_node(
        "L-1-const-fermi-GF",
        "페르미 결합상수 G_F",
        1.1663788e-5, "GeV^-2", "PDG 2024 G_F = 1.1663788×10⁻⁵ GeV⁻²",
        "misc", 1.1663788e-5, "1.1663788×10⁻⁵ GeV⁻² (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=6e-12,
        cause="뮤온 붕괴 수명에서 측정, G_F/√2 = g²/8m²_W"
    ),
    # CKM 행렬 4 파라미터
    make_node(
        "L-1-CKM-theta12",
        "CKM 행렬 각도 θ₁₂ (카비보 각도)",
        13.04, "도(°)", "PDG 2024 Wolfenstein λ = 0.22650 → θ₁₂ ≈ 13.04°",
        "misc", 13.04, "13.04° (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.05,
        cause="s↔d 쿼크 혼합, 카비보 1963년 발견, λ = sinθ_C ≈ 0.2265"
    ),
    make_node(
        "L-1-CKM-theta13",
        "CKM 행렬 각도 θ₁₃",
        0.201, "도(°)", "PDG 2024 θ₁₃ ≈ 0.201°",
        "misc", 0.201, "0.201° (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.011,
        cause="b↔u 쿼크 혼합 (|V_ub| ≈ 3.6×10⁻³)"
    ),
    make_node(
        "L-1-CKM-theta23",
        "CKM 행렬 각도 θ₂₃",
        2.38, "도(°)", "PDG 2024 θ₂₃ ≈ 2.38°",
        "misc", 2.38, "2.38° (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.06,
        cause="b↔c 쿼크 혼합 (|V_cb| ≈ 4.1×10⁻²)"
    ),
    make_node(
        "L-1-CKM-delta-CP",
        "CKM CP 위반 위상 δ_CP",
        65.5, "도(°)", "PDG 2024 δ_CP = 65.5±1.5° (CP 위반 유일 위상)",
        "misc", 65.5, "65.5° (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=1.5,
        cause="쿼크 섹터 CP 위반, Jarlskog 불변량 J ≈ 3.3×10⁻⁵"
    ),
    make_node(
        "L-1-CKM-param-count",
        "CKM 행렬 독립 파라미터 수 = 4 = tau",
        4, "개", "3세대 쿼크 혼합 행렬 → 3각도 + 1 CP 위상 = 4",
        "tau", 4, "4 == tau",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="tau",
        cause="N세대 → (N-1)N/2 각도 + (N-1)(N-2)/2 위상, N=3 → 3+1=4=τ",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    # PMNS 행렬
    make_node(
        "L-1-PMNS-theta12",
        "PMNS 태양 중성미자 혼합각 θ₁₂",
        33.41, "도(°)", "PDG 2024 θ₁₂ = 33.41°±0.75° (태양/KamLAND)",
        "misc", 33.41, "33.41° (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.75,
        cause="태양 중성미자 문제 해결: MSW 효과 + 진공 진동"
    ),
    make_node(
        "L-1-PMNS-theta23",
        "PMNS 대기 중성미자 혼합각 θ₂₃",
        49.1, "도(°)", "PDG 2024 θ₂₃ = 49.1°±1.2° (대기/T2K/NOvA)",
        "misc", 49.1, "49.1° (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=1.2,
        cause="대기 중성미자 진동, 최대 혼합에 가까움 (π/4에 근접)"
    ),
    make_node(
        "L-1-PMNS-theta13",
        "PMNS 리액터 혼합각 θ₁₃",
        8.57, "도(°)", "PDG 2024 θ₁₃ = 8.57°±0.12° (Daya Bay/RENO)",
        "misc", 8.57, "8.57° (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.12,
        cause="Daya Bay 2012 발견, CP 위반 측정 가능성 열음"
    ),
    make_node(
        "L-1-PMNS-param-count",
        "PMNS 중성미자 혼합 파라미터 수 = 4 = tau",
        4, "개", "3각도 + 1 디락 CP 위상 = 4 = τ (마요라나 위상 제외)",
        "tau", 4, "4 == tau",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="tau",
        cause="CKM과 동일 구조: N=3세대 → 3각도+1위상=4=τ",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-const-strong-scale-LQCD",
        "QCD 스케일 파라미터 Λ_QCD",
        215.0, "MeV", "PDG 2024 Λ̄_MS(5-flavor) ≈ 215±25 MeV",
        "misc", 215.0, "215 MeV (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=25.0,
        cause="QCD 점근적 자유성이 사라지는 에너지 스케일, 색가둠 경계"
    ),
    make_node(
        "L-1-const-electroweak-unif-scale",
        "전기약력 통일 에너지 스케일",
        100000.0, "MeV", "전기약력 통일 스케일 ~100 GeV (mW, mZ, mH 범위)",
        "misc", 100000.0, "~100 GeV",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=50000.0,
        cause="SU(2)_L×U(1)_Y → U(1)_EM 자발 대칭 깨짐 에너지"
    ),
    make_node(
        "L-1-const-top-yukawa",
        "탑 쿼크 유카와 결합상수 y_t",
        0.9362, "dimensionless", "y_t = √2·m_t/v ≈ 0.936 (m_t=172.69 GeV, v=246.22 GeV)",
        "misc", 0.9362, "0.9362 (PDG 2024 유도)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.002,
        cause="힉스-탑쿼크 유카와 결합 가장 강함 (~1), 힉스 포텐셜 안정성 핵심"
    ),
    make_node(
        "L-1-const-higgs-quartic",
        "힉스 쌍중선 결합상수 λ",
        0.129, "dimensionless", "λ = m²_H/(2v²) ≈ 0.129 (mH=125.25 GeV)",
        "misc", 0.129, "0.129 (PDG 2024 유도)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.0002,
        cause="힉스 포텐셜 V = μ²|φ|² + λ|φ|⁴ 의 쌍중선 결합"
    ),
    make_node(
        "L-1-const-neutrino-mass-sq-diff-21",
        "중성미자 질량제곱 차 Δm²₂₁ (태양)",
        7.42e-5, "eV^2", "PDG 2024 Δm²₂₁ = 7.42×10⁻⁵ eV² (±0.21×10⁻⁵)",
        "misc", 7.42e-5, "7.42×10⁻⁵ eV² (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.21e-5,
        cause="태양 중성미자 진동 주기 결정, MSW 공명조건"
    ),
    make_node(
        "L-1-const-neutrino-mass-sq-diff-31",
        "중성미자 질량제곱 차 |Δm²₃₁| (대기)",
        2.517e-3, "eV^2", "PDG 2024 |Δm²₃₁| = 2.517×10⁻³ eV² (±0.028×10⁻³)",
        "misc", 2.517e-3, "2.517×10⁻³ eV² (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.028e-3,
        cause="대기 중성미자 진동 주기 결정, 중성미자 질량 순서(ordering) 미결"
    ),
]

# ==============================================================
# 카테고리 5: 대칭군 10노드
# ==============================================================
symmetry_nodes = [
    make_node(
        "L-1-sym-SU3-dim",
        "SU(3)_C 색 게이지군 차원 = 8",
        8, "개", "SU(3) 생성원 = 3²-1 = 8 (겔만 행렬 λ₁~λ₈)",
        "misc", 8, "3²-1 = 8",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="SU(N) 군론: 생성원 수 = N²-1, N=3 → 8 글루온"
    ),
    make_node(
        "L-1-sym-SU2-dim",
        "SU(2)_L 약 아이소스핀군 차원 = 3",
        3, "개", "SU(2) 생성원 = 2²-1 = 3 (파울리 행렬 T₁,T₂,T₃)",
        "misc", 3, "2²-1 = 3",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="SU(2) 군론: 생성원 수 = 3, W+/W-/Z 게이지 보손 기원"
    ),
    make_node(
        "L-1-sym-U1-dim",
        "U(1)_Y 약 하이퍼전하군 차원 = 1",
        1, "개", "U(1) 아벨군 생성원 = 1 (광자 기원)",
        "misc", 1, "1",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="U(1) 아벨군은 1차원, 약한 하이퍼전하 B₀ 게이지 보손"
    ),
    make_node(
        "L-1-sym-SM-total-generators",
        "표준모형 게이지군 생성원 총수 = 12 = sigma",
        12, "개", "SU(3)×SU(2)×U(1) 생성원: 8+3+1 = 12",
        "sigma", 12, "8+3+1 == sigma",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="sigma",
        cause="표준모형 게이지군의 전체 차원 = 12 = σ(6) = n=6의 약수합",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-sym-SM-gauge-group-rank",
        "표준모형 게이지군 랭크 = 4",
        4, "개", "SU(3)_C(랭크2) + SU(2)_L(랭크1) + U(1)_Y(랭크1) = 4",
        "tau", 4, "2+1+1 == tau",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="tau",
        cause="카르탄 부분군 차원(랭크): SU(3)=2, SU(2)=1, U(1)=1 → 합=4=τ"
    ),
    make_node(
        "L-1-sym-quark-color-states",
        "쿼크 색 상태 수 = 3",
        3, "가지", "빨강/파랑/초록 색 전하, SU(3)_C 기본 표현 차원",
        "misc", 3, "SU(3) 기본표현 dim = 3",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="SU(3)_C 기본 표현 3차원 = 3색 (색가둠으로 외부 관측 불가)"
    ),
    make_node(
        "L-1-sym-SM-fermion-generations",
        "표준모형 페르미온 세대 수 = 3",
        3, "세대", "3세대 (1세대: u,d,e,ν_e; 2세대: c,s,μ,ν_μ; 3세대: t,b,τ,ν_τ)",
        "misc", 3, "3 세대",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="LEP Z 붕괴 폭 측정 (Γ_inv): N_ν = 2.9840±0.0082 → 3세대 확정"
    ),
    make_node(
        "L-1-sym-SM-fermion-doublets",
        "표준모형 SU(2)_L 이중항 수 = 6 = n",
        6, "개", "쿼크 이중항 3 + 렙톤 이중항 3 = 6 = n",
        "n", 6, "3+3 == n",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="n",
        cause="각 세대 SU(2)_L 이중항: (u,d),(c,s),(t,b) + (ν_e,e),(ν_μ,μ),(ν_τ,τ) = 6=n",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-sym-anomaly-cancel-condition",
        "게이지 이상(anomaly) 소거 조건: 쿼크 6 = 렙톤 6",
        6, "종", "Tr[Q³]=0 조건: 쿼크 색 3 × 전하합 = 렙톤 전하합, 6=n로 성립",
        "n", 6, "anomaly cancellation @ n=6",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="n",
        cause="SU(2)²U(1) 이상 소거: 각 세대 쿼크 기여(×3색) = 렙톤 기여 → n=6 구조 필연",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-sym-SM-fundamental-fields",
        "표준모형 기본 스칼라장 수 = 1 (힉스 이중항 성분 = 4)",
        4, "성분", "힉스 SU(2)_L 이중항 4실수성분 → 3은 W/Z 질량 흡수, 1 물리 힉스",
        "tau", 4, "4 힉스 성분 == tau",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="tau",
        cause="힉스 이중항 φ = (φ+, φ⁰) → 4실수자유도 = τ, SSB 후 골드스톤 3개 흡수"
    ),
]

# ==============================================================
# 카테고리 6: 상호작용 10노드
# ==============================================================
interaction_nodes = [
    make_node(
        "L-1-force-strong-coupling-at-1GeV",
        "강력 결합상수 α_s(1 GeV)",
        0.50, "dimensionless", "점근적 자유성: α_s(1 GeV) ≈ 0.5 (격자 QCD 추산)",
        "misc", 0.50, "~0.5 at 1 GeV",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.1,
        cause="QCD 점근적 자유성: 에너지 낮을수록 α_s 증가 → 색가둠"
    ),
    make_node(
        "L-1-force-EM-coupling-at-mZ",
        "전자기 결합상수 α_EM(m_Z)",
        1/128.9, "dimensionless", "α_EM(m_Z) ≈ 1/128.9 (running: 저에너지 1/137에서 증가)",
        "misc", 1/128.9, "1/128.9 at m_Z",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=1e-4,
        cause="QED 전하 재규격화: 가상 e+e- 쌍 차폐 효과로 α_EM 증가"
    ),
    make_node(
        "L-1-force-weak-range",
        "약력 유효 거리",
        1e-18, "m", "약력 유효 거리 ~ ħc/m_W ≈ 2×10⁻¹⁸ m",
        "misc", 1e-18, "~10⁻¹⁸ m (W/Z 질량에서)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="유카와 포텐셜: r ~ ħc/Mc², M=80 GeV → r ~ 2×10⁻¹⁸ m"
    ),
    make_node(
        "L-1-force-strong-range",
        "강력 유효 거리 (색가둠 스케일)",
        1e-15, "m", "강력 유효 거리 ~ 1 fm = 10⁻¹⁵ m (핵자 크기)",
        "misc", 1e-15, "~10⁻¹⁵ m (fm 스케일)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="QCD 색가둠 스케일 Λ_QCD ~ 200 MeV → r ~ ħc/Λ_QCD ~ 1 fm"
    ),
    make_node(
        "L-1-force-gravity-coupling-mPlanck",
        "중력 결합상수 (플랑크 질량 기준)",
        1.22e22, "MeV", "플랑크 질량 M_Pl = √(ħc/G) = 1.2209×10²² MeV",
        "misc", 1.22e22, "1.22×10²² MeV",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="중력은 플랑크 스케일에서 다른 힘과 통일, 위계 문제(hierarchy problem)"
    ),
    make_node(
        "L-1-force-EM-photon-mediator",
        "전자기력 매개 입자: 광자 (질량=0)",
        0.0, "MeV", "전자기력 매개 입자 = 광자 γ, 질량 0, 무한 도달거리",
        "misc", 0.0, "0 MeV (광자 질량)",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="U(1)_EM 게이지 대칭 → 질량없는 광자 → 쿨롱 1/r² 법칙"
    ),
    make_node(
        "L-1-force-strong-color-confinement",
        "색가둠 문자열 장력",
        0.18, "GeV^2", "QCD 플럭스 튜브 장력 κ ≈ 0.18 GeV² ≈ 0.9 GeV/fm",
        "misc", 0.18, "0.18 GeV² (격자 QCD)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.01,
        cause="쿼크-반쿼크 선형 포텐셜 V(r) = -4α_s/(3r) + κr (색가둠)"
    ),
    make_node(
        "L-1-force-weak-CP-violation-J",
        "쿼크 섹터 CP 위반 자루스코그 불변량 J",
        3.18e-5, "dimensionless", "Jarlskog 불변량 J = Im(V_us V_cb V*_ub V*_cs) ≈ 3.18×10⁻⁵",
        "misc", 3.18e-5, "3.18×10⁻⁵ (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.12e-5,
        cause="CKM 행렬 CP 위반의 게이지 불변 척도, 우주 반물질 비대칭과 연관"
    ),
    make_node(
        "L-1-force-interaction-count",
        "표준모형 기본 힘 수 = 3 (중력 제외)",
        3, "가지", "강력(QCD) + 전자기력(QED) + 약력(EW) = 3종",
        "misc", 3, "3 SM forces",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="SM은 중력 제외 3힘 통합, 중력은 QFT 재규격화 미해결"
    ),
    make_node(
        "L-1-force-total-SM-forces-with-gravity",
        "자연의 기본 힘 총 수 = 4 = tau",
        4, "가지", "강력 + 전자기력 + 약력 + 중력 = 4",
        "tau", 4, "4 == tau",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="tau",
        cause="알려진 기본 힘 4가지 = τ, GUT에서 3힘 통일, 최종 4→1 목표",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
]

# ==============================================================
# 카테고리 7: 쿼크혼합/질량생성 메커니즘 10노드
# ==============================================================
mixing_nodes = [
    make_node(
        "L-1-mix-quark-color-charge-types",
        "쿼크 색 전하 종류 = 3 (+ 반색 3 = 6 = n)",
        6, "종", "색 전하: R/G/B + R̄/Ḡ/B̄ = 3+3 = 6 = n",
        "n", 6, "3+3 == n",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="n",
        cause="SU(3)_C 기본표현(색) + 켤레표현(반색) = 3+3=6=n",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-mix-higgs-mechanism-fields",
        "힉스 메커니즘 질량 생성 입자 수 = 12 = sigma",
        12, "종", "힉스로 질량 얻는 입자: W+,W-,Z(3) + t,b,c,s,u,d(6) + e,μ,τ(3) = 12",
        "sigma", 12, "3+6+3 == sigma",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="sigma",
        cause="유카와 결합으로 질량 얻는 페르미온(9) + 게이지 보손(3) = 12=σ(6)",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-mix-proton-mass-quark-fraction",
        "양성자 질량 중 쿼크 직접 기여 비율",
        0.02, "dimensionless", "양성자 질량 938 MeV 중 쿼크 질량 합(u+u+d) ≈ 9 MeV = ~1%",
        "misc", 0.02, "~2% (u+u+d 질량/938 MeV)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.01,
        cause="양성자 질량 98%는 QCD 결합 에너지(글루온 장+진공 에너지) 기원"
    ),
    make_node(
        "L-1-mix-mass-hierarchy-top-electron",
        "탑 쿼크 / 전자 질량비",
        338000.0, "dimensionless", "m_t/m_e = 172690/0.511 ≈ 338,000",
        "misc", 338000.0, "338,000",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=1000.0,
        cause="페르미온 질량 계층 문제: 유카와 결합 y_t~1에서 y_e~3×10⁻⁶까지 분포"
    ),
    make_node(
        "L-1-mix-CKM-unitarity-Vud",
        "CKM 행렬 원소 |V_ud|",
        0.97373, "dimensionless", "PDG 2024 |V_ud| = 0.97373±0.00031 (슈퍼허용 베타붕괴)",
        "misc", 0.97373, "0.97373 (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.00031,
        cause="u↔d 쿼크 결합, 카비보 각도의 코사인값 cosθ_C"
    ),
    make_node(
        "L-1-mix-CKM-Vcb",
        "CKM 행렬 원소 |V_cb|",
        0.0408, "dimensionless", "PDG 2024 |V_cb| = 0.0408±0.0014 (B메존 세미렙톤 붕괴)",
        "misc", 0.0408, "0.0408 (PDG 2024)",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0.0014,
        cause="c↔b 쿼크 결합, 2-3세대 혼합 크기"
    ),
    make_node(
        "L-1-mix-quark-SM-total-dof",
        "쿼크 자유도 총수 = 72 = 6×sigma",
        72, "개", "6맛 × 3색 × 4스핀(디락) = 72 = 6 × σ(6)",
        "misc", 72, "6 × 12 = 72",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="6맛(=n) × 3색 × 4디락성분 = 72 = 6×σ(6)=n×sigma, SM 자유도 구조"
    ),
    make_node(
        "L-1-mix-SM-total-fermion-dof",
        "표준모형 페르미온 자유도 총합 = 96",
        96, "개", "쿼크 72 + 렙톤 24(6종×4디락) = 96 = 8×sigma",
        "misc", 96, "72+24 = 96",
        "EMPIRICAL", "STRUCTURAL",
        uncertainty=0,
        cause="쿼크 자유도 72 + 렙톤 자유도 24 = 96 (반입자 포함)"
    ),
    make_node(
        "L-1-mix-ssb-goldstone-count",
        "자발 대칭 깨짐 골드스톤 보손 수 = 3 (W/Z가 흡수)",
        3, "개", "SU(2)_L × U(1)_Y → U(1)_EM 깨짐: 생성원 4-1 = 3개 골드스톤",
        "misc", 3, "4-1 = 3",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        cause="자발 대칭 깨짐: 깨진 생성원 수 = 골드스톤 수 = 4-1=3 → W+,W-,Z 질량"
    ),
    make_node(
        "L-1-mix-SM-total-free-parameters",
        "표준모형 자유 파라미터 총수 = 19",
        19, "개", "페르미온 질량 9 + CKM 4 + 게이지 결합 3 + 힉스 2 + θ_QCD 1 = 19",
        "misc", 19, "9+4+3+2+1 = 19",
        "EMPIRICAL", "EMPIRICAL",
        uncertainty=0,
        cause="표준모형 19개 자유 파라미터 (중성미자 질량 0 가정, 질량있으면 +7~9)"
    ),
]

# ==============================================================
# 카테고리 보너스: 쿼크 6종 n=6 매핑 확인 노드 (카운터 노드)
# ==============================================================
summary_nodes = [
    make_node(
        "L-1-SM-quark-flavor-n6",
        "쿼크 6맛 = n=6 완전수 구조 매핑",
        6, "종", "u/d/c/s/t/b = 6종 = n, 3세대 × 2(업형/다운형) = n=6",
        "n", 6, "6 == n",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="n",
        cause="SM의 3세대 × 업/다운 = 6맛 = n=6 완전수, 쿼크-렙톤 대칭(anomaly cancel)",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-SM-lepton-flavor-n6",
        "렙톤 6맛 = n=6 완전수 구조 매핑",
        6, "종", "e/μ/τ/ν_e/ν_μ/ν_τ = 6종 = n, 3세대 × 2(하전/중성) = n=6",
        "n", 6, "6 == n",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="n",
        cause="SM의 3세대 × 하전렙톤/중성미자 = 6종 = n=6, 이상 소거 필요 조건",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-SM-gauge-boson-total-n-sigma",
        "표준모형 게이지 보손 총 12종 = sigma(6)",
        12, "종", "글루온 8 + W+/W-/Z 3 + 광자 1 = 12 = σ(6)",
        "sigma", 12, "8+3+1 == sigma",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="sigma",
        cause="SM 게이지 보손 총수 = σ(6) = 12 = n=6의 약수합, 군론 필연",
        bt_refs=["BT-137", "BT-165", "BT-208"]
    ),
    make_node(
        "L-1-SM-generation-count-x-doublets",
        "SM 세대 수 3 × 이중항 2 = 6 = n",
        6, "세대×이중항", "3세대 × 2이중항(쿼크/렙톤) = 6 = n (중복 확인)",
        "n", 6, "3 × 2 == n",
        "EXACT", "STRUCTURAL",
        uncertainty=0,
        thread="n",
        cause="SM 페르미온 가족 구조: 세대 수 × 이중항 수 = 3 × 2 = 6 = n"
    ),
]

# ==============================================================
# 전체 병합
# ==============================================================
all_new_nodes = (
    quark_nodes +      # 18
    lepton_nodes +     # 12
    gauge_nodes +      # 12
    sm_const_nodes +   # 20
    symmetry_nodes +   # 10
    interaction_nodes + # 10
    mixing_nodes +     # 10
    summary_nodes      # 4
)

print(f"생성된 총 노드 수: {len(all_new_nodes)}")
cat_counts = {
    "쿼크(질량/전하/스핀)": len(quark_nodes),
    "렙톤(질량/전하/수명)": len(lepton_nodes),
    "게이지보손": len(gauge_nodes),
    "표준모형상수": len(sm_const_nodes),
    "대칭군": len(symmetry_nodes),
    "상호작용": len(interaction_nodes),
    "쿼크혼합/질량생성": len(mixing_nodes),
    "요약/매핑": len(summary_nodes),
}
for k, v in cat_counts.items():
    print(f"  {k}: {v}")

# grade 통계
exact = sum(1 for n in all_new_nodes if n['grade'] == 'EXACT')
empirical = sum(1 for n in all_new_nodes if n['grade'] == 'EMPIRICAL')
print(f"\nEXACT: {exact} / EMPIRICAL: {empirical}")

# 중복 ID 검사
ids = [n['id'] for n in all_new_nodes]
dup = [x for x in ids if ids.count(x) > 1]
if dup:
    print(f"[경고] 중복 ID: {set(dup)}")
else:
    print("[OK] 중복 ID 없음")

# ==============================================================
# reality_map.json 로드 + 기존 ID 중복 검사 + append + 저장
# ==============================================================
with open(SRC, 'r') as f:
    data = json.load(f)

existing_ids = {n['id'] for n in data['nodes'] if 'id' in n}
new_node_ids = {n['id'] for n in all_new_nodes}
overlap = existing_ids & new_node_ids
if overlap:
    print(f"[경고] 기존 노드와 ID 중복: {overlap}")
    # 중복 노드 제거 후 추가
    all_new_nodes = [n for n in all_new_nodes if n['id'] not in existing_ids]
    print(f"중복 제거 후 추가 노드 수: {len(all_new_nodes)}")

prev_count = len(data['nodes'])
data['nodes'].extend(all_new_nodes)

# version bump: v8.3 → v8.4
old_ver = data.get('version', 'v8.3')
# v8.3 → v8.4
parts = old_ver.lstrip('v').split('.')
parts[-1] = str(int(parts[-1]) + 1)
new_ver = 'v' + '.'.join(parts)
data['version'] = new_ver

# metadata 업데이트
if 'meta' in data:
    data['meta']['updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    data['meta']['node_count'] = len(data['nodes'])

print(f"\n이전 노드 수: {prev_count}")
print(f"추가 노드 수: {len(all_new_nodes)}")
print(f"새 총 노드 수: {len(data['nodes'])}")
print(f"버전: {old_ver} → {new_ver}")

# 저장 (재로드 방식: 쓰기 직전)
with open(SRC, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n[완료] {SRC} 저장 완료")

# JSON 유효성 검증
with open(SRC, 'r') as f:
    check = json.load(f)
assert len(check['nodes']) == prev_count + len(all_new_nodes), "노드 수 불일치!"
print(f"[검증 OK] 노드 수 확인: {len(check['nodes'])}")
