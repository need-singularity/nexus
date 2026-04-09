#!/usr/bin/env python3
"""
L8_galactic 노드 ~200개 생성 및 reality_map.json 추가
카테고리:
  A. 우리은하 구조 (20노드)
  B. 로컬 그룹 (30노드)
  C. 주요 은하 (40노드)
  D. 은하단 (30노드)
  E. 대규모 구조 (20노드)
  F. 우주상수 (30노드)
  G. 은하 유형 (30노드)
"""
import json, copy, shutil
from pathlib import Path

PATH = Path("/Users/ghost/Dev/nexus/shared/reality_map.json")

def E(id, claim, measured, unit, detail, source, source_url, n6_expr="misc", grade="EMPIRICAL", causal="EMPIRICAL", thread="misc", origin="natural", uncertainty=None, bt_refs=None):
    node = {
        "id": id,
        "level": "L8_galactic",
        "claim": claim,
        "measured": measured,
        "unit": unit,
        "detail": detail,
        "source": source,
        "source_url": source_url,
        "n6_expr": n6_expr,
        "grade": grade,
        "causal": causal,
        "thread": thread,
        "origin": origin,
        "children": [],
        "siblings": [],
        "bt_refs": bt_refs or []
    }
    if uncertainty is not None:
        node["uncertainty"] = uncertainty
    return node

# ─────────────────────────────────────────────
# A. 우리은하 구조 (20노드)
# ─────────────────────────────────────────────
milkyway_nodes = [
    E("L8-mw-diameter-kly",
      "우리은하 지름 약 100 kly (킬로광년)",
      100, "kly",
      "우리은하 원반 추정 지름. 불확도 ±15 kly.",
      "Rix & Bovy 2013, ARA&A 51 511; Xu et al. 2015 ApJ",
      "https://ui.adsabs.harvard.edu/abs/2013ARA%26A..51..511R",
      uncertainty=15),

    E("L8-mw-thickness-kly",
      "우리은하 얇은 원반 두께 약 1 kly",
      1.0, "kly",
      "얇은 원반(thin disk) 반치폭 ~300 pc = ~1 kly",
      "Gilmore & Reid 1983, MNRAS 202 1025",
      "https://ui.adsabs.harvard.edu/abs/1983MNRAS.202.1025G",
      uncertainty=0.2),

    E("L8-mw-stellar-count",
      "우리은하 별 수 추정 1~4×10^11",
      2.5e11, "개",
      "관측 불확도 크며 중앙값 약 2.5×10^11. 연구마다 1e11~4e11 범위.",
      "Bland-Hawthorn & Gerhard 2016, ARA&A 54 529",
      "https://ui.adsabs.harvard.edu/abs/2016ARA%26A..54..529B",
      uncertainty=1.5e11),

    E("L8-mw-spiral-arms",
      "우리은하 주요 나선팔 수 4개",
      4, "개",
      "페르세우스팔, 방패-남십자팔, 궁수팔, 노르마팔. 부분 팔 포함 시 6개.",
      "Churchwell et al. 2009, PASP 121 213",
      "https://ui.adsabs.harvard.edu/abs/2009PASP..121..213C"),

    E("L8-mw-gc-distance-kly",
      "태양-은하중심 거리 약 26.4 kly (8.08 kpc)",
      26.4, "kly",
      "GRAVITY Collaboration 2019 측정값 R0=8.178±0.026 kpc → 26.67 kly. VLBI 8.08 kpc도 사용.",
      "GRAVITY Collaboration 2019, A&A 625 L10",
      "https://doi.org/10.1051/0004-6361/201935656",
      uncertainty=0.1),

    E("L8-mw-rotation-period-myr",
      "태양계 은하 공전주기 약 225~250 Myr",
      230, "Myr",
      "갤럭틱 이어(cosmic year). 태양계 속도 ~220 km/s 기준.",
      "Bland-Hawthorn & Gerhard 2016, ARA&A 54 529",
      "https://ui.adsabs.harvard.edu/abs/2016ARA%26A..54..529B",
      uncertainty=10),

    E("L8-mw-total-mass-Msun",
      "우리은하 전체 질량(암흑물질 포함) ~1.5×10^12 M☉",
      1.5e12, "M☉",
      "위성은하 궤도 + 탈출속도 분석. Posti & Helmi 2019 는 1.3×10^12 M☉.",
      "Posti & Helmi 2019, A&A 621 A56",
      "https://doi.org/10.1051/0004-6361/201833355",
      uncertainty=0.3e12),

    E("L8-mw-dark-matter-fraction",
      "우리은하 암흑물질 질량 비율 ~85%",
      0.85, "비율",
      "총 질량 중 별/가스/먼지 이외 암흑물질 추정 비율.",
      "Bland-Hawthorn & Gerhard 2016, ARA&A 54 529",
      "https://ui.adsabs.harvard.edu/abs/2016ARA%26A..54..529B",
      uncertainty=0.05),

    E("L8-mw-disk-mass-Msun",
      "우리은하 별/가스 원반 질량 ~6×10^10 M☉",
      6e10, "M☉",
      "항성 원반 ~5×10^10 + 가스 ~1×10^10 M☉",
      "Bland-Hawthorn & Gerhard 2016, ARA&A 54 529",
      "https://ui.adsabs.harvard.edu/abs/2016ARA%26A..54..529B",
      uncertainty=1e10),

    E("L8-mw-bulge-mass-Msun",
      "우리은하 중심 팽대부 질량 ~1.5×10^10 M☉",
      1.5e10, "M☉",
      "바-팽대부 포함. Launhardt et al. 2002 0.86-1.5×10^10 M☉ 범위.",
      "Portail et al. 2017, MNRAS 465 1621",
      "https://ui.adsabs.harvard.edu/abs/2017MNRAS.465.1621P",
      uncertainty=0.3e10),

    E("L8-mw-sgra-mass-Msun",
      "은하중심 블랙홀 Sgr A* 질량 4.15×10^6 M☉",
      4.154e6, "M☉",
      "GRAVITY Collaboration 2019 가장 정밀 측정. 불확도 ±0.014×10^6 M☉.",
      "GRAVITY Collaboration 2019, A&A 625 L10",
      "https://doi.org/10.1051/0004-6361/201935656",
      uncertainty=1.4e4),

    E("L8-mw-halo-radius-kly",
      "우리은하 암흑물질 헤일로 반경 ~600 kly",
      600, "kly",
      "비리얼 반경 추정. 연구에 따라 300~700 kly 범위.",
      "Deason et al. 2020, MNRAS 496 3929",
      "https://ui.adsabs.harvard.edu/abs/2020MNRAS.496.3929D",
      uncertainty=100),

    E("L8-mw-solar-velocity-kms",
      "태양계 은하 공전속도 약 220 km/s",
      220, "km/s",
      "LSR(Local Standard of Rest) 기준 은하중심 공전. VLBI 측정 240±10 km/s 도 있음.",
      "Reid et al. 2019, ApJ 885 131",
      "https://ui.adsabs.harvard.edu/abs/2019ApJ...885..131R",
      uncertainty=10),

    E("L8-mw-age-gyr",
      "우리은하 추정 나이 ~13.6 Gyr",
      13.6, "Gyr",
      "가장 오래된 별 클러스터 연대 및 핵합성 연대측정 기반.",
      "Miglio et al. 2021, A&A 645 A85",
      "https://doi.org/10.1051/0004-6361/202038307",
      uncertainty=0.8),

    E("L8-mw-metallicity-gradient",
      "우리은하 원반 금속성 기울기 약 -0.06 dex/kpc",
      -0.06, "dex/kpc",
      "반경 방향 금속성 감소율. 산소/철 다양한 원소 평균.",
      "Luck & Lambert 2011, AJ 142 136",
      "https://ui.adsabs.harvard.edu/abs/2011AJ....142..136L",
      uncertainty=0.01),

    E("L8-mw-sfr-Msun-yr",
      "우리은하 현재 별 생성률 약 1~3 M☉/yr",
      1.65, "M☉/yr",
      "Chomiuk & Povich 2011 추정 1.5±0.7 M☉/yr. 적외선+전파 복합.",
      "Chomiuk & Povich 2011, AJ 142 197",
      "https://ui.adsabs.harvard.edu/abs/2011AJ....142..197C",
      uncertainty=0.7),

    E("L8-mw-type",
      "우리은하 형태: 막대 나선은하 SBbc",
      "SBbc", "허블 유형",
      "Spitzer GLIMPSE 자료 기반 막대 구조 확인. de Vaucouleurs 분류.",
      "Churchwell et al. 2009, PASP 121 213",
      "https://ui.adsabs.harvard.edu/abs/2009PASP..121..213C"),

    E("L8-mw-globular-clusters",
      "우리은하 구상성단 수 약 150~160개",
      157, "개",
      "Harris 1996(2010 개정판) 카탈로그 기준.",
      "Harris 2010, arXiv:1012.3224",
      "https://arxiv.org/abs/1012.3224",
      uncertainty=5),

    E("L8-mw-ism-hydrogen-fraction",
      "우리은하 성간매질 수소 질량 분율 ~70%",
      0.70, "질량 분율",
      "HI + H2 합산. 원시 우주 수소 비율과 유사하나 금속 오염으로 약간 낮음.",
      "Kalberla & Kerp 2009, ARA&A 47 27",
      "https://ui.adsabs.harvard.edu/abs/2009ARA%26A..47...27K",
      uncertainty=0.05),

    E("L8-mw-satellite-count",
      "우리은하 위성은하 확인 수 ~60개 (완전 목록 미확정)",
      61, "개",
      "2024년 기준 확인된 위성은하. 희미한 초저표면밀도 은하 포함 시 더 많음.",
      "Drlica-Wagner et al. 2020, ApJS 249 14",
      "https://ui.adsabs.harvard.edu/abs/2020ApJS..249...14D",
      uncertainty=10),
]

# ─────────────────────────────────────────────
# B. 로컬 그룹 (30노드)
# ─────────────────────────────────────────────
local_group_nodes = [
    E("L8-lg-member-count",
      "로컬 그룹 은하 수 ~80개",
      80, "개",
      "우리은하+M31 중력 지배권 내 확인 은하. 작은 은하 포함 미확정.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=10),

    E("L8-lg-diameter-mpc",
      "로컬 그룹 지름 약 3 Mpc",
      3.0, "Mpc",
      "우리은하~M31 0.77 Mpc. 전체 지배 반경 약 1.5 Mpc.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=0.3),

    E("L8-m31-distance-mly",
      "M31 안드로메다 은하까지 거리 2.537 Mly (0.778 Mpc)",
      2.537, "Mly",
      "세페이드 거리. McConnachie 2012 기준.",
      "Ribas et al. 2005, ApJ 635 L37",
      "https://ui.adsabs.harvard.edu/abs/2005ApJ...635L..37R",
      uncertainty=0.02),

    E("L8-m31-mass-Msun",
      "M31 안드로메다 총 질량 ~1.5×10^12 M☉",
      1.5e12, "M☉",
      "우리은하와 유사. 불확도 크며 연구별 0.8~2.0×10^12 M☉.",
      "Phelps et al. 2013, ApJ 764 71",
      "https://ui.adsabs.harvard.edu/abs/2013ApJ...764...71P",
      uncertainty=0.4e12),

    E("L8-m31-diameter-kly",
      "M31 안드로메다 지름 약 220 kly",
      220, "kly",
      "우리은하보다 약 2배 큰 직경. 두꺼운 외부 원반 포함.",
      "Ibata et al. 2014, ApJ 780 128",
      "https://ui.adsabs.harvard.edu/abs/2014ApJ...780..128I",
      uncertainty=20),

    E("L8-m31-type",
      "M31 허블 유형 SA(s)b — 막대 없는 나선은하",
      "SA(s)b", "허블 유형",
      "대규모 나선 구조, 막대 미약. de Vaucouleurs 분류.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-m31-approach-velocity-kms",
      "M31-우리은하 접근 속도 약 110 km/s (시선)",
      110, "km/s",
      "시선속도 -110 km/s(접근). 접선방향 불확실해 정면 충돌 가능성 ~50%.",
      "van der Marel et al. 2012, ApJ 753 8",
      "https://ui.adsabs.harvard.edu/abs/2012ApJ...753....8V",
      uncertainty=10),

    E("L8-m31-merger-time-gyr",
      "M31-우리은하 합병 예상 ~4.5 Gyr 후",
      4.5, "Gyr",
      "N체 시뮬레이션 기반 중앙값. 불확도 ±0.5 Gyr.",
      "van der Marel et al. 2012, ApJ 753 9",
      "https://ui.adsabs.harvard.edu/abs/2012ApJ...753....9V",
      uncertainty=0.5),

    E("L8-m31-bh-mass-Msun",
      "M31 중심 블랙홀 질량 ~1.1×10^8 M☉",
      1.1e8, "M☉",
      "항성 속도 분산 기반. Bender et al. 2005 측정.",
      "Bender et al. 2005, ApJ 631 280",
      "https://ui.adsabs.harvard.edu/abs/2005ApJ...631..280B",
      uncertainty=0.2e8),

    E("L8-m33-distance-mly",
      "M33 삼각형 은하 거리 2.73 Mly (0.84 Mpc)",
      2.73, "Mly",
      "세페이드 + TRGB 거리. 로컬 그룹 3번째 큰 은하.",
      "Freedman et al. 1991, ApJ 372 455",
      "https://ui.adsabs.harvard.edu/abs/1991ApJ...372..455F",
      uncertainty=0.05),

    E("L8-m33-mass-Msun",
      "M33 삼각형 은하 질량 ~5×10^10 M☉",
      5e10, "M☉",
      "우리은하의 ~5%. 회전곡선 기반.",
      "Corbelli 2003, MNRAS 342 199",
      "https://ui.adsabs.harvard.edu/abs/2003MNRAS.342..199C",
      uncertainty=1e10),

    E("L8-m33-type",
      "M33 허블 유형 SA(s)cd — 느슨한 나선은하",
      "SA(s)cd", "허블 유형",
      "핵이 작고 나선 구조가 느슨한 Scd형.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-lmc-distance-kly",
      "대마젤란 운(LMC) 거리 약 160 kly (49.97 kpc)",
      163, "kly",
      "TRGB+세페이드 평균. de Grijs et al. 2014 49.97 kpc = 163 kly.",
      "de Grijs et al. 2014, AJ 147 122",
      "https://ui.adsabs.harvard.edu/abs/2014AJ....147..122D",
      uncertainty=2),

    E("L8-lmc-mass-Msun",
      "LMC 총 질량 ~1.4×10^11 M☉",
      1.4e11, "M☉",
      "암흑물질 헤일로 포함. Erkal et al. 2019 1.38×10^11 M☉.",
      "Erkal et al. 2019, MNRAS 487 2685",
      "https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.2685E",
      uncertainty=0.2e11),

    E("L8-lmc-diameter-kly",
      "LMC 지름 약 14.9 kly (4.6 kpc)",
      14.9, "kly",
      "D25 등광도 기준.",
      "van der Marel et al. 2002, AJ 124 2639",
      "https://ui.adsabs.harvard.edu/abs/2002AJ....124.2639V",
      uncertainty=0.5),

    E("L8-smc-distance-kly",
      "소마젤란 운(SMC) 거리 약 200 kly (61.7 kpc)",
      200, "kly",
      "TRGB 기준. 불규칙 왜소은하.",
      "Graczyk et al. 2014, ApJ 780 59",
      "https://ui.adsabs.harvard.edu/abs/2014ApJ...780...59G",
      uncertainty=5),

    E("L8-smc-mass-Msun",
      "SMC 총 질량 ~6.5×10^9 M☉",
      6.5e9, "M☉",
      "암흑물질 포함. Bekki & Stanimirovic 2009.",
      "Bekki & Stanimirovic 2009, MNRAS 395 2003",
      "https://ui.adsabs.harvard.edu/abs/2009MNRAS.395.2003B",
      uncertainty=1e9),

    E("L8-sgr-dwarf-distance-kly",
      "궁수자리 왜소 타원은하 거리 약 70 kly (21.4 kpc)",
      70, "kly",
      "우리은하에 흡수 중인 위성은하. Ibata et al. 1994 발견.",
      "Ibata et al. 1994, Nature 370 194",
      "https://ui.adsabs.harvard.edu/abs/1994Natur.370..194I",
      uncertainty=3),

    E("L8-fornax-dwarf-distance-kly",
      "포르낙스 왜소 타원은하 거리 약 460 kly (141 kpc)",
      460, "kly",
      "로컬 그룹 내 큰 왜소 타원은하. 6개 구상성단 보유.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=10),

    E("L8-sculptor-dwarf-distance-kly",
      "조각가자리 왜소 구형 은하 거리 약 287 kly",
      287, "kly",
      "고전적 위성 왜소 구형 은하 (dSph).",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=10),

    E("L8-ic10-distance-mly",
      "IC 10 불규칙 왜소은하 거리 약 2.57 Mly (0.79 Mpc)",
      2.57, "Mly",
      "로컬 그룹 내 활발한 별 생성 불규칙 은하.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=0.05),

    E("L8-ngc147-distance-mly",
      "NGC 147 왜소 타원은하 거리 약 2.58 Mly",
      2.58, "Mly",
      "M31 위성은하. 구상성단 4개.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=0.06),

    E("L8-ngc185-distance-mly",
      "NGC 185 왜소 타원은하 거리 약 2.08 Mly",
      2.08, "Mly",
      "M31 위성. 핵에 성간물질 보유.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=0.05),

    E("L8-ngc205-distance-mly",
      "NGC 205 (M110) 왜소 타원은하 거리 약 2.69 Mly",
      2.69, "Mly",
      "M31의 밝은 위성 타원은하. 젊은 별 성단 포함.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=0.06),

    E("L8-ic1613-distance-mly",
      "IC 1613 고립 불규칙 왜소은하 거리 약 2.38 Mly",
      2.38, "Mly",
      "별 생성 활발. 금속성 매우 낮음.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=0.05),

    E("L8-wolf-lundmark-distance-mly",
      "Wolf-Lundmark-Melotte(WLM) 은하 거리 약 3.27 Mly",
      3.27, "Mly",
      "로컬 그룹 주변부 불규칙 왜소은하.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=0.1),

    E("L8-tucana-distance-kly",
      "투카나 왜소 구형 은하 거리 약 2,870 kly (880 kpc)",
      2870, "kly",
      "로컬 그룹 가장자리 고립 왜소 구형 은하.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=50),

    E("L8-andromeda-i-distance-kly",
      "Andromeda I 왜소 구형 은하 거리 약 2,457 kly",
      2457, "kly",
      "M31 위성 왜소 구형 은하.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=50),

    E("L8-phoenix-dwarf-distance-kly",
      "피닉스 왜소 전환 은하 거리 약 1,440 kly (441 kpc)",
      1440, "kly",
      "왜소 구형↔불규칙 전환형(transition) 은하.",
      "McConnachie 2012, AJ 144 4",
      "https://ui.adsabs.harvard.edu/abs/2012AJ....144....4M",
      uncertainty=30),

    E("L8-lg-total-mass-Msun",
      "로컬 그룹 총 질량 약 2~4×10^12 M☉",
      3e12, "M☉",
      "우리은하+M31 암흑물질 헤일로 합산 추정. 타이밍 논증 기반.",
      "Partridge et al. 2013, MNRAS 436 1096",
      "https://ui.adsabs.harvard.edu/abs/2013MNRAS.436.1096P",
      uncertainty=1e12),
]

# ─────────────────────────────────────────────
# C. 주요 은하 (40노드)
# ─────────────────────────────────────────────
notable_galaxies_nodes = [
    # M87
    E("L8-m87-distance-mly",
      "M87 (처녀자리 A) 거리 약 53.5 Mly (16.4 Mpc)",
      53.5, "Mly",
      "표면 밝기 요동(SBF) 기반. 처녀자리 은하단 중심.",
      "Blakeslee et al. 2009, ApJ 694 556",
      "https://ui.adsabs.harvard.edu/abs/2009ApJ...694..556B",
      uncertainty=1.0),

    E("L8-m87-bh-mass-Msun",
      "M87 중심 블랙홀 질량 6.5×10^9 M☉",
      6.5e9, "M☉",
      "EHT 이벤트 호라이즌 망원경 2019 역사적 첫 블랙홀 촬영 기반.",
      "EHT Collaboration 2019, ApJL 875 L1",
      "https://doi.org/10.3847/2041-8213/ab0ec7",
      uncertainty=0.7e9),

    E("L8-m87-jet-length-kly",
      "M87 상대론적 제트 길이 약 5 kly (1.5 kpc)",
      5.0, "kly",
      "HST 가시광선 + 전파 관측. 제트 속도 ~0.99c.",
      "Owen et al. 1989, AJ 97 1291",
      "https://ui.adsabs.harvard.edu/abs/1989AJ.....97.1291O",
      uncertainty=0.5),

    E("L8-m87-mass-Msun",
      "M87 총 질량 약 6×10^12 M☉",
      6e12, "M☉",
      "X선 온도 분포 기반 동역학 질량.",
      "Gebhardt & Thomas 2009, ApJ 700 1690",
      "https://ui.adsabs.harvard.edu/abs/2009ApJ...700.1690G",
      uncertainty=1e12),

    E("L8-m87-type",
      "M87 허블 유형 E0p — 타원은하, 이례적 제트",
      "E0p", "허블 유형",
      "거의 구형 타원. 강한 전파원 Virgo A = 3C 274.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    # NGC 5128 / Cen A
    E("L8-ngc5128-distance-mly",
      "NGC 5128 (센타우루스 A) 거리 약 13 Mly (3.8 Mpc)",
      13.0, "Mly",
      "TRGB 및 행성상 성운 거리 지시자 기반.",
      "Harris et al. 2010, PASA 27 457",
      "https://ui.adsabs.harvard.edu/abs/2010PASA...27..457H",
      uncertainty=0.5),

    E("L8-ngc5128-bh-mass-Msun",
      "NGC 5128 중심 블랙홀 질량 ~5.5×10^7 M☉",
      5.5e7, "M☉",
      "항성 동역학 기반. Neumayer 2010 측정.",
      "Neumayer 2010, PASA 27 449",
      "https://ui.adsabs.harvard.edu/abs/2010PASA...27..449N",
      uncertainty=0.3e7),

    E("L8-ngc5128-type",
      "NGC 5128 허블 유형 S0 병합 타원: peculiar",
      "S0/E5p", "허블 유형",
      "중앙 먼지 레인 = 나선은하 병합 흔적. 밝은 전파원 Cen A.",
      "Israel 1998, A&ARv 8 237",
      "https://ui.adsabs.harvard.edu/abs/1998A%26ARv...8..237I"),

    # M81 (Bode's Galaxy)
    E("L8-m81-distance-mly",
      "M81 (보데 은하) 거리 약 11.7 Mly (3.6 Mpc)",
      11.7, "Mly",
      "세페이드 + TRGB 기반. Freedman et al. 1994.",
      "Freedman et al. 1994, ApJ 427 628",
      "https://ui.adsabs.harvard.edu/abs/1994ApJ...427..628F",
      uncertainty=0.2),

    E("L8-m81-type",
      "M81 허블 유형 SA(s)ab — 나선은하",
      "SA(s)ab", "허블 유형",
      "M82와 중력 상호작용 중. 매우 뚜렷한 나선 구조.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    # M82 (Cigar Galaxy)
    E("L8-m82-distance-mly",
      "M82 (시거 은하) 거리 약 11.4 Mly",
      11.4, "Mly",
      "M81과 상호작용 중인 강렬 별 생성 은하(스타버스트).",
      "Freedman et al. 1994, ApJ 427 628",
      "https://ui.adsabs.harvard.edu/abs/1994ApJ...427..628F",
      uncertainty=0.2),

    E("L8-m82-sfr-Msun-yr",
      "M82 별 생성률 약 10~13 M☉/yr",
      10.0, "M☉/yr",
      "스타버스트 은하. 중앙부 집중 별 생성. 우리은하의 ~7배.",
      "Kennicutt 1998, ARA&A 36 189",
      "https://ui.adsabs.harvard.edu/abs/1998ARA%26A..36..189K",
      uncertainty=3),

    # NGC 1275 (Perseus A)
    E("L8-ngc1275-distance-mly",
      "NGC 1275 (페르세우스 A) 거리 약 237 Mly (72.7 Mpc)",
      237, "Mly",
      "페르세우스 은하단 중심의 cD 은하. 적색편이 z=0.01756.",
      "NED — NASA/IPAC Extragalactic Database",
      "https://ned.ipac.caltech.edu/byname?objname=NGC+1275",
      uncertainty=5),

    E("L8-ngc1275-bh-mass-Msun",
      "NGC 1275 중심 블랙홀 질량 ~8×10^8 M☉",
      8e8, "M☉",
      "X선 광도 및 M-sigma 관계 추정.",
      "Graham et al. 2011, ApJ 746 113",
      "https://ui.adsabs.harvard.edu/abs/2011ApJ...746..113G",
      uncertainty=2e8),

    # NGC 4889 (Coma cluster giant)
    E("L8-ngc4889-bh-mass-Msun",
      "NGC 4889 중심 블랙홀 질량 ~2.1×10^10 M☉",
      2.1e10, "M☉",
      "McConnell et al. 2011 측정. 확인된 가장 무거운 블랙홀 중 하나.",
      "McConnell et al. 2011, Nature 480 215",
      "https://doi.org/10.1038/nature10636",
      uncertainty=1.6e10),

    E("L8-ngc4889-distance-mly",
      "NGC 4889 거리 약 308 Mly (94.4 Mpc)",
      308, "Mly",
      "코마 은하단 중심 cD 은하.",
      "NED — NASA/IPAC Extragalactic Database",
      "https://ned.ipac.caltech.edu/byname?objname=NGC+4889",
      uncertainty=10),

    # NGC 4486B (M87 companion)
    E("L8-ngc1300-distance-mly",
      "NGC 1300 막대 나선은하 거리 약 69.4 Mly",
      69.4, "Mly",
      "Hubble Heritage 표적. 전형적 SBb 막대 나선 구조.",
      "Freedman et al. 2001, ApJ 553 47",
      "https://ui.adsabs.harvard.edu/abs/2001ApJ...553...47F",
      uncertainty=3),

    # NGC 3031 / M81 group
    E("L8-ngc253-distance-mly",
      "NGC 253 (조각가 은하) 거리 약 10.7 Mly",
      10.7, "Mly",
      "조각가자리 그룹 중심. 강한 스타버스트 활동.",
      "Dalcanton et al. 2009, ApJS 183 67",
      "https://ui.adsabs.harvard.edu/abs/2009ApJS..183...67D",
      uncertainty=0.3),

    E("L8-ngc4038-distance-mly",
      "NGC 4038/4039 안테나 은하 거리 약 65 Mly",
      65.0, "Mly",
      "충돌·병합 중인 은하 쌍. 강렬 별 생성. 우주 병합 원형 사례.",
      "Schweizer et al. 2008, AJ 136 1482",
      "https://ui.adsabs.harvard.edu/abs/2008AJ....136.1482S",
      uncertainty=5),

    # Sombrero Galaxy
    E("L8-m104-distance-mly",
      "M104 솜브레로 은하 거리 약 31.1 Mly",
      31.1, "Mly",
      "SBa. 두꺼운 먼지 레인과 큰 핵 팽대부 특징.",
      "Ford et al. 1996, ApJ 458 455",
      "https://ui.adsabs.harvard.edu/abs/1996ApJ...458..455F",
      uncertainty=1),

    E("L8-m104-bh-mass-Msun",
      "M104 솜브레로 은하 블랙홀 질량 ~10^9 M☉",
      1e9, "M☉",
      "항성 속도 분산 M-sigma 관계.",
      "Kormendy et al. 1996, ApJ 473 L91",
      "https://ui.adsabs.harvard.edu/abs/1996ApJ...473L..91K",
      uncertainty=3e8),

    # Whirlpool
    E("L8-m51-distance-mly",
      "M51 소용돌이 은하 거리 약 23 Mly",
      23.0, "Mly",
      "Sbc 나선. NGC 5195와 상호작용. 최초 나선 구조 발견(1845).",
      "Ciardullo et al. 2002, ApJ 577 31",
      "https://ui.adsabs.harvard.edu/abs/2002ApJ...577...31C",
      uncertainty=1),

    # NGC 6744
    E("L8-ngc6744-distance-mly",
      "NGC 6744 우리은하 유사 나선은하 거리 약 31 Mly",
      31.0, "Mly",
      "SABbc. 우리은하와 형태 유사. Spitzer + HST 연구.",
      "Soria et al. 2012, MNRAS 427 2950",
      "https://ui.adsabs.harvard.edu/abs/2012MNRAS.427.2950S",
      uncertainty=2),

    # IC 342
    E("L8-ic342-distance-mly",
      "IC 342 거리 약 10.7 Mly",
      10.7, "Mly",
      "먼지 가려짐으로 관측 어려운 나선은하. IC 342/M81 그룹.",
      "Freedman & Madore 1988, ApJ 332 452",
      "https://ui.adsabs.harvard.edu/abs/1988ApJ...332..452F",
      uncertainty=0.5),

    # Stephan's Quintet
    E("L8-stephans-quintet-distance-mly",
      "슈테판 오중주 거리 약 290 Mly",
      290, "Mly",
      "4개 충돌 은하 + 1개 전경 은하. JWST 첫 공개 이미지 대상.",
      "Mendel et al. 2004, AJ 127 3178",
      "https://ui.adsabs.harvard.edu/abs/2004AJ....127.3178M",
      uncertainty=10),

    # Hoag's Object
    E("L8-hoags-object-distance-mly",
      "호그 천체 거리 약 600 Mly",
      600, "Mly",
      "핵 타원체 + 고리 구조. 형성 기원 미확정 희귀 은하.",
      "Schweizer et al. 1987, AJ 93 1334",
      "https://ui.adsabs.harvard.edu/abs/1987AJ.....93.1334S",
      uncertainty=30),

    # NGC 4993 (GW source host)
    E("L8-ngc4993-distance-mly",
      "NGC 4993 중력파 원천 숙주 은하 거리 약 130 Mly",
      130, "Mly",
      "GW170817 킬로노바 숙주. 최초 중력파 전자기파 동시 관측.",
      "Abbott et al. 2017, Nature 551 85",
      "https://doi.org/10.1038/nature24471",
      uncertainty=10),

    # 3C 273 (quasar)
    E("L8-3c273-distance-gly",
      "3C 273 퀘이사 거리 약 2.44 Gly (z=0.158)",
      2.44, "Gly",
      "가장 밝은 퀘이사 중 하나. 겉보기등급 12.9 (육안 거의 불가).",
      "Schmidt 1963, Nature 197 1040",
      "https://doi.org/10.1038/1971040a0",
      uncertainty=0.05),

    E("L8-3c273-luminosity-Lsun",
      "3C 273 광도 약 4×10^12 L☉",
      4e12, "L☉",
      "볼로메트릭 광도. 우리은하 전체 광도의 약 4배.",
      "Courvoisier 1998, A&ARv 9 1",
      "https://ui.adsabs.harvard.edu/abs/1998A%26ARv...9....1C",
      uncertainty=1e12),

    # NGC 1052-DF2 (Dark-matter-free galaxy)
    E("L8-ngc1052df2-distance-mly",
      "NGC 1052-DF2 암흑물질 결핍 은하 거리 약 64 Mly",
      64, "Mly",
      "van Dokkum et al. 2018 발견. 암흑물질 거의 없는 초저밀도 은하.",
      "van Dokkum et al. 2018, Nature 555 629",
      "https://doi.org/10.1038/nature25767",
      uncertainty=5),

    # Milkomeda (future merger)
    E("L8-milkomeda-mass-Msun",
      "미래 밀코메다(우리은하+M31 병합체) 예상 질량 ~3×10^12 M☉",
      3e12, "M☉",
      "van der Marel et al. 2012 시뮬레이션 기반 병합 후 타원은하 추정.",
      "van der Marel et al. 2012, ApJ 753 8",
      "https://ui.adsabs.harvard.edu/abs/2012ApJ...753....8V",
      uncertainty=0.5e12),

    # NGC 5907 (edge-on spiral)
    E("L8-ngc5907-distance-mly",
      "NGC 5907 (칼 은하) 거리 약 50 Mly",
      50, "Mly",
      "완전 측면 나선은하. 조류 스트림 조각난 위성 흡수 증거.",
      "Shang et al. 1998, ApJ 504 L23",
      "https://ui.adsabs.harvard.edu/abs/1998ApJ...504L..23S",
      uncertainty=3),

    # NGC 4261 (FR I radio galaxy)
    E("L8-ngc4261-bh-mass-Msun",
      "NGC 4261 블랙홀 질량 ~4×10^8 M☉",
      4e8, "M☉",
      "HST 핵 먼지 원반 + 항성 동역학 기반. Ferrarese et al. 1996.",
      "Ferrarese et al. 1996, ApJ 470 444",
      "https://ui.adsabs.harvard.edu/abs/1996ApJ...470..444F",
      uncertainty=1e8),

    # GN-z11 (high-z galaxy)
    E("L8-gnz11-redshift",
      "GN-z11 현재 확인 최고 적색편이 은하 z=10.957",
      10.957, "z",
      "빅뱅 후 약 430 Myr. Oesch et al. 2016 HST. JWST 이후 더 높은 z 후보 다수.",
      "Oesch et al. 2016, ApJ 819 129",
      "https://ui.adsabs.harvard.edu/abs/2016ApJ...819..129O",
      uncertainty=0.002),

    E("L8-gnz11-luminosity-Lsun",
      "GN-z11 UV 광도 약 3×10^9 L☉",
      3e9, "L☉",
      "우주 최초 세대 은하 중 하나. 별 생성 극히 활발.",
      "Oesch et al. 2016, ApJ 819 129",
      "https://ui.adsabs.harvard.edu/abs/2016ApJ...819..129O",
      uncertainty=1e9),

    # Arp 220 (ULIRG)
    E("L8-arp220-distance-mly",
      "Arp 220 초광도 적외선 은하 거리 약 250 Mly",
      250, "Mly",
      "두 은하 병합. 적외선 광도 1.91×10^12 L☉. 원형 ULIRG.",
      "Scoville et al. 1998, ApJ 492 L107",
      "https://ui.adsabs.harvard.edu/abs/1998ApJ...492L.107S",
      uncertainty=10),

    # NGC 1569 (post-starburst)
    E("L8-ngc1569-distance-mly",
      "NGC 1569 거리 약 11 Mly",
      11.0, "Mly",
      "최근 스타버스트 종료. 강한 은하 바람(outflow).",
      "Grocholski et al. 2008, ApJ 676 L79",
      "https://ui.adsabs.harvard.edu/abs/2008ApJ...676L..79G",
      uncertainty=0.5),

    # TON 618 (most massive BH known)
    E("L8-ton618-bh-mass-Msun",
      "TON 618 퀘이사 블랙홀 질량 6.6×10^10 M☉",
      6.6e10, "M☉",
      "현재 알려진 가장 무거운 블랙홀. 적색편이 z=2.219.",
      "Shemmer et al. 2004, ApJ 614 547",
      "https://ui.adsabs.harvard.edu/abs/2004ApJ...614..547S",
      uncertainty=1e10),

    E("L8-ton618-redshift",
      "TON 618 적색편이 z=2.219, 거리 약 10.4 Gly",
      2.219, "z",
      "초질량 블랙홀 퀘이사. 우주 나이 약 30억 년 시점.",
      "Shemmer et al. 2004, ApJ 614 547",
      "https://ui.adsabs.harvard.edu/abs/2004ApJ...614..547S",
      uncertainty=0.001),
]

# ─────────────────────────────────────────────
# D. 은하단 (30노드)
# ─────────────────────────────────────────────
cluster_nodes = [
    # Virgo
    E("L8-virgo-cluster-distance-mly",
      "처녀자리 은하단 거리 약 53.8 Mly (16.5 Mpc)",
      53.8, "Mly",
      "가장 가까운 대형 은하단. ~1300개 은하. 처녀자리 초은하단 중심.",
      "Mei et al. 2007, ApJ 655 144",
      "https://ui.adsabs.harvard.edu/abs/2007ApJ...655..144M",
      uncertainty=2),

    E("L8-virgo-cluster-mass-Msun",
      "처녀자리 은하단 총 질량 약 1.2×10^15 M☉",
      1.2e15, "M☉",
      "X선 온도 + 속도 분산 기반. 암흑물질 포함.",
      "Bohringer et al. 1994, Nature 368 828",
      "https://ui.adsabs.harvard.edu/abs/1994Natur.368..828B",
      uncertainty=0.3e15),

    E("L8-virgo-cluster-galaxy-count",
      "처녀자리 은하단 은하 수 약 1,300~2,000개",
      1500, "개",
      "밝은 은하 1300개 + 왜소은하 포함 시 ~2000개 이상.",
      "Binggeli et al. 1985, AJ 90 1681",
      "https://ui.adsabs.harvard.edu/abs/1985AJ.....90.1681B",
      uncertainty=300),

    E("L8-virgo-cluster-radius-mly",
      "처녀자리 은하단 비리얼 반경 약 7.3 Mly (2.24 Mpc)",
      7.3, "Mly",
      "비리얼 반경 R200 기준.",
      "McLaughlin 1999, AJ 117 2398",
      "https://ui.adsabs.harvard.edu/abs/1999AJ....117.2398M",
      uncertainty=0.5),

    # Coma Cluster
    E("L8-coma-cluster-distance-mly",
      "코마 은하단 거리 약 321 Mly (98.4 Mpc)",
      321, "Mly",
      "암흑물질 최초 증거(Zwicky 1933). 수천 개 은하.",
      "Carter et al. 2008, ApJS 176 424",
      "https://ui.adsabs.harvard.edu/abs/2008ApJS..176..424C",
      uncertainty=10),

    E("L8-coma-cluster-mass-Msun",
      "코마 은하단 총 질량 약 1.4×10^15 M☉",
      1.4e15, "M☉",
      "Zwicky 1933 처음 질량 불일치 지적 → 암흑물질 개념 기원.",
      "Kubo et al. 2007, ApJ 671 1466",
      "https://ui.adsabs.harvard.edu/abs/2007ApJ...671.1466K",
      uncertainty=0.2e15),

    E("L8-coma-cluster-velocity-dispersion-kms",
      "코마 은하단 속도 분산 약 977 km/s",
      977, "km/s",
      "Colless & Dunn 1996 측정.",
      "Colless & Dunn 1996, ApJ 458 435",
      "https://ui.adsabs.harvard.edu/abs/1996ApJ...458..435C",
      uncertainty=50),

    E("L8-coma-cluster-galaxy-count",
      "코마 은하단 확인 은하 수 약 1,000개 이상",
      1000, "개",
      "Abell 카탈로그 기준 풍부도 2 이상 은하단.",
      "Abell et al. 1989, ApJS 70 1",
      "https://ui.adsabs.harvard.edu/abs/1989ApJS...70....1A",
      uncertainty=200),

    # Perseus Cluster
    E("L8-perseus-cluster-distance-mly",
      "페르세우스 은하단 거리 약 237 Mly",
      237, "Mly",
      "X선 가장 밝은 은하단 중 하나. NGC 1275 중심.",
      "Struble & Rood 1999, ApJS 125 35",
      "https://ui.adsabs.harvard.edu/abs/1999ApJS..125...35S",
      uncertainty=8),

    E("L8-perseus-cluster-mass-Msun",
      "페르세우스 은하단 질량 약 6.7×10^14 M☉",
      6.7e14, "M☉",
      "X선 온도 분포 기반.",
      "Churazov et al. 2003, ApJ 590 225",
      "https://ui.adsabs.harvard.edu/abs/2003ApJ...590..225C",
      uncertainty=1e14),

    E("L8-perseus-cluster-sound-waves",
      "페르세우스 은하단 ICM 음파 주기 약 10^7 yr",
      1e7, "yr",
      "Chandra X선 관측으로 발견된 AGN 주입 음파. 파장 ~10 kpc.",
      "Fabian et al. 2003, MNRAS 344 L43",
      "https://ui.adsabs.harvard.edu/abs/2003MNRAS.344L..43F"),

    # Fornax Cluster
    E("L8-fornax-cluster-distance-mly",
      "포르낙스 은하단 거리 약 62 Mly (19.0 Mpc)",
      62, "Mly",
      "두 번째로 가까운 은하단. NGC 1399 중심.",
      "Blakeslee et al. 2009, ApJ 694 556",
      "https://ui.adsabs.harvard.edu/abs/2009ApJ...694..556B",
      uncertainty=2),

    E("L8-fornax-cluster-mass-Msun",
      "포르낙스 은하단 총 질량 약 7×10^13 M☉",
      7e13, "M☉",
      "처녀자리의 약 1/20 질량.",
      "Drinkwater et al. 2001, ApJ 548 L139",
      "https://ui.adsabs.harvard.edu/abs/2001ApJ...548L.139D",
      uncertainty=1e13),

    # Bullet Cluster
    E("L8-bullet-cluster-distance-mly",
      "총알 은하단 (1E 0657-56) 거리 약 3.7 Gly",
      3700, "Mly",
      "암흑물질 직접 증거. X선 가스 vs 중력렌즈 분리 관측.",
      "Clowe et al. 2006, ApJ 648 L109",
      "https://doi.org/10.1086/508162",
      uncertainty=100),

    E("L8-bullet-cluster-mass-Msun",
      "총알 은하단 총 질량 약 1.5×10^15 M☉",
      1.5e15, "M☉",
      "약한 중력렌즈 기반. Clowe et al. 2006.",
      "Clowe et al. 2006, ApJ 648 L109",
      "https://doi.org/10.1086/508162",
      uncertainty=0.3e15),

    # El Gordo
    E("L8-el-gordo-distance-gly",
      "엘 고르도 (ACT-CL J0102-4915) 거리 약 7.2 Gly (z=0.87)",
      7200, "Mly",
      "관측 가능 우주에서 가장 큰 충돌 은하단 후보.",
      "Marriage et al. 2011, ApJ 737 61",
      "https://ui.adsabs.harvard.edu/abs/2011ApJ...737...61M",
      uncertainty=200),

    E("L8-el-gordo-mass-Msun",
      "엘 고르도 총 질량 약 2×10^15 M☉",
      2e15, "M☉",
      "SZ 효과 + X선 온도 기반. Menanteau et al. 2012.",
      "Menanteau et al. 2012, ApJ 748 7",
      "https://ui.adsabs.harvard.edu/abs/2012ApJ...748....7M",
      uncertainty=0.5e15),

    # Abell 2029
    E("L8-abell2029-distance-mly",
      "Abell 2029 은하단 거리 약 1.06 Gly",
      1060, "Mly",
      "매우 둥근 cD 은하 IC 1101 포함. X선 매우 밝음.",
      "Struble & Rood 1999, ApJS 125 35",
      "https://ui.adsabs.harvard.edu/abs/1999ApJS..125...35S",
      uncertainty=30),

    # Abell 1689 (lensing)
    E("L8-abell1689-distance-mly",
      "Abell 1689 중력렌즈 은하단 거리 약 2.2 Gly",
      2200, "Mly",
      "가장 강한 중력렌즈 은하단 중 하나. 암흑물질 분포 연구.",
      "Limousin et al. 2007, ApJ 668 643",
      "https://ui.adsabs.harvard.edu/abs/2007ApJ...668..643L",
      uncertainty=50),

    # ICM temperature (Coma)
    E("L8-coma-icm-temperature-keV",
      "코마 은하단 ICM X선 온도 약 8 keV (9.3×10^7 K)",
      8.0, "keV",
      "은하단 간 플라즈마(ICM) 온도. X선 스펙트럼 기반.",
      "Hughes 1989, ApJ 337 21",
      "https://ui.adsabs.harvard.edu/abs/1989ApJ...337...21H",
      uncertainty=0.5),

    # Virgo SZ effect
    E("L8-virgo-sz-effect",
      "처녀자리 은하단 SZ 효과 Compton y-파라미터 약 10^-4",
      1e-4, "무차원 y",
      "수니야에프-젤도비치 효과. CMB 광자가 ICM 전자에 역산란.",
      "Pointecouteau et al. 1999, A&A 351 L23",
      "https://ui.adsabs.harvard.edu/abs/1999A%26A...351L..23P",
      uncertainty=2e-5),

    # Abell 370
    E("L8-abell370-distance-mly",
      "Abell 370 중력렌즈 은하단 거리 약 4 Gly",
      4000, "Mly",
      "HST Frontier Fields. 아인슈타인 링 발견 최초 은하단 중 하나.",
      "Soucail et al. 1987, A&A 172 L14",
      "https://ui.adsabs.harvard.edu/abs/1987A%26A...172L..14S",
      uncertainty=100),

    # MACS J0717
    E("L8-macsj0717-distance-gly",
      "MACS J0717+3745 은하단 거리 약 5.4 Gly (z=0.548)",
      5400, "Mly",
      "알려진 가장 복잡한 충돌 은하단. 4개 아집단 동시 충돌.",
      "Ebeling et al. 2001, ApJ 553 668",
      "https://ui.adsabs.harvard.edu/abs/2001ApJ...553..668E",
      uncertainty=100),

    # Cluster baryon fraction
    E("L8-cluster-baryon-fraction",
      "은하단 바리온 질량 분율 약 15~17%",
      0.156, "비율",
      "ICM + 항성 바리온 합산. 우주 바리온 분율과 일치 (Ω_b/Ω_m ~ 0.156).",
      "Ettori et al. 2009, A&A 501 61",
      "https://ui.adsabs.harvard.edu/abs/2009A%26A...501...61E",
      uncertainty=0.01),

    # Cluster luminosity function
    E("L8-cluster-mass-function-slope",
      "은하단 질량 함수 Press-Schechter 기울기 ~-2.5 (지수 꼬리)",
      -2.5, "무차원",
      "고질량 끝 지수 감소. 우주 물질 밀도 측정 도구.",
      "Press & Schechter 1974, ApJ 187 425",
      "https://ui.adsabs.harvard.edu/abs/1974ApJ...187..425P",
      uncertainty=0.2),

    # Abell richness class
    E("L8-abell-catalog-count",
      "Abell 은하단 카탈로그 수 4073개",
      4073, "개",
      "Abell et al. 1989 북반구+남반구 합산 풍부도 R>=1 은하단.",
      "Abell et al. 1989, ApJS 70 1",
      "https://ui.adsabs.harvard.edu/abs/1989ApJS...70....1A"),

    # Cool core cluster fraction
    E("L8-cool-core-cluster-fraction",
      "은하단 쿨-코어 은하단 비율 약 50%",
      0.50, "비율",
      "X선 냉각 시간 < 우주 나이 기준. AGN 피드백으로 균형 유지.",
      "Hudson et al. 2010, A&A 513 A37",
      "https://ui.adsabs.harvard.edu/abs/2010A%26A...513A..37H",
      uncertainty=0.1),

    # Virgo infall
    E("L8-virgo-infall-velocity-kms",
      "우리은하의 처녀자리 은하단 방향 인폴 속도 약 250 km/s",
      250, "km/s",
      "로컬 그룹이 처녀자리 중력에 이끌리는 속도 성분.",
      "Tully & Shaya 1984, ApJ 281 31",
      "https://ui.adsabs.harvard.edu/abs/1984ApJ...281...31T",
      uncertainty=50),

    # PLCK G004.5-19.5 (Planck SZ cluster)
    E("L8-planck-sz-cluster-count",
      "Planck 2015 SZ 은하단 카탈로그 수 1653개",
      1653, "개",
      "PSZ2 카탈로그. S/N > 4.5 기준.",
      "Planck Collaboration 2016, A&A 594 A27",
      "https://doi.org/10.1051/0004-6361/201525823"),
]

# ─────────────────────────────────────────────
# E. 대규모 구조 (20노드)
# ─────────────────────────────────────────────
largescale_nodes = [
    E("L8-laniakea-diameter-mly",
      "라니아케아 초은하단 지름 약 520 Mly (160 Mpc)",
      520, "Mly",
      "Tully et al. 2014 정의. 우리은하 포함 초은하단. 허와이어 하와이어로 '측량 불가 하늘'.",
      "Tully et al. 2014, Nature 513 71",
      "https://doi.org/10.1038/nature13674",
      uncertainty=30),

    E("L8-laniakea-mass-Msun",
      "라니아케아 초은하단 질량 약 10^17 M☉",
      1e17, "M☉",
      "수십만 개 은하 포함. Tully et al. 2014 추정.",
      "Tully et al. 2014, Nature 513 71",
      "https://doi.org/10.1038/nature13674",
      uncertainty=3e16),

    E("L8-laniakea-galaxy-count",
      "라니아케아 초은하단 은하 수 약 10^5 개",
      1e5, "개",
      "처녀자리+코마+페르세우스 은하단 포함.",
      "Tully et al. 2014, Nature 513 71",
      "https://doi.org/10.1038/nature13674",
      uncertainty=2e4),

    E("L8-great-attractor-distance-mly",
      "그레이트 어트랙터 방향 거리 약 147~164 Mly",
      160, "Mly",
      "은하수 방향(먼지 차폐). Shapley 초은하단이 실제 인력원 일부.",
      "Dressler et al. 1987, ApJ 313 37",
      "https://ui.adsabs.harvard.edu/abs/1987ApJ...313...37D",
      uncertainty=15),

    E("L8-shapley-supercluster-distance-mly",
      "셰플리 초은하단 거리 약 650 Mly (200 Mpc)",
      650, "Mly",
      "관측 가능 우주 내 가장 큰 물질 집중체 중 하나. 그레이트 어트랙터 뒤.",
      "Raychaudhury 1989, Nature 342 251",
      "https://ui.adsabs.harvard.edu/abs/1989Natur.342..251R",
      uncertainty=30),

    E("L8-shapley-supercluster-mass-Msun",
      "셰플리 초은하단 질량 약 10^16 M☉",
      1e16, "M☉",
      "수십 개 은하단 복합체.",
      "Reisenegger et al. 2000, ApJ 535 561",
      "https://ui.adsabs.harvard.edu/abs/2000ApJ...535..561R",
      uncertainty=3e15),

    E("L8-cfa2-great-wall-length-mly",
      "CfA2 그레이트 월 길이 약 500 Mly",
      500, "Mly",
      "Geller & Huchra 1989 발견. 최초로 발견된 우주 거대 구조.",
      "Geller & Huchra 1989, Science 246 897",
      "https://doi.org/10.1126/science.246.4932.897",
      uncertainty=50),

    E("L8-sloan-great-wall-length-mly",
      "슬로안 그레이트 월 길이 약 1.38 Gly",
      1380, "Mly",
      "Gott et al. 2005 발견. CfA2 그레이트 월의 3배 크기.",
      "Gott et al. 2005, ApJ 624 463",
      "https://ui.adsabs.harvard.edu/abs/2005ApJ...624..463G",
      uncertainty=100),

    E("L8-hercules-corona-wall-length-gly",
      "헤르쿨레스-북쪽왕관 그레이트 월 길이 약 10 Gly",
      10, "Gly",
      "Horvath et al. 2015 후보. 우주 동질성 스케일 ~300 Mpc 위반 논란.",
      "Horvath et al. 2015, A&A 584 A48",
      "https://doi.org/10.1051/0004-6361/201424829",
      uncertainty=2),

    E("L8-bootes-void-diameter-mly",
      "목동자리 보이드 지름 약 330~420 Mly",
      330, "Mly",
      "Kirshner et al. 1981 발견. 은하 거의 없는 거대 빈 공간.",
      "Kirshner et al. 1981, ApJ 248 L57",
      "https://ui.adsabs.harvard.edu/abs/1981ApJ...248L..57K",
      uncertainty=50),

    E("L8-cold-spot-void-diameter-mly",
      "CMB 콜드 스팟 연관 보이드 지름 약 1.8 Gly",
      1800, "Mly",
      "Naidoo et al. 2016. CMB 온도 이상과 연관된 대형 보이드 후보.",
      "Naidoo et al. 2016, MNRAS 459 L71",
      "https://ui.adsabs.harvard.edu/abs/2016MNRAS.459L..71N",
      uncertainty=300),

    E("L8-pisces-cetus-filament-length-gly",
      "물고기-고래 초은하단 복합체 길이 약 1 Gly",
      1.0, "Gly",
      "우주 거대 필라멘트. 여러 초은하단 연결.",
      "Tully 1987, ApJ 321 280",
      "https://ui.adsabs.harvard.edu/abs/1987ApJ...321..280T",
      uncertainty=0.2),

    E("L8-cosmic-web-filament-density",
      "우주 거대 구조 필라멘트 평균 밀도 우주 평균의 약 2~10배",
      5.0, "ρ/ρ_mean",
      "N체 시뮬레이션 기반. 필라멘트가 바리온 ~40% 포함.",
      "Bond et al. 1996, Nature 380 603",
      "https://doi.org/10.1038/380603a0",
      uncertainty=2),

    E("L8-void-fraction-universe",
      "우주 전체 부피 중 보이드 비율 약 60~80%",
      0.70, "부피 분율",
      "밀도 δ < -0.8 영역 기준. 우주 대부분이 빈 공간.",
      "Pan et al. 2012, MNRAS 421 926",
      "https://ui.adsabs.harvard.edu/abs/2012MNRAS.421..926P",
      uncertainty=0.1),

    E("L8-homogeneity-scale-mly",
      "우주 등방성·동질성 스케일 약 260 Mly (80 Mpc)",
      260, "Mly",
      "이 스케일 이상에서 우주는 균질. SDSS 관측 기반.",
      "Scrimgeour et al. 2012, MNRAS 425 116",
      "https://ui.adsabs.harvard.edu/abs/2012MNRAS.425..116S",
      uncertainty=30),

    E("L8-cmb-dipole-velocity-kms",
      "로컬 그룹의 CMB 쌍극자 운동 속도 약 627 km/s",
      627, "km/s",
      "COBE/WMAP/Planck 측정. 그레이트 어트랙터 방향 bulk flow.",
      "Planck Collaboration 2020, A&A 641 A1",
      "https://doi.org/10.1051/0004-6361/201833887",
      uncertainty=22),

    E("L8-observable-universe-radius-gly",
      "관측 가능한 우주 공동 반경 46.508 Gly",
      46.508, "Gly",
      "빛이 도달할 수 있는 최대 공동 거리. 팽창 우주 고려.",
      "Lineweaver & Davis 2005, Scientific American 292 36",
      "https://doi.org/10.1038/scientificamerican0305-36",
      uncertainty=0.1),

    E("L8-hubble-volume-gly3",
      "허블 부피 약 4.1×10^4 Gly^3",
      4.1e4, "Gly^3",
      "허블 반경 13.8 Gly 구 부피. 인과 지평선 개념.",
      "Lineweaver & Davis 2005, Scientific American 292 36",
      "https://doi.org/10.1038/scientificamerican0305-36"),

    E("L8-particle-horizon-gly",
      "입자 지평선 (현재 공동 거리) 46.5 Gly",
      46.5, "Gly",
      "빛이 빅뱅 이후 도달 가능한 최대 거리. 관측 가능 우주 크기.",
      "Davis & Lineweaver 2004, PASA 21 97",
      "https://doi.org/10.1071/AS03040",
      uncertainty=0.1),

    E("L8-total-galaxy-count",
      "관측 가능 우주 은하 수 추정 약 2×10^12",
      2e12, "개",
      "Conselice et al. 2016 추정. 허블 딥 필드 기반 이전 추정 1~2×10^11의 약 20배.",
      "Conselice et al. 2016, ApJ 830 83",
      "https://ui.adsabs.harvard.edu/abs/2016ApJ...830...83C",
      uncertainty=1e12),
]

# ─────────────────────────────────────────────
# F. 우주상수 (30노드)
# ─────────────────────────────────────────────
cosmological_nodes = [
    # Hubble constant - two camps
    E("L8-H0-planck-km-s-mpc",
      "허블상수 H0 Planck 2018 CMB 기반 67.36 km/s/Mpc",
      67.36, "km/s/Mpc",
      "Planck 2018 TT+TE+EE+lowE+lensing. CMB 이방성 기반.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.54),

    E("L8-H0-shoes-km-s-mpc",
      "허블상수 H0 SH0ES 2022 세페이드 기반 73.04 km/s/Mpc",
      73.04, "km/s/Mpc",
      "리스 et al. 2022 Cepheid+SNIa 사다리법. Hubble Tension 핵심.",
      "Riess et al. 2022, ApJ 934 L7",
      "https://doi.org/10.3847/2041-8213/ac5c5b",
      uncertainty=1.04),

    E("L8-H0-tension-sigma",
      "허블 텐션 유의도 약 5σ (CMB vs 거리 사다리)",
      5.0, "σ",
      "Planck 67.4 vs SH0ES 73.0 km/s/Mpc 불일치. 새 물리학 필요 가능성.",
      "Verde et al. 2019, Nature Astronomy 3 891",
      "https://doi.org/10.1038/s41550-019-0902-0",
      uncertainty=0.5),

    E("L8-omega-lambda",
      "암흑에너지 밀도 파라미터 Ω_Λ = 0.6847",
      0.6847, "무차원",
      "Planck 2018. 우주 에너지 밀도의 약 68.5%가 암흑에너지.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.0073),

    E("L8-omega-matter",
      "전체 물질 밀도 파라미터 Ω_m = 0.3153",
      0.3153, "무차원",
      "Planck 2018. 암흑물질 + 바리온 합산.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.0073),

    E("L8-omega-baryon",
      "바리온 밀도 파라미터 Ω_b = 0.0493",
      0.0493, "무차원",
      "Planck 2018. 원자/이온 물질. 전체 에너지의 약 5%.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.0003),

    E("L8-omega-dark-matter",
      "암흑물질 밀도 파라미터 Ω_cdm = 0.2660",
      0.2660, "무차원",
      "Planck 2018 최적 맞춤. Ω_m - Ω_b.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.0070),

    E("L8-omega-radiation",
      "복사 밀도 파라미터 Ω_r ≈ 9.4×10^-5",
      9.4e-5, "무차원",
      "CMB 광자 + 중성미자. 현재 우주에서 극소.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=1e-6),

    E("L8-cmb-temperature-K",
      "CMB 현재 온도 2.72548 K",
      2.72548, "K",
      "Fixsen 2009 FIRAS 측정. 우주 최정밀 흑체 스펙트럼.",
      "Fixsen 2009, ApJ 707 916",
      "https://ui.adsabs.harvard.edu/abs/2009ApJ...707..916F",
      uncertainty=0.00057),

    E("L8-cmb-peak-temp-fluctuation-K",
      "CMB 온도 요동 진폭 ΔT/T ~ 10^-5",
      1e-5, "ΔT/T",
      "COBE DMR 1992 최초 발견. 구조 형성의 씨앗.",
      "Smoot et al. 1992, ApJ 396 L1",
      "https://ui.adsabs.harvard.edu/abs/1992ApJ...396L...1S",
      uncertainty=2e-6),

    E("L8-universe-age-gyr",
      "우주 나이 13.787 Gyr",
      13.787, "Gyr",
      "Planck 2018 ΛCDM 모형 최적 맞춤.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.020),

    E("L8-sigma8",
      "물질 요동 진폭 σ8 = 0.8111",
      0.8111, "무차원",
      "Planck 2018. 8 h^-1 Mpc 스케일 밀도 요동 표준편차.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.0060),

    E("L8-spectral-index-ns",
      "원시 스펙트럼 지수 n_s = 0.9665",
      0.9665, "무차원",
      "Planck 2018. 인플레이션 이탈 지수. n_s < 1 적색 경사.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.0038),

    E("L8-optical-depth-tau",
      "재이온화 광학 깊이 τ = 0.0561",
      0.0561, "무차원",
      "Planck 2018. 재이온화 epoch z~8 추정.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.0071),

    E("L8-reionization-redshift",
      "재이온화 완료 적색편이 z_reion ≈ 7.7",
      7.7, "z",
      "Planck 2018. 빅뱅 후 약 700 Myr. 퀘이사 Lyman 기울기 관측과 일치.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.7),

    E("L8-recombination-redshift",
      "재결합 시기 적색편이 z_rec ≈ 1100",
      1100, "z",
      "CMB 표면 생성 시기. 빅뱅 후 ~380,000년.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=5),

    E("L8-recombination-time-kyr",
      "재결합 시기 우주 나이 약 380 kyr",
      380, "kyr",
      "CMB 방출 시점. 우주 투명화.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=5),

    E("L8-dark-energy-w",
      "암흑에너지 상태 방정식 w = -1.03 (우주상수 모형 -1)",
      -1.03, "무차원",
      "Planck 2018 + BAO + SNIa 결합 제약. 우주상수 ΛCDM -1과 1σ 일치.",
      "Planck Collaboration 2020, A&A 641 A8",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.03),

    E("L8-critical-density-kg-m3",
      "현재 우주 임계 밀도 ρ_c ≈ 8.62×10^-27 kg/m³",
      8.62e-27, "kg/m³",
      "ρ_c = 3H0²/(8πG). Planck H0=67.36 기준.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.1e-27),

    E("L8-matter-radiation-equality-z",
      "물질-복사 등밀도 시점 적색편이 z_eq ≈ 3387",
      3387, "z",
      "Planck 2018. 물질 우세 → 구조 성장 시작.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=21),

    E("L8-dark-energy-acceleration-z",
      "우주 가속 팽창 시작 적색편이 z_acc ≈ 0.64",
      0.64, "z",
      "Riess et al. 1998 / Perlmutter et al. 1999 초신성 관측으로 발견.",
      "Riess et al. 1998, AJ 116 1009",
      "https://ui.adsabs.harvard.edu/abs/1998AJ....116.1009R",
      uncertainty=0.05),

    E("L8-total-stars-observable-universe",
      "관측 가능 우주 총 별 수 추정 10^23 ~ 10^24",
      1e24, "개",
      "은하 수 2×10^12 × 은하당 별 5×10^11 = ~10^24. 대략적 추정.",
      "Conselice et al. 2016, ApJ 830 83",
      "https://ui.adsabs.harvard.edu/abs/2016ApJ...830...83C",
      uncertainty=9e23),

    E("L8-baryon-asymmetry",
      "바리온 비대칭 파라미터 η = n_b/n_γ ≈ 6×10^-10",
      6e-10, "n_b/n_γ",
      "Planck 2018 + 빅뱅 핵합성 기반. 물질-반물질 비대칭 근원 미해결.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.2e-10),

    E("L8-cmb-photon-number-density",
      "CMB 광자 수 밀도 약 411 /cm³",
      411, "/cm³",
      "온도 2.72548 K 흑체 기준. n_γ = 2ζ(3)/π² × (kT/hc)³.",
      "Fixsen 2009, ApJ 707 916",
      "https://ui.adsabs.harvard.edu/abs/2009ApJ...707..916F",
      uncertainty=2),

    E("L8-neutrino-background-temp-K",
      "우주 배경 중성미자 현재 온도 약 1.945 K",
      1.945, "K",
      "T_ν = (4/11)^(1/3) × T_CMB. 이론값 직접 측정 미완.",
      "Kolb & Turner 1990, The Early Universe (Addison-Wesley)",
      "https://ui.adsabs.harvard.edu/abs/1990eaun.book.....K"),

    E("L8-lambda-cosmological-constant",
      "우주상수 Λ ≈ 1.11×10^-52 m^-2",
      1.11e-52, "m^-2",
      "Ω_Λ × H0² × 3/c² 에서 계산. 암흑에너지 밀도에 대응.",
      "Planck Collaboration 2020, A&A 641 A6",
      "https://doi.org/10.1051/0004-6361/201833910",
      uncertainty=0.02e-52),

    E("L8-inflation-e-folding",
      "인플레이션 e-폴딩 수 N ≥ 60",
      60, "e-폴딩",
      "지평선·평탄성 문제 해결에 필요한 최소 e-폴딩. 정확한 값 미결.",
      "Guth 1981, Phys.Rev.D 23 347",
      "https://doi.org/10.1103/PhysRevD.23.347",
      uncertainty=10),

    E("L8-bbn-helium-fraction",
      "빅뱅 핵합성 예측 헬륨-4 질량 분율 Y_p ≈ 0.247",
      0.247, "질량 분율",
      "관측값 0.245±0.003. 빅뱅 핵합성 강력한 증거.",
      "Peimbert et al. 2016, ApJ 830 33",
      "https://ui.adsabs.harvard.edu/abs/2016ApJ...830...33P",
      uncertainty=0.003),

    E("L8-bbn-deuterium-abundance",
      "빅뱅 핵합성 예측 중수소 풍부도 D/H ≈ 2.55×10^-5",
      2.55e-5, "수 비율",
      "Cooke et al. 2018 퀘이사 흡수선 기반 측정. 바리온 밀도 제약.",
      "Cooke et al. 2018, ApJ 855 102",
      "https://ui.adsabs.harvard.edu/abs/2018ApJ...855..102C",
      uncertainty=0.03e-5),

    E("L8-grav-wave-background",
      "원시 중력파 배경 텐서-스칼라 비 r < 0.056",
      0.056, "상한 r",
      "BICEP/Keck 2021 CMB B-모드 편광 상한. 인플레이션 에너지 척도 제약.",
      "BICEP/Keck Collaboration 2021, Phys.Rev.Lett. 127 151301",
      "https://doi.org/10.1103/PhysRevLett.127.151301"),
]

# ─────────────────────────────────────────────
# G. 은하 유형 (30노드)
# ─────────────────────────────────────────────
galaxy_type_nodes = [
    # Ellipticals
    E("L8-type-E0-example",
      "타원은하 E0 (원형 타원) 예: NGC 1399",
      "E0", "허블 유형",
      "타원율 (1-b/a)×10 = 0. 완전 구형. 포르낙스 은하단 중심.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-E7-example",
      "타원은하 E7 (가장 납작한 타원) 예: NGC 1600",
      "E7", "허블 유형",
      "타원율 최대값. 실제로 E7 이상은 S0 (렌즈형)과 분류 경계.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-S0-example",
      "렌즈형 은하 S0 예: NGC 1023",
      "S0", "허블 유형",
      "원반+팽대부, 나선팔 없음. 타원은하와 나선은하 중간. 은하단에 다수.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-Sa-example",
      "나선은하 Sa (촘촘한 나선) 예: M104 솜브레로",
      "SA(s)a", "허블 유형",
      "큰 팽대부, 촘촘히 감긴 나선팔, 적은 성간물질.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-Sb-example",
      "나선은하 Sb 예: 우리은하, M31",
      "SA(s)b", "허블 유형",
      "중간 팽대부, 중간 나선팔 감김.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-Sc-example",
      "나선은하 Sc (느슨한 나선) 예: M33, M101",
      "SA(s)c", "허블 유형",
      "작은 팽대부, 느슨한 나선팔, 활발한 별 생성.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-Sd-example",
      "나선은하 Sd 예: NGC 300",
      "SA(s)d", "허블 유형",
      "핵이 매우 작고 나선팔 분절.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-SBa-example",
      "막대 나선 SBa 예: NGC 4594",
      "SB(s)a", "허블 유형",
      "강한 막대 구조 + 촘촘한 나선팔.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-SBb-example",
      "막대 나선 SBb 예: M95 (NGC 3351)",
      "SB(r)b", "허블 유형",
      "막대 끝에서 나선팔 시작. 환상(ring) 구조 흔함.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-SBc-example",
      "막대 나선 SBc 예: M109 (NGC 3992)",
      "SB(rs)bc", "허블 유형",
      "우리은하 유형과 유사한 SBbc.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-Irr-I-example",
      "불규칙 은하 Irr I 예: LMC, SMC",
      "IB(s)m", "허블 유형",
      "뚜렷한 구조 없음. 젊고 별 생성 활발. 금속성 낮음.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-Irr-II-example",
      "불규칙 은하 Irr II 예: Arp 220",
      "I0 pec", "허블 유형",
      "병합/상호작용으로 일그러진 은하. 강렬 별 생성.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-cD-example",
      "cD 은하 (은하단 초거대 타원) 예: M87, NGC 1399",
      "cD", "허블 유형",
      "은하단 중심에 위치. 다수 은하 합병 결과. 수십만 kly 크기 가능.",
      "Matthews et al. 1964, AJ 69 635",
      "https://ui.adsabs.harvard.edu/abs/1964AJ.....69..635M"),

    E("L8-type-quasar-example",
      "퀘이사 (준항성 천체) 예: 3C 273, TON 618",
      "AGN-QSO", "활동성 은하핵 유형",
      "광도 극히 높은 AGN. 조기 우주 초질량 블랙홀 강착 원반.",
      "Schmidt 1963, Nature 197 1040",
      "https://doi.org/10.1038/1971040a0"),

    E("L8-type-seyfert1-example",
      "세이퍼트 1 은하 예: NGC 4151",
      "Sy1", "AGN 분류",
      "넓은 허용선 + 좁은 금지선. AGN 직접 시선. 통합 모형.",
      "Seyfert 1943, ApJ 97 28",
      "https://ui.adsabs.harvard.edu/abs/1943ApJ....97...28S"),

    E("L8-type-seyfert2-example",
      "세이퍼트 2 은하 예: NGC 1068 (M77)",
      "Sy2", "AGN 분류",
      "좁은 선만 관측. 먼지 토러스로 AGN 가려짐. 통합 AGN 모형 증거.",
      "Antonucci & Miller 1985, ApJ 297 621",
      "https://ui.adsabs.harvard.edu/abs/1985ApJ...297..621A"),

    E("L8-type-blazar-example",
      "블레이자 예: BL Lac, Mrk 421",
      "BLL/FSRQ", "AGN 분류",
      "제트가 시선 방향으로 향한 AGN. 빠른 변광. 감마선 밝음.",
      "Blandford & Rees 1978, Pittsburgh Conf. Proc.",
      "https://ui.adsabs.harvard.edu/abs/1978blra.conf..328B"),

    E("L8-type-starburst-example",
      "스타버스트 은하 예: M82, NGC 253",
      "SB-galaxy", "활동 유형",
      "별 생성률이 정상 은하의 10~100배. 보통 병합으로 촉발.",
      "Kennicutt 1998, ARA&A 36 189",
      "https://ui.adsabs.harvard.edu/abs/1998ARA%26A..36..189K"),

    E("L8-type-ulirg-example",
      "초광도 적외선 은하(ULIRG) 예: Arp 220",
      "ULIRG", "적외선 분류",
      "L_IR > 10^12 L☉. 먼지에 가려진 격렬 별 생성.",
      "Sanders & Mirabel 1996, ARA&A 34 749",
      "https://ui.adsabs.harvard.edu/abs/1996ARA%26A..34..749S"),

    E("L8-type-dwarf-elliptical-example",
      "왜소 타원은하 dE 예: M32 (NGC 221)",
      "dE2", "허블 유형",
      "M31 위성. 구상성단과 일반 은하 중간 단계.",
      "de Vaucouleurs et al. 1991, RC3 Catalog",
      "https://ui.adsabs.harvard.edu/abs/1991rc3..book.....D"),

    E("L8-type-dsph-example",
      "왜소 구형 은하 dSph 예: 조각가, 포르낙스",
      "dSph", "허블 유형",
      "표면밝기 가장 낮은 은하. 암흑물질 지배.",
      "Mateo 1998, ARA&A 36 435",
      "https://ui.adsabs.harvard.edu/abs/1998ARA%26A..36..435M"),

    E("L8-type-blue-compact-example",
      "청색 콤팩트 왜소은하 BCD 예: I Zw 18",
      "BCD", "허블 유형",
      "금속성 극히 낮음. 원시 은하 유사. 활발한 별 생성.",
      "Sargent & Searle 1970, ApJ 162 L155",
      "https://ui.adsabs.harvard.edu/abs/1970ApJ...162L.155S"),

    E("L8-type-ring-example",
      "고리 은하 예: Hoag's Object, AM 0644-741",
      "R", "특수 구조",
      "중심 핵 + 외부 고리. 조면 충돌 또는 막대 공명으로 형성.",
      "Athanassoula et al. 1997, MNRAS 286 284",
      "https://ui.adsabs.harvard.edu/abs/1997MNRAS.286..284A"),

    E("L8-type-polar-ring-example",
      "극궤도 고리 은하 예: NGC 4650A",
      "PRG", "특수 구조",
      "주 은하와 90도 기울어진 고리. 은하 합병 증거.",
      "Whitmore et al. 1990, AJ 100 1489",
      "https://ui.adsabs.harvard.edu/abs/1990AJ....100.1489W"),

    E("L8-type-lenticular-fraction",
      "은하단 내 렌즈형(S0) 은하 비율 약 40~50%",
      0.45, "비율",
      "처녀자리 은하단 기준. 필드 은하에서는 ~20%.",
      "Dressler 1980, ApJ 236 351",
      "https://ui.adsabs.harvard.edu/abs/1980ApJ...236..351D",
      uncertainty=0.05),

    E("L8-morphology-density-relation",
      "형태-밀도 관계: 은하단 중심일수록 타원은하 비율 증가",
      "E/S0 비율 증가", "정성 법칙",
      "Dressler 1980. 환경이 은하 진화를 결정함을 보인 핵심 관측.",
      "Dressler 1980, ApJ 236 351",
      "https://ui.adsabs.harvard.edu/abs/1980ApJ...236..351D"),

    E("L8-hubble-sequence-revision",
      "허블 분류 1926년 제안, 현재 3D 형태분류 보완 사용",
      1926, "연도",
      "Edwin Hubble 1926. 이후 de Vaucouleurs 개정(1959). SDSS→기계학습 분류로 발전.",
      "Hubble 1926, ApJ 64 321",
      "https://ui.adsabs.harvard.edu/abs/1926ApJ....64..321H"),

    E("L8-type-fraction-spiral",
      "현재 우주 나선은하 비율 약 72% (필드 은하)",
      0.72, "비율",
      "Loveday 1996 APM 기반. 은하단 vs 필드 큰 차이.",
      "Loveday 1996, MNRAS 278 1025",
      "https://ui.adsabs.harvard.edu/abs/1996MNRAS.278.1025L",
      uncertainty=0.05),

    E("L8-type-fraction-elliptical",
      "현재 우주 타원+렌즈형 은하 비율 약 20~30% (필드)",
      0.25, "비율",
      "Loveday 1996. 은하단 중심에서는 ~70%.",
      "Loveday 1996, MNRAS 278 1025",
      "https://ui.adsabs.harvard.edu/abs/1996MNRAS.278.1025L",
      uncertainty=0.05),

    E("L8-red-sequence-blue-cloud",
      "은하 색-등급 이중 분포: 적색 계열 vs 청색 구름",
      2, "집단 수",
      "Baldry et al. 2004 SDSS. 별 생성 활발(청색) vs 종료(적색) 이분법.",
      "Baldry et al. 2004, ApJ 600 681",
      "https://ui.adsabs.harvard.edu/abs/2004ApJ...600..681B"),

    E("L8-green-valley-fraction",
      "녹색 계곡 은하 (전환기) 비율 약 10%",
      0.10, "비율",
      "청색→적색 전환 중인 은하. 피드백 AGN/ram압력 박리 등 원인.",
      "Martin et al. 2007, ApJS 173 342",
      "https://ui.adsabs.harvard.edu/abs/2007ApJS..173..342M",
      uncertainty=0.03),
]

# ─────────────────────────────────────────────
# 병합 및 저장
# ─────────────────────────────────────────────
all_new_nodes = (
    milkyway_nodes +       # A: 20
    local_group_nodes +    # B: 30
    notable_galaxies_nodes + # C: 40
    cluster_nodes +        # D: 30
    largescale_nodes +     # E: 20
    cosmological_nodes +   # F: 30
    galaxy_type_nodes      # G: 30
)

print(f"생성된 L8_galactic 노드 수: {len(all_new_nodes)}")
print(f"  A. 우리은하 구조: {len(milkyway_nodes)}")
print(f"  B. 로컬 그룹: {len(local_group_nodes)}")
print(f"  C. 주요 은하: {len(notable_galaxies_nodes)}")
print(f"  D. 은하단: {len(cluster_nodes)}")
print(f"  E. 대규모 구조: {len(largescale_nodes)}")
print(f"  F. 우주상수: {len(cosmological_nodes)}")
print(f"  G. 은하 유형: {len(galaxy_type_nodes)}")

# 중복 ID 확인
ids = [n["id"] for n in all_new_nodes]
dupes = [i for i in ids if ids.count(i) > 1]
if dupes:
    print(f"WARNING 중복 ID: {set(dupes)}")
else:
    print("ID 중복 없음 OK")

# JSON 로드
with open(PATH, "r") as f:
    data = json.load(f)

existing_ids = {n["id"] for n in data["nodes"] if "id" in n}
added = 0
skipped = 0
for node in all_new_nodes:
    if node["id"] in existing_ids:
        print(f"SKIP (이미 존재): {node['id']}")
        skipped += 1
    else:
        data["nodes"].append(node)
        existing_ids.add(node["id"])
        added += 1

# L8_galactic 엣지 추가 (내부 연결 핵심 몇 개)
L8_edges = [
    {"from": "L8-mw-diameter-kly", "to": "L8-mw-gc-distance-kly", "relation": "우리은하 지름 → 은하중심 거리 포함"},
    {"from": "L8-mw-stellar-count", "to": "L8-mw-sfr-Msun-yr", "relation": "별 수 → 별 생성률 누적"},
    {"from": "L8-mw-spiral-arms", "to": "L8-mw-type", "relation": "나선팔 수 → 은하 형태 SBbc"},
    {"from": "L8-mw-total-mass-Msun", "to": "L8-mw-dark-matter-fraction", "relation": "전체 질량 중 암흑물질 비율"},
    {"from": "L8-mw-sgra-mass-Msun", "to": "L8-mw-bulge-mass-Msun", "relation": "BH → 팽대부 포함"},
    {"from": "L8-m31-distance-mly", "to": "L8-m31-approach-velocity-kms", "relation": "거리 + 속도 → 충돌 타임라인"},
    {"from": "L8-m31-approach-velocity-kms", "to": "L8-m31-merger-time-gyr", "relation": "접근 속도 → 병합 시간 추산"},
    {"from": "L8-lmc-distance-kly", "to": "L8-lmc-mass-Msun", "relation": "LMC 거리 + 질량"},
    {"from": "L8-smc-distance-kly", "to": "L8-smc-mass-Msun", "relation": "SMC 거리 + 질량"},
    {"from": "L8-lg-total-mass-Msun", "to": "L8-mw-total-mass-Msun", "relation": "로컬 그룹 총 질량 = MW + M31 + 기타"},
    {"from": "L8-lg-total-mass-Msun", "to": "L8-m31-mass-Msun", "relation": "로컬 그룹 총 질량 = MW + M31 + 기타"},
    # 주요 은하
    {"from": "L8-m87-bh-mass-Msun", "to": "L8-m87-jet-length-kly", "relation": "초질량 BH → 상대론적 제트 구동"},
    {"from": "L8-ngc5128-bh-mass-Msun", "to": "L8-ngc5128-type", "relation": "BH 질량 → AGN 활동 Cen A"},
    {"from": "L8-m82-sfr-Msun-yr", "to": "L8-m81-distance-mly", "relation": "M81-M82 상호작용 → 스타버스트"},
    {"from": "L8-3c273-luminosity-Lsun", "to": "L8-3c273-distance-gly", "relation": "광도 + 거리 → 겉보기 밝기"},
    {"from": "L8-ton618-bh-mass-Msun", "to": "L8-ton618-redshift", "relation": "BH 질량 최대값 + 고적색편이"},
    # 은하단
    {"from": "L8-virgo-cluster-mass-Msun", "to": "L8-virgo-infall-velocity-kms", "relation": "은하단 질량 → 인폴 유발"},
    {"from": "L8-coma-cluster-mass-Msun", "to": "L8-coma-cluster-velocity-dispersion-kms", "relation": "질량 → 비리얼 속도 분산"},
    {"from": "L8-bullet-cluster-mass-Msun", "to": "L8-bullet-cluster-distance-mly", "relation": "충돌 은하단 질량 + 거리"},
    {"from": "L8-cluster-baryon-fraction", "to": "L8-omega-baryon", "relation": "은하단 바리온 분율 ≈ 우주 Ω_b/Ω_m"},
    # 대규모 구조
    {"from": "L8-laniakea-diameter-mly", "to": "L8-virgo-cluster-distance-mly", "relation": "라니아케아 포함 → 처녀자리 은하단"},
    {"from": "L8-laniakea-mass-Msun", "to": "L8-lg-total-mass-Msun", "relation": "초은하단 → 로컬 그룹 포함"},
    {"from": "L8-homogeneity-scale-mly", "to": "L8-observable-universe-radius-gly", "relation": "동질성 스케일 이상 → 등방 우주"},
    # 우주상수
    {"from": "L8-H0-planck-km-s-mpc", "to": "L8-H0-tension-sigma", "relation": "Planck H0 vs SH0ES → 허블 텐션"},
    {"from": "L8-H0-shoes-km-s-mpc", "to": "L8-H0-tension-sigma", "relation": "SH0ES H0 vs Planck → 허블 텐션"},
    {"from": "L8-omega-lambda", "to": "L8-dark-energy-acceleration-z", "relation": "Ω_Λ → 우주 가속 팽창"},
    {"from": "L8-omega-matter", "to": "L8-omega-baryon", "relation": "Ω_m = Ω_cdm + Ω_b"},
    {"from": "L8-omega-matter", "to": "L8-omega-dark-matter", "relation": "Ω_m = Ω_cdm + Ω_b"},
    {"from": "L8-cmb-temperature-K", "to": "L8-cmb-photon-number-density", "relation": "T_CMB → 광자 수 밀도"},
    {"from": "L8-cmb-temperature-K", "to": "L8-neutrino-background-temp-K", "relation": "T_CMB → T_ν = (4/11)^(1/3) × T_CMB"},
    {"from": "L8-universe-age-gyr", "to": "L8-dark-energy-acceleration-z", "relation": "우주 나이 → 가속 시작 시점"},
    {"from": "L8-recombination-redshift", "to": "L8-cmb-temperature-K", "relation": "재결합 → CMB 방출"},
    {"from": "L8-bbn-helium-fraction", "to": "L8-omega-baryon", "relation": "BBN Y_p ↔ Ω_b 제약"},
    {"from": "L8-bbn-deuterium-abundance", "to": "L8-omega-baryon", "relation": "BBN D/H ↔ Ω_b 제약"},
    # 은하 유형 → 실제 은하 연결
    {"from": "L8-type-E0-example", "to": "L8-m87-type", "relation": "E형 → M87 E0p"},
    {"from": "L8-type-SBb-example", "to": "L8-mw-type", "relation": "SBb계열 → 우리은하 SBbc"},
    {"from": "L8-type-Irr-I-example", "to": "L8-lmc-distance-kly", "relation": "Irr I → LMC"},
    {"from": "L8-type-quasar-example", "to": "L8-3c273-distance-gly", "relation": "QSO형 → 3C 273"},
    {"from": "L8-type-cD-example", "to": "L8-m87-mass-Msun", "relation": "cD → M87 초거대 타원"},
    {"from": "L8-type-starburst-example", "to": "L8-m82-sfr-Msun-yr", "relation": "스타버스트 → M82"},
    {"from": "L8-morphology-density-relation", "to": "L8-type-lenticular-fraction", "relation": "형태-밀도 → S0 비율 증가"},
    {"from": "L8-red-sequence-blue-cloud", "to": "L8-green-valley-fraction", "relation": "이중분포 → 전환 녹색 계곡"},
    # L7 bridge (우리은하 → 별 수준 연결)
    {"from": "L8-mw-sfr-Msun-yr", "to": "L8-mw-stellar-count", "relation": "별 생성률 × 우주 나이 → 별 누적 수"},
    {"from": "L8-mw-age-gyr", "to": "L8-universe-age-gyr", "relation": "은하 나이 < 우주 나이 (일관성)"},
    {"from": "L8-total-stars-observable-universe", "to": "L8-total-galaxy-count", "relation": "총 별 수 = 은하 수 × 은하당 별 수"},
    {"from": "L8-observable-universe-radius-gly", "to": "L8-hubble-volume-gly3", "relation": "반경 → 부피"},
]

# 기존 엣지 집합 (중복 방지)
existing_edge_keys = set()
for e in data.get("edges", []):
    existing_edge_keys.add((e.get("from"), e.get("to")))

new_edge_count = 0
for edge in L8_edges:
    key = (edge["from"], edge["to"])
    if key not in existing_edge_keys:
        data["edges"].append(edge)
        existing_edge_keys.add(key)
        new_edge_count += 1

# _meta 업데이트
old_version = data["_meta"].get("version", "8.4")
new_version = "8.5"
data["_meta"]["version"] = new_version
data["version"] = new_version
data["_meta"]["date"] = "2026-04-08"
data["_meta"]["node_count"] = len(data["nodes"])
data["_meta"]["edge_count"] = len(data["edges"])
data["_meta"]["levels"].append("L8_galactic")

data["_meta"]["origin_stats"]["natural"] = data["_meta"]["origin_stats"].get("natural", 0) + added
data["_meta"]["grade_stats"]["EMPIRICAL"] = data["_meta"]["grade_stats"].get("EMPIRICAL", 0) + added

data["_meta"].setdefault("changelog", []).append({
    "version": new_version,
    "date": "2026-04-08",
    "change": "L8_galactic 레벨 신설 — 은하/우주 스케일 노드 추가",
    "added_nodes": added,
    "added_edges": new_edge_count,
    "categories": {
        "A_milkyway": len(milkyway_nodes),
        "B_local_group": len(local_group_nodes),
        "C_notable_galaxies": len(notable_galaxies_nodes),
        "D_clusters": len(cluster_nodes),
        "E_large_scale": len(largescale_nodes),
        "F_cosmological": len(cosmological_nodes),
        "G_galaxy_types": len(galaxy_type_nodes),
    },
    "sources": ["Planck 2018", "NED", "SIMBAD", "NASA/IPAC", "McConnachie 2012",
                "EHT 2019", "GRAVITY 2019", "Riess 2022", "Tully 2014"],
    "before_total_nodes": 678,
    "after_total_nodes": len(data["nodes"]),
})

# 저장
with open(PATH, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n완료:")
print(f"  추가된 노드: {added}")
print(f"  건너뜀: {skipped}")
print(f"  추가된 엣지: {new_edge_count}")
print(f"  총 노드: {len(data['nodes'])}")
print(f"  총 엣지: {len(data['edges'])}")
print(f"  버전: {old_version} → {new_version}")
