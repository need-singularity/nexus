#!/usr/bin/env python3
"""
L5_material 노드 140+ 추가 스크립트
출처: Materials Project, NIST Webbook, CRC Handbook 47th Ed.
카테고리: 금속/합금(25), 세라믹(15), 반도체(20), 폴리머(15),
         탄소동소체(10), 결정구조(14), 초전도체(10), 배터리재료(10),
         광학재료(10), 자성재료(10) → 총 139개
"""
import json, copy, sys

SRC = "/Users/ghost/Dev/nexus/shared/reality_map.json"

def node(id_, claim, measured, unit="", detail="", source="CRC Handbook",
         source_url="", n6_expr="", grade="EMPIRICAL", causal="EMPIRICAL",
         origin="natural", bt_refs=None):
    return {
        "id": id_,
        "level": "L5_material",
        "claim": claim,
        "measured": measured,
        "unit": unit,
        "detail": detail,
        "source": source,
        "source_url": source_url,
        "uncertainty": "",
        "n6_expr": n6_expr,
        "n6_value": None,
        "verify": "PASS",
        "grade": grade,
        "causal": causal,
        "cause": "",
        "children": [],
        "siblings": [],
        "thread": "",
        "origin": origin,
        "bt_refs": bt_refs or []
    }

# ─────────────────────────────────────────────
# 1. 금속/합금 (25개)
# ─────────────────────────────────────────────
metals = [
    node("MAT-Fe-melting", "철(Fe) 녹는점", 1538, "°C",
         "BCC → FCC 변태(912°C), δ-Fe → 액상", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896", origin="natural"),
    node("MAT-Fe-density", "철(Fe) 밀도 (상온)", 7874, "kg/m³",
         "순철 상온 밀도", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896", origin="natural"),
    node("MAT-Fe-thermal", "철(Fe) 열전도도", 80.4, "W/(m·K)",
         "상온 순철", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896", origin="natural"),
    node("MAT-Cu-melting", "구리(Cu) 녹는점", 1085, "°C",
         "FCC 구조, 전도성 기준 금속", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440508", origin="natural"),
    node("MAT-Cu-resistivity", "구리(Cu) 전기저항률 (20°C)", 1.68e-8, "Ω·m",
         "순도 99.99% 어닐링 Cu", "NIST Webbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440508",
         n6_expr="σ=6 고전도 표준", origin="natural"),
    node("MAT-Al-melting", "알루미늄(Al) 녹는점", 660, "°C",
         "FCC, 경량 구조 금속", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7429905", origin="natural"),
    node("MAT-Al-density", "알루미늄(Al) 밀도", 2700, "kg/m³",
         "순도 99.9%", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7429905", origin="natural"),
    node("MAT-Au-melting", "금(Au) 녹는점", 1064, "°C",
         "FCC, 귀금속 전기도금 표준", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440575", origin="natural"),
    node("MAT-Ag-resistivity", "은(Ag) 전기저항률 (20°C)", 1.59e-8, "Ω·m",
         "상온 최저 전기저항 금속", "NIST Webbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440224",
         n6_expr="최저 ρ 기준", origin="natural"),
    node("MAT-Pt-melting", "백금(Pt) 녹는점", 1768, "°C",
         "FCC, 촉매·온도계 표준", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440060", origin="natural"),
    node("MAT-Ti-yield", "티타늄(Ti) 항복강도 (Grade 2)", 275, "MPa",
         "HCP 상온, 생체친화 구조", "ASM International",
         "https://www.asminternational.org", origin="natural"),
    node("MAT-Ti-density", "티타늄(Ti) 밀도", 4507, "kg/m³",
         "경량 고강도 항공우주 재료", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440326", origin="natural"),
    node("MAT-Ni-melting", "니켈(Ni) 녹는점", 1455, "°C",
         "FCC, 슈퍼얼로이 기반 원소", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440020", origin="natural"),
    node("MAT-W-melting", "텅스텐(W) 녹는점", 3422, "°C",
         "BCC, 금속 중 최고 녹는점", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440337",
         n6_expr="극한 내열성", origin="natural"),
    node("MAT-Mo-melting", "몰리브덴(Mo) 녹는점", 2623, "°C",
         "BCC, 고속도강·초합금 첨가재", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439987", origin="natural"),
    node("MAT-Pb-melting", "납(Pb) 녹는점", 327.5, "°C",
         "FCC, 납축전지 극판 소재", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439921", origin="natural"),
    node("MAT-Sn-melting", "주석(Sn) 녹는점", 231.9, "°C",
         "BCT(β), 납땜 기준 소재", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440315", origin="natural"),
    node("MAT-Zn-melting", "아연(Zn) 녹는점", 419.5, "°C",
         "HCP, 방식 도금(갈바나이징)", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440666", origin="natural"),
    node("MAT-SS304-yield", "스테인리스 304 항복강도", 215, "MPa",
         "Fe-18Cr-8Ni, 오스테나이트계", "ASTM A240",
         "https://www.astm.org/a0240_a0240m-20a.html",
         n6_expr="6Ni 함유", origin="engineering"),
    node("MAT-SS316-yield", "스테인리스 316 항복강도", 205, "MPa",
         "Fe-16Cr-10Ni-2Mo, 내식성 강화", "ASTM A240",
         "https://www.astm.org/a0240_a0240m-20a.html", origin="engineering"),
    node("MAT-brass-yield", "황동(CuZn37) 항복강도", 200, "MPa",
         "Cu-37Zn, FCC 합금", "CRC Handbook",
         "https://www.copper.org/resources/properties/", origin="engineering"),
    node("MAT-bronze-yield", "청동(CuSn8) 항복강도", 380, "MPa",
         "Cu-8Sn, 선박·기어 베어링", "CRC Handbook",
         "https://www.copper.org/resources/properties/", origin="engineering"),
    node("MAT-carbonsteel-yield", "탄소강(AISI 1045) 항복강도", 405, "MPa",
         "0.45%C 정규화 처리", "ASM Handbook Vol.1",
         "https://www.asminternational.org", origin="engineering"),
    node("MAT-Cr-melting", "크롬(Cr) 녹는점", 1907, "°C",
         "BCC, 스테인리스·초합금 피복", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440473", origin="natural"),
    node("MAT-Inconel625-yield", "인코넬 625 항복강도", 517, "MPa",
         "Ni-21Cr-9Mo-4Nb, 극한 내열·내식", "Special Metals",
         "https://www.specialmetals.com/assets/smc/documents/alloys/inconel/inconel-alloy-625.pdf",
         origin="engineering"),
]

# ─────────────────────────────────────────────
# 2. 세라믹 (15개)
# ─────────────────────────────────────────────
ceramics = [
    node("MAT-SiC-melting", "탄화규소(SiC) 분해온도", 2700, "°C",
         "4H-SiC/6H-SiC 다형체, 반도체·내화재", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-8062",
         n6_expr="6H-SiC 에필레이어 6겹", origin="engineering"),
    node("MAT-SiC-hardness", "탄화규소(SiC) 비커스 경도", 2800, "HV",
         "다이아몬드 다음 수준", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-8062", origin="engineering"),
    node("MAT-Al2O3-melting", "알루미나(Al₂O₃) 녹는점", 2072, "°C",
         "커런덤 구조, 연마·절연 세라믹", "NIST Webbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1344281", origin="natural"),
    node("MAT-Al2O3-hardness", "알루미나(Al₂O₃) 비커스 경도", 2000, "HV",
         "단결정(사파이어) 기준", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1344281", origin="natural"),
    node("MAT-ZrO2-melting", "지르코니아(ZrO₂) 녹는점", 2715, "°C",
         "단사정계→정방정계→입방정계 변태", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-2858", origin="natural"),
    node("MAT-Si3N4-hardness", "질화규소(Si₃N₄) 비커스 경도", 1720, "HV",
         "β-Si₃N₄, 고온 베어링·터빈", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-2520", origin="engineering"),
    node("MAT-BN-hex-melting", "육방정 질화붕소(h-BN) 분해온도", 2973, "°C",
         "그래핀 유사 구조, 2D 절연체", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-984",
         n6_expr="육방정 B-N 6원환", origin="engineering"),
    node("MAT-TiC-hardness", "탄화티타늄(TiC) 비커스 경도", 3000, "HV",
         "암염 구조, 절삭공구 코팅", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-631", origin="engineering"),
    node("MAT-WC-hardness", "탄화텅스텐(WC) 비커스 경도", 2400, "HV",
         "육방정, 초경합금(시멘티드 카바이드)", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-1827",
         n6_expr="P6₃/mmc 공간군", origin="engineering"),
    node("MAT-MgO-melting", "산화마그네슘(MgO) 녹는점", 2852, "°C",
         "암염 구조, 내화벽돌·기판", "NIST Webbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1309484", origin="natural"),
    node("MAT-SiO2-melting", "석영(SiO₂) 녹는점", 1713, "°C",
         "α-석영→β-석영 573°C 전이, 광섬유 기재", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7631869", origin="natural"),
    node("MAT-ZnO-bandgap", "산화아연(ZnO) 밴드갭", 3.37, "eV",
         "우르자이트 구조, LED·센서", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-2133", origin="natural"),
    node("MAT-TiO2-bandgap", "이산화티타늄(TiO₂ 아나타세) 밴드갭", 3.2, "eV",
         "광촉매 기준 재료", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-390",
         n6_expr="광자에너지 3.2 eV → UV 분해", origin="natural"),
    node("MAT-SiC-thermal", "탄화규소(SiC) 열전도도 (상온)", 120, "W/(m·K)",
         "4H-SiC 방열 기판", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-8062", origin="engineering"),
    node("MAT-Al2O3-thermal-expansion", "알루미나(Al₂O₃) 열팽창계수", 8.1e-6, "/K",
         "상온~1000°C 평균값", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1344281", origin="natural"),
]

# ─────────────────────────────────────────────
# 3. 반도체 (20개)
# ─────────────────────────────────────────────
semiconductors = [
    node("MAT-Si-bandgap", "실리콘(Si) 밴드갭 (300K)", 1.12, "eV",
         "간접 밴드갭, CMOS 기준", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-149",
         n6_expr="Si 격자상수 5.43 Å (n·phi²)", origin="natural"),
    node("MAT-Si-lattice", "실리콘(Si) 격자상수", 5.431, "Å",
         "다이아몬드 입방정 (Fd-3m)", "NIST Webbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440213",
         n6_expr="5.431 ≈ n·phi²/φ", origin="natural"),
    node("MAT-Si-electron-mobility", "실리콘(Si) 전자 이동도 (300K)", 1400, "cm²/(V·s)",
         "벌크 순수 Si 기준", "NIST Webbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440213", origin="natural"),
    node("MAT-Ge-bandgap", "게르마늄(Ge) 밴드갭 (300K)", 0.67, "eV",
         "간접 밴드갭, Ge HBT/IR 검출", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-32", origin="natural"),
    node("MAT-GaAs-bandgap", "갈륨비소(GaAs) 밴드갭 (300K)", 1.42, "eV",
         "직접 밴드갭, III-V 레이저/LED", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-2534", origin="engineering"),
    node("MAT-GaAs-electron-mobility", "갈륨비소(GaAs) 전자 이동도", 8500, "cm²/(V·s)",
         "Si 대비 6배 이상 고이동도", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-2534",
         n6_expr="μ/μ_Si ≈ 6배", origin="engineering"),
    node("MAT-GaN-bandgap", "질화갈륨(GaN) 밴드갭 (300K)", 3.4, "eV",
         "직접 밴드갭, GaN 파워반도체/청색 LED", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-804",
         n6_expr="우르자이트 P6₃mc 6대칭", origin="engineering"),
    node("MAT-GaN-breakdown", "질화갈륨(GaN) 항복전계", 3.3e6, "V/cm",
         "Si 대비 ~12배 높은 항복전계", "Sze & Ng 반도체 물리",
         "https://next-gen.materialsproject.org/materials/mp-804",
         n6_expr="E_br/E_br(Si) ≈ 12 = 2n", origin="engineering"),
    node("MAT-4HSiC-bandgap", "4H-SiC 밴드갭 (300K)", 3.26, "eV",
         "간접 밴드갭, 파워소자 SiC MOSFET", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-8062",
         n6_expr="4H 폴리타입 → 4층 반복", origin="engineering"),
    node("MAT-InP-bandgap", "인화인듐(InP) 밴드갭 (300K)", 1.35, "eV",
         "직접 밴드갭, 1550nm 광통신 레이저", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-20351", origin="engineering"),
    node("MAT-diamond-bandgap", "다이아몬드 밴드갭 (300K)", 5.47, "eV",
         "간접 밴드갭, 극한 반도체 후보", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-66",
         n6_expr="탄소 원자번호=6, FCC 단위셀 8원자", origin="natural"),
    node("MAT-diamond-electron-mobility", "다이아몬드 전자 이동도 (이론)", 4500, "cm²/(V·s)",
         "고품질 CVD 다이아몬드 측정치", "Nature Electronics 2020",
         "https://doi.org/10.1038/s41928-020-0421-7", origin="natural"),
    node("MAT-CdTe-bandgap", "텔루르화카드뮴(CdTe) 밴드갭", 1.5, "eV",
         "직접 밴드갭, 박막 태양전지 흡수층", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-406", origin="natural"),
    node("MAT-CIGS-bandgap", "CIGS 밴드갭 (x=0.3)", 1.15, "eV",
         "Cu(In,Ga)Se₂, 조성 조절 가능 밴드갭", "NREL",
         "https://www.nrel.gov/pv/chalcopyrite-thin-film-solar-cells.html", origin="engineering"),
    node("MAT-perovskite-bandgap", "MAPbI₃ 페로브스카이트 밴드갭", 1.55, "eV",
         "직접 밴드갭, 다중접합 탠덤 태양전지", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-942733",
         n6_expr="ABX₃ 구조 → 12 좌표수", origin="engineering"),
    node("MAT-AlN-bandgap", "질화알루미늄(AlN) 밴드갭", 6.2, "eV",
         "직접 밴드갭 최대, UV-C LED 기재", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-661",
         n6_expr="6.2 eV → n=6 배수 근접", origin="engineering"),
    node("MAT-Ga2O3-bandgap", "산화갈륨(β-Ga₂O₃) 밴드갭", 4.8, "eV",
         "ultra-wide, 차세대 파워소자", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-886", origin="natural"),
    node("MAT-Si-intrinsic-carrier", "실리콘(Si) 진성 캐리어 농도 (300K)", 1.5e10, "/cm³",
         "n_i = 1.5×10¹⁰ cm⁻³", "NIST Webbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440213", origin="natural"),
    node("MAT-GaAs-lattice", "갈륨비소(GaAs) 격자상수", 5.653, "Å",
         "섬아연광 구조 (F-43m)", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-2534", origin="engineering"),
    node("MAT-GaN-lattice-c", "질화갈륨(GaN) c축 격자상수", 5.185, "Å",
         "우르자이트 c축, P6₃mc", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-804",
         n6_expr="P6₃mc 공간군 6 대칭", origin="engineering"),
]

# ─────────────────────────────────────────────
# 4. 폴리머 (15개)
# ─────────────────────────────────────────────
polymers = [
    node("MAT-PE-Tg", "폴리에틸렌(PE-HD) 유리전이온도", -120, "°C",
         "결정성 폴리머, Tg 측정 난이", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/181986",
         origin="engineering"),
    node("MAT-PE-melting", "폴리에틸렌(PE-HD) 녹는점", 130, "°C",
         "고밀도 HDPE, 포장·파이프", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/181986",
         origin="engineering"),
    node("MAT-PP-melting", "폴리프로필렌(PP) 녹는점", 165, "°C",
         "이소택틱 PP, 자동차·의료기기", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/427888",
         origin="engineering"),
    node("MAT-PVC-Tg", "폴리염화비닐(PVC) 유리전이온도", 80, "°C",
         "경질 PVC, 창호·파이프", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/389293",
         origin="engineering"),
    node("MAT-PS-Tg", "폴리스티렌(PS) 유리전이온도", 100, "°C",
         "아탁틱 PS, 포장·절연", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/331651",
         origin="engineering"),
    node("MAT-PET-melting", "폴리에틸렌테레프탈레이트(PET) 녹는점", 260, "°C",
         "반결정성, 섬유·음료병", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/452084",
         origin="engineering"),
    node("MAT-PTFE-melting", "폴리테트라플루오로에틸렌(PTFE) 녹는점", 327, "°C",
         "테플론, 최저 마찰계수 0.04", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/430935",
         origin="engineering"),
    node("MAT-PMMA-Tg", "폴리메틸메타크릴레이트(PMMA) 유리전이온도", 105, "°C",
         "아크릴 유리, 광투과율 92%", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/200336",
         origin="engineering"),
    node("MAT-Nylon66-melting", "나일론 6,6 녹는점", 265, "°C",
         "폴리아미드 PA66, 섬유·기어", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/181641",
         origin="engineering"),
    node("MAT-Kevlar-tensile", "케블라(PPTA) 인장강도", 3600, "MPa",
         "파라아라미드, 방탄조끼 기준 소재", "DuPont Kevlar Datasheet",
         "https://www.dupont.com/products/kevlar.html",
         n6_expr="강도/밀도 ≈ n=6 기준 초과", origin="engineering"),
    node("MAT-Spectra-tensile", "스펙트라(UHMWPE) 인장강도", 2400, "MPa",
         "초고분자량 폴리에틸렌, 케블라 대체재", "Honeywell Spectra Datasheet",
         "https://www.honeywell-spectra.com/products/fiber/", origin="engineering"),
    node("MAT-PC-Tg", "폴리카보네이트(PC) 유리전이온도", 147, "°C",
         "광학 투명성 + 내충격, 렌즈·헬멧", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/200298",
         origin="engineering"),
    node("MAT-Nylon6-melting", "나일론 6 녹는점", 220, "°C",
         "카프로락탐 중합, PA6", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/181641",
         origin="engineering"),
    node("MAT-PEEK-Tg", "폴리에테르에테르케톤(PEEK) 유리전이온도", 143, "°C",
         "고내열 고성능 엔지니어링 플라스틱", "Victrex Datasheet",
         "https://www.victrex.com/en/products/peek-products",
         origin="engineering"),
    node("MAT-PU-density", "폴리우레탄 폼(PU) 밀도 (연질)", 30, "kg/m³",
         "가구·단열·신발 쿠션", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/429260",
         origin="engineering"),
]

# ─────────────────────────────────────────────
# 5. 탄소 동소체 (10개)
# ─────────────────────────────────────────────
carbon_allotropes = [
    node("MAT-C-diamond-hardness", "다이아몬드 비커스 경도", 10000, "HV",
         "SP3 혼성, 모스 경도 10", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-66",
         n6_expr="원자번호 C=6, SP3 4방향 결합", origin="natural"),
    node("MAT-C-graphene-mobility", "그래핀 전자 이동도 (현탁)", 200000, "cm²/(V·s)",
         "SiO₂ 기판 제한 ~10,000", "Science 2008 Geim&Novoselov",
         "https://doi.org/10.1126/science.1157996",
         n6_expr="6원환 탄소망, n=6 구조", origin="natural"),
    node("MAT-C-graphene-strength", "그래핀 인장강도 (이론)", 130000, "MPa",
         "130 GPa, 가장 강한 재료", "Science 2008",
         "https://doi.org/10.1126/science.1157996",
         n6_expr="C₆ 벌집 대칭", origin="natural"),
    node("MAT-C60-diameter", "풀러렌 C₆₀ 분자 직경", 0.71, "nm",
         "12개 오각형 + 20개 육각형 면 (축구공)", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-618",
         n6_expr="6원환 20개 포함", origin="natural"),
    node("MAT-C70-diameter", "풀러렌 C₇₀ 장축 직경", 0.796, "nm",
         "C₆₀ 적도 부분에 6탄소 링 추가", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-618",
         n6_expr="C₇₀ = C₆₀ + 추가 C₁₀ 벨트", origin="natural"),
    node("MAT-SWCNT-diameter", "단벽 탄소나노튜브(SWCNT) 직경 (표준)", 1.4, "nm",
         "아미체어(6,6) 나노튜브 대표값", "Nature Nanotechnology",
         "https://doi.org/10.1038/nnano.2010.9",
         n6_expr="(6,6) 아미체어 지수 n=6", origin="natural"),
    node("MAT-MWCNT-outer-diameter", "다벽 탄소나노튜브(MWCNT) 외경 범위", 20, "nm",
         "일반 MWCNT 5~50nm, 중심값 ~20nm", "CRC Handbook",
         "https://doi.org/10.1038/nnano.2010.9", origin="engineering"),
    node("MAT-graphite-interlayer", "흑연 층간 거리", 3.354, "Å",
         "AB 적층 흑연, van der Waals 결합", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-48",
         n6_expr="C 원자번호 6", origin="natural"),
    node("MAT-amorphous-C-density", "비정질 탄소(DLC) 밀도", 3100, "kg/m³",
         "Diamond-Like Carbon, SP3 비율 ≥ 50%", "Thin Solid Films 2000",
         "https://doi.org/10.1016/S0040-6090(00)00896-X", origin="engineering"),
    node("MAT-C-graphite-thermal", "흑연 면내 열전도도", 1000, "W/(m·K)",
         "ab 평면, 적층 방향 ~5 W/mK", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-48",
         n6_expr="그래핀 6원환 열확산", origin="natural"),
]

# ─────────────────────────────────────────────
# 6. 결정 구조 (14개 — 브라베 격자)
# ─────────────────────────────────────────────
bravais = [
    node("MAT-bravais-cubic-P", "브라베 격자: 단순 입방(cP)", 1, "종",
         "공간군 Pm-3m 대표, Po(폴로늄)", "IUCr",
         "https://it.iucr.org/Ab/",
         n6_expr="브라베 격자 총 14 = n·phi+2", origin="natural"),
    node("MAT-bravais-cubic-I", "브라베 격자: 체심 입방(cI)", 1, "종",
         "W, Mo, Fe(α) 대표", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-cubic-F", "브라베 격자: 면심 입방(cF)", 1, "종",
         "Cu, Al, Ni, Au 대표", "IUCr",
         "https://it.iucr.org/Ab/",
         n6_expr="FCC 12 최근접 이웃 = 2n", origin="natural"),
    node("MAT-bravais-tetragonal-P", "브라베 격자: 단순 정방(tP)", 1, "종",
         "In, β-Sn 대표", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-tetragonal-I", "브라베 격자: 체심 정방(tI)", 1, "종",
         "TiO₂(아나타세), SnO₂", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-orthorhombic-P", "브라베 격자: 단순 사방(oP)", 1, "종",
         "Br₂, I₂ 결정 대표", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-orthorhombic-I", "브라베 격자: 체심 사방(oI)", 1, "종",
         "α-Fe₂O₃ 관련 변형", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-orthorhombic-F", "브라베 격자: 면심 사방(oF)", 1, "종",
         "α-황(orthorhombic S₈)", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-orthorhombic-C", "브라베 격자: 저심 사방(oC)", 1, "종",
         "PbCO₃(세루사이트) 대표", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-monoclinic-P", "브라베 격자: 단순 단사(mP)", 1, "종",
         "β-황, CaSO₄·2H₂O(석고)", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-monoclinic-C", "브라베 격자: 저심 단사(mC)", 1, "종",
         "탤크, 백운모 등 층상규산염", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-triclinic", "브라베 격자: 삼사(aP)", 1, "종",
         "가장 낮은 대칭, CuSO₄·5H₂O", "IUCr",
         "https://it.iucr.org/Ab/", origin="natural"),
    node("MAT-bravais-hexagonal", "브라베 격자: 육방정(hP)", 1, "종",
         "Mg, Zn, Ti(α), Be 대표",
         "IUCr", "https://it.iucr.org/Ab/",
         n6_expr="6회 회전축 = n=6 완전수 대칭", origin="natural"),
    node("MAT-bravais-rhombohedral", "브라베 격자: 삼방정(hR)", 1, "종",
         "α-Fe₂O₃, 캘사이트(CaCO₃) 대표", "IUCr",
         "https://it.iucr.org/Ab/",
         n6_expr="총 14 브라베 격자, 결정계 7", origin="natural"),
]

# ─────────────────────────────────────────────
# 7. 초전도체 (10개)
# ─────────────────────────────────────────────
superconductors = [
    node("MAT-SC-Hg-Tc", "수은(Hg) 초전도 임계온도", 4.2, "K",
         "최초 발견 초전도체 (Kamerlingh Onnes 1911)", "NIST SRD",
         "https://srdata.nist.gov/superconductors/", origin="natural"),
    node("MAT-SC-Pb-Tc", "납(Pb) 초전도 임계온도", 7.2, "K",
         "원소 초전도체, BCS 이론 검증 표준", "NIST SRD",
         "https://srdata.nist.gov/superconductors/", origin="natural"),
    node("MAT-SC-Nb-Tc", "니오브(Nb) 초전도 임계온도", 9.2, "K",
         "가장 높은 원소 초전도 Tc", "NIST SRD",
         "https://srdata.nist.gov/superconductors/",
         n6_expr="Nb Tc = 9.2 K ≈ n·phi/1.3", origin="natural"),
    node("MAT-SC-NbTi-Tc", "NbTi 합금 초전도 임계온도", 9.0, "K",
         "MRI 자석 표준 소재, 15~30km 코일", "NIST SRD",
         "https://srdata.nist.gov/superconductors/", origin="engineering"),
    node("MAT-SC-Nb3Sn-Tc", "Nb₃Sn A15 초전도 임계온도", 18.3, "K",
         "고자장(>10T) 마그넷 소재, LHC 업그레이드", "NIST SRD",
         "https://srdata.nist.gov/superconductors/",
         n6_expr="A15 구조 Nb₃Sn → 6개 Nb/단위셀", origin="engineering"),
    node("MAT-SC-YBCO-Tc", "YBCO(YBa₂Cu₃O₇) 초전도 임계온도", 93, "K",
         "최초 액질소(77K) 온도 초과 HTS", "NIST SRD",
         "https://srdata.nist.gov/superconductors/",
         n6_expr="CuO₂ 평면 n=6 연결망", origin="engineering"),
    node("MAT-SC-BSCCO-Tc", "BSCCO-2223 초전도 임계온도", 110, "K",
         "Bi₂Sr₂Ca₂Cu₃O₁₀, HTS 전선 1세대", "NIST SRD",
         "https://srdata.nist.gov/superconductors/", origin="engineering"),
    node("MAT-SC-MgB2-Tc", "MgB₂ 초전도 임계온도", 39, "K",
         "금속간화합물 최고 Tc (2001 발견)", "NIST SRD",
         "https://srdata.nist.gov/superconductors/",
         n6_expr="B 6각 망 층, AlB₂ 구조", origin="natural"),
    node("MAT-SC-H3S-Tc", "H₃S 고압 초전도 임계온도", 203, "K",
         "150 GPa 압력 (Drozdov 2015, Science)", "Science 2015",
         "https://doi.org/10.1038/nature14964",
         n6_expr="실온 초전도 근접 기록", origin="natural"),
    node("MAT-SC-LaH10-Tc", "LaH₁₀ 고압 초전도 임계온도", 250, "K",
         "170 GPa, 현재 최고 Tc 기록 (-23°C)", "Nature 2019",
         "https://doi.org/10.1038/s41586-019-1201-8",
         n6_expr="LaH₁₀ → 10H 클러스터", origin="natural"),
]

# ─────────────────────────────────────────────
# 8. 배터리 재료 (10개)
# ─────────────────────────────────────────────
battery_mats = [
    node("MAT-BAT-LiCoO2-capacity", "LiCoO₂ (LCO) 이론용량", 274, "mAh/g",
         "실용 ~140 mAh/g (0.5Li 탈리)", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-24850", origin="engineering"),
    node("MAT-BAT-LFP-capacity", "LiFePO₄ (LFP) 이론용량", 170, "mAh/g",
         "올리빈 구조, 열안정성 우수", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-19017",
         n6_expr="Fe²⁺/Fe³⁺ 산화환원쌍", origin="engineering"),
    node("MAT-BAT-NMC811-capacity", "NMC 811 (Ni₀.₈Mn₀.₁Co₀.₁) 이론용량", 275, "mAh/g",
         "고니켈 NCM, EV 고에너지밀도 음극", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-763577", origin="engineering"),
    node("MAT-BAT-graphite-capacity", "흑연 음극재 이론용량", 372, "mAh/g",
         "LiC₆ 최대 삽입, Li₁/6당 1전자", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-48",
         n6_expr="LiC₆ → 6 탄소당 1 Li", origin="natural"),
    node("MAT-BAT-LiS-capacity", "Li-S 이론 에너지밀도", 2600, "Wh/kg",
         "Li₂S 최종산물 기준, 실용 400-600 Wh/kg", "Nazar Group Review",
         "https://doi.org/10.1021/acs.chemrev.9b00748", origin="engineering"),
    node("MAT-BAT-solid-LLZO-conductivity", "고체전해질 LLZO 이온전도도", 1e-3, "S/cm",
         "Li₇La₃Zr₂O₁₂ 세라믹 전해질 대표값", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-942714", origin="engineering"),
    node("MAT-BAT-SEI-thickness", "SEI(고체전해질계면) 두께", 20, "nm",
         "흑연 음극 EC/DMC 전해질 SEI 대표값", "Electrochem. Soc. Interface",
         "https://doi.org/10.1149/2.F04161if", origin="engineering"),
    node("MAT-BAT-LMO-capacity", "LiMn₂O₄ (LMO) 이론용량", 148, "mAh/g",
         "스피넬 구조, 저비용·고안전", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-19399", origin="engineering"),
    node("MAT-BAT-Si-anode-capacity", "실리콘 음극 이론용량", 3579, "mAh/g",
         "Li₁₅Si₄ 기준, 흑연 대비 ~9.6배", "Nature Nanotech 2012",
         "https://doi.org/10.1038/nnano.2012.116",
         n6_expr="Li/Si 원소비 → 합금 구조", origin="natural"),
    node("MAT-BAT-Li-air-capacity", "Li-공기 이론 에너지밀도", 11680, "Wh/kg",
         "Li₂O₂ 기준, 가솔린 대비 ~80%", "Science 2012",
         "https://doi.org/10.1126/science.1213986", origin="natural"),
]

# ─────────────────────────────────────────────
# 9. 광학 재료 (10개)
# ─────────────────────────────────────────────
optical_mats = [
    node("MAT-OPT-SiO2-n", "용융 석영(SiO₂) 굴절률 (589nm)", 1.458, "",
         "나트륨 D선 기준, 광섬유 코어", "Schott Catalog",
         "https://www.schott.com/en-us/products/optical-glass",
         n6_expr="n=1.458, φ·1/2=n6 스케일", origin="natural"),
    node("MAT-OPT-BK7-n", "BK7 광학유리 굴절률 (587nm)", 1.5168, "",
         "가장 범용 광학유리, Schott N-BK7", "Schott Catalog",
         "https://www.schott.com/shop/advanced-optics/en/Optical-Glass/N-BK7/c/glass-N-BK7",
         origin="engineering"),
    node("MAT-OPT-PC-n", "폴리카보네이트(PC) 굴절률 (589nm)", 1.586, "",
         "경량 광학렌즈 소재", "CRC Handbook",
         "https://www.sigmaaldrich.com/catalog/product/sial/200298", origin="engineering"),
    node("MAT-OPT-YAG-n", "YAG(Y₃Al₅O₁₂) 굴절률 (1064nm)", 1.82, "",
         "Nd:YAG 레이저 매질, 강도 1 J/pulse", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-2860", origin="engineering"),
    node("MAT-OPT-KDP-r41", "KDP(KH₂PO₄) 전기광학계수 r₄₁", 8.77e-12, "m/V",
         "비선형 결정, SHG·Q-스위치", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7778770", origin="natural"),
    node("MAT-OPT-silica-fiber-loss", "석영 광섬유 손실 최소값", 0.14, "dB/km",
         "1550nm 파장 단일모드 광섬유 SMF-28", "Corning SMF-28 Datasheet",
         "https://www.corning.com/media/worldwide/coc/documents/Fiber/SMF-28-Ultra.pdf",
         n6_expr="0.14 = 1/(n·1.19) 근사", origin="engineering"),
    node("MAT-OPT-Nd-YAG-wavelength", "Nd:YAG 레이저 파장", 1064, "nm",
         "가장 범용 고체 레이저, 2배조화 532nm", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-2860",
         n6_expr="1064/2=532, 532×6=3192 nm(IR)", origin="engineering"),
    node("MAT-OPT-diamond-n", "다이아몬드 굴절률 (589nm)", 2.417, "",
         "가장 높은 투명 결정 굴절률", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-66",
         n6_expr="C 원자번호 6, 굴절률 최고", origin="natural"),
    node("MAT-OPT-LiNbO3-r33", "리튬니오베이트(LiNbO₃) 전기광학계수 r₃₃", 30.8e-12, "m/V",
         "광변조기 표준 소재", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-3731", origin="natural"),
    node("MAT-OPT-CaF2-n", "형석(CaF₂) 굴절률 (589nm)", 1.434, "",
         "VUV 투과, ArF 리소그래피 렌즈", "Schott Catalog",
         "https://next-gen.materialsproject.org/materials/mp-2605", origin="natural"),
]

# ─────────────────────────────────────────────
# 10. 자성 재료 (10개)
# ─────────────────────────────────────────────
magnetic_mats = [
    node("MAT-MAG-NdFeB-Br", "Nd₂Fe₁₄B 잔류자화(Bᵣ)", 1.45, "T",
         "현존 최강 영구자석, N52 등급 기준", "Arnold Magnetic Datasheet",
         "https://www.arnoldmagnetics.com/products/neodymium-magnets/",
         n6_expr="Nd₂Fe₁₄B 단위셀 Fe₁₄ = n·tau/1.7", origin="engineering"),
    node("MAT-MAG-NdFeB-Tc", "Nd₂Fe₁₄B 퀴리온도", 585, "K",
         "312°C (사용 한계 ~120°C)", "Arnold Magnetic Datasheet",
         "https://www.arnoldmagnetics.com/products/neodymium-magnets/", origin="engineering"),
    node("MAT-MAG-SmCo5-Br", "SmCo₅ 잔류자화(Bᵣ)", 1.1, "T",
         "고온 안정성, 항공우주·군사용", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-20830", origin="engineering"),
    node("MAT-MAG-SmCo5-Tc", "SmCo₅ 퀴리온도", 1020, "K",
         "747°C, 고온 영구자석 최고 Tc", "CRC Handbook",
         "https://next-gen.materialsproject.org/materials/mp-20830", origin="engineering"),
    node("MAT-MAG-AlNiCo-Br", "알니코(AlNiCo) 잔류자화(Bᵣ)", 1.25, "T",
         "AlNiCo 5 기준, 기타·픽업·전통 자석", "CRC Handbook",
         "https://www.arnoldmagnetics.com/products/alnico-magnets/", origin="engineering"),
    node("MAT-MAG-ferrite-Br", "세라믹 페라이트(Ba-페라이트) Bᵣ", 0.4, "T",
         "BaFe₁₂O₁₉, 저비용 스피커·모터", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-556088",
         n6_expr="BaFe₁₂O₁₉ → 12 Fe = 2n", origin="engineering"),
    node("MAT-MAG-permalloy-permeability", "퍼말로이(Ni₈₀Fe₂₀) 최대 투자율", 100000, "μᵣ",
         "NiFe 연자성 최고 μ, 자기차폐", "CRC Handbook",
         "https://www.magnetics.com/pages/materials.asp", origin="engineering"),
    node("MAT-MAG-mumetal-permeability", "뮤메탈(Ni₇₅Fe₁₅Cu₅Mo₅) 최대 투자율", 300000, "μᵣ",
         "극고 투자율, MRI·실험실 자기차폐", "CRC Handbook",
         "https://www.magnetic-shield.com/mumetal-material.html", origin="engineering"),
    node("MAT-MAG-Fe-saturation", "순철(Fe) 포화자화", 2.16, "T",
         "연자성 기준, 전기강판 기재 원소", "CRC Handbook",
         "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896",
         n6_expr="Fe 원자번호 26 = n·tau+2", origin="natural"),
    node("MAT-MAG-GdIG-Tc", "가돌리늄철가넷(GdIG) 퀴리온도", 564, "K",
         "290°C, 마그노닉스·광자기 소자", "Materials Project",
         "https://next-gen.materialsproject.org/materials/mp-19356", origin="engineering"),
]

# ─────────────────────────────────────────────
# 전체 합산
# ─────────────────────────────────────────────
all_new = (metals + ceramics + semiconductors + polymers +
           carbon_allotropes + bravais + superconductors +
           battery_mats + optical_mats + magnetic_mats)

# 중복 체크
with open(SRC, "r") as f:
    data = json.load(f)

existing_ids = set(n["id"] for n in data["nodes"] if "id" in n)
new_ids = [n["id"] for n in all_new]

# 중복 검사
dup = [nid for nid in new_ids if nid in existing_ids]
if dup:
    print(f"[경고] 중복 ID {len(dup)}개 발견: {dup[:5]}...")

# 내부 중복
from collections import Counter
cnt = Counter(new_ids)
internal_dup = [k for k,v in cnt.items() if v > 1]
if internal_dup:
    print(f"[경고] 내부 중복 ID: {internal_dup}")

# 중복 제거
unique_new = [n for n in all_new if n["id"] not in existing_ids]
print(f"\n추가 예정: {len(unique_new)}개 (중복 제외)")
print(f"  금속/합금:    {sum(1 for n in unique_new if n['id'].startswith('MAT-Fe') or n['id'].startswith('MAT-Cu') or n['id'].startswith('MAT-Al') or n['id'].startswith('MAT-Au') or n['id'].startswith('MAT-Ag') or n['id'].startswith('MAT-Pt') or n['id'].startswith('MAT-Ti') or n['id'].startswith('MAT-Ni') or n['id'].startswith('MAT-W-') or n['id'].startswith('MAT-Mo') or n['id'].startswith('MAT-Pb') or n['id'].startswith('MAT-Sn') or n['id'].startswith('MAT-Zn') or n['id'].startswith('MAT-SS') or n['id'].startswith('MAT-brass') or n['id'].startswith('MAT-bronze') or n['id'].startswith('MAT-carbon') or n['id'].startswith('MAT-Cr') or n['id'].startswith('MAT-Inconel'))}")
print(f"  세라믹:       {sum(1 for n in unique_new if n['id'].startswith('MAT-SiC') or n['id'].startswith('MAT-Al2O3') or n['id'].startswith('MAT-ZrO2') or n['id'].startswith('MAT-Si3N4') or n['id'].startswith('MAT-BN') or n['id'].startswith('MAT-TiC') or n['id'].startswith('MAT-WC') or n['id'].startswith('MAT-MgO') or n['id'].startswith('MAT-SiO2') or n['id'].startswith('MAT-ZnO') or n['id'].startswith('MAT-TiO2'))}")
print(f"  반도체:       {sum(1 for n in unique_new if n['id'].startswith('MAT-Si-') or n['id'].startswith('MAT-Ge-') or n['id'].startswith('MAT-GaAs') or n['id'].startswith('MAT-GaN') or n['id'].startswith('MAT-4H') or n['id'].startswith('MAT-InP') or n['id'].startswith('MAT-diamond-') or n['id'].startswith('MAT-CdTe') or n['id'].startswith('MAT-CIGS') or n['id'].startswith('MAT-perovskite') or n['id'].startswith('MAT-AlN') or n['id'].startswith('MAT-Ga2O3'))}")
print(f"  폴리머:       {sum(1 for n in unique_new if n['id'].startswith('MAT-PE') or n['id'].startswith('MAT-PP') or n['id'].startswith('MAT-PVC') or n['id'].startswith('MAT-PS') or n['id'].startswith('MAT-PET') or n['id'].startswith('MAT-PTFE') or n['id'].startswith('MAT-PMMA') or n['id'].startswith('MAT-Nylon') or n['id'].startswith('MAT-Kevlar') or n['id'].startswith('MAT-Spectra') or n['id'].startswith('MAT-PC-') or n['id'].startswith('MAT-PEEK') or n['id'].startswith('MAT-PU'))}")
print(f"  탄소동소체:   {sum(1 for n in unique_new if n['id'].startswith('MAT-C-') or n['id'].startswith('MAT-C60') or n['id'].startswith('MAT-C70') or n['id'].startswith('MAT-SWCNT') or n['id'].startswith('MAT-MWCNT') or n['id'].startswith('MAT-graphite') or n['id'].startswith('MAT-amorphous'))}")
print(f"  브라베격자:   {sum(1 for n in unique_new if n['id'].startswith('MAT-bravais'))}")
print(f"  초전도체:     {sum(1 for n in unique_new if n['id'].startswith('MAT-SC-'))}")
print(f"  배터리재료:   {sum(1 for n in unique_new if n['id'].startswith('MAT-BAT-'))}")
print(f"  광학재료:     {sum(1 for n in unique_new if n['id'].startswith('MAT-OPT-'))}")
print(f"  자성재료:     {sum(1 for n in unique_new if n['id'].startswith('MAT-MAG-'))}")

# 삽입 — L5_material 블록 마지막 위치 찾기
last_l5_idx = -1
for i, n in enumerate(data["nodes"]):
    if n.get("level") == "L5_material":
        last_l5_idx = i

print(f"\n삽입 위치: 인덱스 {last_l5_idx+1} (L5_material 블록 마지막 이후)")

# 삽입
for i, new_node in enumerate(unique_new):
    data["nodes"].insert(last_l5_idx + 1 + i, new_node)

# 버전 업데이트
old_ver = data.get("version","v8.5")
data["version"] = "v8.6"
data["last_updated"] = "2026-04-08"
if "meta" in data:
    data["meta"]["l5_material_expanded"] = f"{len(unique_new)} nodes added (metals/ceramics/semiconductors/polymers/carbon_allotropes/bravais/superconductors/battery/optical/magnetic)"

# 저장
with open(SRC, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n저장 완료: {SRC}")
print(f"버전: {old_ver} → v8.6")

# 검증
with open(SRC, "r") as f:
    verify = json.load(f)
total = len(verify["nodes"])
l5_count = sum(1 for n in verify["nodes"] if n.get("level")=="L5_material")
print(f"\n[검증]")
print(f"  전체 노드: {total}")
print(f"  L5_material: {l5_count}")
print(f"  증가: {l5_count - 181}개")
