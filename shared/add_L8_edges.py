#!/usr/bin/env python3
"""
L8_galactic 고아 노드 엣지 추가 — 모든 127개 연결
"""
import json
from pathlib import Path

PATH = Path("/Users/ghost/Dev/nexus/shared/reality_map.json")

with open(PATH, "r") as f:
    data = json.load(f)

existing_edge_keys = set()
for e in data.get("edges", []):
    existing_edge_keys.add((e.get("from"), e.get("to")))

new_edges = [
    # ── A. 우리은하 구조 내부 연결 ──
    ("L8-mw-thickness-kly", "L8-mw-diameter-kly", "원반 두께 vs 지름: 비율 1:100"),
    ("L8-mw-disk-mass-Msun", "L8-mw-total-mass-Msun", "원반 질량 ⊂ 전체 질량"),
    ("L8-mw-halo-radius-kly", "L8-mw-diameter-kly", "헤일로 반경 >> 원반 지름"),
    ("L8-mw-halo-radius-kly", "L8-mw-dark-matter-fraction", "헤일로 반경 → 암흑물질 지배"),
    ("L8-mw-rotation-period-myr", "L8-mw-solar-velocity-kms", "공전 속도 × 주기 = 궤도 둘레"),
    ("L8-mw-solar-velocity-kms", "L8-mw-gc-distance-kly", "속도 + 거리 → 공전 주기"),
    ("L8-mw-globular-clusters", "L8-mw-halo-radius-kly", "구상성단 대부분 헤일로에 분포"),
    ("L8-mw-ism-hydrogen-fraction", "L8-mw-sfr-Msun-yr", "수소 가스 → 별 생성 연료"),
    ("L8-mw-metallicity-gradient", "L8-mw-gc-distance-kly", "반경 거리 → 금속성 기울기"),
    ("L8-mw-satellite-count", "L8-mw-halo-radius-kly", "위성은하 헤일로 내 분포"),
    ("L8-mw-age-gyr", "L8-mw-stellar-count", "나이 × 별 생성률 → 별 누적"),
    ("L8-mw-bulge-mass-Msun", "L8-mw-disk-mass-Msun", "팽대부 + 원반 = 바리온 질량"),

    # ── B. 로컬 그룹 내부 연결 ──
    ("L8-lg-member-count", "L8-lg-diameter-mpc", "은하 수 + 지름 → 그룹 밀도"),
    ("L8-lg-diameter-mpc", "L8-m31-distance-mly", "로컬 그룹 지름 = 2 × MW-M31 거리"),
    ("L8-m31-diameter-kly", "L8-m31-mass-Msun", "M31 크기 + 질량"),
    ("L8-m31-bh-mass-Msun", "L8-m31-mass-Msun", "M31 BH ⊂ M31 전체 질량"),
    ("L8-m31-type", "L8-m31-diameter-kly", "M31 SA(s)b 형태 → 크기"),
    ("L8-m33-distance-mly", "L8-lg-member-count", "M33 로컬 그룹 3위"),
    ("L8-m33-mass-Msun", "L8-m33-distance-mly", "M33 질량 + 거리"),
    ("L8-m33-type", "L8-m33-mass-Msun", "M33 Scd 형태 → 작은 질량"),
    ("L8-lmc-diameter-kly", "L8-lmc-distance-kly", "LMC 크기 + 거리"),
    ("L8-sgr-dwarf-distance-kly", "L8-mw-satellite-count", "궁수자리 왜소 → 위성은하 목록"),
    ("L8-fornax-dwarf-distance-kly", "L8-mw-satellite-count", "포르낙스 왜소 → 위성은하"),
    ("L8-sculptor-dwarf-distance-kly", "L8-mw-satellite-count", "조각가 왜소 → 위성은하"),
    ("L8-ic10-distance-mly", "L8-lg-member-count", "IC 10 로컬 그룹 구성원"),
    ("L8-ngc147-distance-mly", "L8-m31-distance-mly", "NGC 147 M31 위성"),
    ("L8-ngc185-distance-mly", "L8-m31-distance-mly", "NGC 185 M31 위성"),
    ("L8-ngc205-distance-mly", "L8-m31-distance-mly", "M110 M31 위성"),
    ("L8-ic1613-distance-mly", "L8-lg-member-count", "IC 1613 로컬 그룹"),
    ("L8-wolf-lundmark-distance-mly", "L8-lg-member-count", "WLM 로컬 그룹 주변부"),
    ("L8-tucana-distance-kly", "L8-lg-member-count", "투카나 로컬 그룹 가장자리"),
    ("L8-andromeda-i-distance-kly", "L8-m31-distance-mly", "Andromeda I M31 위성"),
    ("L8-phoenix-dwarf-distance-kly", "L8-lg-member-count", "피닉스 왜소 로컬 그룹"),
    ("L8-milkomeda-mass-Msun", "L8-m31-merger-time-gyr", "병합 → 밀코메다 생성"),

    # ── C. 주요 은하 내부 연결 ──
    ("L8-m87-distance-mly", "L8-virgo-cluster-distance-mly", "M87 = 처녀자리 은하단 중심"),
    ("L8-m87-mass-Msun", "L8-m87-bh-mass-Msun", "M87 전체 질량 포함 BH"),
    ("L8-m87-type", "L8-m87-mass-Msun", "M87 E0p 형태 → 거대 질량"),
    ("L8-ngc5128-distance-mly", "L8-ngc5128-bh-mass-Msun", "Cen A 거리 + BH 질량"),
    ("L8-m81-type", "L8-m81-distance-mly", "M81 형태 + 거리"),
    ("L8-m82-distance-mly", "L8-m82-sfr-Msun-yr", "M82 거리 + 별 생성률"),
    ("L8-m82-distance-mly", "L8-m81-distance-mly", "M81-M82 같은 그룹"),
    ("L8-ngc1275-distance-mly", "L8-ngc1275-bh-mass-Msun", "페르세우스 A 거리 + BH"),
    ("L8-ngc1275-distance-mly", "L8-perseus-cluster-distance-mly", "NGC 1275 = 페르세우스 은하단 중심"),
    ("L8-ngc4889-distance-mly", "L8-ngc4889-bh-mass-Msun", "NGC 4889 거리 + BH"),
    ("L8-ngc4889-distance-mly", "L8-coma-cluster-distance-mly", "NGC 4889 코마 은하단"),
    ("L8-m104-distance-mly", "L8-m104-bh-mass-Msun", "솜브레로 거리 + BH"),
    ("L8-gnz11-redshift", "L8-gnz11-luminosity-Lsun", "GN-z11 고적색편이 + 광도"),
    ("L8-gnz11-redshift", "L8-universe-age-gyr", "GN-z11 z=11 → 우주 나이 430 Myr 시점"),
    ("L8-arp220-distance-mly", "L8-type-ulirg-example", "Arp 220 = ULIRG 원형"),
    ("L8-ngc4038-distance-mly", "L8-type-Irr-II-example", "안테나 은하 = 병합 Irr II"),
    ("L8-ngc4993-distance-mly", "L8-ngc5128-distance-mly", "같은 남반구 은하 영역"),
    ("L8-hoags-object-distance-mly", "L8-type-ring-example", "호그 천체 = 고리 은하"),
    ("L8-ngc1052df2-distance-mly", "L8-type-dwarf-elliptical-example", "암흑물질 결핍 왜소 타원"),
    ("L8-stephans-quintet-distance-mly", "L8-ngc1300-distance-mly", "특수 은하 그룹"),
    ("L8-m51-distance-mly", "L8-type-Sc-example", "M51 Sbc 나선"),
    ("L8-ngc6744-distance-mly", "L8-mw-type", "NGC 6744 우리은하 유사 SBbc"),
    ("L8-ic342-distance-mly", "L8-mw-diameter-kly", "IC 342 우리은하 유사 크기"),
    ("L8-ngc5907-distance-mly", "L8-mw-halo-radius-kly", "NGC 5907 위성 흡수 = 헤일로 성장"),
    ("L8-ngc253-distance-mly", "L8-type-starburst-example", "NGC 253 스타버스트"),
    ("L8-ngc4261-bh-mass-Msun", "L8-m87-bh-mass-Msun", "FR I 전파 은하 BH 비교"),
    ("L8-ton618-bh-mass-Msun", "L8-ngc4889-bh-mass-Msun", "초질량 BH 비교"),
    ("L8-ngc1569-distance-mly", "L8-type-starburst-example", "NGC 1569 사후 스타버스트"),

    # ── D. 은하단 내부 연결 ──
    ("L8-virgo-cluster-galaxy-count", "L8-virgo-cluster-mass-Msun", "처녀자리 은하 수 + 질량"),
    ("L8-virgo-cluster-radius-mly", "L8-virgo-cluster-mass-Msun", "은하단 반경 + 질량"),
    ("L8-virgo-sz-effect", "L8-virgo-cluster-mass-Msun", "SZ 효과 세기 ∝ 은하단 질량"),
    ("L8-coma-cluster-distance-mly", "L8-coma-cluster-mass-Msun", "코마 은하단 거리 + 질량"),
    ("L8-coma-cluster-galaxy-count", "L8-coma-cluster-mass-Msun", "코마 은하 수 + 질량"),
    ("L8-coma-icm-temperature-keV", "L8-coma-cluster-mass-Msun", "ICM 온도 → 비리얼 질량 추정"),
    ("L8-coma-icm-temperature-keV", "L8-coma-cluster-velocity-dispersion-kms", "ICM 온도 ↔ 속도 분산 (비리얼)"),
    ("L8-perseus-cluster-distance-mly", "L8-perseus-cluster-mass-Msun", "페르세우스 거리 + 질량"),
    ("L8-perseus-cluster-sound-waves", "L8-perseus-cluster-mass-Msun", "AGN 음파 → ICM 가열"),
    ("L8-fornax-cluster-distance-mly", "L8-fornax-cluster-mass-Msun", "포르낙스 거리 + 질량"),
    ("L8-el-gordo-distance-gly", "L8-el-gordo-mass-Msun", "엘 고르도 거리 + 질량"),
    ("L8-el-gordo-mass-Msun", "L8-bullet-cluster-mass-Msun", "거대 충돌 은하단 질량 비교"),
    ("L8-abell1689-distance-mly", "L8-abell-catalog-count", "Abell 카탈로그 구성원"),
    ("L8-abell2029-distance-mly", "L8-abell-catalog-count", "Abell 카탈로그 구성원"),
    ("L8-abell370-distance-mly", "L8-abell-catalog-count", "Abell 카탈로그 구성원"),
    ("L8-macsj0717-distance-gly", "L8-el-gordo-distance-gly", "고적색편이 거대 은하단 비교"),
    ("L8-planck-sz-cluster-count", "L8-abell-catalog-count", "SZ vs 광학 은하단 카탈로그"),
    ("L8-cool-core-cluster-fraction", "L8-perseus-cluster-sound-waves", "쿨 코어 + AGN 피드백"),
    ("L8-cluster-mass-function-slope", "L8-sigma8", "질량 함수 기울기 ↔ σ8 제약"),
    ("L8-virgo-infall-velocity-kms", "L8-cmb-dipole-velocity-kms", "인폴 속도 ⊂ CMB 쌍극자 운동"),

    # ── E. 대규모 구조 내부 연결 ──
    ("L8-great-attractor-distance-mly", "L8-shapley-supercluster-distance-mly", "그레이트 어트랙터 뒤에 셰플리"),
    ("L8-shapley-supercluster-distance-mly", "L8-shapley-supercluster-mass-Msun", "셰플리 거리 + 질량"),
    ("L8-shapley-supercluster-mass-Msun", "L8-laniakea-mass-Msun", "셰플리 → 라니아케아 인접"),
    ("L8-cfa2-great-wall-length-mly", "L8-sloan-great-wall-length-mly", "그레이트 월 크기 비교"),
    ("L8-sloan-great-wall-length-mly", "L8-hercules-corona-wall-length-gly", "우주 벽 스케일 증가"),
    ("L8-bootes-void-diameter-mly", "L8-void-fraction-universe", "목동 보이드 = 대표 빈 공간"),
    ("L8-cold-spot-void-diameter-mly", "L8-bootes-void-diameter-mly", "대형 보이드 비교"),
    ("L8-pisces-cetus-filament-length-gly", "L8-laniakea-diameter-mly", "필라멘트 > 초은하단"),
    ("L8-cosmic-web-filament-density", "L8-void-fraction-universe", "필라멘트 밀도 vs 보이드 부피"),
    ("L8-cmb-dipole-velocity-kms", "L8-great-attractor-distance-mly", "CMB 쌍극자 → 그레이트 어트랙터 방향"),
    ("L8-particle-horizon-gly", "L8-observable-universe-radius-gly", "입자 지평선 = 관측 가능 반경"),
    ("L8-hubble-volume-gly3", "L8-particle-horizon-gly", "부피 = (4/3)π × 반경³"),
    ("L8-total-galaxy-count", "L8-laniakea-galaxy-count", "총 은하 수 >> 라니아케아"),

    # ── F. 우주상수 내부 연결 ──
    ("L8-omega-radiation", "L8-matter-radiation-equality-z", "복사 밀도 → 등밀도 시점"),
    ("L8-matter-radiation-equality-z", "L8-recombination-redshift", "등밀도 z >> 재결합 z"),
    ("L8-recombination-time-kyr", "L8-recombination-redshift", "재결합 시점 kyr + z"),
    ("L8-reionization-redshift", "L8-recombination-redshift", "재결합 → 암흑 시대 → 재이온화"),
    ("L8-optical-depth-tau", "L8-reionization-redshift", "광학 깊이 τ → 재이온화 z"),
    ("L8-spectral-index-ns", "L8-inflation-e-folding", "n_s < 1 → 인플레이션 이탈"),
    ("L8-grav-wave-background", "L8-inflation-e-folding", "텐서 r 상한 → 인플레이션 에너지 제약"),
    ("L8-dark-energy-w", "L8-omega-lambda", "w=-1 검증 → Ω_Λ 우주상수 지지"),
    ("L8-lambda-cosmological-constant", "L8-omega-lambda", "Λ값 ↔ Ω_Λ 파라미터 환산"),
    ("L8-critical-density-kg-m3", "L8-H0-planck-km-s-mpc", "ρ_c = 3H0²/8πG"),
    ("L8-critical-density-kg-m3", "L8-omega-matter", "Ω_m = ρ_m/ρ_c"),
    ("L8-sigma8", "L8-matter-radiation-equality-z", "σ8 ↔ 구조 성장 이력"),
    ("L8-baryon-asymmetry", "L8-bbn-helium-fraction", "η → BBN Y_p 계산"),
    ("L8-baryon-asymmetry", "L8-omega-baryon", "바리온 비대칭 → Ω_b"),
    ("L8-cmb-peak-temp-fluctuation-K", "L8-cmb-temperature-K", "요동 진폭 ΔT/T ∝ T_CMB"),
    ("L8-cmb-photon-number-density", "L8-baryon-asymmetry", "η = n_b/n_γ"),
    ("L8-neutrino-background-temp-K", "L8-cmb-temperature-K", "T_ν 관계"),
    ("L8-dark-energy-acceleration-z", "L8-lambda-cosmological-constant", "가속 → Λ 양수"),

    # ── G. 은하 유형 내부 연결 ──
    ("L8-type-E7-example", "L8-type-E0-example", "E0~E7 타원 연속 분류"),
    ("L8-type-S0-example", "L8-type-E7-example", "S0 = E7과 분류 경계"),
    ("L8-type-Sa-example", "L8-type-S0-example", "Sa → S0 원반 은하 계열"),
    ("L8-type-Sb-example", "L8-type-Sa-example", "Sa→Sb 나선 느슨해짐"),
    ("L8-type-Sc-example", "L8-type-Sb-example", "Sb→Sc 나선 더 느슨"),
    ("L8-type-Sd-example", "L8-type-Sc-example", "Sc→Sd 핵 더 작아짐"),
    ("L8-type-SBa-example", "L8-type-Sa-example", "막대 여부 분기 SBa vs Sa"),
    ("L8-type-SBc-example", "L8-type-SBb-example", "SBb→SBc 더 느슨한 막대 나선"),
    ("L8-type-SBc-example", "L8-mw-type", "우리은하 SBbc ∈ SBc 계열"),
    ("L8-type-Irr-II-example", "L8-type-Irr-I-example", "Irr I vs II 불규칙 구분"),
    ("L8-type-blazar-example", "L8-type-seyfert1-example", "블레이자 ⊂ AGN 통합 모형"),
    ("L8-type-seyfert2-example", "L8-type-seyfert1-example", "Sy1/Sy2 통합 AGN 모형"),
    ("L8-type-quasar-example", "L8-type-seyfert1-example", "QSO = 고광도 Sy1 계열"),
    ("L8-type-ulirg-example", "L8-type-starburst-example", "ULIRG = 극단 스타버스트"),
    ("L8-type-dwarf-elliptical-example", "L8-type-dsph-example", "dE vs dSph 왜소 은하"),
    ("L8-type-blue-compact-example", "L8-type-Irr-I-example", "BCD ~ 불규칙 왜소"),
    ("L8-type-ring-example", "L8-type-polar-ring-example", "고리 유형 비교"),
    ("L8-type-cD-example", "L8-type-E0-example", "cD ⊃ E형 초거대 타원"),
    ("L8-hubble-sequence-revision", "L8-type-E0-example", "허블 분류 체계 기원"),
    ("L8-type-fraction-spiral", "L8-type-fraction-elliptical", "나선 + 타원 비율 합산"),
    ("L8-morphology-density-relation", "L8-type-fraction-elliptical", "밀도 → 타원 비율 증가"),
    ("L8-green-valley-fraction", "L8-red-sequence-blue-cloud", "녹색 계곡 ⊂ 색-등급 분포"),
    ("L8-type-lenticular-fraction", "L8-type-S0-example", "S0 은하 비율"),

    # ── 레벨 간 연결 (L7 celestial → L8 galactic) ──
    ("L8-mw-diameter-kly", "L8-laniakea-diameter-mly", "은하 지름 << 초은하단"),
    ("L8-universe-age-gyr", "L8-mw-age-gyr", "우주 나이 > 은하 나이"),
    ("L8-total-stars-observable-universe", "L8-mw-stellar-count", "우주 총 별 >> 은하 별"),
]

added = 0
skipped = 0
for frm, to, rel in new_edges:
    key = (frm, to)
    if key not in existing_edge_keys:
        data["edges"].append({"from": frm, "to": to, "relation": rel})
        existing_edge_keys.add(key)
        added += 1
    else:
        skipped += 1

# 메타 업데이트
data["_meta"]["edge_count"] = len(data["edges"])

with open(PATH, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"엣지 추가: {added} / 건너뜀: {skipped}")
print(f"총 엣지: {len(data['edges'])}")

# 고아 노드 재확인
l8_ids = {n["id"] for n in data["nodes"] if n.get("level") == "L8_galactic"}
edge_ids2 = set()
for e in data["edges"]:
    edge_ids2.add(e.get("from",""))
    edge_ids2.add(e.get("to",""))
orphan = l8_ids - edge_ids2
print(f"L8 고아 노드 잔여: {len(orphan)}")
if orphan:
    for o in sorted(orphan):
        print(" ", o)
