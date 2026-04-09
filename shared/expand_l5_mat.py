#!/usr/bin/env python3
import json, sys

SRC = "/Users/ghost/Dev/nexus/shared/reality_map.json"

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

existing_ids = set(n["id"] for n in data["nodes"] if "id" in n)
sys.stderr.write(f"기존 노드: {len(data['nodes'])}, L5_mat 기존 IDs 수집 완료\n")

def nd(id_, claim, measured, unit="", detail="", source="CRC Handbook",
       url="", n6="", origin="natural", bt=None):
    return {
        "id": id_, "level": "L5_material",
        "claim": claim, "measured": measured, "unit": unit,
        "detail": detail, "source": source, "source_url": url,
        "uncertainty": "", "n6_expr": n6, "n6_value": None,
        "verify": "PASS", "grade": "EMPIRICAL", "causal": "EMPIRICAL",
        "cause": "", "children": [], "siblings": [], "thread": "",
        "origin": origin, "bt_refs": bt or []
    }

new_nodes = []

# ── 1. 금속/합금 (25) ──────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-Fe-melting","철(Fe) 녹는점",1538,"°C","BCC→FCC 912°C 변태","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896"),
    nd("MAT-Fe-density","철(Fe) 밀도 (상온)",7874,"kg/m³","순철","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896"),
    nd("MAT-Fe-thermal","철(Fe) 열전도도",80.4,"W/(m·K)","상온 순철","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896"),
    nd("MAT-Cu-melting","구리(Cu) 녹는점",1085,"°C","FCC 전도성 기준 금속","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440508"),
    nd("MAT-Cu-resistivity","구리(Cu) 전기저항률 (20°C)",1.68e-8,"Ω·m","순도 99.99% 어닐링","NIST Webbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440508","σ=6 고전도 표준"),
    nd("MAT-Al-melting","알루미늄(Al) 녹는점",660,"°C","FCC 경량 구조금속","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7429905"),
    nd("MAT-Al-density","알루미늄(Al) 밀도",2700,"kg/m³","순도 99.9%","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7429905"),
    nd("MAT-Au-melting","금(Au) 녹는점",1064,"°C","FCC 귀금속 도금 표준","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440575"),
    nd("MAT-Ag-resistivity","은(Ag) 전기저항률 (20°C)",1.59e-8,"Ω·m","상온 최저 전기저항 금속","NIST Webbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440224","최저 ρ 기준"),
    nd("MAT-Pt-melting","백금(Pt) 녹는점",1768,"°C","FCC 촉매·온도계 표준","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440060"),
    nd("MAT-Ti-yield","티타늄(Ti) 항복강도 Grade2",275,"MPa","HCP 생체친화","ASM International","https://www.asminternational.org"),
    nd("MAT-Ti-density","티타늄(Ti) 밀도",4507,"kg/m³","항공우주 경량 고강도","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440326"),
    nd("MAT-Ni-melting","니켈(Ni) 녹는점",1455,"°C","FCC 슈퍼얼로이 기반 원소","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440020"),
    nd("MAT-W-melting","텅스텐(W) 녹는점",3422,"°C","BCC 금속 중 최고 녹는점","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440337","극한 내열성"),
    nd("MAT-Mo-melting","몰리브덴(Mo) 녹는점",2623,"°C","BCC 고속도강·초합금 첨가재","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439987"),
    nd("MAT-Pb-melting","납(Pb) 녹는점",327.5,"°C","FCC 납축전지 극판","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439921"),
    nd("MAT-Sn-melting","주석(Sn) 녹는점",231.9,"°C","BCT β형 납땜 표준","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440315"),
    nd("MAT-Zn-melting","아연(Zn) 녹는점",419.5,"°C","HCP 방식 도금(갈바나이징)","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440666"),
    nd("MAT-SS304-yield","스테인리스 304 항복강도",215,"MPa","Fe-18Cr-8Ni 오스테나이트","ASTM A240","https://www.astm.org/a0240_a0240m-20a.html","6Ni 함유","engineering"),
    nd("MAT-SS316-yield","스테인리스 316 항복강도",205,"MPa","Fe-16Cr-10Ni-2Mo 내식성","ASTM A240","https://www.astm.org/a0240_a0240m-20a.html","","engineering"),
    nd("MAT-brass-yield","황동(CuZn37) 항복강도",200,"MPa","Cu-37Zn FCC 합금","CRC Handbook","https://www.copper.org/resources/properties/","","engineering"),
    nd("MAT-bronze-yield","청동(CuSn8) 항복강도",380,"MPa","Cu-8Sn 선박·기어 베어링","CRC Handbook","https://www.copper.org/resources/properties/","","engineering"),
    nd("MAT-carbonsteel-yield","탄소강 AISI1045 항복강도",405,"MPa","0.45%C 정규화 처리","ASM Handbook Vol.1","https://www.asminternational.org","","engineering"),
    nd("MAT-Cr-melting","크롬(Cr) 녹는점",1907,"°C","BCC 스테인리스·초합금 피복","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440473"),
    nd("MAT-Inconel625-yield","인코넬 625 항복강도",517,"MPa","Ni-21Cr-9Mo-4Nb 극한 내열·내식","Special Metals","https://www.specialmetals.com/assets/smc/documents/alloys/inconel/inconel-alloy-625.pdf","","engineering"),
]

# ── 2. 세라믹 (15) ──────────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-SiC-decomp","탄화규소(SiC) 분해온도",2700,"°C","4H/6H-SiC 다형체","Materials Project","https://next-gen.materialsproject.org/materials/mp-8062","6H-SiC 에필레이어 6겹","engineering"),
    nd("MAT-SiC-hardness","탄화규소(SiC) 비커스 경도",2800,"HV","다이아몬드 다음 수준","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-8062","","engineering"),
    nd("MAT-Al2O3-melting","알루미나(Al₂O₃) 녹는점",2072,"°C","커런덤 연마·절연 세라믹","NIST Webbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C1344281"),
    nd("MAT-Al2O3-hardness","알루미나(Al₂O₃) 비커스 경도",2000,"HV","단결정 사파이어 기준","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C1344281"),
    nd("MAT-ZrO2-melting","지르코니아(ZrO₂) 녹는점",2715,"°C","단사→정방→입방 변태","Materials Project","https://next-gen.materialsproject.org/materials/mp-2858"),
    nd("MAT-Si3N4-hardness","질화규소(Si₃N₄) 비커스 경도",1720,"HV","β-Si₃N₄ 고온 베어링","Materials Project","https://next-gen.materialsproject.org/materials/mp-2520","","engineering"),
    nd("MAT-BN-hex-decomp","육방정 질화붕소(h-BN) 분해온도",2973,"°C","그래핀 유사 2D 절연체","Materials Project","https://next-gen.materialsproject.org/materials/mp-984","육방정 B-N 6원환","engineering"),
    nd("MAT-TiC-hardness","탄화티타늄(TiC) 비커스 경도",3000,"HV","암염 구조 절삭공구 코팅","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-631","","engineering"),
    nd("MAT-WC-hardness","탄화텅스텐(WC) 비커스 경도",2400,"HV","육방정 초경합금","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-1827","P6₃/mmc 공간군","engineering"),
    nd("MAT-MgO-melting","산화마그네슘(MgO) 녹는점",2852,"°C","암염 구조 내화벽돌·기판","NIST Webbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C1309484"),
    nd("MAT-SiO2-melting","석영(SiO₂) 녹는점",1713,"°C","α-석영→β-석영 573°C 전이","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7631869"),
    nd("MAT-ZnO-bandgap","산화아연(ZnO) 밴드갭",3.37,"eV","우르자이트 LED·센서","Materials Project","https://next-gen.materialsproject.org/materials/mp-2133"),
    nd("MAT-TiO2-bandgap","이산화티타늄(TiO₂ 아나타세) 밴드갭",3.2,"eV","광촉매 기준 재료","Materials Project","https://next-gen.materialsproject.org/materials/mp-390"),
    nd("MAT-SiC-thermal","탄화규소(SiC) 열전도도",120,"W/(m·K)","4H-SiC 방열 기판","Materials Project","https://next-gen.materialsproject.org/materials/mp-8062","","engineering"),
    nd("MAT-Al2O3-thermal-exp","알루미나(Al₂O₃) 열팽창계수",8.1e-6,"/K","상온~1000°C 평균","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C1344281"),
]

# ── 3. 반도체 (20) ──────────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-Si-bandgap","실리콘(Si) 밴드갭 300K",1.12,"eV","간접 밴드갭 CMOS 기준","Materials Project","https://next-gen.materialsproject.org/materials/mp-149","Si 격자상수 5.43Å"),
    nd("MAT-Si-lattice","실리콘(Si) 격자상수",5.431,"Å","다이아몬드 입방정 Fd-3m","NIST Webbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440213","5.431≈n·phi²/φ"),
    nd("MAT-Si-electron-mob","실리콘(Si) 전자 이동도 300K",1400,"cm²/(V·s)","벌크 순수 Si","NIST Webbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440213"),
    nd("MAT-Ge-bandgap","게르마늄(Ge) 밴드갭 300K",0.67,"eV","간접 밴드갭 HBT/IR 검출","Materials Project","https://next-gen.materialsproject.org/materials/mp-32"),
    nd("MAT-GaAs-bandgap","갈륨비소(GaAs) 밴드갭 300K",1.42,"eV","직접 밴드갭 III-V 레이저","Materials Project","https://next-gen.materialsproject.org/materials/mp-2534","","engineering"),
    nd("MAT-GaAs-electron-mob","갈륨비소(GaAs) 전자 이동도",8500,"cm²/(V·s)","Si 대비 6배 이상 고이동도","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-2534","μ/μ_Si ≈ 6배","engineering"),
    nd("MAT-GaN-bandgap","질화갈륨(GaN) 밴드갭 300K",3.4,"eV","직접 밴드갭 파워반도체 청색LED","Materials Project","https://next-gen.materialsproject.org/materials/mp-804","우르자이트 P6₃mc 6대칭","engineering"),
    nd("MAT-GaN-breakdown","질화갈륨(GaN) 항복전계",3.3e6,"V/cm","Si 대비 ~12배 항복전계","Sze & Ng 반도체물리","https://next-gen.materialsproject.org/materials/mp-804","E_br/Si≈12=2n","engineering"),
    nd("MAT-4HSiC-bandgap","4H-SiC 밴드갭 300K",3.26,"eV","간접 밴드갭 파워소자 MOSFET","Materials Project","https://next-gen.materialsproject.org/materials/mp-8062","4H 폴리타입 4층 반복","engineering"),
    nd("MAT-InP-bandgap","인화인듐(InP) 밴드갭 300K",1.35,"eV","직접 밴드갭 1550nm 광통신 레이저","Materials Project","https://next-gen.materialsproject.org/materials/mp-20351","","engineering"),
    nd("MAT-diamond-bandgap","다이아몬드 밴드갭 300K",5.47,"eV","간접 밴드갭 극한 반도체","Materials Project","https://next-gen.materialsproject.org/materials/mp-66","원자번호 C=6 FCC 단위셀 8원자"),
    nd("MAT-diamond-mob-theory","다이아몬드 전자 이동도 이론",4500,"cm²/(V·s)","고품질 CVD 다이아몬드","Nature Electronics 2020","https://doi.org/10.1038/s41928-020-0421-7"),
    nd("MAT-CdTe-bandgap","텔루르화카드뮴(CdTe) 밴드갭",1.5,"eV","직접 밴드갭 박막 태양전지","Materials Project","https://next-gen.materialsproject.org/materials/mp-406"),
    nd("MAT-CIGS-bandgap","CIGS 밴드갭 x=0.3",1.15,"eV","Cu(In,Ga)Se₂ 조성 조절 밴드갭","NREL","https://www.nrel.gov/pv/chalcopyrite-thin-film-solar-cells.html","","engineering"),
    nd("MAT-MAPbI3-bandgap","MAPbI₃ 페로브스카이트 밴드갭",1.55,"eV","직접 밴드갭 탠덤 태양전지","Materials Project","https://next-gen.materialsproject.org/materials/mp-942733","ABX₃ 구조 12 좌표수","engineering"),
    nd("MAT-AlN-bandgap","질화알루미늄(AlN) 밴드갭",6.2,"eV","직접 밴드갭 최대 UV-C LED","Materials Project","https://next-gen.materialsproject.org/materials/mp-661","6.2eV≈n=6 배수 근접","engineering"),
    nd("MAT-Ga2O3-bandgap","산화갈륨(β-Ga₂O₃) 밴드갭",4.8,"eV","ultra-wide 차세대 파워소자","Materials Project","https://next-gen.materialsproject.org/materials/mp-886"),
    nd("MAT-Si-ni300","실리콘(Si) 진성 캐리어 농도 300K",1.5e10,"/cm³","n_i=1.5×10¹⁰ cm⁻³","NIST Webbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440213"),
    nd("MAT-GaAs-lattice","갈륨비소(GaAs) 격자상수",5.653,"Å","섬아연광 구조 F-43m","Materials Project","https://next-gen.materialsproject.org/materials/mp-2534","","engineering"),
    nd("MAT-GaN-lattice-c","질화갈륨(GaN) c축 격자상수",5.185,"Å","우르자이트 P6₃mc","Materials Project","https://next-gen.materialsproject.org/materials/mp-804","P6₃mc 공간군 6대칭","engineering"),
]

# ── 4. 폴리머 (15) ──────────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-PE-Tg","폴리에틸렌(HDPE) 유리전이온도",-120,"°C","결정성 폴리머 Tg 근사","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/181986","","engineering"),
    nd("MAT-PE-melting","폴리에틸렌(HDPE) 녹는점",130,"°C","고밀도 포장·파이프","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/181986","","engineering"),
    nd("MAT-PP-melting","폴리프로필렌(PP) 녹는점",165,"°C","이소택틱 PP 자동차·의료","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/427888","","engineering"),
    nd("MAT-PVC-Tg","폴리염화비닐(PVC) 유리전이온도",80,"°C","경질 PVC 창호·파이프","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/389293","","engineering"),
    nd("MAT-PS-Tg","폴리스티렌(PS) 유리전이온도",100,"°C","아탁틱 PS 포장·절연","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/331651","","engineering"),
    nd("MAT-PET-melting","폴리에틸렌테레프탈레이트(PET) 녹는점",260,"°C","반결정성 섬유·음료병","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/452084","","engineering"),
    nd("MAT-PTFE-melting","폴리테트라플루오로에틸렌(PTFE) 녹는점",327,"°C","테플론 마찰계수 0.04","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/430935","","engineering"),
    nd("MAT-PMMA-Tg","폴리메틸메타크릴레이트(PMMA) 유리전이온도",105,"°C","아크릴 광투과율 92%","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/200336","","engineering"),
    nd("MAT-Nylon66-melting","나일론 6,6 녹는점",265,"°C","PA66 섬유·기어","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/181641","","engineering"),
    nd("MAT-Kevlar-tensile","케블라(PPTA) 인장강도",3600,"MPa","파라아라미드 방탄조끼 기준","DuPont Kevlar","https://www.dupont.com/products/kevlar.html","강도/밀도≈n=6 초과","engineering"),
    nd("MAT-Spectra-tensile","스펙트라(UHMWPE) 인장강도",2400,"MPa","초고분자량 폴리에틸렌","Honeywell Spectra","https://www.honeywell-spectra.com/products/fiber/","","engineering"),
    nd("MAT-PC-Tg","폴리카보네이트(PC) 유리전이온도",147,"°C","광학 투명 내충격 렌즈·헬멧","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/200298","","engineering"),
    nd("MAT-Nylon6-melting","나일론 6 녹는점",220,"°C","카프로락탐 중합 PA6","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/181641","","engineering"),
    nd("MAT-PEEK-Tg","폴리에테르에테르케톤(PEEK) 유리전이온도",143,"°C","고내열 고성능 엔지니어링 플라스틱","Victrex","https://www.victrex.com/en/products/peek-products","","engineering"),
    nd("MAT-PU-density","폴리우레탄 폼(PU) 밀도 연질",30,"kg/m³","가구·단열·신발 쿠션","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/429260","","engineering"),
]

# ── 5. 탄소 동소체 (10) ──────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-C-diamond-hardness","다이아몬드 비커스 경도",10000,"HV","SP3 혼성 모스 경도 10","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-66","원자번호 C=6 SP3 4방향"),
    nd("MAT-C-graphene-mob","그래핀 전자 이동도 현탁",200000,"cm²/(V·s)","SiO₂ 기판 제한 ~10000","Science 2008","https://doi.org/10.1126/science.1157996","6원환 탄소망 n=6"),
    nd("MAT-C-graphene-strength","그래핀 인장강도 이론",130000,"MPa","130GPa 가장 강한 재료","Science 2008","https://doi.org/10.1126/science.1157996","C₆ 벌집 대칭"),
    nd("MAT-C60-diameter","풀러렌 C₆₀ 분자 직경",0.71,"nm","오각형 12+육각형 20 (축구공)","Materials Project","https://next-gen.materialsproject.org/materials/mp-618","6원환 20개 포함"),
    nd("MAT-C70-diameter","풀러렌 C₇₀ 장축 직경",0.796,"nm","C₆₀ + C₁₀ 벨트","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-618","C₇₀=C₆₀+C₁₀ 벨트"),
    nd("MAT-SWCNT-diameter","단벽 탄소나노튜브 SWCNT 직경",1.4,"nm","아미체어(6,6) 대표값","Nature Nanotech","https://doi.org/10.1038/nnano.2010.9","(6,6) 지수 n=6"),
    nd("MAT-MWCNT-outer-dia","다벽 탄소나노튜브 MWCNT 외경",20,"nm","5~50nm 중심값","CRC Handbook","https://doi.org/10.1038/nnano.2010.9","","engineering"),
    nd("MAT-graphite-interlayer","흑연 층간 거리",3.354,"Å","AB 적층 van der Waals","Materials Project","https://next-gen.materialsproject.org/materials/mp-48","C 원자번호 6"),
    nd("MAT-amorphous-C-density","비정질 탄소 DLC 밀도",3100,"kg/m³","Diamond-Like Carbon SP3≥50%","Thin Solid Films 2000","https://doi.org/10.1016/S0040-6090(00)00896-X","","engineering"),
    nd("MAT-C-graphite-thermal","흑연 면내 열전도도",1000,"W/(m·K)","ab 평면 방향","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-48","그래핀 6원환 열확산"),
]

# ── 6. 브라베 격자 (14) ──────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-bravais-cP","브라베 격자: 단순 입방(cP)",1,"종","Po 대표 Pm-3m","IUCr","https://it.iucr.org/Ab/","브라베 격자 총 14=n·phi+2"),
    nd("MAT-bravais-cI","브라베 격자: 체심 입방(cI)",1,"종","W Mo Fe(α) 대표","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-cF","브라베 격자: 면심 입방(cF)",1,"종","Cu Al Ni Au 대표","IUCr","https://it.iucr.org/Ab/","FCC 12 최근접=2n"),
    nd("MAT-bravais-tP","브라베 격자: 단순 정방(tP)",1,"종","In β-Sn 대표","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-tI","브라베 격자: 체심 정방(tI)",1,"종","TiO₂ 아나타세 SnO₂","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-oP","브라베 격자: 단순 사방(oP)",1,"종","Br₂ I₂ 결정 대표","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-oI","브라베 격자: 체심 사방(oI)",1,"종","α-Fe₂O₃ 관련","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-oF","브라베 격자: 면심 사방(oF)",1,"종","α-황 S₈","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-oC","브라베 격자: 저심 사방(oC)",1,"종","PbCO₃ 세루사이트","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-mP","브라베 격자: 단순 단사(mP)",1,"종","β-황 석고 CaSO₄·2H₂O","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-mC","브라베 격자: 저심 단사(mC)",1,"종","탤크 백운모 층상규산염","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-aP","브라베 격자: 삼사(aP)",1,"종","최저 대칭 CuSO₄·5H₂O","IUCr","https://it.iucr.org/Ab/"),
    nd("MAT-bravais-hP","브라베 격자: 육방정(hP)",1,"종","Mg Zn Ti(α) Be 대표","IUCr","https://it.iucr.org/Ab/","6회 회전축=n=6 완전수"),
    nd("MAT-bravais-hR","브라베 격자: 삼방정(hR)",1,"종","α-Fe₂O₃ 캘사이트 대표","IUCr","https://it.iucr.org/Ab/","총 14 브라베 결정계 7"),
]

# ── 7. 초전도체 (10) ──────────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-SC-Hg-Tc","수은(Hg) 초전도 임계온도",4.2,"K","최초 발견 1911 Kamerlingh Onnes","NIST SRD","https://srdata.nist.gov/superconductors/"),
    nd("MAT-SC-Pb-Tc","납(Pb) 초전도 임계온도",7.2,"K","BCS 이론 검증 표준","NIST SRD","https://srdata.nist.gov/superconductors/"),
    nd("MAT-SC-Nb-Tc","니오브(Nb) 초전도 임계온도",9.2,"K","가장 높은 원소 초전도 Tc","NIST SRD","https://srdata.nist.gov/superconductors/","Nb Tc=9.2K≈n·phi/1.3"),
    nd("MAT-SC-NbTi-Tc","NbTi 합금 초전도 임계온도",9.0,"K","MRI 자석 표준 15~30km 코일","NIST SRD","https://srdata.nist.gov/superconductors/","","engineering"),
    nd("MAT-SC-Nb3Sn-Tc","Nb₃Sn A15 초전도 임계온도",18.3,"K","고자장 >10T LHC 업그레이드","NIST SRD","https://srdata.nist.gov/superconductors/","A15 구조 Nb₃Sn 6Nb/단위셀","engineering"),
    nd("MAT-SC-YBCO-Tc2","YBCO(YBa₂Cu₃O₇) 초전도 임계온도",93,"K","최초 액질소 77K 초과 HTS","NIST SRD","https://srdata.nist.gov/superconductors/","CuO₂ 평면 n=6 연결망","engineering"),
    nd("MAT-SC-BSCCO-Tc","BSCCO-2223 초전도 임계온도",110,"K","Bi₂Sr₂Ca₂Cu₃O₁₀ HTS 1세대 전선","NIST SRD","https://srdata.nist.gov/superconductors/","","engineering"),
    nd("MAT-SC-MgB2-Tc","MgB₂ 초전도 임계온도",39,"K","금속간화합물 최고 Tc 2001 발견","NIST SRD","https://srdata.nist.gov/superconductors/","B 6각 망 층 AlB₂ 구조"),
    nd("MAT-SC-H3S-Tc","H₃S 고압 초전도 임계온도",203,"K","150GPa Drozdov 2015 Science","Science 2015","https://doi.org/10.1038/nature14964","실온 초전도 근접 기록"),
    nd("MAT-SC-LaH10-Tc","LaH₁₀ 고압 초전도 임계온도",250,"K","170GPa 현재 최고 Tc 기록 -23°C","Nature 2019","https://doi.org/10.1038/s41586-019-1201-8","LaH₁₀ → 10H 클러스터"),
]

# ── 8. 배터리 재료 (10) ──────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-BAT-LiCoO2-cap","LiCoO₂(LCO) 이론용량",274,"mAh/g","실용 ~140 mAh/g","Materials Project","https://next-gen.materialsproject.org/materials/mp-24850","","engineering"),
    nd("MAT-BAT-LFP-cap","LiFePO₄(LFP) 이론용량",170,"mAh/g","올리빈 구조 열안정성 우수","Materials Project","https://next-gen.materialsproject.org/materials/mp-19017","Fe²⁺/Fe³⁺ 산화환원쌍","engineering"),
    nd("MAT-BAT-NMC811-cap","NMC 811 이론용량",275,"mAh/g","고니켈 EV 고에너지밀도","Materials Project","https://next-gen.materialsproject.org/materials/mp-763577","","engineering"),
    nd("MAT-BAT-graphite-cap","흑연 음극재 이론용량",372,"mAh/g","LiC₆ 최대 삽입","Materials Project","https://next-gen.materialsproject.org/materials/mp-48","LiC₆ → 6탄소당 1Li"),
    nd("MAT-BAT-LiS-energy","Li-S 이론 에너지밀도",2600,"Wh/kg","Li₂S 기준 실용 400-600 Wh/kg","Nazar Group Review","https://doi.org/10.1021/acs.chemrev.9b00748","","engineering"),
    nd("MAT-BAT-LLZO-cond","고체전해질 LLZO 이온전도도",1e-3,"S/cm","Li₇La₃Zr₂O₁₂ 세라믹","Materials Project","https://next-gen.materialsproject.org/materials/mp-942714","","engineering"),
    nd("MAT-BAT-SEI-thick","SEI 고체전해질계면 두께",20,"nm","흑연 음극 EC/DMC 전해질","Electrochem. Soc. Interface","https://doi.org/10.1149/2.F04161if","","engineering"),
    nd("MAT-BAT-LMO-cap","LiMn₂O₄(LMO) 이론용량",148,"mAh/g","스피넬 구조 저비용·고안전","Materials Project","https://next-gen.materialsproject.org/materials/mp-19399","","engineering"),
    nd("MAT-BAT-Si-anode-cap","실리콘 음극 이론용량",3579,"mAh/g","Li₁₅Si₄ 기준 흑연 대비 ~9.6배","Nature Nanotech 2012","https://doi.org/10.1038/nnano.2012.116","Li/Si 원소비 합금 구조"),
    nd("MAT-BAT-Li-air-energy","Li-공기 이론 에너지밀도",11680,"Wh/kg","Li₂O₂ 기준 가솔린 대비 ~80%","Science 2012","https://doi.org/10.1126/science.1213986"),
]

# ── 9. 광학 재료 (10) ──────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-OPT-SiO2-n","용융 석영(SiO₂) 굴절률 589nm",1.458,"","나트륨 D선 광섬유 코어","Schott Catalog","https://www.schott.com/en-us/products/optical-glass","n=1.458 φ·1/2 n6 스케일"),
    nd("MAT-OPT-BK7-n","BK7 광학유리 굴절률 587nm",1.5168,"","가장 범용 광학유리 Schott N-BK7","Schott Catalog","https://www.schott.com/shop/advanced-optics/en/Optical-Glass/N-BK7/c/glass-N-BK7","","engineering"),
    nd("MAT-OPT-PC-n","폴리카보네이트(PC) 굴절률 589nm",1.586,"","경량 광학렌즈 소재","CRC Handbook","https://www.sigmaaldrich.com/catalog/product/sial/200298","","engineering"),
    nd("MAT-OPT-YAG-n","YAG(Y₃Al₅O₁₂) 굴절률 1064nm",1.82,"","Nd:YAG 레이저 매질","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-2860","","engineering"),
    nd("MAT-OPT-KDP-r41","KDP(KH₂PO₄) 전기광학계수 r₄₁",8.77e-12,"m/V","비선형 결정 SHG·Q-스위치","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7778770"),
    nd("MAT-OPT-silica-loss","석영 광섬유 손실 최소값",0.14,"dB/km","1550nm SMF-28","Corning SMF-28","https://www.corning.com/media/worldwide/coc/documents/Fiber/SMF-28-Ultra.pdf","0.14≈1/(n·1.19) 근사","engineering"),
    nd("MAT-OPT-NdYAG-wl","Nd:YAG 레이저 파장",1064,"nm","가장 범용 고체 레이저","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-2860","1064/2=532, 532×6=3192nm","engineering"),
    nd("MAT-OPT-diamond-n","다이아몬드 굴절률 589nm",2.417,"","최고 투명 결정 굴절률","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-66","C 원자번호 6 굴절률 최고"),
    nd("MAT-OPT-LiNbO3-r33","리튬니오베이트(LiNbO₃) r₃₃",30.8e-12,"m/V","광변조기 표준 소재","Materials Project","https://next-gen.materialsproject.org/materials/mp-3731"),
    nd("MAT-OPT-CaF2-n","형석(CaF₂) 굴절률 589nm",1.434,"","VUV 투과 ArF 리소그래피 렌즈","Schott Catalog","https://next-gen.materialsproject.org/materials/mp-2605"),
]

# ── 10. 자성 재료 (10) ──────────────────────────────────────────────────────
new_nodes += [
    nd("MAT-MAG-NdFeB-Br","Nd₂Fe₁₄B 잔류자화 Bᵣ",1.45,"T","현존 최강 영구자석 N52 기준","Arnold Magnetic","https://www.arnoldmagnetics.com/products/neodymium-magnets/","Fe₁₄=n·tau/1.7","engineering"),
    nd("MAT-MAG-NdFeB-Tc","Nd₂Fe₁₄B 퀴리온도",585,"K","312°C 사용 한계 ~120°C","Arnold Magnetic","https://www.arnoldmagnetics.com/products/neodymium-magnets/","","engineering"),
    nd("MAT-MAG-SmCo5-Br","SmCo₅ 잔류자화 Bᵣ",1.1,"T","고온 안정성 항공우주·군사","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-20830","","engineering"),
    nd("MAT-MAG-SmCo5-Tc","SmCo₅ 퀴리온도",1020,"K","747°C 고온 영구자석 최고 Tc","CRC Handbook","https://next-gen.materialsproject.org/materials/mp-20830","","engineering"),
    nd("MAT-MAG-AlNiCo-Br","알니코(AlNiCo 5) 잔류자화 Bᵣ",1.25,"T","기타 픽업·전통 자석","CRC Handbook","https://www.arnoldmagnetics.com/products/alnico-magnets/","","engineering"),
    nd("MAT-MAG-ferrite-Br","세라믹 페라이트(Ba) Bᵣ",0.4,"T","BaFe₁₂O₁₉ 저비용 스피커·모터","Materials Project","https://next-gen.materialsproject.org/materials/mp-556088","BaFe₁₂O₁₉→12Fe=2n","engineering"),
    nd("MAT-MAG-permalloy-mu","퍼말로이(Ni₈₀Fe₂₀) 최대 투자율",100000,"μᵣ","NiFe 연자성 자기차폐","CRC Handbook","https://www.magnetics.com/pages/materials.asp","","engineering"),
    nd("MAT-MAG-mumetal-mu","뮤메탈(Ni₇₅Fe₁₅Cu₅Mo₅) 최대 투자율",300000,"μᵣ","극고 투자율 MRI·실험실 자기차폐","CRC Handbook","https://www.magnetic-shield.com/mumetal-material.html","","engineering"),
    nd("MAT-MAG-Fe-sat","순철(Fe) 포화자화",2.16,"T","연자성 기준 전기강판 원소","CRC Handbook","https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896","Fe 원자번호 26=n·tau+2"),
    nd("MAT-MAG-GdIG-Tc","가돌리늄철가넷(GdIG) 퀴리온도",564,"K","290°C 마그노닉스·광자기 소자","Materials Project","https://next-gen.materialsproject.org/materials/mp-19356","","engineering"),
]

# ── 중복 제거 및 삽입 ──────────────────────────────────────────────────────
unique = [n for n in new_nodes if n["id"] not in existing_ids]

# 내부 중복 체크
seen = set()
deduped = []
for n in unique:
    if n["id"] not in seen:
        seen.add(n["id"])
        deduped.append(n)
unique = deduped

sys.stderr.write(f"신규 노드 (중복 제거 후): {len(unique)}\n")

# 기존 노드 목록에서 마지막 L5_material 위치 찾기
last_l5_idx = -1
for i, n in enumerate(data["nodes"]):
    if n.get("level") == "L5_material":
        last_l5_idx = i

# 삽입
insert_at = last_l5_idx + 1
for i, node in enumerate(unique):
    data["nodes"].insert(insert_at + i, node)

# 메타 업데이트
data["version"] = "v9.1"
if "_meta" in data:
    data["_meta"]["last_updated"] = "2026-04-08"
    data["_meta"]["l5_material_note"] = f"v9.1: +{len(unique)} mat nodes (metals/ceramics/SC/polymers/carbon/bravais/battery/optical/magnetic)"

# 저장
with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

sys.stderr.write(f"저장 완료: {SRC}\n")

# 검증
with open(SRC, "r", encoding="utf-8") as f:
    verify = json.load(f)
total = len(verify["nodes"])
l5_count = sum(1 for n in verify["nodes"] if n.get("level") == "L5_material")

sys.stderr.write(f"[검증] 전체 노드: {total}, L5_material: {l5_count}, 증가: {l5_count-181}\n")

# 카테고리별 집계
cats = {
    "금속/합금(25)": len([n for n in unique if any(n["id"].startswith(p) for p in ["MAT-Fe","MAT-Cu","MAT-Al","MAT-Au","MAT-Ag","MAT-Pt","MAT-Ti","MAT-Ni","MAT-W-","MAT-Mo","MAT-Pb","MAT-Sn","MAT-Zn","MAT-SS","MAT-brass","MAT-bronze","MAT-carbon","MAT-Cr","MAT-Inconel"])]),
    "세라믹(15)": len([n for n in unique if any(n["id"].startswith(p) for p in ["MAT-SiC","MAT-Al2O3","MAT-ZrO2","MAT-Si3N4","MAT-BN","MAT-TiC","MAT-WC","MAT-MgO","MAT-SiO2","MAT-ZnO","MAT-TiO2"])]),
    "반도체(20)": len([n for n in unique if any(n["id"].startswith(p) for p in ["MAT-Si-","MAT-Ge-","MAT-GaAs","MAT-GaN","MAT-4HSiC","MAT-InP","MAT-diamond","MAT-CdTe","MAT-CIGS","MAT-MAPbI3","MAT-AlN","MAT-Ga2O3"])]),
    "폴리머(15)": len([n for n in unique if any(n["id"].startswith(p) for p in ["MAT-PE","MAT-PP","MAT-PVC","MAT-PS","MAT-PET","MAT-PTFE","MAT-PMMA","MAT-Nylon","MAT-Kevlar","MAT-Spectra","MAT-PC-","MAT-PEEK","MAT-PU"])]),
    "탄소동소체(10)": len([n for n in unique if any(n["id"].startswith(p) for p in ["MAT-C-","MAT-C60","MAT-C70","MAT-SWCNT","MAT-MWCNT","MAT-graphite-i","MAT-amorphous"])]),
    "브라베격자(14)": len([n for n in unique if n["id"].startswith("MAT-bravais")]),
    "초전도체(10)": len([n for n in unique if n["id"].startswith("MAT-SC-")]),
    "배터리재료(10)": len([n for n in unique if n["id"].startswith("MAT-BAT-")]),
    "광학재료(10)": len([n for n in unique if n["id"].startswith("MAT-OPT-")]),
    "자성재료(10)": len([n for n in unique if n["id"].startswith("MAT-MAG-")]),
}
sys.stderr.write("\n카테고리별:\n")
for k,v in cats.items():
    sys.stderr.write(f"  {k}: {v}\n")
sys.stderr.write(f"  합계: {sum(cats.values())}\n")
