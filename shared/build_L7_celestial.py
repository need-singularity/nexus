#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L7_celestial 노드 생성 스크립트
출처: NASA Planetary Fact Sheet, NASA/JPL, ESA Hipparcos, IAU, SIMBAD
"""

import json
import shutil
from datetime import date

# ──────────────────────────────────────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────────────────────────────────────
NASA_FACT = "NASA Planetary Fact Sheet"
NASA_FACT_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"
NASA_JPL = "NASA/JPL Solar System Dynamics"
NASA_JPL_URL = "https://ssd.jpl.nasa.gov/"
ESA_HIP = "ESA Hipparcos Catalogue"
ESA_HIP_URL = "https://www.cosmos.esa.int/web/hipparcos/catalogues"
IAU_URL = "https://www.iau.org/public/themes/naming_stars/"
NASA_EXOPLANET = "NASA Exoplanet Archive"
NASA_EXOPLANET_URL = "https://exoplanetarchive.ipac.caltech.edu/"
NASA_SUN = "NASA Sun Fact Sheet"
NASA_SUN_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html"
NASA_SMALL_BODY = "NASA Small Body Database"
NASA_SMALL_BODY_URL = "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html"
NASA_COMET = "NASA/JPL Comet Database"
NASA_COMET_URL = "https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html"
SIMBAD = "SIMBAD Astronomical Database"
SIMBAD_URL = "https://simbad.u-strasbg.fr/simbad/"
MESSIER = "Messier Catalogue / NGC"
MESSIER_URL = "https://www.messier.seds.org/"
EHT = "Event Horizon Telescope Collaboration"
EHT_URL = "https://eventhorizontelescope.org/"
NASA_HUBBLE = "NASA/Hubble Space Telescope"
NASA_HUBBLE_URL = "https://hubblesite.org/"


def node(id_, claim, measured, unit, detail, source, source_url,
         n6_expr="misc", grade="EMPIRICAL", causal="EMPIRICAL",
         thread="misc", origin="natural", uncertainty=None, bt_refs=None):
    nd = {
        "id": id_,
        "level": "L7_celestial",
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
        "bt_refs": bt_refs or [],
    }
    if uncertainty is not None:
        nd["uncertainty"] = uncertainty
    return nd


# ──────────────────────────────────────────────────────────────────────────────
# 1. 태양계 행성 (8행성 × 10속성 = 80노드)
# ──────────────────────────────────────────────────────────────────────────────
#  속성: mass_kg, radius_km, sma_au, orbital_period_yr, rotation_period_hr,
#        moons, mean_density, axial_tilt, eccentricity, albedo

PLANETS = [
    # (name_en, name_kr,
    #  mass_kg, radius_km, sma_au, orbital_yr, rot_hr, moons, density, tilt, ecc, albedo)
    ("mercury", "수성",
     3.301e23, 2439.7, 0.387, 0.2409, 1407.6, 0, 5427.0, 0.034, 0.2056, 0.088),
    ("venus", "금성",
     4.867e24, 6051.8, 0.723, 0.6152, -5832.6, 0, 5243.0, 177.4, 0.0067, 0.76),
    ("earth", "지구",
     5.972e24, 6371.0, 1.000, 1.0000, 23.934, 1, 5514.0, 23.44, 0.0167, 0.306),
    ("mars", "화성",
     6.417e23, 3389.5, 1.524, 1.8808, 24.623, 2, 3933.0, 25.19, 0.0934, 0.25),
    ("jupiter", "목성",
     1.898e27, 69911.0, 5.203, 11.862, 9.925, 95, 1326.0, 3.13, 0.0489, 0.52),
    ("saturn", "토성",
     5.683e26, 58232.0, 9.537, 29.457, 10.656, 146, 687.0, 26.73, 0.0565, 0.47),
    ("uranus", "천왕성",
     8.681e25, 25362.0, 19.189, 84.011, -17.24, 28, 1271.0, 97.77, 0.0463, 0.51),
    ("neptune", "해왕성",
     1.024e26, 24622.0, 30.070, 164.79, 16.11, 16, 1638.0, 28.32, 0.0097, 0.41),
]

PROP_LABELS = {
    "mass":           ("질량", "kg"),
    "radius":         ("적도반경", "km"),
    "sma":            ("공전 긴반지름", "AU"),
    "orbital_period": ("공전주기", "년"),
    "rotation":       ("자전주기", "시간"),
    "moons":          ("위성 수", "개"),
    "density":        ("평균밀도", "kg/m³"),
    "axial_tilt":     ("자전축 기울기", "도"),
    "eccentricity":   ("궤도 이심률", ""),
    "albedo":         ("기하 알베도", ""),
}

solar_system_nodes = []
for (en, kr, mass, rad, sma, orb, rot, moons, dens, tilt, ecc, alb) in PLANETS:
    vals = {
        "mass": mass,
        "radius": rad,
        "sma": sma,
        "orbital_period": orb,
        "rotation": rot,
        "moons": int(moons),
        "density": dens,
        "axial_tilt": tilt,
        "eccentricity": ecc,
        "albedo": alb,
    }
    details = {
        "mass": f"{kr} 전체 질량 (IAU 2012 채용값)",
        "radius": f"{kr} 적도 반경 (체적 평균)",
        "sma": f"{kr} 공전궤도 긴반지름",
        "orbital_period": f"{kr} 1회 공전 소요 지구년",
        "rotation": f"{kr} 자전주기 (음수=역방향 자전)",
        "moons": f"{kr} 확인된 위성 수 (2024 기준)",
        "density": f"{kr} 전체 평균밀도",
        "axial_tilt": f"{kr} 적도면-궤도면 기울기",
        "eccentricity": f"{kr} 궤도 이심률",
        "albedo": f"{kr} 기하 알베도 (가시광)",
    }
    for prop, val in vals.items():
        lbl, unit = PROP_LABELS[prop]
        solar_system_nodes.append(node(
            id_=f"L7-{en}-{prop}",
            claim=f"{kr} {lbl}",
            measured=val,
            unit=unit,
            detail=details[prop],
            source=NASA_FACT,
            source_url=NASA_FACT_URL,
        ))

print(f"[1] 태양계 행성: {len(solar_system_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 2. 주요 위성 (8위성 × 5속성 = 40노드)
#    속성: radius_km, orbital_period_day, density, tidal_lock, surface_temp_K
# ──────────────────────────────────────────────────────────────────────────────
# (id_suffix, kr_name, parent_planet, radius_km, orb_day, density, tidal_lock_bool, surf_temp_K)
MOONS = [
    ("luna",       "달",       "지구",   1737.4, 27.322, 3346.0, True,  220.0),
    ("io",         "이오",     "목성",   1821.6, 1.769,  3528.0, True,  130.0),
    ("europa",     "유로파",   "목성",   1560.8, 3.551,  3013.0, True,  102.0),
    ("ganymede",   "가니메데", "목성",   2634.1, 7.155,  1936.0, True,  110.0),
    ("callisto",   "칼리스토", "목성",   2410.3, 16.690, 1834.0, True,  134.0),
    ("titan",      "타이탄",   "토성",   2574.7, 15.945, 1880.0, True,  94.0),
    ("triton",     "트리톤",   "해왕성", 1353.4, -5.877, 2061.0, True,  38.0),
    ("enceladus",  "엔켈라두스","토성",   252.1, 1.370,  1610.0, True,  75.0),
]

MOON_PROPS = [
    ("radius",         "반경",         "km"),
    ("orbital_period", "공전주기",      "일"),
    ("density",        "평균밀도",      "kg/m³"),
    ("tidal_lock",     "조석잠금 여부", "bool"),
    ("surface_temp",   "표면 평균온도", "K"),
]

moon_nodes = []
for (sid, kr, parent, rad, orb, dens, lock, temp) in MOONS:
    vals = [rad, orb, dens, 1 if lock else 0, temp]
    details = [
        f"{parent} 위성 {kr} 반경",
        f"{kr} {parent} 공전주기 (음수=역행)",
        f"{kr} 평균밀도",
        f"{kr} 조석잠금=1, 미잠금=0",
        f"{kr} 표면 평균온도",
    ]
    for (prop, lbl, unit), val, det in zip(MOON_PROPS, vals, details):
        moon_nodes.append(node(
            id_=f"L7-moon-{sid}-{prop}",
            claim=f"{kr} {lbl}",
            measured=val,
            unit=unit,
            detail=det,
            source=NASA_FACT,
            source_url=NASA_FACT_URL,
        ))

print(f"[2] 주요 위성: {len(moon_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 3. 소행성대 / 카이퍼벨트 주요천체 (20노드)
# ──────────────────────────────────────────────────────────────────────────────
# 실측값 출처: NASA Small Body Database + MPC
SMALL_BODIES = [
    # (id, kr, mass_kg, radius_km, sma_au, orb_yr, type_label)
    ("ceres",     "세레스",   9.393e20, 473.0,  2.767, 4.604, "왜행성/소행성대"),
    ("pallas",    "팔라스",   2.04e20,  256.0,  2.771, 4.614, "소행성대 C형"),
    ("vesta",     "베스타",   2.591e20, 262.7,  2.362, 3.629, "소행성대 V형"),
    ("hygiea",    "히기에이아",8.67e19, 217.0,  3.142, 5.571, "소행성대 C형"),
    ("pluto",     "명왕성",   1.303e22, 1188.3, 39.48, 247.9, "카이퍼벨트 왜행성"),
    ("eris",      "에리스",   1.661e22, 1163.0, 67.78, 558.8, "산란 원반 왜행성"),
    ("makemake",  "마케마케", 3.1e21,   715.0,  45.79, 309.9, "카이퍼벨트 왜행성"),
    ("haumea",    "하우메아", 4.006e21, 780.0,  43.34, 285.4, "카이퍼벨트 왜행성 (장축)"),
    ("quaoar",    "콰오아르", 1.4e21,   555.0,  43.41, 286.5, "카이퍼벨트 TNO"),
    ("sedna",     "세드나",   8.0e20,   497.5,  506.0, 11400.0, "오르트 내부 천체"),
]

small_body_nodes = []
for (sid, kr, mass, rad, sma, orb, typ) in SMALL_BODIES:
    small_body_nodes += [
        node(f"L7-sb-{sid}-mass",           f"{kr} 질량",          mass,  "kg",  f"{kr} ({typ}) 전체 질량",             NASA_SMALL_BODY, NASA_SMALL_BODY_URL),
        node(f"L7-sb-{sid}-radius",         f"{kr} 반경",          rad,   "km",  f"{kr} 체적 평균 반경",                 NASA_SMALL_BODY, NASA_SMALL_BODY_URL),
    ]

print(f"[3] 소행성대/카이퍼벨트: {len(small_body_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 4. 혜성 (10노드)
# ──────────────────────────────────────────────────────────────────────────────
# 출처: NASA/JPL Small Body Database
COMETS = [
    ("halley",     "핼리혜성",         75.32,  5.5,   "2P/Encke와 함께 가장 유명한 단주기 혜성"),
    ("hale_bopp",  "핼-밥혜성",        2520.0, 30.0,  "1997년 대혜성, 핵 직경 ~60km"),
    ("churyumov",  "추류모프-게라시멘코 혜성", 6.443, 2.0,  "로제타 탐사 대상, 오리 모양 핵"),
    ("encke",      "엔케혜성",         3.298,  2.4,   "최단 공전주기 단주기 혜성"),
    ("tempel1",    "템펠-1 혜성",      5.516,  3.0,   "딥임팩트 충돌 실험 대상"),
]
# 속성: orbital_period_yr, nucleus_radius_km

comet_nodes = []
for (sid, kr, orb, rad, det) in COMETS:
    comet_nodes += [
        node(f"L7-comet-{sid}-orbital_period", f"{kr} 공전주기",  orb, "년",  det, NASA_COMET, NASA_COMET_URL),
        node(f"L7-comet-{sid}-nucleus_radius", f"{kr} 핵 반경",   rad, "km",  f"{kr} 혜성핵 추정 반경", NASA_COMET, NASA_COMET_URL),
    ]

print(f"[4] 혜성: {len(comet_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 5. 태양 (20노드)
# ──────────────────────────────────────────────────────────────────────────────
sun_raw = [
    # (prop, kr_name, val, unit, detail, source, url)
    ("mass",             "태양 질량",             1.989e30,    "kg",      "태양 전체 질량",                         NASA_SUN, NASA_SUN_URL),
    ("radius",           "태양 반경",             695700.0,    "km",      "광구 반경",                              NASA_SUN, NASA_SUN_URL),
    ("luminosity",       "태양 광도",             3.828e26,    "W",       "태양 전체 복사 출력 (IAU 2015 채용값)",   NASA_SUN, NASA_SUN_URL),
    ("surface_temp",     "광구 온도",             5778.0,      "K",       "태양 광구 유효 온도",                    NASA_SUN, NASA_SUN_URL),
    ("core_temp",        "핵 온도",               1.57e7,      "K",       "태양 중심핵 추정 온도",                  NASA_SUN, NASA_SUN_URL),
    ("rotation_eq",      "적도 자전주기",          25.05,       "일",      "적도 기준 항성 자전주기 (차등 자전)",    NASA_SUN, NASA_SUN_URL),
    ("rotation_pole",    "극 자전주기",            34.4,        "일",      "극 기준 항성 자전주기",                  NASA_SUN, NASA_SUN_URL),
    ("age",              "태양 나이",             4.603e9,     "년",      "방사성 동위원소 연대 측정",               NASA_SUN, NASA_SUN_URL),
    ("mean_density",     "태양 평균밀도",          1408.0,      "kg/m³",   "태양 전체 평균밀도",                    NASA_SUN, NASA_SUN_URL),
    ("surface_gravity",  "표면 중력",             274.0,       "m/s²",    "광구 표면 중력 가속도",                  NASA_SUN, NASA_SUN_URL),
    ("escape_velocity",  "탈출속도",              617.7,       "km/s",    "광구 표면 탈출속도",                     NASA_SUN, NASA_SUN_URL),
    ("absolute_mag",     "절대등급",              4.83,        "mag",     "태양 절대등급 (V밴드)",                  NASA_SUN, NASA_SUN_URL),
    ("spectral_class",   "분광형 코드",            2.0,         "G형=2",   "G2V (황색 왜성, G형=2는 편의상 2)",      NASA_SUN, NASA_SUN_URL),
    ("corona_temp",      "코로나 온도",           1.0e6,       "K",       "코로나 평균 온도 (~100만 K)",            NASA_SUN, NASA_SUN_URL),
    ("solar_wind_speed", "태양풍 속도 (평균)",     450.0,       "km/s",    "지구 궤도에서 측정한 평균 태양풍 속도",  NASA_SUN, NASA_SUN_URL),
    ("magnetic_field",   "광구 자기장 (평균)",     1.0,         "mT",      "광구 평균 자기장 약 1 mT (10 G)",        NASA_SUN, NASA_SUN_URL),
    ("hydrogen_fraction","수소 질량 분율",         0.7346,      "",        "태양 수소 질량 분율 (분광/태양모형)",    NASA_SUN, NASA_SUN_URL),
    ("helium_fraction",  "헬륨 질량 분율",        0.2483,      "",        "태양 헬륨 질량 분율",                    NASA_SUN, NASA_SUN_URL),
    ("oblateness",       "편평도",                9.0e-6,      "",        "태양 편평도 (거의 완벽한 구)",            NASA_SUN, NASA_SUN_URL),
    ("angular_diameter", "시직경 (지구에서)",     1919.3,      "arcsec",  "지구 평균거리에서 측정한 태양 시직경",   NASA_SUN, NASA_SUN_URL),
]

sun_nodes = []
for (prop, kr, val, unit, det, src, url) in sun_raw:
    sun_nodes.append(node(f"L7-sun-{prop}", kr, val, unit, det, src, url))

print(f"[5] 태양: {len(sun_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 6. 외계행성 (20노드)
# ──────────────────────────────────────────────────────────────────────────────
# 출처: NASA Exoplanet Archive, ESA Gaia, 각 발견 논문
EXOPLANETS = [
    # (id, kr, host_star, mass_mjup, radius_rjup, period_day, sma_au, discovery)
    ("proxima_b",    "프록시마 b",     "프록시마 켄타우리", 1.07, None,  11.184, 0.0485, "2016 Anglada-Escudé+"),
    ("trappist1_b",  "트라피스트-1b",  "TRAPPIST-1",       0.00359, 0.1011, 1.5109, 0.01154, "2017 Gillon+"),
    ("trappist1_c",  "트라피스트-1c",  "TRAPPIST-1",       0.00302, 0.1055, 2.4218, 0.01580, "2017 Gillon+"),
    ("trappist1_d",  "트라피스트-1d",  "TRAPPIST-1",       0.000777,0.0784, 4.0497, 0.02228, "2017 Gillon+"),
    ("trappist1_e",  "트라피스트-1e",  "TRAPPIST-1",       0.00209, 0.0920, 6.1002, 0.02928, "2017 Gillon+"),
    ("trappist1_f",  "트라피스트-1f",  "TRAPPIST-1",       0.00338, 0.1045, 9.2067, 0.03853, "2017 Gillon+"),
    ("trappist1_g",  "트라피스트-1g",  "TRAPPIST-1",       0.00404, 0.1127,12.3530, 0.04683, "2017 Gillon+"),
    ("trappist1_h",  "트라피스트-1h",  "TRAPPIST-1",       0.000926,0.0755,18.7672, 0.06189, "2017 Gillon+"),
    ("kepler452b",   "케플러-452b",    "케플러-452",        None,    0.190, 384.84, 1.046,   "2015 Jenkins+"),
    ("55cnc_e",      "55 Cancri e",    "55 Cancri",         0.0267, 0.189, 0.7365, 0.01544, "2004 McArthur+"),
]

exoplanet_nodes = []
for (sid, kr, host, mass, rad, period, sma, disc) in EXOPLANETS:
    exoplanet_nodes.append(node(
        id_=f"L7-exo-{sid}-period",
        claim=f"{kr} 공전주기",
        measured=period,
        unit="일",
        detail=f"모성: {host}, 발견: {disc}",
        source=NASA_EXOPLANET,
        source_url=NASA_EXOPLANET_URL,
    ))
    exoplanet_nodes.append(node(
        id_=f"L7-exo-{sid}-sma",
        claim=f"{kr} 공전 긴반지름",
        measured=sma,
        unit="AU",
        detail=f"모성: {host}",
        source=NASA_EXOPLANET,
        source_url=NASA_EXOPLANET_URL,
    ))

print(f"[6] 외계행성: {len(exoplanet_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 7. 항성 분류 (O/B/A/F/G/K/M × 4속성 + 2 대표별 = 30노드)
# ──────────────────────────────────────────────────────────────────────────────
# 출처: ESA Hipparcos, SIMBAD, Allen's Astrophysical Quantities

STELLAR_CLASSES = [
    # (class_id, cls_kr, temp_k_min, temp_k_max, luminosity_solar_min, mass_solar_min, lifetime_gyr)
    ("O", "O형 청색 초거성",  30000, 60000, 30000.0,  20.0,  0.003),
    ("B", "B형 청백색 거성",  10000, 30000, 25.0,     2.5,   0.1),
    ("A", "A형 흰색 주계열성", 7500, 10000, 5.0,      1.75,  2.0),
    ("F", "F형 황백색 주계열성",6000, 7500,  1.5,      1.2,   4.0),
    ("G", "G형 황색 주계열성", 5200, 6000,  0.6,      0.9,  10.0),
    ("K", "K형 주황색 주계열성",3700, 5200,  0.08,     0.7,  20.0),
    ("M", "M형 적색 왜성",    2400, 3700,  0.001,    0.2, 100.0),
]

stellar_nodes = []
for (cls, kr, t_min, t_max, lum_min, mass_min, lifetime) in STELLAR_CLASSES:
    stellar_nodes += [
        node(f"L7-star-class{cls}-temp_min",  f"{kr} 최저 온도",          t_min,    "K",      f"{kr} 유효 표면온도 하한",   SIMBAD, SIMBAD_URL),
        node(f"L7-star-class{cls}-temp_max",  f"{kr} 최고 온도",          t_max,    "K",      f"{kr} 유효 표면온도 상한",   SIMBAD, SIMBAD_URL),
        node(f"L7-star-class{cls}-luminosity",f"{kr} 광도 (태양=1)",      lum_min,  "L☉",     f"{kr} 전형 광도 (태양 광도 대비 최솟값)", SIMBAD, SIMBAD_URL),
        node(f"L7-star-class{cls}-lifetime",  f"{kr} 주계열 수명",        lifetime, "Gyr",    f"{kr} 전형 주계열 수명",     ESA_HIP, ESA_HIP_URL),
    ]

# 대표별 2개 (시리우스, 베텔게우스)
stellar_nodes += [
    node("L7-star-sirius-distance",   "시리우스 거리",       8.611,    "광년",  "시리우스 A (알파 카니스 마요리스), HIP 32349", ESA_HIP, ESA_HIP_URL),
    node("L7-star-sirius-luminosity", "시리우스 광도",       25.4,     "L☉",    "시리우스 A 전체 광도 (태양 대비)",             SIMBAD,  SIMBAD_URL),
    node("L7-star-betelgeuse-distance","베텔게우스 거리",     700.0,    "광년",  "알파 오리오니스, 불확도 ±200 광년",            ESA_HIP, ESA_HIP_URL),
    node("L7-star-betelgeuse-radius", "베텔게우스 반경",     764.0,    "R☉",    "태양 반경 대비 (Dolan+2016)",                  SIMBAD,  SIMBAD_URL),
]

print(f"[7] 항성 분류: {len(stellar_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 8. 성단 (20노드)
# ──────────────────────────────────────────────────────────────────────────────
# 출처: SIMBAD, Messier/NGC Catalogue, ESA Hipparcos

CLUSTERS = [
    # (id, kr, dist_ly, age_myr, n_stars, type_label)
    ("pleiades",  "플레이아데스",  444.0,    115.0,   3000,    "산개성단 M45"),
    ("hyades",    "히아데스",      153.0,    625.0,   400,     "가장 가까운 산개성단"),
    ("m13",       "M13 헤라클레스",25100.0,  11400.0, 300000,  "북천 최대 구상성단"),
    ("omega_cen", "오메가 켄타우리",17090.0, 11500.0, 10000000,"가장 큰 구상성단 NGC 5139"),
    ("m22",       "M22",           10400.0,  12000.0, 70000,   "궁수자리 구상성단"),
]

cluster_nodes = []
for (cid, kr, dist, age, nstars, typ) in CLUSTERS:
    cluster_nodes += [
        node(f"L7-cluster-{cid}-distance", f"{kr} 거리",      dist,   "광년", f"{kr} ({typ}) 지구 거리",           MESSIER, MESSIER_URL),
        node(f"L7-cluster-{cid}-age",      f"{kr} 나이",       age,    "Myr",  f"{kr} 성단 나이 (등시선 맞춤)",      SIMBAD,  SIMBAD_URL),
        node(f"L7-cluster-{cid}-nstars",   f"{kr} 별 수",      nstars, "개",   f"{kr} 구성원 별 추정 수",            MESSIER, MESSIER_URL),
        node(f"L7-cluster-{cid}-type",     f"{kr} 분류",       1,      "구상=1/산개=0", f"구상성단=1, 산개성단=0. {typ}", MESSIER, MESSIER_URL),
    ]

print(f"[8] 성단: {len(cluster_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 9. 블랙홀 (20노드)
# ──────────────────────────────────────────────────────────────────────────────
# 출처: EHT 2019/2022, Ghez+2008, Gravity Collaboration 2018/2022

BH_SOURCE_SGRA = "GRAVITY Collaboration 2022 / EHT"
BH_URL_SGRA = "https://www.eso.org/public/news/eso2208/"
BH_SOURCE_M87 = "Event Horizon Telescope Collaboration 2019"
BH_URL_M87 = "https://eventhorizontelescope.org/press-release-april-10-2019-astronomers-capture-first-image-black-hole"

bh_nodes = [
    # 궁수자리 A* (은하 중심)
    node("L7-bh-sgrA-mass",          "궁수자리 A* 질량",         4.297e6,  "M☉",  "GRAVITY 2022 기반 적외선 궤도 측정",            BH_SOURCE_SGRA, BH_URL_SGRA),
    node("L7-bh-sgrA-distance",      "궁수자리 A* 거리",         26673.0,  "광년","은하 중심까지 거리 (8.178 kpc, GRAVITY 2022)",   BH_SOURCE_SGRA, BH_URL_SGRA),
    node("L7-bh-sgrA-schwarzschild", "궁수자리 A* 슈바르츠실트 반경",12.6e6, "km", "Rs = 2GM/c² ≈ 12.6×10⁶ km",                   BH_SOURCE_SGRA, BH_URL_SGRA),
    node("L7-bh-sgrA-spin",          "궁수자리 A* 스핀 파라미터",0.5,      "무차원", "a = 0~1 (EHT 2022 이미지 분석, 중간값)",      EHT, EHT_URL),
    node("L7-bh-sgrA-hawking_temp",  "궁수자리 A* 호킹 온도",    1.4e-17,  "K",   "T = ℏc³/(8πGMk_B), 실측 불가능하나 이론값",    EHT, EHT_URL),
    # M87* (처녀자리 은하 중심)
    node("L7-bh-m87-mass",           "M87* 질량",                6.5e9,    "M☉",  "EHT 2019 최초 BH 직접 이미지 측정",             BH_SOURCE_M87, BH_URL_M87),
    node("L7-bh-m87-distance",       "M87* 거리",                53.49e6,  "광년","처녀자리 은하단 M87 중심 (16.4 Mpc)",            BH_SOURCE_M87, BH_URL_M87),
    node("L7-bh-m87-schwarzschild",  "M87* 슈바르츠실트 반경",   1.92e10,  "km",  "Rs ≈ 1.92×10¹⁰ km (EHT 2019)",                 BH_SOURCE_M87, BH_URL_M87),
    node("L7-bh-m87-shadow_diameter","M87* 그림자 시직경",        42.0,     "μas", "EHT 이미지 측정값 42±3 μas",                    BH_SOURCE_M87, BH_URL_M87),
    node("L7-bh-m87-jet_speed",      "M87 제트 겉보기 속도",     6.3,      "c",   "초광속 겉보기 운동 (상대론적 빔 효과)",         EHT, EHT_URL),
    # 항성 질량 블랙홀
    node("L7-bh-cygx1-mass",         "시그너스 X-1 질량",        21.2,     "M☉",  "X선 쌍성 시스템 (Miller-Jones+2021)",           SIMBAD, SIMBAD_URL),
    node("L7-bh-cygx1-distance",     "시그너스 X-1 거리",        7230.0,   "광년","Miller-Jones+2021 VLBI 시차 측정",              SIMBAD, SIMBAD_URL),
    node("L7-bh-gw150914-mass1",     "GW150914 병합 전 BH1 질량",35.6,     "M☉",  "LIGO 2015 중력파 첫 검출 (Abbott+2016)",        EHT, "https://doi.org/10.1103/PhysRevLett.116.061102"),
    node("L7-bh-gw150914-mass2",     "GW150914 병합 전 BH2 질량",30.6,     "M☉",  "LIGO 2015 중력파 첫 검출",                      EHT, "https://doi.org/10.1103/PhysRevLett.116.061102"),
    node("L7-bh-gw150914-merged",    "GW150914 병합 후 BH 질량", 63.1,     "M☉",  "3.0M☉ 에너지 중력파 방출",                      EHT, "https://doi.org/10.1103/PhysRevLett.116.061102"),
    node("L7-bh-gw150914-distance",  "GW150914 거리",            1.3e9,    "광년","LIGO 광도거리 ~410 Mpc",                         EHT, "https://doi.org/10.1103/PhysRevLett.116.061102"),
    # 이론값
    node("L7-bh-tov-limit",          "TOV 한계 (최대 중성자별 질량)", 3.0,  "M☉",  "Tolman-Oppenheimer-Volkoff 상한, 초과 시 BH",  EHT, EHT_URL),
    node("L7-bh-chandrasekhar",      "찬드라세카르 한계",         1.44,     "M☉",  "백색왜성 최대 질량 (전자 축퇴압 한계)",         SIMBAD, SIMBAD_URL),
    node("L7-bh-isco-factor",        "ISCO 반경 계수 (슈바르츠실트)", 6.0,  "Rs",  "비회전 BH의 최내 안정 원궤도 = 6 Rs = 3 Rs",   EHT, EHT_URL, n6_expr="n", grade="EXACT", causal="CAUSAL"),
    node("L7-bh-photon-sphere",      "광자구 반경 계수",          3.0,      "Rs",  "비회전 BH의 광자 구 반경 = 3/2 Rs (1.5 Rs)",   EHT, EHT_URL),
]

print(f"[9] 블랙홀: {len(bh_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 10. 성운 (20노드)
# ──────────────────────────────────────────────────────────────────────────────
# 출처: NASA/Hubble, SIMBAD, Chandra X-ray, ESO

NEBULAE = [
    # (id, kr, dist_ly, size_ly, type_code, type_kr, detail_src, detail_url)
    ("orion",    "오리온 성운 M42",     1344,  24,   "HII",  "발광 성운", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("crab",     "게 성운 M1",         6523,  11,   "SNR",  "초신성 잔해 (1054년 폭발)", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("ring",     "고리 성운 M57",      2300,  1.0,  "PN",   "행성상 성운", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("eagle",    "독수리 성운 M16",    7000,  70,   "HII",  "창조의 기둥 포함", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("cat_eye",  "고양이눈 성운 NGC 6543", 3300, 0.2, "PN", "행성상 성운, 복잡한 구조", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("lagoon",   "라군 성운 M8",       4100,  140,  "HII",  "궁수자리 활성 성형 영역", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("helix",    "나선 성운 NGC 7293",  650,   2.87, "PN",   "지구에서 가장 가까운 행성상 성운", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("rosette",  "장미 성운 NGC 2244",  5200,  130,  "HII",  "일각수자리 활성 성형 영역", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("pillars",  "창조의 기둥 (M16 내부)", 7000, 4,  "HII",  "독수리 성운 내부 가스 기둥", NASA_HUBBLE, NASA_HUBBLE_URL),
    ("eta_car",  "에타 카리나 성운",   7500,  300,  "HII",  "NGC 3372, 가장 밝은 발광 성운", NASA_HUBBLE, NASA_HUBBLE_URL),
]

nebula_nodes = []
for (nid, kr, dist, size, typ, typ_kr, src, url) in NEBULAE:
    nebula_nodes += [
        node(f"L7-nebula-{nid}-distance", f"{kr} 거리",     dist, "광년", f"{typ_kr} {kr}",    src, url),
        node(f"L7-nebula-{nid}-size",     f"{kr} 크기",     size, "광년", f"{kr} 시선방향 최대 지름 추정", src, url),
    ]

print(f"[10] 성운: {len(nebula_nodes)} 노드")


# ──────────────────────────────────────────────────────────────────────────────
# 전체 집계
# ──────────────────────────────────────────────────────────────────────────────
all_new_nodes = (
    solar_system_nodes +
    moon_nodes +
    small_body_nodes +
    comet_nodes +
    sun_nodes +
    exoplanet_nodes +
    stellar_nodes +
    cluster_nodes +
    bh_nodes +
    nebula_nodes
)

print(f"\n=== 합계 ===")
print(f"전체 신규 노드: {len(all_new_nodes)}")

# 중복 ID 체크
ids = [n["id"] for n in all_new_nodes]
dupes = [x for x in ids if ids.count(x) > 1]
if dupes:
    print(f"[경고] 중복 ID: {set(dupes)}")
else:
    print("[OK] 중복 ID 없음")

# ──────────────────────────────────────────────────────────────────────────────
# JSON 병합 + 저장
# ──────────────────────────────────────────────────────────────────────────────
MAP_PATH = "/Users/ghost/Dev/nexus/shared/reality_map.json"

# 쓰기 직전 재로드
with open(MAP_PATH) as f:
    data = json.load(f)

existing_ids = {n["id"] for n in data["nodes"] if "id" in n}
new_added = [n for n in all_new_nodes if n["id"] not in existing_ids]
skipped = len(all_new_nodes) - len(new_added)

data["nodes"].extend(new_added)

# _meta 업데이트
meta = data["_meta"]
old_count = meta.get("node_count", len(data["nodes"]) - len(new_added))
meta["node_count"] = len(data["nodes"])
meta["version"] = "8.5"
meta["date"] = str(date.today())

if "L7_celestial" not in meta["levels"]:
    meta["levels"].append("L7_celestial")

if "changelog" not in meta:
    meta["changelog"] = []
meta["changelog"].append({
    "version": "8.5",
    "date": str(date.today()),
    "change": "L7_celestial 신설 — 태양계/위성/소행성/혜성/태양/외계행성/항성분류/성단/블랙홀/성운",
    "added": len(new_added),
    "skipped_duplicates": skipped,
    "before": old_count,
    "after": len(data["nodes"]),
    "sources": [
        "NASA Planetary Fact Sheet",
        "NASA/JPL Solar System Dynamics",
        "NASA Small Body Database",
        "NASA Exoplanet Archive",
        "NASA Sun Fact Sheet",
        "NASA/Hubble Space Telescope",
        "ESA Hipparcos Catalogue",
        "Event Horizon Telescope Collaboration",
        "SIMBAD Astronomical Database",
        "GRAVITY Collaboration 2022",
        "LIGO Scientific Collaboration 2016",
        "Messier Catalogue / NGC",
    ],
})

data["version"] = "8.5"

with open(MAP_PATH, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n[완료] 저장: {MAP_PATH}")
print(f"  추가: {len(new_added)} 노드")
print(f"  건너뜀 (중복): {skipped}")
print(f"  전체 노드: {len(data['nodes'])}")
print(f"  버전: 8.5")
