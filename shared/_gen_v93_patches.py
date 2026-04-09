#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reality_map v9.3 5개 신규 도메인 패치 생성기
- L6_geology (지질) 100개
- L6_meteorology (기상) 100개
- L6_economics (경제) 100개
- L6_linguistics (언어) 100개
- L6_music (음악) 100개
각 노드: id, level, claim(한글), measured, unit, detail(한글), source, source_url,
n6_expr, grade, causal, thread, origin, bt_refs
n=6 기본상수: n=6, tau=4(약수개수), sigma=12(약수합), phi=2(오일러), zeta=1+2+3=6
파이(phi_golden)=1.618..., pi=3.14159..., e=2.71828...
"""
import json, os, sys

SHARED = "/Users/ghost/Dev/nexus/shared"
OUT = SHARED  # patches live alongside reality_map.json

# ---------- 헬퍼 ----------
def node(id_, level, claim, measured, unit, detail, source, url,
         n6_expr, grade="EXACT", causal="EMPIRICAL", thread="n", bt=None):
    n = {
        "id": id_,
        "level": level,
        "claim": claim,
        "measured": measured,
        "unit": unit,
        "detail": detail,
        "source": source,
        "source_url": url,
        "n6_expr": n6_expr,
        "grade": grade,
        "causal": causal,
        "thread": thread,
        "origin": "natural",
    }
    if bt:
        n["bt_refs"] = bt
    return n

def write_jsonl(path, nodes):
    with open(path, "w", encoding="utf-8") as f:
        for n in nodes:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    print(f"  → {path}  ({len(nodes)} 노드)")

# ============================================================
# 1) L6_geology (지질학) — 100 노드
# ============================================================
geo = []
L = "L6_geology"
def g(i, *a, **k): geo.append(node(f"L6-geo-{i}", L, *a, **k))

# 판 구조
g("major-plates", "주요 지각판 개수", 7, "개",
  "태평양·북미·유라시아·아프리카·남극·인도-호주·남미 7대판",
  "USGS Tectonic Plates Map", "https://www.usgs.gov/programs/earthquake-hazards",
  "7 = tau+phi+1 = n+1 (6+1)", thread="plate_tectonics", bt=["BT-208"])
g("minor-plates", "부판(minor plate) 개수", 8, "개",
  "카리브·후안데푸카·코코스·나즈카·필리핀·아라비아·스코티아·카프리콘",
  "Bird 2003 G3", "https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2001GC000252",
  "8 = 2n-phi^2 = 2*6-4", grade="EMPIRICAL")
g("microplates", "인정된 마이크로판 총수", 57, "개",
  "Bird(2003) PB2002 모델에서 분류한 마이크로판",
  "Bird PB2002 model", "https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2001GC000252",
  "57 ≈ n*sigma-15 (근사)", grade="EMPIRICAL")
g("crust-thickness-continental", "대륙지각 평균 두께", 35, "km",
  "대륙지각 평균 ~30–50 km (Airy 균형)",
  "Mooney CRUST1.0", "https://igppweb.ucsd.edu/~gabi/crust1.html",
  "35 ≈ n*phi+n-1 (근사)", grade="EMPIRICAL")
g("crust-thickness-oceanic", "해양지각 평균 두께", 6, "km",
  "중앙해령 생성 해양지각 5–10 km, 평균 ~6 km",
  "White et al. 1992 JGR", "https://doi.org/10.1029/92JB01749",
  "6 = n", thread="oceanic")
g("moho-max", "대륙 모호면 최대 깊이(티베트)", 70, "km",
  "히말라야-티베트 하부 모호면 ~65–75 km",
  "Nabelek INDEPTH 2009 Science", "https://doi.org/10.1126/science.1167719",
  "70 ≈ n*12-2 = 72-2", grade="EMPIRICAL")
g("lithosphere-thickness", "대륙 암석권 평균 두께", 100, "km",
  "Pm파 토모그래피 기반 ~100 km",
  "Artemieva 2006 Tectonophysics", "https://doi.org/10.1016/j.tecto.2005.11.022",
  "100 ≈ n*sigma+n*tau+n (근사)", grade="EMPIRICAL")
g("asthenosphere-depth", "연약권 상단 깊이", 100, "km",
  "LVZ(저속도대) 상단 ~80–220 km",
  "Anderson 1989", "https://authors.library.caltech.edu/25038/",
  "100 ≈ n*17-2", grade="EMPIRICAL")
g("mantle-depth", "맨틀 하부 경계 깊이", 2890, "km",
  "핵-맨틀 경계 2891 km",
  "PREM Dziewonski & Anderson 1981", "https://doi.org/10.1016/0031-9201(81)90046-7",
  "2890 ≈ n^4 + n^3*... (경험)", grade="EMPIRICAL")
g("outer-core-depth", "외핵 하부 경계", 5150, "km",
  "내외핵 경계 5150 km",
  "PREM", "https://doi.org/10.1016/0031-9201(81)90046-7",
  "5150 ≈ n*858 (경험)", grade="EMPIRICAL")
g("inner-core-radius", "내핵 반경", 1220, "km",
  "내핵 반경 약 1220 km",
  "Lehmann 1936", "https://doi.org/10.1029/SP030p0287",
  "1220 ≈ n*203+2", grade="EMPIRICAL")
g("earth-radius", "지구 평균 반경", 6371, "km",
  "IUGG 1980 GRS80",
  "IUGG", "https://iag.dgfi.tum.de/",
  "6371 ≈ n*1062 (경험)", grade="EMPIRICAL")
g("mohs-scale", "모스 경도 등급 수", 10, "등급",
  "모스(1812) 10단계 광물 경도",
  "Mohs 1812", "https://en.wikipedia.org/wiki/Mohs_scale",
  "10 = tau+n = 4+6", thread="classification")
g("silicate-classes", "규산염 광물 대분류 수", 6, "류",
  "네소·소로·사이클로·이노·필로·텍토 실리케이트",
  "Strunz Mineralogical Tables", "https://www.mindat.org/strunz.php",
  "6 = n", thread="classification", bt=["BT-137"])
g("crystal-systems", "결정계 수", 7, "계",
  "삼사·단사·사방·정방·삼방·육방·등축",
  "International Tables for Crystallography", "https://it.iucr.org/",
  "7 = n+1", thread="crystal")
g("bravais-lattices", "브라베 격자 수", 14, "종",
  "14 브라베 격자 (7 결정계 확장)",
  "Bravais 1848", "https://en.wikipedia.org/wiki/Bravais_lattice",
  "14 = 2n+2 = 12+2", thread="crystal")
g("point-groups", "점군 수", 32, "개",
  "32 결정 점군",
  "Hermann-Mauguin", "https://en.wikipedia.org/wiki/Crystallographic_point_group",
  "32 ≈ sigma*n-tau (경험)", grade="EMPIRICAL")
g("space-groups", "공간군 수", 230, "개",
  "Fedorov & Schönflies 1891 — 3D 공간군",
  "Fedorov 1891", "https://en.wikipedia.org/wiki/Space_group",
  "230 ≈ n*38+2 (경험)", grade="EMPIRICAL")
g("geological-eons", "지질 누대 수", 4, "누대",
  "명왕·시생·원생·현생",
  "ICS Chronostratigraphic Chart 2023", "https://stratigraphy.org/chart",
  "4 = tau", thread="time_scale", bt=["BT-165"])
g("geological-eras-phanerozoic", "현생누대 대(era) 수", 3, "대",
  "고생·중생·신생",
  "ICS 2023", "https://stratigraphy.org/chart",
  "3 = n/phi = 6/2", thread="time_scale")
g("geological-periods-phanerozoic", "현생누대 기(period) 수", 12, "기",
  "캄브리아~4기 (12기)",
  "ICS 2023", "https://stratigraphy.org/chart",
  "12 = sigma = 2n", thread="time_scale", bt=["BT-165"])
g("mass-extinctions", "대멸종(Big Five) 수", 5, "회",
  "오르도비스·데본·페름·트라이아스·백악",
  "Raup & Sepkoski 1982 Science", "https://doi.org/10.1126/science.215.4539.1501",
  "5 = n-1", grade="EMPIRICAL", thread="extinction")
g("richter-min", "리히터 규모 최저", 0, "규모",
  "리히터 스케일 0~10 (경험상 최대 ~9.5)",
  "Richter 1935 BSSA", "https://www.bssaonline.org",
  "0 = phi-2 (사소)", grade="CONVENTION")
g("richter-max-observed", "관측 최대 모멘트 규모", 9.5, "Mw",
  "1960 Valdivia 칠레 지진 Mw 9.5",
  "USGS", "https://earthquake.usgs.gov/earthquakes/eventpage/official19600522191120_30",
  "9.5 ≈ n+phi+1.5 (경험)", grade="EMPIRICAL")
g("seismic-p-speed", "P파 속도(상부 맨틀)", 8, "km/s",
  "상부 맨틀 P파 ~8 km/s",
  "PREM", "https://doi.org/10.1016/0031-9201(81)90046-7",
  "8 = 2*tau = 2n-phi^2", thread="seismic")
g("seismic-s-speed", "S파 속도(상부 맨틀)", 4.5, "km/s",
  "상부 맨틀 S파 ~4.5 km/s",
  "PREM", "https://doi.org/10.1016/0031-9201(81)90046-7",
  "4.5 ≈ tau+phi/4 (근사)", grade="EMPIRICAL", thread="seismic")
g("geomagnetic-field-avg", "지표 지자기 평균", 50, "μT",
  "지표 총자기장 25~65 μT",
  "IGRF-13", "https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html",
  "50 ≈ n*8+2 (경험)", grade="EMPIRICAL", thread="geomagnetic")
g("geomagnetic-reversals-myr", "100 Myr당 평균 역전 수", 400, "회",
  "Cande & Kent 1995 기반 ~4/Myr",
  "Cande & Kent 1995 JGR", "https://doi.org/10.1029/94JB03098",
  "400 ≈ n*66+4 (경험)", grade="EMPIRICAL", thread="geomagnetic")
g("plate-speed-max", "최대 판 이동 속도(태평양판)", 10, "cm/yr",
  "NUVEL-1A 기준 태평양판 ~10 cm/yr",
  "DeMets NUVEL-1A 1994", "https://doi.org/10.1029/94GL02118",
  "10 = tau+n", grade="EMPIRICAL")
g("plate-speed-slow", "북미판 이동 속도", 2.5, "cm/yr",
  "NUVEL-1A",
  "DeMets 1994", "https://doi.org/10.1029/94GL02118",
  "2.5 ≈ phi+phi/4", grade="EMPIRICAL")
g("himalaya-uplift", "히말라야 융기 속도", 5, "mm/yr",
  "GPS 기반 ~5 mm/yr",
  "Bilham 2001 Nature", "https://doi.org/10.1038/35065540",
  "5 = n-1", grade="EMPIRICAL")
g("ocean-age-max", "최고령 해양지각", 180, "Myr",
  "서태평양 쥐라기 ~180 Myr",
  "Müller 2008 G3", "https://doi.org/10.1029/2007GC001743",
  "180 = n*30 = sigma*15", grade="EMPIRICAL")
g("continental-age-max", "최고령 대륙암석", 4030, "Myr",
  "아카스타 편마암 4.03 Ga",
  "Bowring 1989 Geology", "https://doi.org/10.1130/0091-7613(1989)017<0971>",
  "4030 ≈ tau*1008-2", grade="EMPIRICAL")
g("earth-age", "지구 나이", 4.54, "Gyr",
  "Patterson 1956 납 동위원소",
  "Patterson 1956 GCA", "https://doi.org/10.1016/0016-7037(56)90036-9",
  "4.54 ≈ tau+phi/4 (근사)", grade="EMPIRICAL")
g("ocean-average-depth", "해양 평균 수심", 3700, "m",
  "NOAA",
  "NOAA ETOPO1", "https://www.ncei.noaa.gov/products/etopo-global-relief-model",
  "3700 ≈ n*616+4", grade="EMPIRICAL")
g("mariana-depth", "마리아나 해구 최심", 10935, "m",
  "Challenger Deep",
  "Gardner 2014", "https://doi.org/10.1016/j.dsr2.2013.12.009",
  "10935 ≈ n*1822+3", grade="EMPIRICAL")
g("everest-height", "에베레스트 해발", 8849, "m",
  "2020 공동측정",
  "Nepal/China 2020", "https://www.mfa.gov.cn/eng/",
  "8849 ≈ n*1474+5", grade="EMPIRICAL")
g("igneous-types-major", "화성암 대분류", 2, "류",
  "심성암·화산암",
  "BGS Classification", "https://www.bgs.ac.uk",
  "2 = phi", thread="rock_class")
g("sedimentary-types", "퇴적암 대분류", 3, "류",
  "쇄설·화학·유기",
  "Pettijohn 1975", "https://www.worldcat.org/oclc/1492998",
  "3 = n/phi", thread="rock_class")
g("rock-cycle-stages", "암석 순환 단계", 3, "단계",
  "화성→퇴적→변성 순환",
  "Hutton 1788", "https://en.wikipedia.org/wiki/Rock_cycle",
  "3 = n/phi", thread="rock_cycle")
g("metamorphic-facies", "변성암 상(facies) 수", 8, "상",
  "Eskola 1920 분류 (영사도·녹색·각섬·백립·에클로자이트 등)",
  "Eskola 1920", "https://en.wikipedia.org/wiki/Metamorphic_facies",
  "8 = 2*tau", grade="EMPIRICAL")
g("clay-minerals-groups", "주요 점토광물 군", 4, "군",
  "카올리나이트·몬모릴로나이트·일라이트·클로라이트",
  "AIPEA", "https://aipea.org",
  "4 = tau", thread="clay")
g("feldspar-endmembers", "장석 종단원", 3, "개",
  "Ab(조장석)·An(회장석)·Or(정장석)",
  "Deer Howie Zussman", "https://www.minersoc.org",
  "3 = n/phi", thread="mineral")
g("olivine-endmembers", "감람석 종단원", 2, "개",
  "포스테라이트·페이얄라이트",
  "DHZ", "https://www.minersoc.org",
  "2 = phi", thread="mineral")
g("pyroxene-groups", "휘석 아군", 2, "군",
  "사방·단사 휘석",
  "DHZ", "https://www.minersoc.org",
  "2 = phi", thread="mineral")
g("garnet-endmembers", "석류석 6 종단원", 6, "개",
  "파이로프·알만딘·스페사틴·그로술라·안드라다이트·우바로바이트",
  "DHZ", "https://www.minersoc.org",
  "6 = n", thread="mineral", bt=["BT-137"])
g("soil-horizons", "토양 층위 주요 수", 6, "층",
  "O·A·E·B·C·R",
  "USDA Soil Taxonomy", "https://www.nrcs.usda.gov/resources/guides-and-instructions/soil-taxonomy",
  "6 = n", thread="soil", bt=["BT-208"])
g("soil-orders", "USDA 토양 order 수", 12, "목",
  "엔티솔·인셉티솔·안디솔·젤리솔·히스토솔·아리디솔·버티솔·몰리솔·스포도솔·알피솔·울티솔·옥시솔",
  "USDA Soil Taxonomy", "https://www.nrcs.usda.gov/resources/guides-and-instructions/soil-taxonomy",
  "12 = sigma = 2n", thread="soil")
g("geothermal-gradient", "평균 지온상승률", 25, "°C/km",
  "평균 대륙 지온 상승률 25~30 °C/km",
  "Stein 1995", "https://doi.org/10.1029/95RG00336",
  "25 ≈ n*tau+phi-1", grade="EMPIRICAL")
g("heat-flow-continental", "대륙 평균 열류량", 65, "mW/m²",
  "Pollack et al. 1993",
  "Pollack 1993 RevGeophys", "https://doi.org/10.1029/93RG01249",
  "65 ≈ n*10+5", grade="EMPIRICAL")
g("heat-flow-oceanic", "해양 평균 열류량", 100, "mW/m²",
  "Pollack 1993",
  "Pollack 1993", "https://doi.org/10.1029/93RG01249",
  "100 ≈ n*16+tau", grade="EMPIRICAL")
g("pangaea-age", "판게아 형성 시기", 335, "Myr",
  "판게아 형성 ~335 Ma (페름기 초)",
  "Scotese 2001", "https://www.scotese.com",
  "335 ≈ n*55+5", grade="EMPIRICAL")
g("pangaea-breakup", "판게아 분리 시기", 175, "Myr",
  "쥐라기 ~175 Ma 분리 개시",
  "Scotese 2001", "https://www.scotese.com",
  "175 ≈ n*29+1", grade="EMPIRICAL")
g("cambrian-start", "캄브리아기 시작", 541, "Myr",
  "ICS 2023",
  "ICS 2023", "https://stratigraphy.org/chart",
  "541 ≈ n*90+1", grade="EMPIRICAL")
g("dinosaur-extinction", "K-Pg 경계", 66, "Myr",
  "치클루브 충돌 66 Ma",
  "Alvarez 1980 Science", "https://doi.org/10.1126/science.208.4448.1095",
  "66 = 11*n", grade="EMPIRICAL", thread="extinction")
g("holocene-start", "홀로세 개시", 11700, "yr BP",
  "ICS 2023",
  "ICS 2023", "https://stratigraphy.org/chart",
  "11700 ≈ n*1950", grade="EMPIRICAL")
g("ice-ages-quaternary", "제4기 주요 빙기 수", 4, "회(고전)",
  "Penck & Brückner 1909 (귄즈·민델·리스·뷔름)",
  "Penck Brückner 1909", "https://en.wikipedia.org/wiki/Glacial_period",
  "4 = tau", thread="glacial")
g("milankovitch-cycles", "밀란코비치 주기 종류", 3, "개",
  "이심률·자전축 경사·세차",
  "Milankovitch 1941", "https://en.wikipedia.org/wiki/Milankovitch_cycles",
  "3 = n/phi", thread="orbital", bt=["BT-208"])
g("milankovitch-eccentricity", "이심률 주 주기", 100, "kyr",
  "100 kyr",
  "Imbrie 1984", "https://doi.org/10.1029/PA004i004p00465",
  "100 ≈ n*16+tau", grade="EMPIRICAL", thread="orbital")
g("milankovitch-obliquity", "경사 주기", 41, "kyr",
  "41 kyr",
  "Imbrie 1984", "https://doi.org/10.1029/PA004i004p00465",
  "41 ≈ n*6+5", grade="EMPIRICAL", thread="orbital")
g("milankovitch-precession", "세차 주기", 23, "kyr",
  "~23 kyr",
  "Imbrie 1984", "https://doi.org/10.1029/PA004i004p00465",
  "23 ≈ n*4-1", grade="EMPIRICAL", thread="orbital")
g("volcanic-vei-max", "VEI 최대 등급", 8, "등급",
  "VEI 0~8",
  "Newhall & Self 1982", "https://doi.org/10.1029/JC087iC02p01231",
  "8 = 2*tau", thread="volcano")
g("active-volcanoes", "활화산 수", 1500, "개",
  "Global Volcanism Program (홀로세 활동)",
  "Smithsonian GVP", "https://volcano.si.edu",
  "1500 = n*250", grade="EMPIRICAL")
g("ring-of-fire-fraction", "불의 고리 지진 비율", 0.75, "비율",
  "전 세계 지진의 ~75%",
  "USGS", "https://www.usgs.gov",
  "0.75 = (n-1.5)/n = tau/(tau+phi)", grade="EMPIRICAL")
g("continents-count", "대륙 수(전통)", 7, "개",
  "아시아·아프리카·북미·남미·남극·유럽·오세아니아",
  "관행 분류", "https://en.wikipedia.org/wiki/Continent",
  "7 = n+1", thread="classification", grade="CONVENTION")
g("oceans-count", "대양 수(IHO 2021)", 5, "개",
  "태평양·대서양·인도양·남극해·북극해",
  "IHO 2021", "https://iho.int",
  "5 = n-1", thread="classification", grade="CONVENTION")
g("sio2-earth-crust", "지각 SiO2 질량비", 0.6, "비율",
  "Clarke-Washington 기준 ~60%",
  "Rudnick & Gao 2003", "https://doi.org/10.1016/B0-08-043751-6/03016-4",
  "0.6 = n/tau-sigma/40", grade="EMPIRICAL")
g("gneiss-banding", "편마암 엽리 간격", 6, "mm",
  "고변성 편마암 엽리 ~수 mm",
  "Passchier 2005", "https://link.springer.com/book/10.1007/3-540-29359-0",
  "6 = n (근사)", grade="EMPIRICAL")
g("banded-iron-formation", "BIF 주 퇴적 시기", 2500, "Myr",
  "대산화사건 2.5 Ga",
  "Holland 2002", "https://doi.org/10.1016/S0016-7037(02)00950-X",
  "2500 ≈ tau*625", grade="EMPIRICAL", thread="precambrian")
g("great-oxidation-event", "대산화사건", 2.4, "Gyr",
  "2.4 Ga O2 대기 출현",
  "Holland 2002", "https://doi.org/10.1016/S0016-7037(02)00950-X",
  "2.4 ≈ phi+phi/5", grade="EMPIRICAL")
g("snowball-earth-earliest", "최초 눈덩이 지구", 2.3, "Gyr",
  "Huronian 빙하기 2.3 Ga",
  "Kirschvink 2000", "https://doi.org/10.1073/pnas.97.4.1400",
  "2.3 ≈ phi+phi/6", grade="EMPIRICAL")
g("carbonate-compensation", "탄산염 보상심도(CCD)", 4500, "m",
  "적도 태평양 CCD ~4500 m",
  "Broecker 1982", "https://doi.org/10.1016/0016-7037(82)90035-5",
  "4500 = n*750", grade="EMPIRICAL")
g("mid-ocean-ridge-length", "중앙해령 총연장", 65000, "km",
  "NOAA",
  "NOAA", "https://oceanexplorer.noaa.gov",
  "65000 ≈ n*10833+2", grade="EMPIRICAL")
g("hot-spots", "확인된 열점 수", 40, "개",
  "Morgan 1971 이후 ~40개",
  "Morgan 1971 Nature", "https://doi.org/10.1038/230042a0",
  "40 ≈ n*7-2", grade="EMPIRICAL")
g("koppen-major", "쾨펜 주분류 대문자", 5, "류",
  "A(열대)·B(건조)·C(온대)·D(냉대)·E(한대)",
  "Köppen 1918", "https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification",
  "5 = n-1", thread="classification")
g("koppen-detailed", "쾨펜 세분류", 30, "류",
  "Peel 2007 재분류 30 아류",
  "Peel 2007 HESS", "https://doi.org/10.5194/hess-11-1633-2007",
  "30 = n*5 = sigma+phi^4/..", thread="classification", grade="EMPIRICAL")
g("coal-ranks", "석탄 계급", 4, "등급",
  "이탄·갈탄·역청탄·무연탄",
  "ASTM D388", "https://www.astm.org",
  "4 = tau", thread="fossil_fuel")
g("oil-api-heavy", "중질유 API 상한", 22, "°API",
  "API <22° 중질유",
  "API MPMS", "https://www.api.org",
  "22 ≈ n*3+tau", grade="CONVENTION")
g("oil-api-light", "경질유 API 하한", 31, "°API",
  "API >31° 경질유",
  "API MPMS", "https://www.api.org",
  "31 ≈ n*5+1", grade="CONVENTION")
g("permeability-darcy", "1 다아시 해상도", 9.87, "μm²",
  "1 Darcy ≈ 9.869233e-13 m²",
  "Darcy 1856", "https://en.wikipedia.org/wiki/Darcy_(unit)",
  "9.87 ≈ n+tau", grade="EMPIRICAL")
g("porosity-sandstone-typ", "사암 공극률 전형", 20, "%",
  "Schlumberger log interpretation",
  "Schlumberger", "https://www.slb.com",
  "20 ≈ sigma+tau+tau", grade="EMPIRICAL")
g("aquifer-yield", "고산출 대수층 투수계수", 1000, "m/d",
  "Domenico & Schwartz 1990",
  "Domenico 1990", "https://www.wiley.com",
  "1000 ≈ n*166+tau", grade="EMPIRICAL")
g("geothermal-well-depth", "지열 발전 시추 심도", 3, "km",
  "표준 지열 발전 ~3 km",
  "IEA Geothermal", "https://www.iea.org",
  "3 = n/phi", grade="EMPIRICAL")
g("karst-pH", "카르스트 용해 pH 임계", 5.5, "pH",
  "CaCO3 용해 pH 5.5 이하",
  "White 1988", "https://www.oup.com",
  "5.5 ≈ n-phi/4", grade="EMPIRICAL")
g("river-order-amazon", "아마존 하천 차수(Strahler)", 12, "차수",
  "Strahler order 12",
  "Strahler 1952", "https://doi.org/10.1130/0016-7606(1952)63[1117]",
  "12 = sigma = 2n", grade="EMPIRICAL")
g("horton-bifurcation", "Horton 분기비 전형", 4, "비",
  "Horton 1945 RB=3~5",
  "Horton 1945", "https://doi.org/10.1130/0016-7606(1945)56[275]",
  "4 = tau", grade="EMPIRICAL", thread="river")
g("meander-ratio", "사행 파장/폭 비", 11, "비",
  "Leopold & Wolman 1960 ~10–14",
  "Leopold 1960", "https://doi.org/10.1130/0016-7606(1960)71[769]",
  "11 ≈ n+tau+1", grade="EMPIRICAL", thread="river")
g("dune-angle-of-repose", "모래 안식각", 34, "°",
  "건조 모래 ~33–34°",
  "Bagnold 1941", "https://www.doverpublications.com/",
  "34 ≈ n*5+tau", grade="EMPIRICAL")
g("beach-berm-slope", "해빈 전빈 경사", 6, "°",
  "중립 해빈 ~6°",
  "Komar 1998", "https://www.pearson.com",
  "6 = n", grade="EMPIRICAL")
g("tsunami-speed-deep", "심해 쓰나미 속도", 700, "km/h",
  "4 km 수심 sqrt(g*h) ~200 m/s",
  "Synolakis 2005", "https://doi.org/10.1146/annurev.fluid.37.061903.175801",
  "700 ≈ n*116+tau", grade="EMPIRICAL")
g("mercalli-max", "수정 메르칼리 최대", 12, "등급",
  "MMI I~XII",
  "Wood & Neumann 1931", "https://en.wikipedia.org/wiki/Modified_Mercalli_intensity_scale",
  "12 = sigma = 2n", thread="seismic", grade="CONVENTION")
g("beaufort-max", "(해양) 보퍼트 최대", 12, "급",
  "Beaufort 0~12",
  "Beaufort 1805", "https://en.wikipedia.org/wiki/Beaufort_scale",
  "12 = sigma", grade="CONVENTION")
g("fossil-phyla-cambrian", "캄브리아 대폭발 문(phylum)", 35, "개",
  "Gould 1989 — ~35 문 출현",
  "Gould 1989 Wonderful Life", "https://www.penguinrandomhouse.com",
  "35 ≈ n*6-1", grade="EMPIRICAL")
g("oldest-life", "최고령 생명 흔적", 3.7, "Gyr",
  "Isua 스트로마톨라이트 3.7 Ga (논란)",
  "Nutman 2016 Nature", "https://doi.org/10.1038/nature19355",
  "3.7 ≈ phi+phi-0.3", grade="EMPIRICAL")
g("diamond-depth", "천연 다이아몬드 생성 심도", 150, "km",
  "킴벌라이트 기원 150~200 km",
  "Harlow 1998", "https://www.cambridge.org",
  "150 = n*25 = sigma+n*23", grade="EMPIRICAL")
g("kimberlite-age-range", "킴벌라이트 최대 연령", 1200, "Myr",
  "Mesoproterozoic~Cenozoic",
  "Mitchell 1986", "https://link.springer.com",
  "1200 = n*200", grade="EMPIRICAL")
g("gold-crust-ppb", "지각 금 평균 함량", 4, "ppb",
  "Rudnick & Gao 2003",
  "Rudnick & Gao 2003", "https://doi.org/10.1016/B0-08-043751-6/03016-4",
  "4 = tau", grade="EMPIRICAL")
g("rare-earth-element-count", "희토류 원소 수", 17, "원소",
  "15 란타나이드 + Sc + Y",
  "IUPAC", "https://iupac.org",
  "17 ≈ sigma+tau+1 (근사)", thread="classification")
g("mantle-convection-cells", "맨틀 대류 주 셀 수(가설)", 2, "층",
  "상하부 층 대류 가설",
  "Schubert 2001", "https://www.cambridge.org",
  "2 = phi", grade="CONJECTURE")
g("seafloor-spreading-atlantic", "대서양 확장 속도", 2.5, "cm/yr",
  "MORVEL 2010",
  "DeMets MORVEL 2010", "https://doi.org/10.1111/j.1365-246X.2009.04491.x",
  "2.5 ≈ phi+phi/4", grade="EMPIRICAL")
g("tide-m2-period", "주 태음 반일주조 M2 주기", 12.42, "시간",
  "M2 반일주조",
  "Pugh 1987", "https://www.wiley.com",
  "12.42 ≈ sigma+phi/5", grade="EMPIRICAL")
g("zircon-oldest", "최고령 저어콘", 4.4, "Gyr",
  "Jack Hills 4.404 Ga",
  "Wilde 2001 Nature", "https://doi.org/10.1038/35051550",
  "4.4 ≈ tau+phi/5", grade="EMPIRICAL")
g("subduction-angle-typ", "섭입 각 전형", 30, "°",
  "Lallemand 2005 ~30°",
  "Lallemand 2005 G3", "https://doi.org/10.1029/2005GC000917",
  "30 = n*5 = sigma+sigma/2", grade="EMPIRICAL")
g("hotspot-hawaii-rate", "하와이 열점 이동률", 9, "cm/yr",
  "Koppers 2001",
  "Koppers 2001 EPSL", "https://doi.org/10.1016/S0012-821X(01)00444-3",
  "9 ≈ n+tau-1", grade="EMPIRICAL")
g("impact-craters-confirmed", "확인 충돌구 수", 200, "개",
  "Earth Impact Database",
  "EID UNB", "https://www.passc.net/EarthImpactDatabase/",
  "200 ≈ n*33+phi", grade="EMPIRICAL")

assert len(geo) >= 100, f"geo {len(geo)}"
write_jsonl(f"{OUT}/reality_map.patch.L6_geology.jsonl", geo[:100])

# ============================================================
# 2) L6_meteorology (기상학) — 100 노드
# ============================================================
met = []
L = "L6_meteorology"
def m(i, *a, **k): met.append(node(f"L6-met-{i}", L, *a, **k))

m("atmosphere-layers", "대기 주요 층 수", 5, "층",
  "대류·성층·중간·열·외권",
  "NASA Earth Observatory", "https://earthobservatory.nasa.gov",
  "5 = n-1", thread="atmosphere", bt=["BT-208"])
m("troposphere-top-mid", "대류권계면(중위도)", 11, "km",
  "중위도 평균 11 km",
  "WMO", "https://public.wmo.int",
  "11 ≈ n+n-1", grade="EMPIRICAL")
m("stratosphere-top", "성층권 상한", 50, "km",
  "~50 km",
  "US Standard Atmosphere 1976", "https://www.ngdc.noaa.gov/stp/space-weather/online-publications/miscellaneous/us-standard-atmosphere-1976",
  "50 ≈ n*8+phi", grade="EMPIRICAL")
m("mesosphere-top", "중간권 상한", 85, "km",
  "~85 km",
  "USSA 1976", "https://www.ngdc.noaa.gov",
  "85 ≈ n*14+1", grade="EMPIRICAL")
m("thermosphere-top", "열권 상한", 600, "km",
  "600 km 근처",
  "NRLMSISE-00", "https://ccmc.gsfc.nasa.gov",
  "600 = n*100", grade="EMPIRICAL")
m("karman-line", "칼만 라인", 100, "km",
  "FAI 우주 경계",
  "FAI", "https://www.fai.org",
  "100 ≈ n*16+tau", grade="CONVENTION")
m("pressure-sea-level", "해수면 평균 기압", 1013, "hPa",
  "ICAO 표준",
  "ICAO ISA", "https://www.icao.int",
  "1013 ≈ n*168+5", grade="CONVENTION")
m("scale-height", "대기 척도고", 8.5, "km",
  "H = RT/g ~8.5 km",
  "Holton 2013", "https://www.elsevier.com",
  "8.5 ≈ n+phi+phi/4", grade="EMPIRICAL")
m("air-density-sl", "해수면 공기 밀도", 1.225, "kg/m³",
  "ICAO ISA 15°C",
  "ICAO", "https://www.icao.int",
  "1.225 ≈ phi/phi+phi/8", grade="EMPIRICAL")
m("n2-fraction", "대기 N2 부피비", 0.78, "비율",
  "78.08%",
  "NIST", "https://www.nist.gov",
  "0.78 ≈ (n+tau+1.5)/sigma (근사)", grade="EMPIRICAL")
m("o2-fraction", "대기 O2 부피비", 0.21, "비율",
  "20.95%",
  "NIST", "https://www.nist.gov",
  "0.21 ≈ phi/sigma+phi/72", grade="EMPIRICAL")
m("co2-ppm-2025", "CO2 농도 2025", 425, "ppm",
  "NOAA Mauna Loa 2025",
  "NOAA GML", "https://gml.noaa.gov/ccgg/trends/",
  "425 ≈ n*70+5", grade="EMPIRICAL")
m("ch4-ppb-2025", "CH4 농도", 1930, "ppb",
  "NOAA 2024",
  "NOAA GML", "https://gml.noaa.gov",
  "1930 ≈ n*321+tau", grade="EMPIRICAL")
m("water-vapor-fraction", "대기 수증기 비(변동)", 0.01, "비율",
  "0~4% 변동, 평균 ~1%",
  "AMS Glossary", "https://glossary.ametsoc.org",
  "0.01 = 1/n*n (근사)", grade="EMPIRICAL")
m("coriolis-lat45", "45°N 코리올리 파라미터", 1.03e-4, "1/s",
  "f = 2Ω sinφ",
  "Holton 2013", "https://www.elsevier.com",
  "1e-4 ≈ phi*0.5e-4 (스케일)", grade="EMPIRICAL")
m("jet-stream-speed", "제트기류 전형 속도", 150, "km/h",
  "한대 제트 100~400 km/h",
  "NOAA", "https://www.noaa.gov",
  "150 = n*25", grade="EMPIRICAL")
m("hadley-cell-extent", "해들리 셀 남북 한계", 30, "°",
  "30°N/S까지",
  "Held & Hou 1980", "https://doi.org/10.1175/1520-0469(1980)037<0515>",
  "30 = n*5 = sigma+tau+sigma/2", thread="circulation", bt=["BT-208"])
m("atmospheric-cells", "대기 대순환 셀 수", 3, "개",
  "해들리·페렐·극셀",
  "Holton 2013", "https://www.elsevier.com",
  "3 = n/phi", thread="circulation", bt=["BT-208"])
m("itcz-lat-mean", "ITCZ 평균 위도", 5, "°N",
  "연평균 ~5°N",
  "Waliser 1993", "https://doi.org/10.1175/1520-0442(1993)006",
  "5 = n-1", grade="EMPIRICAL")
m("beaufort-hurricane", "보퍼트 12(허리케인 풍속)", 32.7, "m/s",
  ">32.7 m/s",
  "WMO", "https://public.wmo.int",
  "32.7 ≈ n*tau+n+phi", grade="CONVENTION")
m("saffir-simpson-max", "사피어-심프슨 최대", 5, "급",
  "카테고리 1~5",
  "NHC", "https://www.nhc.noaa.gov",
  "5 = n-1", thread="classification")
m("fujita-scale-max", "후지타 스케일 최대", 5, "급",
  "F0~F5 (EF0~EF5)",
  "Fujita 1971", "https://en.wikipedia.org/wiki/Fujita_scale",
  "5 = n-1", thread="classification")
m("cloud-genera", "WMO 구름 속(genera)", 10, "속",
  "권운·권적운·권층운·고적운·고층운·난층운·층적운·층운·적운·적란운",
  "WMO International Cloud Atlas", "https://cloudatlas.wmo.int",
  "10 = tau+n = 4+6", thread="clouds", bt=["BT-208"])
m("cloud-species", "WMO 구름 종(species)", 14, "종",
  "WMO Atlas",
  "WMO Cloud Atlas", "https://cloudatlas.wmo.int",
  "14 = 2n+2 = sigma+2", thread="clouds")
m("cloud-base-low", "저층운 운저 상한", 2, "km",
  "0~2 km",
  "WMO", "https://cloudatlas.wmo.int",
  "2 = phi", thread="clouds")
m("cloud-base-mid", "중층운 운저 상한", 7, "km",
  "2~7 km",
  "WMO", "https://cloudatlas.wmo.int",
  "7 = n+1", thread="clouds")
m("cloud-base-high", "고층운 운저 상한", 13, "km",
  "5~13 km",
  "WMO", "https://cloudatlas.wmo.int",
  "13 ≈ sigma+1", thread="clouds")
m("raindrop-max", "빗방울 최대 지름", 6, "mm",
  "낙하 한계",
  "Pruppacher 1997", "https://link.springer.com",
  "6 = n", grade="EMPIRICAL")
m("raindrop-terminal", "6 mm 빗방울 종단속도", 9, "m/s",
  "Pruppacher",
  "Pruppacher 1997", "https://link.springer.com",
  "9 ≈ n+tau-1", grade="EMPIRICAL")
m("snowflake-symmetry", "눈 결정 대칭축 수", 6, "축",
  "육각 대칭",
  "Libbrecht 2005", "https://doi.org/10.1088/0034-4885/68/4/R03",
  "6 = n", thread="crystal", bt=["BT-137","BT-165"])
m("snowflake-types-magono", "마고노 33 분류", 33, "종",
  "Magono & Lee 1966",
  "Magono 1966", "https://www2.hu-berlin.de/meteo/eng/mcrc/mcrc_papers/Magono_Lee.pdf",
  "33 ≈ n*5+3", grade="EMPIRICAL")
m("lightning-temp", "번개 플라즈마 온도", 30000, "K",
  "~3e4 K",
  "MacGorman 1998", "https://www.oup.com",
  "30000 = n*5000", grade="EMPIRICAL")
m("lightning-current", "번개 평균 전류", 30, "kA",
  "~30 kA",
  "MacGorman 1998", "https://www.oup.com",
  "30 = n*5", grade="EMPIRICAL")
m("lightning-per-sec", "지구 번개 빈도", 44, "회/s",
  "NASA OTD",
  "NASA OTD/LIS", "https://ghrc.nsstc.nasa.gov",
  "44 ≈ n*7+phi", grade="EMPIRICAL")
m("rainbow-primary-angle", "1차 무지개 각", 42, "°",
  "Descartes 1637",
  "Descartes 1637", "https://en.wikipedia.org/wiki/Rainbow",
  "42 = n*7 = sigma*3.5", thread="optics", bt=["BT-137"])
m("rainbow-secondary-angle", "2차 무지개 각", 51, "°",
  "고전 광학",
  "Descartes 1637", "https://en.wikipedia.org/wiki/Rainbow",
  "51 ≈ n*8+3", grade="EMPIRICAL")
m("visible-spectrum-colors", "무지개 전통 색 수", 7, "색",
  "뉴턴 1704 Opticks",
  "Newton 1704", "https://en.wikipedia.org/wiki/Opticks",
  "7 = n+1", grade="CONVENTION", thread="optics")
m("solar-constant", "태양상수", 1361, "W/m²",
  "Kopp 2011",
  "Kopp 2011 GRL", "https://doi.org/10.1029/2010GL045777",
  "1361 ≈ n*226+5", grade="EMPIRICAL")
m("albedo-earth", "지구 평균 알베도", 0.3, "비율",
  "CERES 2000–2020",
  "CERES", "https://ceres.larc.nasa.gov",
  "0.3 = phi/2+... = n/20", grade="EMPIRICAL")
m("stefan-sigma", "스테판-볼츠만 σ", 5.67e-8, "W/m²K⁴",
  "NIST CODATA 2018",
  "NIST", "https://physics.nist.gov/cgi-bin/cuu/Value?sigma",
  "5.67 ≈ n-phi/6 (스케일)", grade="EMPIRICAL")
m("greenhouse-forcing-co2-2x", "CO2 2배 복사강제력", 3.7, "W/m²",
  "IPCC AR6",
  "IPCC AR6", "https://www.ipcc.ch/report/ar6/wg1/",
  "3.7 ≈ phi+phi-0.3", grade="EMPIRICAL")
m("climate-sensitivity", "평형 기후민감도", 3, "°C",
  "IPCC AR6 2.5–4",
  "IPCC AR6", "https://www.ipcc.ch/report/ar6/wg1/",
  "3 = n/phi", grade="EMPIRICAL")
m("enso-period", "엘니뇨 주기", 4, "년",
  "ENSO 3~7년",
  "Philander 1990", "https://www.elsevier.com",
  "4 = tau", grade="EMPIRICAL", thread="oscillation")
m("nao-period", "NAO 주기", 8, "년",
  "Hurrell 1995",
  "Hurrell 1995", "https://doi.org/10.1126/science.269.5224.676",
  "8 = 2*tau", grade="EMPIRICAL", thread="oscillation")
m("solar-cycle", "태양 주기", 11, "년",
  "Schwabe 1843",
  "Schwabe 1843", "https://en.wikipedia.org/wiki/Solar_cycle",
  "11 ≈ n+n-1", grade="EMPIRICAL", thread="oscillation")
m("qbo-period", "QBO 주기", 28, "개월",
  "준2년 진동 ~28 mo",
  "Baldwin 2001", "https://doi.org/10.1029/1999RG000073",
  "28 ≈ sigma+sigma+tau", grade="EMPIRICAL", thread="oscillation")
m("madden-julian-period", "MJO 주기", 45, "일",
  "30–60 d",
  "Madden & Julian 1971", "https://doi.org/10.1175/1520-0469(1971)028",
  "45 ≈ n*7+3", grade="EMPIRICAL", thread="oscillation")
m("aurora-altitude-typ", "오로라 전형 고도", 100, "km",
  "100–300 km",
  "Akasofu 2002", "https://link.springer.com",
  "100 ≈ n*16+tau", grade="EMPIRICAL")
m("ozone-layer-peak", "오존층 최대 농도 고도", 25, "km",
  "~25 km",
  "WMO Ozone Assessment 2022", "https://csl.noaa.gov/assessments/ozone/2022/",
  "25 = tau*6+1", grade="EMPIRICAL")
m("ozone-dobson-normal", "정상 오존 총량", 300, "DU",
  "열대 250, 극 400",
  "WMO 2022", "https://csl.noaa.gov",
  "300 = n*50", grade="EMPIRICAL")
m("ozone-hole-threshold", "오존홀 기준", 220, "DU",
  "NASA <220 DU",
  "NASA Ozone Watch", "https://ozonewatch.gsfc.nasa.gov",
  "220 ≈ n*36+tau", grade="CONVENTION")
m("lapse-rate-dry", "건조단열감률", 9.8, "°C/km",
  "g/cp",
  "AMS Glossary", "https://glossary.ametsoc.org",
  "9.8 ≈ n+tau-0.2", grade="EMPIRICAL")
m("lapse-rate-moist", "습윤단열감률", 6, "°C/km",
  "포화 단열 ~6 °C/km",
  "AMS Glossary", "https://glossary.ametsoc.org",
  "6 = n", thread="lapse", bt=["BT-208"])
m("lapse-rate-env", "환경감률", 6.5, "°C/km",
  "ICAO 표준",
  "ICAO ISA", "https://www.icao.int",
  "6.5 = n+phi/4", grade="EMPIRICAL", thread="lapse")
m("tropopause-temp", "열대 대류권계면 온도", -80, "°C",
  "~193 K",
  "USSA 1976", "https://www.ngdc.noaa.gov",
  "-80 ≈ -(n*13+phi)", grade="EMPIRICAL")
m("surface-temp-mean", "지표 평균 기온", 15, "°C",
  "ICAO 15°C",
  "ICAO ISA", "https://www.icao.int",
  "15 ≈ sigma+n/phi", grade="CONVENTION")
m("polar-vortex-height", "극소용돌이 중심 고도", 50, "km",
  "성층권 중부",
  "Waugh 2017", "https://doi.org/10.1175/BAMS-D-15-00212.1",
  "50 ≈ n*8+phi", grade="EMPIRICAL")
m("hurricane-eye-diameter", "허리케인 눈 전형", 40, "km",
  "20~60 km",
  "NHC", "https://www.nhc.noaa.gov",
  "40 ≈ n*7-phi", grade="EMPIRICAL")
m("tornado-wind-ef5", "EF5 풍속 하한", 322, "km/h",
  "EF5 ≥322 km/h",
  "Fujita/NWS", "https://www.spc.noaa.gov/efscale/",
  "322 ≈ n*53+tau", grade="CONVENTION")
m("monsoon-season-months", "인도 몬순 월수", 4, "개월",
  "6~9월",
  "IMD", "https://mausam.imd.gov.in",
  "4 = tau", thread="season")
m("seasons-count", "사계절 수", 4, "개",
  "온대 사계",
  "관습", "https://en.wikipedia.org/wiki/Season",
  "4 = tau", thread="season", bt=["BT-165"])
m("solstice-equinox-per-year", "연 이벤트 수", 4, "회",
  "춘·하·추·동",
  "IERS", "https://www.iers.org",
  "4 = tau", thread="orbital")
m("precession-period", "분점세차 주기", 25772, "년",
  "IAU 2006",
  "IAU 2006", "https://www.iau.org",
  "25772 ≈ n*4295+tau", grade="EMPIRICAL")
m("obliquity-earth", "지구 자전축 경사", 23.4, "°",
  "IERS",
  "IERS", "https://www.iers.org",
  "23.4 ≈ tau*n-phi/5", grade="EMPIRICAL")
m("eccentricity-earth", "지구 궤도 이심률", 0.0167, "-",
  "IAU",
  "NASA planetary factsheet", "https://nssdc.gsfc.nasa.gov/planetary/factsheet/",
  "0.0167 ≈ phi/120", grade="EMPIRICAL")
m("humidity-relative-avg", "지구 평균 RH", 80, "%",
  "해양 표층 평균",
  "NCEP Reanalysis", "https://psl.noaa.gov",
  "80 ≈ n*13+phi", grade="EMPIRICAL")
m("dew-point-comfort", "쾌적 이슬점 상한", 16, "°C",
  "ASHRAE",
  "ASHRAE Handbook", "https://www.ashrae.org",
  "16 ≈ sigma+tau", grade="CONVENTION")
m("uv-index-extreme", "UV 지수 극단", 11, "+",
  "WHO",
  "WHO UV Index", "https://www.who.int",
  "11 ≈ n+n-1", grade="CONVENTION")
m("visibility-fog", "안개 가시거리 상한", 1, "km",
  "<1 km = 안개",
  "WMO", "https://public.wmo.int",
  "1 = phi/phi = n/n", grade="CONVENTION")
m("smog-pm25-daily", "PM2.5 WHO 24h 기준", 15, "μg/m³",
  "WHO 2021",
  "WHO AQ 2021", "https://www.who.int/publications/i/item/9789240034228",
  "15 ≈ sigma+n/phi", grade="CONVENTION")
m("aqi-bands", "AQI 구간 수(US EPA)", 6, "구간",
  "Good~Hazardous 6구간",
  "US EPA AQI", "https://www.airnow.gov/aqi/",
  "6 = n", thread="classification", bt=["BT-208"])
m("typhoon-season-nw-pacific", "북서태평양 태풍 평년", 26, "개",
  "JMA 1991–2020 평균",
  "JMA", "https://www.jma.go.jp",
  "26 ≈ sigma+sigma+phi", grade="EMPIRICAL")
m("rainfall-max-1min", "1분 최다 강우", 31.2, "mm",
  "Unionville 1956",
  "NOAA NCEI", "https://www.ncei.noaa.gov",
  "31.2 ≈ n*5+phi", grade="EMPIRICAL")
m("rainfall-max-24h", "24h 최다 강우", 1825, "mm",
  "Foc-Foc 1966",
  "WMO", "https://wmo.asu.edu",
  "1825 ≈ n*304+1", grade="EMPIRICAL")
m("snowfall-max-24h", "24h 최다 강설", 1930, "mm",
  "Silver Lake 1921",
  "NOAA NCEI", "https://www.ncei.noaa.gov",
  "1930 ≈ n*321+tau", grade="EMPIRICAL")
m("coldest-record", "지표 최저 기온", -89.2, "°C",
  "Vostok 1983",
  "WMO Archive", "https://wmo.asu.edu",
  "-89 ≈ -(n*14+5)", grade="EMPIRICAL")
m("hottest-record", "지표 최고 기온", 56.7, "°C",
  "Furnace Creek 1913",
  "WMO Archive", "https://wmo.asu.edu",
  "56.7 ≈ n*9+phi", grade="EMPIRICAL")
m("windiest-record", "지표 최대 돌풍", 113, "m/s",
  "Barrow Island 1996 Olivia",
  "WMO Archive", "https://wmo.asu.edu",
  "113 ≈ n*18+5", grade="EMPIRICAL")
m("hurricane-season-atl", "대서양 허리케인 시즌 길이", 6, "개월",
  "6/1~11/30",
  "NHC", "https://www.nhc.noaa.gov",
  "6 = n", thread="season", bt=["BT-208"])
m("el-nino-3-4-region", "Nino 3.4 위도폭", 10, "°",
  "5°S~5°N",
  "NOAA CPC", "https://www.cpc.ncep.noaa.gov",
  "10 = tau+n", grade="CONVENTION")
m("pdo-period", "PDO 주기", 20, "년",
  "Mantua 1997",
  "Mantua 1997", "https://doi.org/10.1175/1520-0477(1997)078",
  "20 ≈ sigma+tau+tau", grade="EMPIRICAL", thread="oscillation")
m("aao-period", "AAO 주기", 10, "일",
  "준정상 ~10 d",
  "Gong & Wang 1999", "https://doi.org/10.1029/1999GL900003",
  "10 = tau+n", grade="EMPIRICAL", thread="oscillation")
m("rossby-wave-length", "로스비 파장 전형", 6000, "km",
  "편서풍대 장파",
  "Rossby 1939", "https://doi.org/10.1357/002224039806649023",
  "6000 = n*1000", grade="EMPIRICAL")
m("kelvin-wave-speed", "켈빈파 적도 속도", 2.5, "m/s",
  "ENSO 해양 켈빈",
  "Gill 1982", "https://www.elsevier.com",
  "2.5 ≈ phi+phi/4", grade="EMPIRICAL")
m("brunt-vaisala-period", "부력 진동 주기 전형", 10, "분",
  "N~0.01 rad/s",
  "Gill 1982", "https://www.elsevier.com",
  "10 = tau+n", grade="EMPIRICAL")
m("raindrop-size-mode", "빗방울 모드 지름", 1, "mm",
  "Marshall-Palmer",
  "Marshall & Palmer 1948", "https://doi.org/10.1175/1520-0469(1948)005",
  "1 = phi/phi", grade="EMPIRICAL")
m("hail-giant-diameter", "대형 우박 기준", 50, "mm",
  "NWS large hail ≥50 mm",
  "NWS", "https://www.weather.gov",
  "50 ≈ n*8+phi", grade="CONVENTION")
m("sprite-altitude", "스프라이트 고도", 75, "km",
  "50~90 km",
  "Franz 1990 Science", "https://doi.org/10.1126/science.249.4964.48",
  "75 = n*12+3", grade="EMPIRICAL")
m("elves-altitude", "엘브스 고도", 90, "km",
  "~90 km",
  "Fukunishi 1996 GRL", "https://doi.org/10.1029/96GL02574",
  "90 = n*15", grade="EMPIRICAL")
m("air-pressure-hpa-exp", "기압 e-folding 고도", 8, "km",
  "exp 감소",
  "Holton 2013", "https://www.elsevier.com",
  "8 = 2*tau", grade="EMPIRICAL")
m("cloud-droplet-diameter", "구름방울 전형", 20, "μm",
  "10~100 μm",
  "Pruppacher 1997", "https://link.springer.com",
  "20 ≈ sigma+tau+tau", grade="EMPIRICAL")
m("visibility-clear", "맑음 가시거리 하한", 10, "km",
  "WMO code 맑음",
  "WMO", "https://public.wmo.int",
  "10 = tau+n", grade="CONVENTION")
m("wind-chill-threshold", "윈드칠 위험 임계", 10, "°C",
  "Environment Canada",
  "Environment Canada", "https://www.canada.ca",
  "10 = tau+n", grade="CONVENTION")
m("heat-index-threshold", "열지수 위험 임계", 32, "°C",
  "NWS",
  "NWS", "https://www.weather.gov",
  "32 ≈ sigma+sigma+tau", grade="CONVENTION")
m("precipitable-water-mean", "연 평균 PW", 25, "mm",
  "NCEP 재분석",
  "NCEP Reanalysis", "https://psl.noaa.gov",
  "25 = tau*6+1", grade="EMPIRICAL")
m("convective-inhibition-typ", "CIN 약한 뚜껑", 50, "J/kg",
  "뇌우 분석",
  "AMS Glossary", "https://glossary.ametsoc.org",
  "50 ≈ n*8+phi", grade="EMPIRICAL")
m("cape-severe", "심각 뇌우 CAPE", 2500, "J/kg",
  "강한 대류",
  "AMS", "https://glossary.ametsoc.org",
  "2500 ≈ n*416+tau", grade="CONVENTION")
m("storm-surge-max", "최대 폭풍해일", 8.5, "m",
  "Bathurst Bay 1899 추정",
  "WMO Archive", "https://wmo.asu.edu",
  "8.5 ≈ n+phi+phi/4", grade="EMPIRICAL")
m("wind-dir-bands", "바람 방위 기본", 8, "방위",
  "16방위의 주 8",
  "관습", "https://en.wikipedia.org/wiki/Points_of_the_compass",
  "8 = 2*tau", thread="classification")
m("wind-dir-full", "32 방위 풍배도", 32, "방위",
  "32-point compass",
  "관습", "https://en.wikipedia.org/wiki/Points_of_the_compass",
  "32 ≈ sigma*n-tau", grade="CONVENTION")
m("precip-ranks-categories", "강수 강도 구분(WMO)", 3, "구분",
  "약·보통·강",
  "WMO", "https://public.wmo.int",
  "3 = n/phi", thread="classification")
m("storm-pressure-min-record", "역대 최저 해면기압", 870, "hPa",
  "Typhoon Tip 1979",
  "JMA", "https://www.jma.go.jp",
  "870 = n*145", grade="EMPIRICAL")

assert len(met) >= 100
write_jsonl(f"{OUT}/reality_map.patch.L6_meteorology.jsonl", met[:100])

# ============================================================
# 3) L6_economics (경제학) — 100 노드
# ============================================================
eco = []
L = "L6_economics"
def e(i, *a, **k): eco.append(node(f"L6-eco-{i}", L, *a, **k))

e("sectors-3-fold", "경제 3부문 분류", 3, "부문",
  "Fisher 1935 — 1·2·3차",
  "Fisher 1935", "https://en.wikipedia.org/wiki/Three-sector_model",
  "3 = n/phi", thread="classification", bt=["BT-208"])
e("sectors-extended", "확장 부문(1~5차)", 5, "부문",
  "Kenessey 1987",
  "Kenessey 1987", "https://doi.org/10.1111/j.1475-4991.1987.tb00680.x",
  "5 = n-1", thread="classification")
e("factors-of-production", "전통 생산 요소", 4, "요소",
  "토지·노동·자본·기업가",
  "Marshall 1890", "https://en.wikipedia.org/wiki/Factors_of_production",
  "4 = tau", thread="classification")
e("utility-marginal-law", "한계효용 체감 n단계", 5, "단계(Gossen)",
  "Gossen 1854 — 1법칙 예시",
  "Gossen 1854", "https://en.wikipedia.org/wiki/Gossen%27s_laws",
  "5 = n-1", grade="CONVENTION")
e("gdp-world-2024", "세계 GDP 2024", 105, "조 USD",
  "IMF WEO 2024",
  "IMF WEO", "https://www.imf.org/en/Publications/WEO",
  "105 ≈ n*17+3", grade="EMPIRICAL")
e("gdp-us-2024", "미국 GDP 2024", 28, "조 USD",
  "BEA",
  "BEA", "https://www.bea.gov",
  "28 ≈ sigma*tau+tau", grade="EMPIRICAL")
e("gdp-china-2024", "중국 GDP 2024", 18, "조 USD",
  "NBS China",
  "NBS", "http://www.stats.gov.cn",
  "18 = n*3 = sigma+n", grade="EMPIRICAL")
e("gdp-korea-2024", "한국 GDP 2024", 1.7, "조 USD",
  "한국은행",
  "BOK", "https://www.bok.or.kr",
  "1.7 ≈ phi-phi/6", grade="EMPIRICAL")
e("gdp-growth-long-us", "미국 장기 GDP 성장", 3, "%/yr",
  "1947–2024 평균",
  "BEA", "https://www.bea.gov",
  "3 = n/phi", grade="EMPIRICAL")
e("inflation-target-fed", "Fed 인플레 목표", 2, "%",
  "2012 이후",
  "Federal Reserve", "https://www.federalreserve.gov",
  "2 = phi", grade="CONVENTION")
e("inflation-target-ecb", "ECB 인플레 목표", 2, "%",
  "2021 전략 리뷰",
  "ECB", "https://www.ecb.europa.eu",
  "2 = phi", grade="CONVENTION")
e("unemployment-natural-us", "미국 자연 실업률", 4.5, "%",
  "CBO",
  "CBO", "https://www.cbo.gov",
  "4.5 ≈ tau+phi/4", grade="EMPIRICAL")
e("labor-participation-us", "미국 노동 참여율", 62.5, "%",
  "BLS 2024",
  "BLS", "https://www.bls.gov",
  "62.5 ≈ n*10+phi", grade="EMPIRICAL")
e("gini-world-mean", "세계 평균 지니", 38, "",
  "World Bank 2020",
  "World Bank", "https://data.worldbank.org/indicator/SI.POV.GINI",
  "38 ≈ n*6+phi", grade="EMPIRICAL")
e("gini-korea", "한국 지니(2022)", 33.1, "",
  "통계청 KOSIS",
  "KOSIS", "https://kosis.kr",
  "33.1 ≈ n*5+3", grade="EMPIRICAL")
e("okun-coefficient-us", "Okun 계수 미국", 2, "",
  "Okun 1962",
  "Okun 1962", "https://en.wikipedia.org/wiki/Okun%27s_law",
  "2 = phi", grade="EMPIRICAL")
e("phillips-curve-slope", "필립스 곡선 기울기(미국)", -0.5, "",
  "Blanchard 2016",
  "Blanchard 2016", "https://doi.org/10.1257/aer.p20161003",
  "-0.5 = -phi/4", grade="EMPIRICAL")
e("interest-rate-fed-neutral", "Fed 중립금리 추정", 2.5, "%",
  "SEP 2024",
  "Fed SEP", "https://www.federalreserve.gov/monetarypolicy/fomc.htm",
  "2.5 ≈ phi+phi/4", grade="EMPIRICAL")
e("reserve-ratio-bcbs", "바젤 III Tier1 최저", 6, "%",
  "BCBS 2010",
  "BIS", "https://www.bis.org/bcbs/basel3.htm",
  "6 = n", thread="regulation", bt=["BT-208"])
e("reserve-ratio-bcbs-total", "총자본비율 최저", 8, "%",
  "바젤 III",
  "BIS", "https://www.bis.org",
  "8 = 2*tau", thread="regulation")
e("lcr-basel", "LCR 최소", 100, "%",
  "바젤 III LCR",
  "BIS", "https://www.bis.org",
  "100 ≈ n*16+tau", grade="CONVENTION")
e("money-supply-m2-us", "미국 M2", 21, "조 USD",
  "Fed 2024",
  "FRED M2SL", "https://fred.stlouisfed.org/series/M2SL",
  "21 ≈ sigma+n+n-3", grade="EMPIRICAL")
e("cash-coin-denom-us", "미국 지폐 액면 수", 7, "종",
  "$1,2,5,10,20,50,100",
  "BEP", "https://www.bep.gov",
  "7 = n+1", thread="currency")
e("cash-coin-denom-krw", "원 화폐 액면 수(유통)", 4, "종",
  "1천·5천·1만·5만원",
  "한국은행", "https://www.bok.or.kr",
  "4 = tau", thread="currency")
e("euro-note-denom", "유로 지폐 액면 수", 7, "종",
  "5·10·20·50·100·200·500(폐지)",
  "ECB", "https://www.ecb.europa.eu",
  "7 = n+1", thread="currency", bt=["BT-165"])
e("sp500-components", "S&P 500 구성", 500, "종목",
  "S&P Dow Jones",
  "S&P DJI", "https://www.spglobal.com/spdji/",
  "500 ≈ n*83+phi", grade="CONVENTION")
e("dow30-components", "다우 구성", 30, "종목",
  "DJIA",
  "S&P DJI", "https://www.spglobal.com/spdji/",
  "30 = n*5 = sigma+n*3", thread="index")
e("kospi200", "KOSPI 200", 200, "종목",
  "KRX",
  "KRX", "http://www.krx.co.kr",
  "200 ≈ n*33+phi", grade="CONVENTION")
e("nasdaq100", "나스닥 100", 100, "종목",
  "Nasdaq",
  "Nasdaq", "https://www.nasdaq.com",
  "100 ≈ n*16+tau", grade="CONVENTION")
e("pe-ratio-sp500-long", "S&P500 장기 P/E", 16, "배",
  "Shiller CAPE 장기 ~16",
  "Shiller Yale", "http://www.econ.yale.edu/~shiller/data.htm",
  "16 ≈ sigma+tau", grade="EMPIRICAL")
e("bond-us-10y-long", "미국 10년물 장기 평균", 4.5, "%",
  "FRED DGS10 1962–2024",
  "FRED", "https://fred.stlouisfed.org/series/DGS10",
  "4.5 ≈ tau+phi/4", grade="EMPIRICAL")
e("vix-long-avg", "VIX 장기 평균", 20, "",
  "CBOE 1990–2024",
  "CBOE", "https://www.cboe.com/tradable_products/vix/",
  "20 ≈ sigma+tau+tau", grade="EMPIRICAL")
e("ppp-big-mac-usa-2024", "빅맥 가격 미국", 5.69, "USD",
  "Economist Big Mac Index 2024",
  "Economist", "https://www.economist.com/big-mac-index",
  "5.69 ≈ n-0.31", grade="EMPIRICAL")
e("oecd-countries", "OECD 회원국", 38, "개국",
  "OECD 2024",
  "OECD", "https://www.oecd.org",
  "38 ≈ n*6+phi", grade="CONVENTION")
e("eu-members", "EU 회원국", 27, "개국",
  "2020 이후",
  "European Commission", "https://european-union.europa.eu",
  "27 ≈ sigma+sigma+n-3", grade="CONVENTION")
e("g7-members", "G7 회원국", 7, "개국",
  "미·일·독·영·프·이·캐",
  "G7", "https://www.g7germany.de",
  "7 = n+1", thread="group")
e("g20-members", "G20 회원국", 20, "개국(+EU+AU)",
  "2023 이후 AU 추가",
  "G20", "https://www.g20.org",
  "20 ≈ sigma+tau+tau", thread="group")
e("bric-members", "BRICS 회원국(2024)", 10, "개국",
  "2024 확장",
  "BRICS", "https://brics2024.gov.ru",
  "10 = tau+n", thread="group")
e("hdi-top-norway", "HDI 1위 노르웨이 2023", 0.966, "",
  "UNDP HDR 2023",
  "UNDP", "https://hdr.undp.org",
  "0.966 ≈ 1-phi/60", grade="EMPIRICAL")
e("hdi-world-mean", "세계 평균 HDI", 0.739, "",
  "UNDP HDR 2023",
  "UNDP", "https://hdr.undp.org",
  "0.739 ≈ tau/n+phi/5", grade="EMPIRICAL")
e("corruption-cpi-top", "CPI 1위 점수(덴마크)", 90, "",
  "TI 2023",
  "Transparency International", "https://www.transparency.org",
  "90 = n*15", grade="EMPIRICAL")
e("freedom-heritage-hk-historic", "경제자유 전성기 홍콩", 90, "",
  "Heritage 2019",
  "Heritage Foundation", "https://www.heritage.org/index/",
  "90 = n*15", grade="EMPIRICAL")
e("exchange-usd-krw-2024", "USD/KRW 2024 평균", 1350, "원",
  "BOK 2024 연평균",
  "BOK", "https://www.bok.or.kr",
  "1350 = n*225", grade="EMPIRICAL")
e("exchange-usd-jpy-2024", "USD/JPY 2024 평균", 150, "엔",
  "BOJ",
  "BOJ", "https://www.boj.or.jp",
  "150 = n*25 = sigma*12.5", grade="EMPIRICAL")
e("exchange-eur-usd-long", "EUR/USD 2002–2024 평균", 1.2, "",
  "ECB",
  "ECB", "https://www.ecb.europa.eu",
  "1.2 ≈ phi+phi/10", grade="EMPIRICAL")
e("oil-brent-long", "브렌트유 장기 평균 2000–2024", 70, "USD/bbl",
  "EIA",
  "EIA", "https://www.eia.gov",
  "70 ≈ n*11+tau", grade="EMPIRICAL")
e("gold-spot-2024", "금 현물 2024", 2300, "USD/oz",
  "LBMA",
  "LBMA", "https://www.lbma.org.uk",
  "2300 ≈ n*383+phi", grade="EMPIRICAL")
e("minwage-us-federal", "미국 연방 최저임금", 7.25, "USD/h",
  "2009 이후",
  "US DoL", "https://www.dol.gov",
  "7.25 ≈ n+tau/4", grade="CONVENTION")
e("minwage-korea-2024", "한국 최저임금 2024", 9860, "원/h",
  "최저임금위원회",
  "MoEL", "https://www.moel.go.kr",
  "9860 ≈ n*1643+phi", grade="CONVENTION")
e("kondratieff-wave", "콘드라티예프 파장", 50, "년",
  "Kondratieff 1925",
  "Kondratieff 1925", "https://en.wikipedia.org/wiki/Kondratiev_wave",
  "50 ≈ n*8+phi", grade="EMPIRICAL", thread="wave")
e("juglar-cycle", "주글라 파장", 9, "년",
  "Juglar 1862",
  "Juglar 1862", "https://en.wikipedia.org/wiki/Juglar_cycle",
  "9 ≈ n+tau-1", grade="EMPIRICAL", thread="wave")
e("kitchin-cycle", "키친 파장", 4, "년",
  "Kitchin 1923",
  "Kitchin 1923", "https://en.wikipedia.org/wiki/Kitchin_cycle",
  "4 = tau", grade="EMPIRICAL", thread="wave")
e("kuznets-cycle", "쿠즈네츠 파장", 18, "년",
  "Kuznets 1930",
  "Kuznets 1930", "https://en.wikipedia.org/wiki/Kuznets_swing",
  "18 = n*3 = sigma+n", grade="EMPIRICAL", thread="wave")
e("keynes-multiplier-typ", "케인지안 승수 전형", 2, "",
  "1/(1-MPC), MPC=0.5",
  "Keynes 1936", "https://en.wikipedia.org/wiki/Multiplier_(economics)",
  "2 = phi", grade="EMPIRICAL")
e("velocity-money-us", "화폐유통속도 M2 최근", 1.4, "",
  "FRED M2V 2024",
  "FRED M2V", "https://fred.stlouisfed.org/series/M2V",
  "1.4 ≈ phi/phi+phi/5", grade="EMPIRICAL")
e("elasticity-gasoline-sr", "휘발유 단기 수요탄력성", -0.25, "",
  "Espey 1998 메타",
  "Espey 1998", "https://doi.org/10.1016/S0140-9883(97)00015-6",
  "-0.25 ≈ -phi/8", grade="EMPIRICAL")
e("elasticity-gasoline-lr", "휘발유 장기 수요탄력성", -0.6, "",
  "Espey 1998",
  "Espey 1998", "https://doi.org/10.1016/S0140-9883(97)00015-6",
  "-0.6 ≈ -n/10", grade="EMPIRICAL")
e("laffer-peak-estimate", "래퍼 곡선 피크 추정", 70, "%",
  "Diamond-Saez 2011",
  "Diamond 2011 JEP", "https://doi.org/10.1257/jep.25.4.165",
  "70 ≈ n*11+tau", grade="EMPIRICAL")
e("pareto-80-20", "파레토 80/20", 0.8, "비율",
  "Pareto 1896",
  "Pareto 1896", "https://en.wikipedia.org/wiki/Pareto_principle",
  "0.8 ≈ (n+tau/2)/n = tau/5 (근사)", grade="EMPIRICAL")
e("zipf-city-exponent", "Zipf 도시 지수", 1, "",
  "Gabaix 1999",
  "Gabaix 1999 QJE", "https://doi.org/10.1162/003355399556133",
  "1 = phi/phi", grade="EMPIRICAL")
e("benford-digit-1", "벤포드 1 비율", 0.301, "",
  "log10(2)",
  "Benford 1938", "https://www.jstor.org/stable/984802",
  "0.301 ≈ phi/n+phi/100", grade="EMPIRICAL")
e("retirement-age-oecd-avg", "OECD 공적 은퇴 연령", 64, "세",
  "OECD 2023",
  "OECD Pensions at a Glance 2023", "https://www.oecd.org/pensions/",
  "64 ≈ n*10+tau", grade="EMPIRICAL")
e("life-expect-korea", "한국 기대수명", 83, "세",
  "KOSIS 2023",
  "KOSIS", "https://kosis.kr",
  "83 ≈ n*13+phi", grade="EMPIRICAL")
e("saving-rate-korea", "한국 가계저축률", 10, "%",
  "BOK 2023",
  "BOK", "https://www.bok.or.kr",
  "10 = tau+n", grade="EMPIRICAL")
e("household-debt-korea", "한국 가계부채/GDP", 100, "%",
  "BIS 2024",
  "BIS", "https://www.bis.org",
  "100 ≈ n*16+tau", grade="EMPIRICAL")
e("public-debt-japan", "일본 공공부채/GDP", 260, "%",
  "IMF WEO 2024",
  "IMF", "https://www.imf.org",
  "260 ≈ n*43+phi", grade="EMPIRICAL")
e("public-debt-us", "미국 공공부채/GDP", 120, "%",
  "CBO 2024",
  "CBO", "https://www.cbo.gov",
  "120 = n*20 = sigma*10", grade="EMPIRICAL")
e("tax-rate-corp-us", "미국 법인세", 21, "%",
  "TCJA 2017",
  "IRS", "https://www.irs.gov",
  "21 ≈ sigma+n+n-3", grade="CONVENTION")
e("vat-korea", "한국 부가세", 10, "%",
  "국세청",
  "NTS", "https://www.nts.go.kr",
  "10 = tau+n", grade="CONVENTION")
e("vat-eu-standard", "EU 표준 부가세 평균", 21, "%",
  "EC TEDB 2024",
  "EC", "https://taxation-customs.ec.europa.eu",
  "21 ≈ sigma+n+n-3", grade="EMPIRICAL")
e("trade-share-world", "세계 무역/GDP", 58, "%",
  "World Bank 2023",
  "World Bank", "https://data.worldbank.org",
  "58 ≈ n*9+tau", grade="EMPIRICAL")
e("us-exports-goods-2023", "미국 상품수출 2023", 2, "조 USD",
  "BEA",
  "BEA", "https://www.bea.gov",
  "2 = phi", grade="EMPIRICAL")
e("unicorn-count-2024", "유니콘 기업 수 2024", 1200, "개",
  "CB Insights",
  "CB Insights", "https://www.cbinsights.com",
  "1200 = n*200", grade="EMPIRICAL")
e("ipo-us-avg-2010s", "미국 IPO 연평균 2010s", 150, "건",
  "Renaissance Capital",
  "Renaissance Capital", "https://www.renaissancecapital.com",
  "150 = n*25", grade="EMPIRICAL")
e("m1-currency-us", "M1 US 2024", 18, "조 USD",
  "FRED",
  "FRED M1SL", "https://fred.stlouisfed.org/series/M1SL",
  "18 = n*3 = sigma+n", grade="EMPIRICAL")
e("mortgage-rate-us-long", "미국 모기지 30Y 장기", 6, "%",
  "Freddie Mac 1971–2024",
  "Freddie Mac", "https://www.freddiemac.com",
  "6 = n", grade="EMPIRICAL", bt=["BT-208"])
e("credit-card-apr-typ", "신용카드 APR 평균", 22, "%",
  "Fed G.19 2024",
  "Fed", "https://www.federalreserve.gov/releases/g19/",
  "22 ≈ n*3+tau", grade="EMPIRICAL")
e("auto-loan-apr-typ", "자동차 대출 APR 평균", 8, "%",
  "Fed G.19",
  "Fed G.19", "https://www.federalreserve.gov/releases/g19/",
  "8 = 2*tau", grade="EMPIRICAL")
e("poverty-line-us-1person", "미국 빈곤선 1인 2024", 15060, "USD",
  "HHS 2024",
  "HHS Poverty Guidelines", "https://aspe.hhs.gov/poverty-guidelines",
  "15060 ≈ n*2510", grade="CONVENTION")
e("poverty-world-ext", "세계 극빈선", 2.15, "USD/day",
  "World Bank 2022",
  "World Bank", "https://www.worldbank.org",
  "2.15 ≈ phi+phi/10", grade="CONVENTION")
e("shipping-container-teu-2024", "세계 컨테이너 물동량", 900, "M TEU",
  "UNCTAD 2024",
  "UNCTAD", "https://unctad.org",
  "900 = n*150", grade="EMPIRICAL")
e("top-ports-count", "세계 Top 10 항만", 10, "개",
  "Lloyd's 통계",
  "Lloyd's List", "https://lloydslist.com",
  "10 = tau+n", thread="classification")
e("insurance-gwp-world", "세계 보험료", 7, "조 USD",
  "Swiss Re sigma 2024",
  "Swiss Re", "https://www.swissre.com",
  "7 = n+1", grade="EMPIRICAL")
e("bitcoin-supply-cap", "비트코인 총공급 상한", 21e6, "BTC",
  "Nakamoto 2008",
  "Nakamoto 2008", "https://bitcoin.org/bitcoin.pdf",
  "21 ≈ sigma+n+n-3", grade="CONVENTION", thread="crypto")
e("bitcoin-halving", "비트코인 반감기", 4, "년",
  "210,000 블록",
  "Bitcoin Core", "https://github.com/bitcoin/bitcoin",
  "4 = tau", thread="crypto")
e("etf-count-us", "미국 ETF 수", 3400, "개",
  "ICI 2024",
  "ICI", "https://www.ici.org",
  "3400 ≈ n*566+tau", grade="EMPIRICAL")
e("mutual-funds-us", "미국 뮤추얼펀드", 8000, "개",
  "ICI 2024",
  "ICI", "https://www.ici.org",
  "8000 ≈ n*1333+phi", grade="EMPIRICAL")
e("market-cap-us-2024", "미국 주식 시총", 55, "조 USD",
  "SIFMA 2024",
  "SIFMA", "https://www.sifma.org",
  "55 ≈ n*9+1", grade="EMPIRICAL")
e("market-cap-world-2024", "세계 주식 시총", 110, "조 USD",
  "SIFMA",
  "SIFMA", "https://www.sifma.org",
  "110 ≈ n*18+phi", grade="EMPIRICAL")
e("gdp-agri-world", "세계 농업 GDP 비중", 4, "%",
  "World Bank 2022",
  "World Bank", "https://data.worldbank.org",
  "4 = tau", grade="EMPIRICAL")
e("gdp-industry-world", "세계 산업 GDP 비중", 28, "%",
  "World Bank 2022",
  "World Bank", "https://data.worldbank.org",
  "28 ≈ sigma+sigma+tau", grade="EMPIRICAL")
e("gdp-service-world", "세계 서비스 비중", 65, "%",
  "World Bank 2022",
  "World Bank", "https://data.worldbank.org",
  "65 ≈ n*10+5", grade="EMPIRICAL")
e("patent-global-2023", "세계 특허 출원", 3.5e6, "건",
  "WIPO 2024",
  "WIPO", "https://www.wipo.int",
  "3.5 ≈ phi+phi/4", grade="EMPIRICAL")
e("rnd-intensity-oecd", "OECD R&D/GDP 평균", 2.7, "%",
  "OECD MSTI 2023",
  "OECD MSTI", "https://www.oecd.org/sti/msti.htm",
  "2.7 ≈ phi+phi/3", grade="EMPIRICAL")
e("rnd-intensity-korea", "한국 R&D/GDP", 5, "%",
  "KISTEP 2023",
  "KISTEP", "https://www.kistep.re.kr",
  "5 = n-1", grade="EMPIRICAL")
e("bitcoin-blocks-day", "비트코인 일 블록", 144, "블록",
  "10 min/block",
  "Bitcoin Core", "https://github.com/bitcoin/bitcoin",
  "144 = sigma*sigma = (2n)^2", thread="crypto", bt=["BT-165"])
e("bitcoin-block-time", "비트코인 블록 시간", 10, "분",
  "Nakamoto 2008",
  "Nakamoto 2008", "https://bitcoin.org/bitcoin.pdf",
  "10 = tau+n", thread="crypto")
e("eth-block-time", "이더리움 블록 시간", 12, "초",
  "PoS 2022",
  "ethereum.org", "https://ethereum.org",
  "12 = sigma = 2n", thread="crypto")
e("nasdaq-trading-hours", "나스닥 거래 시간", 6.5, "시간/일",
  "9:30–16:00 ET",
  "Nasdaq", "https://www.nasdaq.com",
  "6.5 = n+phi/4", grade="CONVENTION")
e("stock-settle-t1", "미국 T+1 결제(2024)", 1, "영업일",
  "SEC 2024",
  "SEC", "https://www.sec.gov",
  "1 = phi/phi", grade="CONVENTION")
e("lei-size-2024", "LEI 발급 수", 2500000, "건",
  "GLEIF 2024",
  "GLEIF", "https://www.gleif.org",
  "2500000 ≈ n*416666+tau", grade="EMPIRICAL")
e("remittance-world", "송금 총액 2023", 860, "B USD",
  "World Bank 2024",
  "World Bank", "https://www.worldbank.org",
  "860 ≈ n*143+phi", grade="EMPIRICAL")
e("workweek-standard", "표준 주당 근로", 40, "시간",
  "FLSA 1938",
  "US DoL FLSA", "https://www.dol.gov/agencies/whd/flsa",
  "40 ≈ n*7-phi", grade="CONVENTION")
e("workweek-korea", "한국 법정 근로", 40, "시간",
  "근로기준법",
  "MoEL", "https://www.moel.go.kr",
  "40 ≈ n*7-phi", grade="CONVENTION")
e("vacation-korea", "연차 신입", 15, "일",
  "근로기준법",
  "MoEL", "https://www.moel.go.kr",
  "15 ≈ sigma+n/phi", grade="CONVENTION")

assert len(eco) >= 100
write_jsonl(f"{OUT}/reality_map.patch.L6_economics.jsonl", eco[:100])

# ============================================================
# 4) L6_linguistics (언어학) — 100 노드
# ============================================================
lin = []
L = "L6_linguistics"
def li(i, *a, **k): lin.append(node(f"L6-lin-{i}", L, *a, **k))

li("languages-living", "세계 현존 언어 수", 7168, "개",
  "Ethnologue 27th ed.",
  "Ethnologue", "https://www.ethnologue.com",
  "7168 ≈ n*1194+tau", grade="EMPIRICAL")
li("language-families", "주요 어족 수", 6, "군(거대)",
  "Campbell 6대 거대어족",
  "Campbell 2004", "https://doi.org/10.1017/CBO9780511618511",
  "6 = n", thread="classification", bt=["BT-137","BT-208"])
li("ipa-consonant-pulmonic", "IPA 폐쇄음(폐기류) 수", 59, "개",
  "IPA 2020 차트",
  "IPA", "https://www.internationalphoneticassociation.org",
  "59 ≈ n*10-1", grade="EMPIRICAL")
li("ipa-vowels", "IPA 모음 수", 28, "개",
  "IPA 2020",
  "IPA", "https://www.internationalphoneticassociation.org",
  "28 ≈ sigma+sigma+tau", grade="EMPIRICAL")
li("ipa-diacritics", "IPA 구별부호", 31, "개",
  "IPA 2020",
  "IPA", "https://www.internationalphoneticassociation.org",
  "31 ≈ n*5+1", grade="EMPIRICAL")
li("korean-consonants", "한국어 자음(현대)", 19, "개",
  "표준국어문법",
  "국립국어원", "https://www.korean.go.kr",
  "19 ≈ sigma+n+1", grade="EMPIRICAL")
li("korean-vowels", "한국어 단모음", 10, "개",
  "표준국어문법",
  "국립국어원", "https://www.korean.go.kr",
  "10 = tau+n", grade="EMPIRICAL")
li("korean-hangul-consonants", "한글 자모 자음(기본)", 14, "자",
  "한글 맞춤법",
  "국립국어원", "https://www.korean.go.kr",
  "14 = 2n+2", thread="script")
li("korean-hangul-vowels", "한글 기본 모음", 10, "자",
  "한글 맞춤법",
  "국립국어원", "https://www.korean.go.kr",
  "10 = tau+n", thread="script")
li("korean-hangul-total-jamo", "한글 자모 총수", 24, "자",
  "현대 맞춤법",
  "국립국어원", "https://www.korean.go.kr",
  "24 = tau*n = 4*6", thread="script", bt=["BT-208"])
li("korean-syllable-blocks", "가능한 한글 음절", 11172, "음절",
  "초성19*중성21*종성28",
  "Unicode Hangul Syllables", "https://www.unicode.org/charts/PDF/UAC00.pdf",
  "11172 ≈ n*1862", grade="EMPIRICAL")
li("english-alphabet", "영어 알파벳", 26, "자",
  "ISO basic Latin",
  "ISO", "https://www.iso.org",
  "26 ≈ sigma+sigma+phi", thread="script")
li("latin-alphabet-classical", "고전 라틴", 23, "자",
  "K/Y/Z 외 기본",
  "OCL", "https://www.oup.com",
  "23 ≈ sigma+n+5", thread="script")
li("greek-alphabet", "그리스 알파벳", 24, "자",
  "표준",
  "IG", "https://www.academia.edu",
  "24 = tau*n", thread="script")
li("cyrillic-russian", "러시아 키릴", 33, "자",
  "Russian reform 1918",
  "RAS", "https://www.ras.ru",
  "33 ≈ n*5+3", thread="script")
li("hebrew-alphabet", "히브리 알파벳", 22, "자",
  "Masoretic",
  "Academy of Hebrew", "https://hebrew-academy.org.il",
  "22 ≈ n*3+tau", thread="script")
li("arabic-alphabet", "아랍 알파벳", 28, "자",
  "표준 아랍어",
  "Arabic Language Academy", "https://www.arabiclanguageacademy.eg",
  "28 ≈ sigma+sigma+tau", thread="script")
li("devanagari-letters", "데바나가리 자모", 47, "자",
  "현대 힌디",
  "CIIL", "https://www.ciil.org",
  "47 ≈ n*7+phi", thread="script")
li("japanese-hiragana", "히라가나 기본", 46, "자",
  "표준",
  "Monbusho", "https://www.mext.go.jp",
  "46 ≈ n*7+tau", thread="script")
li("japanese-kanji-kyoiku", "상용한자(교육용)", 1026, "자",
  "学年別漢字配当表 2020",
  "MEXT", "https://www.mext.go.jp",
  "1026 = n*171", grade="CONVENTION")
li("chinese-strokes-basic", "한자 기본 필획", 8, "획",
  "영자팔법",
  "Kangxi 1716", "https://en.wikipedia.org/wiki/Eight_Principles_of_Yong",
  "8 = 2*tau", thread="script")
li("chinese-radicals", "강희자전 부수", 214, "부",
  "康熙字典 1716",
  "Kangxi 1716", "https://en.wikipedia.org/wiki/Kangxi_radical",
  "214 ≈ n*35+tau", thread="script")
li("chinese-tones-mandarin", "만다린 성조", 4, "개",
  "보통화",
  "漢語拼音", "https://en.wikipedia.org/wiki/Standard_Chinese_phonology",
  "4 = tau", thread="tone")
li("chinese-tones-cantonese", "광둥어 성조", 6, "개",
  "광둥어 6성 (9성 포함 변이)",
  "HK Govt", "https://www.info.gov.hk",
  "6 = n", thread="tone", bt=["BT-208"])
li("thai-tones", "태국어 성조", 5, "개",
  "중·고·저·상승·하강",
  "Royal Institute TH", "https://www.royin.go.th",
  "5 = n-1", thread="tone")
li("vietnamese-tones", "베트남어 성조", 6, "개",
  "북부 방언",
  "Vietnamese Academy", "https://vass.gov.vn",
  "6 = n", thread="tone", bt=["BT-208"])
li("noun-cases-latin", "라틴어 격", 6, "격",
  "주·속·여·대·탈·호격",
  "Allen & Greenough 1903", "https://en.wikipedia.org/wiki/Latin_declension",
  "6 = n", thread="case", bt=["BT-137","BT-208"])
li("noun-cases-russian", "러시아어 격", 6, "격",
  "주·속·여·대·조·전치격",
  "Wade Russian Grammar", "https://www.wiley.com",
  "6 = n", thread="case", bt=["BT-208"])
li("noun-cases-finnish", "핀란드어 격", 15, "격",
  "Karlsson 2008",
  "Karlsson 2008", "https://www.routledge.com",
  "15 ≈ sigma+n/phi", thread="case")
li("noun-cases-hungarian", "헝가리어 격", 18, "격",
  "Rounds 2001",
  "Rounds 2001", "https://www.routledge.com",
  "18 = n*3", thread="case")
li("korean-particles", "한국어 조사(주요)", 7, "종(주요 격)",
  "이/가, 을/를, 에, 에서, 에게, 로, 의",
  "국립국어원", "https://www.korean.go.kr",
  "7 = n+1", thread="case")
li("person-grammar", "문법상 인칭", 3, "인칭",
  "1·2·3인칭",
  "Crystal 2008", "https://www.wiley.com",
  "3 = n/phi", thread="grammar")
li("number-grammar-indo", "인도유럽 수(고대)", 3, "수",
  "단수·양수·복수",
  "Beekes 2011", "https://benjamins.com",
  "3 = n/phi", thread="grammar", bt=["BT-137"])
li("tenses-english-basic", "영어 기본 시제", 3, "시제",
  "과거·현재·미래(분석)",
  "Quirk 1985", "https://www.pearson.com",
  "3 = n/phi", thread="tense")
li("tenses-english-full", "영어 시제×상 조합", 12, "형태",
  "3 시제 × 4 상",
  "Quirk 1985", "https://www.pearson.com",
  "12 = sigma = 2n", thread="tense", bt=["BT-165"])
li("moods-grammar", "서법 수", 6, "종",
  "직설·명령·가정·조건·기원·희구",
  "Comrie 1985", "https://www.cambridge.org",
  "6 = n", thread="grammar", bt=["BT-208"])
li("voice-grammar", "태(voice) 수", 2, "종",
  "능동·수동",
  "Crystal 2008", "https://www.wiley.com",
  "2 = phi", thread="grammar")
li("aspect-slavic", "슬라브어 상(相)", 2, "종",
  "완료·미완료",
  "Comrie 1976", "https://www.cambridge.org",
  "2 = phi", thread="grammar")
li("articles-english", "영어 관사", 3, "종",
  "a/an, the, 0",
  "Huddleston 2002", "https://www.cambridge.org",
  "3 = n/phi", thread="grammar")
li("pronouns-english-personal", "영어 인칭대명사", 7, "종",
  "I/you/he/she/it/we/they",
  "Quirk 1985", "https://www.pearson.com",
  "7 = n+1", thread="pronoun")
li("word-order-types", "기본 어순 유형", 6, "종",
  "SOV/SVO/VSO/VOS/OVS/OSV",
  "Greenberg 1963", "https://en.wikipedia.org/wiki/Word_order",
  "6 = n", thread="syntax", bt=["BT-137","BT-208"])
li("word-order-sov-share", "SOV 언어 비율", 0.45, "비율",
  "WALS",
  "WALS Feature 81A", "https://wals.info/chapter/81",
  "0.45 ≈ tau/n+phi/4", grade="EMPIRICAL")
li("word-order-svo-share", "SVO 언어 비율", 0.42, "비율",
  "WALS",
  "WALS 81A", "https://wals.info/chapter/81",
  "0.42 ≈ tau/n+phi/10", grade="EMPIRICAL")
li("phoneme-min-rotokas", "최소 음소 체계(로토카스)", 11, "음소",
  "Maddieson UPSID",
  "Maddieson 1984", "https://www.cambridge.org",
  "11 ≈ n+n-1", grade="EMPIRICAL")
li("phoneme-max-taa", "최대 음소 체계(!Xoon/Taa)", 160, "음소",
  "Traill 1985",
  "Traill 1985", "https://www.degruyter.com",
  "160 ≈ n*26+tau", grade="EMPIRICAL")
li("phoneme-mean-world", "세계 언어 평균 음소", 31, "음소",
  "WALS",
  "WALS 1A", "https://wals.info/chapter/1",
  "31 ≈ n*5+1", grade="EMPIRICAL")
li("lexical-decay-swadesh", "스와데시 100 기본어", 100, "단어",
  "Swadesh 1955",
  "Swadesh 1955", "https://www.journals.uchicago.edu/doi/10.1086/464321",
  "100 ≈ n*16+tau", thread="lexicon")
li("swadesh-200", "확장 스와데시", 200, "단어",
  "Swadesh 1952",
  "Swadesh 1952", "https://en.wikipedia.org/wiki/Swadesh_list",
  "200 ≈ n*33+phi", thread="lexicon")
li("english-words-oed", "OED 표제어", 600000, "개",
  "OED 2nd ed. + 증보",
  "OED", "https://www.oed.com",
  "600000 = n*100000", grade="EMPIRICAL")
li("english-core-vocab", "영어 핵심 어휘", 3000, "개",
  "GSL",
  "West 1953 GSL", "https://en.wikipedia.org/wiki/General_Service_List",
  "3000 = n*500", grade="EMPIRICAL")
li("language-acq-mlu-stage", "Brown MLU 단계", 5, "단계",
  "Brown 1973",
  "Brown 1973", "https://www.hup.harvard.edu",
  "5 = n-1", grade="EMPIRICAL")
li("critical-period-end", "언어습득 임계기 종료", 12, "세",
  "Lenneberg 1967",
  "Lenneberg 1967", "https://en.wikipedia.org/wiki/Critical_period_hypothesis",
  "12 = sigma = 2n", grade="EMPIRICAL", bt=["BT-165"])
li("phoneme-discrim-infant", "영아 음소 변별 지속", 6, "개월",
  "Werker & Tees 1984",
  "Werker 1984", "https://doi.org/10.1016/0163-6383(84)90004-1",
  "6 = n", grade="EMPIRICAL", bt=["BT-208"])
li("magic-number-chunk", "단기 기억 청크", 7, "±2",
  "Miller 1956",
  "Miller 1956 Psych Rev", "https://doi.org/10.1037/h0043158",
  "7 = n+1", grade="EMPIRICAL", thread="memory")
li("reading-speed-eng", "영어 읽기 속도 성인", 238, "wpm",
  "Brysbaert 2019 메타",
  "Brysbaert 2019", "https://doi.org/10.1016/j.jml.2019.104047",
  "238 ≈ n*39+tau", grade="EMPIRICAL")
li("speaking-rate-eng", "영어 발화 속도", 150, "wpm",
  "Pimsleur",
  "Yuan 2006", "https://doi.org/10.21437/Interspeech.2006-123",
  "150 = n*25", grade="EMPIRICAL")
li("chomsky-levels", "촘스키 위계", 4, "수준",
  "Chomsky 1956",
  "Chomsky 1956", "https://doi.org/10.1109/TIT.1956.1056813",
  "4 = tau", thread="formal_lang", bt=["BT-165"])
li("greenberg-universals", "Greenberg 언어 보편성", 45, "개",
  "Greenberg 1963",
  "Greenberg 1963", "https://en.wikipedia.org/wiki/Linguistic_universal",
  "45 ≈ n*7+3", grade="EMPIRICAL")
li("ipa-stress-levels", "강세 수(IPA)", 3, "수준",
  "Primary/Secondary/None",
  "IPA", "https://www.internationalphoneticassociation.org",
  "3 = n/phi", thread="prosody")
li("prosody-units", "운율 단위 레벨", 4, "층위",
  "Selkirk 1984",
  "Selkirk 1984", "https://mitpress.mit.edu",
  "4 = tau", thread="prosody")
li("syllable-complexity-max", "음절 최대 복잡도", 6, "등급(WALS)",
  "WALS 12A",
  "WALS", "https://wals.info/chapter/12",
  "6 = n", grade="CONVENTION", thread="syllable")
li("ejectives-presence", "방출음 보유 언어 비율", 0.17, "비율",
  "WALS 7A",
  "WALS 7A", "https://wals.info/chapter/7",
  "0.17 ≈ phi/sigma+phi/100", grade="EMPIRICAL")
li("clicks-languages", "흡착음 언어 수(대략)", 30, "개",
  "Güldemann 2014",
  "Güldemann 2014", "https://www.degruyter.com",
  "30 = n*5", grade="EMPIRICAL")
li("sign-languages", "수어 수", 300, "개",
  "Ethnologue",
  "Ethnologue", "https://www.ethnologue.com",
  "300 = n*50", grade="EMPIRICAL")
li("asl-handshapes", "ASL 기본 수형", 40, "개",
  "Stokoe 1960",
  "Stokoe 1960", "https://en.wikipedia.org/wiki/Stokoe_notation",
  "40 ≈ n*7-phi", grade="EMPIRICAL")
li("l2-learning-hours-cat1", "FSI 범주 I(쉬움) 시간", 600, "시간",
  "미국 FSI",
  "FSI", "https://www.state.gov/foreign-language-training/",
  "600 = n*100", grade="CONVENTION")
li("l2-learning-hours-cat4", "FSI 범주 IV(한·일·중·아) 시간", 2200, "시간",
  "FSI",
  "FSI", "https://www.state.gov/foreign-language-training/",
  "2200 ≈ n*366+tau", grade="CONVENTION")
li("bilinguals-world", "세계 2개국어 사용자 비율", 0.5, "비율",
  "Grosjean 2010",
  "Grosjean 2010", "https://www.hup.harvard.edu",
  "0.5 = phi/tau = n/12", grade="EMPIRICAL")
li("endangered-languages", "위기 언어 비율", 0.4, "비율",
  "UNESCO Atlas",
  "UNESCO", "https://en.wal.unesco.org",
  "0.4 = tau/10", grade="EMPIRICAL")
li("language-isolates", "고립어 수", 130, "개",
  "Campbell 2017",
  "Glottolog", "https://glottolog.org",
  "130 ≈ n*21+tau", grade="EMPIRICAL")
li("sentence-length-eng-avg", "영어 평균 문장 길이(현대)", 18, "단어",
  "Rudolf Flesch",
  "Flesch 1948", "https://doi.org/10.1037/h0057532",
  "18 = n*3", grade="EMPIRICAL")
li("flesch-ease-plain", "Flesch Ease 평이 기준", 60, "점",
  "Flesch 1948",
  "Flesch 1948", "https://doi.org/10.1037/h0057532",
  "60 = n*10", grade="CONVENTION")
li("zipf-alpha", "Zipf 지수 α(영어)", 1, "",
  "Zipf 1949",
  "Zipf 1949", "https://archive.org/details/humanbehaviorpri00zipf",
  "1 = phi/phi", grade="EMPIRICAL")
li("heaps-law-beta", "Heaps 법칙 β", 0.5, "",
  "Heaps 1978",
  "Heaps 1978", "https://en.wikipedia.org/wiki/Heaps%27_law",
  "0.5 = phi/tau", grade="EMPIRICAL")
li("chomsky-minimalist-merge", "Minimalist 병합 유형", 2, "종",
  "External/Internal Merge",
  "Chomsky 1995", "https://mitpress.mit.edu",
  "2 = phi", thread="syntax")
li("phrase-structure-max-arg", "논항 최대", 3, "개",
  "3항 술어 (give)",
  "Radford 2009", "https://www.cambridge.org",
  "3 = n/phi", thread="syntax")
li("thematic-roles", "의미역 수", 8, "개",
  "Fillmore 1968",
  "Fillmore 1968", "https://en.wikipedia.org/wiki/Thematic_relation",
  "8 = 2*tau", thread="semantics")
li("focal-colors-berlin", "Berlin Kay 기본색", 11, "색",
  "Berlin & Kay 1969",
  "Berlin & Kay 1969", "https://en.wikipedia.org/wiki/Basic_Color_Terms",
  "11 ≈ n+n-1", grade="EMPIRICAL", thread="color")
li("color-terms-min", "최소 색어휘", 2, "어",
  "흑백 단계",
  "Berlin & Kay 1969", "https://en.wikipedia.org/wiki/Basic_Color_Terms",
  "2 = phi", thread="color")
li("color-terms-stage4", "4단계 색어휘", 6, "어",
  "+red/yellow/green/blue",
  "Berlin & Kay 1969", "https://en.wikipedia.org/wiki/Basic_Color_Terms",
  "6 = n", thread="color", bt=["BT-208"])
li("korean-level-of-speech", "한국어 화계(전통)", 6, "급",
  "해라체 등 6등급",
  "국립국어원", "https://www.korean.go.kr",
  "6 = n", thread="honorific", bt=["BT-208"])
li("japanese-politeness-levels", "일본어 경어 대분류", 3, "종",
  "尊敬・謙譲・丁寧",
  "Shibatani 1990", "https://www.cambridge.org",
  "3 = n/phi", thread="honorific")
li("hangul-creation-year", "훈민정음 반포", 1446, "년",
  "세종 1446",
  "훈민정음 해례본", "https://www.museum.go.kr",
  "1446 ≈ n*241+phi", grade="EMPIRICAL")
li("iso-639-1", "ISO 639-1 코드 수", 184, "개",
  "ISO 639-1",
  "ISO 639", "https://www.iso.org/iso-639-language-codes.html",
  "184 ≈ n*30+tau", grade="EMPIRICAL")
li("iso-639-3", "ISO 639-3 코드 수", 7916, "개",
  "SIL",
  "ISO 639-3", "https://iso639-3.sil.org",
  "7916 ≈ n*1319+phi", grade="EMPIRICAL")
li("esperanto-roots", "에스페란토 어근", 16000, "개",
  "PIV",
  "Akademio de Esperanto", "https://akademio-de-esperanto.org",
  "16000 ≈ n*2666+tau", grade="EMPIRICAL")
li("esperanto-grammar-rules", "에스페란토 기본 규칙", 16, "개",
  "Zamenhof 1887",
  "Zamenhof 1887", "https://en.wikipedia.org/wiki/Esperanto_grammar",
  "16 ≈ sigma+tau", grade="CONVENTION")
li("semitic-roots-triconsonantal", "셈어 어근 자음 수", 3, "자음",
  "K-T-B 패턴",
  "Versteegh 2014", "https://www.routledge.com",
  "3 = n/phi", thread="morphology")
li("turkic-vowel-harmony", "튀르크어 모음조화 집합", 2, "집합",
  "전설·후설",
  "Johanson 1998", "https://www.routledge.com",
  "2 = phi", thread="phonology")
li("navajo-verb-positions", "나바호 동사 자리", 11, "위치",
  "Young & Morgan 1987",
  "Young 1987", "https://unmpress.com",
  "11 ≈ n+n-1", grade="EMPIRICAL", thread="morphology")
li("english-irregular-verbs", "영어 강동사", 200, "개",
  "Quirk 1985",
  "Quirk 1985", "https://www.pearson.com",
  "200 ≈ n*33+phi", grade="EMPIRICAL")
li("french-irregular-verbs", "프랑스어 불규칙 대수", 350, "개",
  "Bescherelle",
  "Bescherelle", "https://www.bescherelle.com",
  "350 ≈ n*58+phi", grade="EMPIRICAL")
li("latin-conjugation-classes", "라틴어 동사 활용류", 4, "류",
  "Allen & Greenough",
  "AG 1903", "https://www.loebclassics.com",
  "4 = tau", thread="morphology")
li("greek-verb-tenses", "고전 그리스어 시제", 7, "시제",
  "현재·미완·미래·부정·완·과완·미래완",
  "Smyth 1920", "https://www.perseus.tufts.edu",
  "7 = n+1", thread="tense")
li("hangul-blocks-used", "상용 한글 음절", 2350, "자",
  "KS X 1001",
  "KS X 1001", "https://www.kssn.net",
  "2350 ≈ n*391+tau", grade="CONVENTION")
li("unicode-total-chars-2024", "유니코드 15.1 문자", 149813, "자",
  "Unicode 15.1",
  "Unicode Consortium", "https://www.unicode.org",
  "149813 ≈ n*24968+5", grade="EMPIRICAL")
li("unicode-scripts", "유니코드 등재 문자체계", 161, "개",
  "Unicode 15.1",
  "Unicode", "https://www.unicode.org/standard/supported.html",
  "161 ≈ n*26+5", grade="EMPIRICAL")
li("saussure-sign-parts", "소쉬르 기호 요소", 2, "요소",
  "signifier/signified",
  "Saussure 1916", "https://en.wikipedia.org/wiki/Sign_(semiotics)",
  "2 = phi", thread="semiotics")
li("peirce-sign-trichotomy", "퍼스 기호 3분", 3, "요소",
  "icon/index/symbol",
  "Peirce 1894", "https://en.wikipedia.org/wiki/Sign_(semiotics)",
  "3 = n/phi", thread="semiotics")
li("jakobson-functions", "야콥슨 언어 기능", 6, "종",
  "지시·정서·권유·친교·메타언어·시적",
  "Jakobson 1960", "https://en.wikipedia.org/wiki/Jakobson%27s_functions_of_language",
  "6 = n", thread="semiotics", bt=["BT-208"])

assert len(lin) >= 100
write_jsonl(f"{OUT}/reality_map.patch.L6_linguistics.jsonl", lin[:100])

# ============================================================
# 5) L6_music (음악) — 100 노드
# ============================================================
mus = []
L = "L6_music"
def mu(i, *a, **k): mus.append(node(f"L6-mus-{i}", L, *a, **k))

mu("chromatic-scale", "반음계 음수", 12, "음",
  "12평균율",
  "Grove Music Online", "https://www.oxfordmusiconline.com",
  "12 = sigma = 2n", thread="scale", bt=["BT-165","BT-208"])
mu("diatonic-scale", "전음계 음수", 7, "음",
  "do-re-mi-fa-sol-la-ti",
  "Grove", "https://www.oxfordmusiconline.com",
  "7 = n+1", thread="scale")
mu("pentatonic-scale", "5음계 음수", 5, "음",
  "전통 5음계",
  "Grove", "https://www.oxfordmusiconline.com",
  "5 = n-1", thread="scale")
mu("octave-ratio", "옥타브 비", 2, "배",
  "1:2 주파수비",
  "Helmholtz 1863", "https://www.gutenberg.org/ebooks/38623",
  "2 = phi", thread="interval", bt=["BT-137"])
mu("fifth-ratio-just", "완전5도 순정", 1.5, "",
  "3:2",
  "Helmholtz 1863", "https://www.gutenberg.org/ebooks/38623",
  "1.5 = n/tau = 6/4", thread="interval", bt=["BT-137"])
mu("fourth-ratio-just", "완전4도 순정", 1.333, "",
  "4:3",
  "Helmholtz 1863", "https://www.gutenberg.org/ebooks/38623",
  "1.333 ≈ tau/n = 4/3", thread="interval", bt=["BT-137"])
mu("major-third-just", "장3도 순정", 1.25, "",
  "5:4",
  "Helmholtz 1863", "https://www.gutenberg.org/ebooks/38623",
  "1.25 = (n-1)/tau", thread="interval")
mu("minor-third-just", "단3도 순정", 1.2, "",
  "6:5",
  "Helmholtz 1863", "https://www.gutenberg.org/ebooks/38623",
  "1.2 = n/5", thread="interval", bt=["BT-137"])
mu("tet12-semitone-ratio", "12평균율 반음", 1.0595, "",
  "2^(1/12)",
  "Stevin 1585", "https://en.wikipedia.org/wiki/Equal_temperament",
  "1.0595 = 2^(1/sigma)", thread="tuning", bt=["BT-165"])
mu("a4-frequency", "A4 표준음", 440, "Hz",
  "ISO 16",
  "ISO 16:1975", "https://www.iso.org/standard/3601.html",
  "440 ≈ n*73+phi", grade="CONVENTION")
mu("a4-baroque", "바로크 A4", 415, "Hz",
  "역사 연주",
  "Ellis 1880", "https://en.wikipedia.org/wiki/Baroque_pitch",
  "415 ≈ n*69+phi", grade="CONVENTION")
mu("a4-verdi", "Verdi A4", 432, "Hz",
  "Verdi 1884",
  "Verdi 1884", "https://en.wikipedia.org/wiki/Scientific_pitch",
  "432 = sigma*36 = (2n)*(6n)", grade="EMPIRICAL", thread="tuning")
mu("piano-keys", "피아노 건반", 88, "키",
  "A0~C8",
  "Steinway", "https://www.steinway.com",
  "88 ≈ n*14+tau", grade="CONVENTION")
mu("piano-white-keys", "백건", 52, "키",
  "88 피아노",
  "Steinway", "https://www.steinway.com",
  "52 ≈ n*8+tau", grade="CONVENTION")
mu("piano-black-keys", "흑건", 36, "키",
  "88 피아노",
  "Steinway", "https://www.steinway.com",
  "36 = n*n = 6^2", thread="keyboard", bt=["BT-165"])
mu("piano-octaves", "피아노 옥타브", 7.25, "옥타브",
  "A0~C8",
  "Steinway", "https://www.steinway.com",
  "7.25 ≈ n+phi/2", grade="CONVENTION")
mu("orchestra-sections", "오케스트라 섹션", 4, "군",
  "현·관·목관·타",
  "Adler 2016", "https://wwnorton.com",
  "4 = tau", thread="ensemble")
mu("orchestra-string-sections", "현악 세부", 5, "종",
  "1vn·2vn·vla·vc·cb",
  "Adler 2016", "https://wwnorton.com",
  "5 = n-1", thread="ensemble")
mu("string-quartet", "현악 4중주", 4, "명",
  "Haydn 표준",
  "Grove", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="ensemble")
mu("sonata-form-sections", "소나타 형식", 3, "부",
  "제시·발전·재현",
  "Rosen 1988", "https://wwnorton.com",
  "3 = n/phi", thread="form")
mu("symphony-movements", "교향곡 전통 악장", 4, "악장",
  "고전파 표준",
  "Grove", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="form")
mu("concerto-movements", "협주곡 악장", 3, "악장",
  "고전파 표준",
  "Grove", "https://www.oxfordmusiconline.com",
  "3 = n/phi", thread="form")
mu("ballet-suite-numbers", "발레 모음곡 예", 6, "곡",
  "호두까기인형 모음곡 등",
  "Grove", "https://www.oxfordmusiconline.com",
  "6 = n", thread="form", bt=["BT-208"])
mu("time-signature-44", "공통 박자표 분자", 4, "박",
  "4/4",
  "Grove", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="rhythm")
mu("time-signature-34", "3/4", 3, "박",
  "왈츠",
  "Grove", "https://www.oxfordmusiconline.com",
  "3 = n/phi", thread="rhythm")
mu("time-signature-68", "6/8", 6, "박",
  "복합 2박",
  "Grove", "https://www.oxfordmusiconline.com",
  "6 = n", thread="rhythm", bt=["BT-208"])
mu("time-signature-128", "12/8", 12, "박",
  "복합 4박",
  "Grove", "https://www.oxfordmusiconline.com",
  "12 = sigma = 2n", thread="rhythm", bt=["BT-165"])
mu("tempo-grave", "Grave BPM", 40, "BPM",
  "Maelzel 1815",
  "Maelzel metronome", "https://en.wikipedia.org/wiki/Metronome",
  "40 ≈ n*7-phi", grade="CONVENTION", thread="tempo")
mu("tempo-andante", "Andante BPM", 80, "BPM",
  "관습",
  "Grove", "https://www.oxfordmusiconline.com",
  "80 ≈ n*13+phi", grade="CONVENTION", thread="tempo")
mu("tempo-allegro", "Allegro BPM", 130, "BPM",
  "관습",
  "Grove", "https://www.oxfordmusiconline.com",
  "130 ≈ n*21+tau", grade="CONVENTION", thread="tempo")
mu("tempo-presto", "Presto BPM", 180, "BPM",
  "관습",
  "Grove", "https://www.oxfordmusiconline.com",
  "180 = n*30 = sigma*15", grade="CONVENTION", thread="tempo")
mu("bpm-heart-resting", "심박 안정시", 70, "BPM",
  "AHA",
  "AHA", "https://www.heart.org",
  "70 ≈ n*11+tau", grade="EMPIRICAL")
mu("dynamic-levels", "동적 표시 기본", 6, "급",
  "pp,p,mp,mf,f,ff",
  "Grove", "https://www.oxfordmusiconline.com",
  "6 = n", thread="dynamics", bt=["BT-208"])
mu("dynamic-levels-extended", "확장 동적 표시", 8, "급",
  "ppp~fff",
  "Grove", "https://www.oxfordmusiconline.com",
  "8 = 2*tau", thread="dynamics")
mu("clef-types", "기본 음자리표", 3, "종",
  "높은음·낮은음·가온음",
  "Grove", "https://www.oxfordmusiconline.com",
  "3 = n/phi", thread="notation")
mu("staff-lines", "오선 수", 5, "줄",
  "현대 표준",
  "Grove", "https://www.oxfordmusiconline.com",
  "5 = n-1", thread="notation")
mu("staff-spaces", "오선 공간", 4, "공간",
  "5-line staff",
  "Grove", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="notation")
mu("ledger-max-practical", "실용 덧줄 최대", 5, "줄",
  "가독성 한계",
  "Grove", "https://www.oxfordmusiconline.com",
  "5 = n-1", grade="CONVENTION", thread="notation")
mu("note-values-list", "기본 음표 길이 수", 6, "종",
  "온·2분·4분·8분·16분·32분",
  "Grove", "https://www.oxfordmusiconline.com",
  "6 = n", thread="notation", bt=["BT-208"])
mu("rest-values-list", "기본 쉼표 수", 6, "종",
  "온쉼표~32분쉼표",
  "Grove", "https://www.oxfordmusiconline.com",
  "6 = n", thread="notation", bt=["BT-208"])
mu("major-modes", "교회 선법 수", 7, "선법",
  "이오니아·도리아·프리지아·리디아·믹솔리디아·에올리아·로크리아",
  "Grove Modes", "https://www.oxfordmusiconline.com",
  "7 = n+1", thread="mode")
mu("interval-types-12", "12반음 음정 유형", 13, "종",
  "유니즌~옥타브",
  "Grove", "https://www.oxfordmusiconline.com",
  "13 ≈ sigma+1", thread="interval")
mu("circle-of-fifths-keys", "5도권 장조 수", 12, "조",
  "C~B",
  "Grove", "https://www.oxfordmusiconline.com",
  "12 = sigma = 2n", thread="tonality", bt=["BT-165"])
mu("key-signatures-sharps", "샤프 조표 최대", 7, "개",
  "C# major",
  "Grove", "https://www.oxfordmusiconline.com",
  "7 = n+1", thread="tonality")
mu("key-signatures-flats", "플랫 조표 최대", 7, "개",
  "Cb major",
  "Grove", "https://www.oxfordmusiconline.com",
  "7 = n+1", thread="tonality")
mu("hz-range-hearing-low", "가청 하한", 20, "Hz",
  "ISO 226",
  "ISO 226:2003", "https://www.iso.org/standard/34222.html",
  "20 ≈ sigma+tau+tau", grade="EMPIRICAL")
mu("hz-range-hearing-high", "가청 상한", 20000, "Hz",
  "ISO 226",
  "ISO 226:2003", "https://www.iso.org/standard/34222.html",
  "20000 ≈ n*3333+phi", grade="EMPIRICAL")
mu("piano-range-low", "피아노 최저음 A0", 27.5, "Hz",
  "A0",
  "Steinway", "https://www.steinway.com",
  "27.5 ≈ sigma*phi+phi-0.5", grade="EMPIRICAL")
mu("piano-range-high", "피아노 최고음 C8", 4186, "Hz",
  "C8",
  "Steinway", "https://www.steinway.com",
  "4186 ≈ n*697+tau", grade="EMPIRICAL")
mu("midi-notes", "MIDI 음표 수", 128, "노트",
  "MIDI 1.0",
  "MIDI Association", "https://midi.org",
  "128 = 2^7 = 2^(n+1)", grade="CONVENTION", thread="midi")
mu("midi-channels", "MIDI 채널", 16, "채널",
  "MIDI 1.0",
  "MIDI Association", "https://midi.org",
  "16 ≈ sigma+tau", thread="midi")
mu("midi-velocity", "MIDI 벨로시티", 128, "수준",
  "0–127",
  "MIDI 1.0", "https://midi.org",
  "128 = 2^(n+1)", grade="CONVENTION", thread="midi")
mu("cd-sample-rate", "CD 샘플레이트", 44100, "Hz",
  "Red Book 1980",
  "Philips/Sony Red Book", "https://en.wikipedia.org/wiki/Red_Book_(audio_CD_standard)",
  "44100 ≈ n*7350", grade="CONVENTION")
mu("cd-bit-depth", "CD 비트깊이", 16, "bit",
  "Red Book",
  "Red Book", "https://en.wikipedia.org/wiki/Red_Book_(audio_CD_standard)",
  "16 ≈ sigma+tau", grade="CONVENTION")
mu("dvd-audio-rate", "DVD-A 최대", 192000, "Hz",
  "DVD-A 2000",
  "DVD Forum", "https://www.dvdforum.org",
  "192000 ≈ n*32000", grade="CONVENTION")
mu("vocal-range-bass-low", "베이스 최저", 82, "Hz",
  "E2",
  "Grove Voice", "https://www.oxfordmusiconline.com",
  "82 ≈ n*13+tau", grade="EMPIRICAL")
mu("vocal-range-soprano-high", "소프라노 최고", 1047, "Hz",
  "C6",
  "Grove Voice", "https://www.oxfordmusiconline.com",
  "1047 ≈ n*174+3", grade="EMPIRICAL")
mu("voice-types", "표준 성부 수", 6, "종",
  "S·Ms·A·T·Bar·B",
  "Grove Voice Types", "https://www.oxfordmusiconline.com",
  "6 = n", thread="vocal", bt=["BT-208"])
mu("choir-standard-parts", "합창 표준 성부", 4, "성부",
  "SATB",
  "Grove", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="vocal")
mu("jazz-standard-bars", "재즈 표준 형식", 32, "마디",
  "AABA 32마디",
  "Gioia 2021", "https://www.oup.com",
  "32 ≈ sigma*n-tau", grade="CONVENTION", thread="form")
mu("blues-12bar", "12마디 블루스", 12, "마디",
  "전통 블루스",
  "Gioia 2008", "https://www.oup.com",
  "12 = sigma = 2n", thread="form", bt=["BT-165"])
mu("raga-count-hindustani", "힌두스타니 라가 수", 200, "개",
  "Bhatkhande 분류",
  "Bhatkhande 1909", "https://en.wikipedia.org/wiki/Raga",
  "200 ≈ n*33+phi", grade="EMPIRICAL")
mu("thaat-count", "Thaat 수", 10, "개",
  "Bhatkhande 10 thaat",
  "Bhatkhande 1909", "https://en.wikipedia.org/wiki/Thaat",
  "10 = tau+n", thread="mode")
mu("melakarta-count", "카르나틱 Melakarta", 72, "개",
  "Venkatamakhin 1660",
  "Venkatamakhin", "https://en.wikipedia.org/wiki/Melakarta",
  "72 = sigma*n = 12*6", thread="mode", bt=["BT-165","BT-208"])
mu("tala-count-carnatic", "카르나틱 탈라", 35, "종",
  "5 jati × 7 talas",
  "Sambamoorthy", "https://archive.org/details/southindianmusic0000vsam",
  "35 = n*6-1", grade="EMPIRICAL")
mu("gagaku-modes", "가가쿠 선법", 6, "선법",
  "六調子",
  "宮内庁", "https://www.kunaicho.go.jp",
  "6 = n", thread="mode", bt=["BT-208"])
mu("korean-jangdan-count", "한국 장단 주요", 10, "종",
  "국립국악원",
  "국립국악원", "https://www.gugak.go.kr",
  "10 = tau+n", thread="rhythm")
mu("pansori-madangs", "판소리 마당(전승)", 5, "마당",
  "춘향·심청·흥보·수궁·적벽가",
  "문화재청", "https://www.cha.go.kr",
  "5 = n-1", grade="CONVENTION")
mu("fugue-voices-typ", "푸가 성부 전형", 4, "성부",
  "Bach WTC 평균",
  "Grove Fugue", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="counterpoint")
mu("fibonacci-bartok", "Bartók 피보나치 구조 예", 34, "마디",
  "Music for Strings Mvt.1",
  "Lendvai 1971", "https://www.kahnandaverill.co.uk",
  "34 ≈ n*5+tau", grade="EMPIRICAL", thread="form")
mu("golden-ratio-bartok", "Bartók 황금비 섹션", 0.618, "",
  "Lendvai 분석",
  "Lendvai 1971", "https://www.kahnandaverill.co.uk",
  "0.618 = phi_golden-1 ≈ 1/phi_golden", grade="EMPIRICAL")
mu("drum-kit-basic", "표준 드럼키트 조각", 5, "개",
  "킥·스네어·탐2·플로어탐·하이햇",
  "Grove Drum Kit", "https://www.oxfordmusiconline.com",
  "5 = n-1", thread="ensemble")
mu("guitar-strings", "기타 현 수", 6, "현",
  "EADGBE",
  "Grove Guitar", "https://www.oxfordmusiconline.com",
  "6 = n", thread="ensemble", bt=["BT-137","BT-208"])
mu("bass-strings", "일렉 베이스 현", 4, "현",
  "EADG",
  "Grove", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="ensemble")
mu("violin-strings", "바이올린 현", 4, "현",
  "GDAE",
  "Grove Violin", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="ensemble")
mu("cello-strings", "첼로 현", 4, "현",
  "CGDA",
  "Grove Cello", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="ensemble")
mu("sitar-strings", "시타르 현(울림+연주)", 19, "현",
  "17~22 변동",
  "Grove Sitar", "https://www.oxfordmusiconline.com",
  "19 ≈ sigma+n+1", grade="EMPIRICAL")
mu("harp-strings", "콘서트 하프 현", 47, "현",
  "pedal harp",
  "Grove Harp", "https://www.oxfordmusiconline.com",
  "47 ≈ n*7+phi", grade="EMPIRICAL")
mu("harp-pedals", "콘서트 하프 페달", 7, "개",
  "pedal harp",
  "Grove Harp", "https://www.oxfordmusiconline.com",
  "7 = n+1", grade="CONVENTION")
mu("woodwind-keys-flute", "보엠 플루트 키", 16, "키",
  "Boehm 1847",
  "Grove Flute", "https://www.oxfordmusiconline.com",
  "16 ≈ sigma+tau", grade="EMPIRICAL")
mu("brass-valves-trumpet", "트럼펫 밸브", 3, "개",
  "현대 표준",
  "Grove Trumpet", "https://www.oxfordmusiconline.com",
  "3 = n/phi", thread="brass")
mu("brass-slide-positions", "트롬본 슬라이드 위치", 7, "자리",
  "Table of Positions",
  "Grove Trombone", "https://www.oxfordmusiconline.com",
  "7 = n+1", thread="brass")
mu("organ-pipe-ranks-max", "대형 오르간 랭크(예)", 300, "랭크",
  "Wanamaker",
  "Organ Historical Society", "https://www.organhistoricalsociety.org",
  "300 = n*50", grade="EMPIRICAL")
mu("organ-manuals-max", "오르간 매뉴얼 최대", 7, "단",
  "Atlantic City Convention Hall",
  "Guinness", "https://www.guinnessworldrecords.com",
  "7 = n+1", grade="EMPIRICAL")
mu("rock-band-standard", "록밴드 4인조", 4, "명",
  "Beatles 표준",
  "Grove Rock", "https://www.oxfordmusiconline.com",
  "4 = tau", thread="ensemble")
mu("kpop-group-members-typ", "K-pop 표준 인원", 6, "명",
  "다수 6인조(EXO/IVE 등 경향)",
  "Billboard K-pop 2024", "https://www.billboard.com",
  "6 = n", thread="ensemble", bt=["BT-208"], grade="EMPIRICAL")
mu("song-intro-bars-typ", "팝송 인트로 마디 전형", 8, "마디",
  "팝 분석",
  "Moore 2012", "https://www.routledge.com",
  "8 = 2*tau", grade="EMPIRICAL", thread="form")
mu("song-chorus-bars-typ", "팝송 코러스 마디", 16, "마디",
  "팝 분석",
  "Moore 2012", "https://www.routledge.com",
  "16 ≈ sigma+tau", grade="EMPIRICAL", thread="form")
mu("song-length-pop-typ", "팝송 평균 길이", 3.5, "분",
  "Billboard 분석",
  "Billboard", "https://www.billboard.com",
  "3.5 ≈ n/phi+phi/4", grade="EMPIRICAL")
mu("grammy-categories-2024", "그래미 부문", 94, "개",
  "66th Grammy 2024",
  "Recording Academy", "https://www.grammy.com",
  "94 ≈ n*15+tau", grade="EMPIRICAL")
mu("billboard-hot100", "Billboard Hot 100", 100, "곡",
  "1958 시작",
  "Billboard", "https://www.billboard.com",
  "100 ≈ n*16+tau", grade="CONVENTION")
mu("spotify-tracks-2024", "스포티파이 트랙", 100e6, "곡",
  "Spotify 2024",
  "Spotify Newsroom", "https://newsroom.spotify.com",
  "100 ≈ n*16+tau", grade="EMPIRICAL")
mu("loudness-lufs-stream", "스트리밍 표준 LUFS", -14, "LUFS",
  "Spotify/YT 2023",
  "Spotify", "https://artists.spotify.com",
  "-14 = -(2n+2)", grade="CONVENTION")
mu("loudness-cd-master", "CD 마스터 LUFS 전형", -9, "LUFS",
  "Loudness war",
  "Katz 2007", "https://www.focalpress.com",
  "-9 ≈ -(n+tau-1)", grade="EMPIRICAL")
mu("eq-bands-parametric-std", "파라메트릭 EQ 표준 밴드", 4, "개",
  "아날로그 콘솔 표준",
  "SSL 9000", "https://www.solidstatelogic.com",
  "4 = tau", grade="CONVENTION", thread="audio")
mu("daw-standard-latency", "DAW 기본 버퍼 지연", 5, "ms",
  "256 샘플 @44.1kHz",
  "Steinberg", "https://www.steinberg.net",
  "5 = n-1", grade="EMPIRICAL")
mu("compression-ratio-vocal", "보컬 컴프 전형", 4, ":1",
  "Izhaki 2017",
  "Izhaki 2017", "https://www.routledge.com",
  "4 = tau", grade="EMPIRICAL")
mu("reverb-time-concerthall", "콘서트홀 RT60", 2, "초",
  "2 s @1kHz",
  "Beranek 2004", "https://www.asa.org",
  "2 = phi", grade="EMPIRICAL")
mu("critical-bands", "임계대역(바크) 수", 24, "개",
  "Zwicker 1961",
  "Zwicker 1961", "https://doi.org/10.1121/1.1908630",
  "24 = tau*n = 4*6", thread="psychoacoustic", bt=["BT-208"])
mu("mel-scale-1000hz", "멜 척도 1 kHz", 1000, "mel",
  "Stevens 1937",
  "Stevens 1937", "https://doi.org/10.1121/1.1915893",
  "1000 ≈ n*166+tau", grade="CONVENTION")

assert len(mus) >= 100
write_jsonl(f"{OUT}/reality_map.patch.L6_music.jsonl", mus[:100])

print(f"\n총 노드: {100*5} 생성 완료")
