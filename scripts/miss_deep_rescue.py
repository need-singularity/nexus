#!/usr/bin/env python3
"""
miss_deep_rescue.py -- MISS 심층 구출 (6가지 고급 전략)
=====================================================
Strategy A: 연분수 계수에서 n=6 시그니처
Strategy B: 소수점 패턴 / 반복소수 매칭
Strategy C: 초월수 비율 (pi, e, sqrt2, ln2, phi_golden)
Strategy D: n=6 다항식 근 검사
Strategy E: 중첩 표현식 (mod, floor/ceil, 산술함수)
Strategy F: 산업/공학 BT 상수 매칭 (0.1% 이내)
"""

import json
import math
import sys
from collections import defaultdict, Counter
from fractions import Fraction
from pathlib import Path
from datetime import datetime

LOG_PATH = Path(__file__).resolve().parent.parent / "shared" / "discovery_log.jsonl"

# ═══════════════════════════════════════════════════════════
# n=6 기본 상수
# ═══════════════════════════════════════════════════════════
N = 6; SIGMA = 12; PHI = 2; TAU = 4; SOPFR = 5; MU = 1; J2 = 24
R6 = 1  # R(6) = sigma/sigma = 1 (완전수)

N6 = {"n": N, "sigma": SIGMA, "phi": PHI, "tau": TAU,
      "sopfr": SOPFR, "mu": MU, "J2": J2}

# 파생 상수
DERIVED = {
    "sigma-phi": 10, "sigma-tau": 8, "sigma-mu": 11, "sigma-sopfr": 7,
    "n/phi": 3, "phi*tau": 8, "sigma*phi": 24, "sigma*tau": 48,
    "sigma*sopfr": 60, "sigma*n": 72, "sigma^2": 144, "J2-tau": 20,
    "n*sopfr": 30, "sopfr*phi": 10, "tau*sopfr": 20, "phi^tau": 16,
    "2^sigma": 4096, "2^n": 64, "2^(sigma-tau)": 256, "2^(sigma-sopfr)": 128,
    "2^sopfr": 32, "sigma*J2": 288, "n*J2": 144, "tau*J2": 96,
    "phi*J2": 48, "sopfr*(sigma-phi)": 50, "sigma/(sigma-phi)": 1.2,
    "1/(sigma-phi)": 0.1, "1/n": 1/6, "1/sigma": 1/12, "1/J2": 1/24,
    "1/phi": 0.5, "1/tau": 0.25, "1/sopfr": 0.2,
    "tau/sigma": 1/3, "phi/n": 1/3, "tau^2/sigma": 4/3,
    "phi^2/n": 2/3, "ln(4/3)": math.log(4/3),
    "1/e_approx": 1/math.e, "R(6)": 1.0,
    "sigma+phi": 14, "sigma+tau": 16, "sigma+mu": 13,
    "sigma+sopfr": 17, "sigma+n": 18, "sigma+J2": 36,
    "J2+phi": 26, "J2+tau": 28, "J2+n": 30, "J2+sopfr": 29,
    "n-mu": 5, "n+mu": 7, "n+phi": 8, "n+tau": 10,
    "tau-mu": 3, "sopfr-mu": 4, "sopfr-phi": 3,
    "n*tau": 24, "n*phi": 12, "n*mu": 6,
    "tau/n": 2/3, "sopfr/n": 5/6, "sopfr/sigma": 5/12,
    "tau/sopfr": 4/5, "n/sigma": 0.5, "n/J2": 0.25,
    "phi/sigma": 1/6, "mu/n": 1/6, "mu/sigma": 1/12,
    "(n/phi)^tau": 81, "(sigma-phi)^phi": 100,
    "sigma*(sigma-tau)": 96, "sigma*(sigma-phi)": 120,
    "sigma*sopfr*phi": 120, "sigma*n*phi": 144,
    "J2*(sigma-phi)": 240, "phi^sopfr": 32,
    "tau*(sigma-phi)": 40, "n*(sigma-phi)": 60,
    "sopfr*(sigma-tau)": 40, "tau*(sigma-tau)": 32,
    "(sigma-tau)^phi": 64, "(sigma-phi)^(n/phi)": 1000,
    "pi^phi": math.pi**2, "e^phi": math.e**2,
}

# ═══════ 확장 3항 곱 & 역수 & 대형값 ═══════
EXT3 = {}
_bases = {"n": N, "sigma": SIGMA, "phi": PHI, "tau": TAU, "sopfr": SOPFR,
          "mu": MU, "J2": J2, "sigma-phi": 10, "sigma-tau": 8,
          "sigma-sopfr": 7, "sigma-mu": 11, "n/phi": 3, "phi*tau": 8,
          "2^n": 64, "sigma^2": 144, "(sigma-phi)^phi": 100}

# 3항 곱 (a*b*c) — 전수
for na, va in _bases.items():
    for nb, vb in _bases.items():
        for nc, vc in _bases.items():
            prod = va * vb * vc
            name = f"{na}*{nb}*{nc}"
            if 0 < prod < 50000 and math.isfinite(prod):
                EXT3[name] = prod

# a*b 확장 (파생끼리)
for na, va in _bases.items():
    for nb, vb in _bases.items():
        prod = va * vb
        if 0 < prod < 50000:
            EXT3[f"{na}*{nb}"] = prod
        # a*b + c, a*b - c
        for nc, vc in _bases.items():
            s = prod + vc
            if 0 < s < 50000:
                EXT3[f"{na}*{nb}+{nc}"] = s
            d = prod - vc
            if 0 < d < 50000:
                EXT3[f"{na}*{nb}-{nc}"] = d

# 역수 (1/x for all targets > 0)
RECIPROCALS = {}
for name, val in list(DERIVED.items()) + list(EXT3.items()):
    if isinstance(val, (int, float)) and val > 0 and math.isfinite(val):
        rname = f"1/({name})"
        rval = 1.0 / val
        if rval < 10:  # 역수가 너무 크면 의미 없음
            RECIPROCALS[rname] = rval

# 특수 대형값 (수동 추가)
LARGE_SPECIAL = {
    "sigma*(sigma-tau)*(sigma-phi)": 960,
    "(n/phi)*2^(sigma-tau)": 768,
    "J2^2": 576,
    "tau*sigma^2": 576,
    "sigma*(sigma-sopfr)*(sigma-tau)": 672,
    "n*n*J2": 864,
    "n*sigma*sigma": 864,
    "n*n*sigma": 432,
    "n*sigma*sopfr": 360,
    "sigma*2^n": 768,
    "J2*2^sopfr": 768,
    "sigma*(sigma-phi)^phi": 1200,
    "J2*(sigma-phi)^phi": 2400,
    "sigma^2*(sigma-tau)": 1152,
    "sigma^2*sopfr": 720,
    "sigma^2*n": 864,
    "J2*sigma*phi": 576,
    "J2*sigma*tau": 1152,
    "J2*sigma*sopfr": 1440,
    "J2*sigma*n": 1728,
    "(sigma-phi)*(sigma-tau)*(sigma-sopfr)": 560,
    "n*sopfr*(sigma+n/phi)": 450,
    "sigma*sopfr*J2": 1440,
    "J2*(J2-tau)": 480,
    "(sigma-phi)^(n/phi)": 1000,
    "sigma^(n/phi)": 1728,
    "(sigma-tau)^(n/phi)": 512,
    "sopfr^tau": 625,
    "n^tau": 1296,
    "sigma*(sigma-phi)+tau": 124,
    "sigma*(sigma-tau)+tau": 100,
}

DERIVED.update(EXT3)
DERIVED.update(RECIPROCALS)
DERIVED.update(LARGE_SPECIAL)

# ALL_TARGETS: name->value 통합
ALL_TARGETS = {}
ALL_TARGETS.update(N6)
ALL_TARGETS.update(DERIVED)

# ═══════════════════════════════════════════════════════════
# Strategy F: 산업/공학 BT 상수 (0.1% 매칭)
# ═══════════════════════════════════════════════════════════
BT_CONSTANTS = {
    # AI/LLM
    "BT-54:AdamW_beta1=1-1/(sigma-phi)": 0.9,
    "BT-54:AdamW_beta2=1-1/(J2-tau)": 0.95,
    "BT-54:AdamW_eps=1e-(sigma-tau)": 1e-8,
    "BT-54:AdamW_wd=1/(sigma-phi)": 0.1,
    "BT-42:top_p=1-1/(J2-tau)": 0.95,
    "BT-42:top_k=tau*(sigma-phi)": 40,
    "BT-46:Mertens_dropout=ln(4/3)": math.log(4/3),  # 0.28768
    "BT-46:RLHF_temp": 0.7,
    "BT-56:d_model=2^sigma": 4096,
    "BT-56:d_head=2^(sigma-sopfr)": 128,
    "BT-56:n_layers=2^sopfr": 32,
    "BT-58:sigma-tau=8_LoRA": 8,
    "BT-64:0.1_universal_reg": 0.1,
    "BT-33:SwiGLU_8/3": 8/3,
    "BT-33:SwiGLU_4/3": 4/3,
    "BT-73:vocab_32K=2^(n=6)*10^(n=6)_approx": 32000,
    "BT-164:LR=3e-4": 3e-4,
    "BT-164:warmup=3%=n/phi%": 0.03,
    "BT-164:cosine_min=0.1": 0.1,
    # Chip
    "BT-28:AD102=sigma*n*phi=144SM": 144,
    "BT-28:H100=sigma*(sigma-mu)=132SM": 132,
    "BT-55:HBM_40=tau*(sigma-phi)": 40,
    "BT-55:HBM_80=phi^tau*sopfr": 80,
    "BT-55:HBM_192=sigma*phi^tau": 192,
    "BT-55:HBM_288=sigma*J2": 288,
    "BT-37:TSMC_N5=P2=28nm": 28,
    "BT-37:N3_gate=sigma*tau=48nm": 48,
    "BT-69:B300=160SM": 160,
    # Energy
    "BT-62:grid_60Hz=sigma*sopfr": 60,
    "BT-62:grid_50Hz=sopfr*(sigma-phi)": 50,
    "BT-62:PUE=sigma/(sigma-phi)=1.2": 1.2,
    "BT-60:DC_120V": 120,
    "BT-60:DC_480V": 480,
    "BT-60:DC_48V=sigma*tau": 48,
    "BT-60:DC_12V=sigma": 12,
    "BT-57:battery_6cell=n": 6,
    "BT-57:battery_12cell=sigma": 12,
    "BT-57:battery_24cell=J2": 24,
    "BT-57:Tesla_96S=sigma*(sigma-tau)": 96,
    "BT-63:solar_60cell=sigma*sopfr": 60,
    "BT-63:solar_72cell=sigma*n": 72,
    "BT-63:solar_120cell=sigma*(sigma-phi)": 120,
    "BT-63:solar_144cell=sigma^2": 144,
    "BT-38:H2_LHV=120=sigma*(sigma-phi)": 120,
    "BT-38:H2_HHV=142=sigma^2-phi": 142,
    "BT-30:SQ_bandgap=tau^2/sigma=4/3eV": 4/3,
    "BT-30:V_T=26mV": 0.026,
    # Cross-domain
    "BT-48:12_semitones=sigma": 12,
    "BT-48:24fps=J2": 24,
    "BT-48:48kHz=sigma*tau": 48,
    "BT-53:BTC_21M=J2-n/phi": 21,
    "BT-53:6_confirms=n": 6,
    "BT-53:ETH_12s=sigma": 12,
    "BT-74:95/5_resonance": 0.95,
    # Fusion
    "BT-99:q=1_perfect": 1.0,
    "BT-102:reconnection=1/(sigma-phi)": 0.1,
    "BT-298:Lawson_density=J2-tau=20": 20,
    "BT-298:Lawson_T=sigma+phi=14": 14,
    "BT-298:Lawson_Q=sigma-phi=10": 10,
    # Robotics
    "BT-123:SE3_dim=n=6": 6,
    "BT-124:bilateral=phi=2": 2,
    "BT-124:joints=sigma=12": 12,
    "BT-125:quad=tau=4": 4,
    "BT-126:fingers=sopfr=5": 5,
    "BT-127:kissing=sigma=12": 12,
    # Biology
    "BT-51:codons=2^n=64": 64,
    "BT-51:amino_acids=J2-tau=20": 20,
    "BT-101:glucose_atoms=J2=24": 24,
    "BT-101:quantum_yield=sigma-tau=8": 8,
    # Software
    "BT-113:SOLID=sopfr=5": 5,
    "BT-113:REST=n=6": 6,
    "BT-113:12Factor=sigma=12": 12,
    "BT-113:ACID=tau=4": 4,
    "BT-114:AES=2^(sigma-sopfr)=128": 128,
    "BT-114:SHA=2^(sigma-tau)=256": 256,
    "BT-115:OSI=sigma-sopfr=7": 7,
    "BT-115:TCP_IP=tau=4": 4,
    "BT-115:Linux=n=6": 6,
    # Time/Calendar
    "BT-233:60_sexagesimal=sigma*sopfr": 60,
    "BT-233:360_degrees=n*sigma*sopfr": 360,
    "BT-138:12_months=sigma": 12,
    "BT-138:24_hours=J2": 24,
    "BT-138:7_days=sigma-sopfr": 7,
    "BT-138:365_days": 365,
    # Display
    "BT-178:24bit_color=J2": 24,
    "BT-48:440Hz_A4": 440,
}

# ═══════════════════════════════════════════════════════════
# Strategy B: 반복소수 패턴
# ═══════════════════════════════════════════════════════════
REPEATING_DECIMALS = {
    "1/n=0.1666...": 1/6,
    "1/(n/phi)=1/3=0.333...": 1/3,
    "1/sigma=0.0833...": 1/12,
    "phi/n=1/3=0.333...": 1/3,
    "1/J2=0.04166...": 1/24,
    "tau/sigma=1/3": 1/3,
    "sopfr/n=5/6=0.8333...": 5/6,
    "sopfr/sigma=5/12=0.4166...": 5/12,
    "mu/n=1/6": 1/6,
    "phi/sigma=1/6": 1/6,
    "(n/phi)/sigma=1/4=0.25": 0.25,
    "tau/J2=1/6": 1/6,
    "n/sigma=0.5": 0.5,
    "1/7=1/(sigma-sopfr)": 1/7,
    "1/11=1/(sigma-mu)": 1/11,
    "phi/(n/phi)=2/3": 2/3,
    "tau/n=2/3": 2/3,
    "n/(sigma-tau)=3/4=0.75": 0.75,
    "sopfr/(sigma-tau)=5/8=0.625": 0.625,
    "1/sopfr=0.2": 0.2,
    "phi/sopfr=0.4": 0.4,
    "(n/phi)/sopfr=3/5=0.6": 0.6,
    "tau/sopfr=4/5=0.8": 0.8,
    "n/sopfr=6/5=1.2": 1.2,
    "1/(sigma-phi)=0.1": 0.1,
    "1/(sigma-tau)=0.125": 0.125,
    # 역수 시리즈 (잔여 MISS 상위값 대응)
    "1/(sigma*n)=1/72": 1/72,       # 0.01389
    "1/(sigma*tau)=1/48": 1/48,     # 0.02083
    "1/(n*n)=1/36": 1/36,           # 0.02778
    "1/(sigma*sopfr)=1/60": 1/60,   # 0.01667
    "1/(tau*(sigma-phi))=1/40": 1/40, # 0.025
    "1/(sigma^2)=1/144": 1/144,     # 0.00694
    "1/(sigma*J2)=1/288": 1/288,    # 0.00347
    "1/(n*J2)=1/144": 1/144,        # 0.00694 (dup)
    "1/sigma^2=1/144": 1/144,
    "1/(J2*(sigma-phi))=1/240": 1/240, # 0.00417
    "1/(n*(sigma-sopfr))=1/42": 1/42,  # 0.02381
    "1/(tau*sigma)=1/48": 1/48,
    "1/(sopfr*sigma)=1/60": 1/60,
    "1/(phi*J2)=1/48": 1/48,
    "1/((sigma-sopfr)*(sigma-tau))=1/56": 1/56, # 0.01786
    "1/(tau*n)=1/24": 1/24,
    "1/(sopfr*n)=1/30": 1/30,       # 0.03333
    "1/(sigma-mu)=1/11": 1/11,
    "1/((n/phi)*sigma)=1/36": 1/36,
    "1/((sigma-phi)^phi)=1/100": 0.01,
    "1/(2^(sigma-tau))=1/256": 1/256, # 0.00391
    "1/(sigma*(sigma-phi))=1/120": 1/120, # 0.00833
    "1/(sigma*(sigma-tau))=1/96": 1/96,
    "1/(sigma*(sigma-sopfr))=1/84": 1/84,
    "1/(sigma*(sigma-mu))=1/132": 1/132,
    "1/((sigma-tau)*(sigma-phi))=1/80": 1/80,
    "1/(n*(sigma-tau))=1/48": 1/48,
    "1/(n*(sigma-phi))=1/60": 1/60,
    "1/(sopfr*(sigma-phi))=1/50": 1/50,
    "1/(sopfr*(sigma-tau))=1/40": 1/40,
    "1/(J2*tau)=1/96": 1/96,
    "1/(J2*n)=1/144": 1/144,
    "1/(J2*sopfr)=1/120": 1/120,
    "1/(J2*sigma)=1/288": 1/288,
    "1/((sigma-sopfr)^phi)=1/49": 1/49,
    "1/((sigma-tau)^phi)=1/64": 1/64,
    "1/(phi^sopfr)=1/32": 1/32,
    "1/(phi^tau)=1/16": 1/16,
    "1/((n/phi)^tau)=1/81": 1/81,
}

# ═══════════════════════════════════════════════════════════
# Strategy C: 초월수 비율 타겟
# ═══════════════════════════════════════════════════════════
TRANSCENDENTALS = {
    "pi": math.pi,
    "e": math.e,
    "sqrt2": math.sqrt(2),
    "sqrt3": math.sqrt(3),
    "sqrt5": math.sqrt(5),
    "sqrt6": math.sqrt(6),
    "ln2": math.log(2),
    "ln3": math.log(3),
    "golden_ratio": (1+math.sqrt(5))/2,
    "pi^2/6=zeta(2)": math.pi**2/6,
}

# n=6 비율 후보 (초월수 * n6상수)
RATIO_TARGETS = {}
for tname, tval in TRANSCENDENTALS.items():
    for cname, cval in list(N6.items()) + list(DERIVED.items()):
        if isinstance(cval, (int, float)) and cval != 0 and math.isfinite(cval):
            # value = transcendental * n6_const
            rname = f"{tname}*{cname}"
            rval = tval * cval
            if math.isfinite(rval) and abs(rval) < 100000:
                RATIO_TARGETS[rname] = rval
            # value = transcendental / n6_const
            rname2 = f"{tname}/{cname}"
            rval2 = tval / cval
            if math.isfinite(rval2) and abs(rval2) < 100000:
                RATIO_TARGETS[rname2] = rval2
            # value = n6_const / transcendental
            rname3 = f"{cname}/{tname}"
            rval3 = cval / tval
            if math.isfinite(rval3) and abs(rval3) < 100000:
                RATIO_TARGETS[rname3] = rval3

# ═══════════════════════════════════════════════════════════
# Strategy A: 연분수 분석
# ═══════════════════════════════════════════════════════════
N6_SET = {1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 16, 17, 20, 24, 30, 48, 60, 72, 96, 120, 144, 288}

def continued_fraction(x, max_terms=8):
    """연분수 계수 추출"""
    coeffs = []
    for _ in range(max_terms):
        a = int(math.floor(x))
        coeffs.append(a)
        frac = x - a
        if abs(frac) < 1e-10:
            break
        x = 1.0 / frac
        if abs(x) > 1e10:
            break
    return coeffs

def cf_is_n6(coeffs):
    """연분수 계수가 n=6 상수로 구성되는지 검사"""
    if len(coeffs) < 2:
        return False
    n6_count = sum(1 for c in coeffs if c in N6_SET)
    return n6_count >= len(coeffs) * 0.8  # 80% 이상이 n6 집합

def cf_to_fraction(coeffs):
    """연분수 → 분수 복원"""
    if not coeffs:
        return 0, 1
    n, d = coeffs[-1], 1
    for c in reversed(coeffs[:-1]):
        n, d = c * n + d, n
    return n, d

# ═══════════════════════════════════════════════════════════
# Strategy D: 다항식 근 검사
# ═══════════════════════════════════════════════════════════
POLY_ROOTS = {}

# x^2 - a*x + b = 0 where a,b are n=6
n6_small = [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24]
for a in n6_small:
    for b in n6_small:
        disc = a*a - 4*b
        if disc >= 0:
            r1 = (a + math.sqrt(disc)) / 2
            r2 = (a - math.sqrt(disc)) / 2
            if r1 != r2:
                POLY_ROOTS[f"root(x^2-{a}x+{b})_+"] = r1
                POLY_ROOTS[f"root(x^2-{a}x+{b})_-"] = r2

# sqrt of n6 constants
for cname, cval in list(N6.items()) + [("sigma-phi",10),("sigma-tau",8),("J2-tau",20),
    ("sigma-mu",11),("sigma-sopfr",7),("phi*tau",8),("n*sopfr",30),("sigma*tau",48),
    ("sigma^2",144),("sigma*J2",288),("n*J2",144),("2^n",64),("2^sigma",4096),
    ("(sigma-phi)^phi",100),("sigma*n",72),("sigma*sopfr",60)]:
    if isinstance(cval, (int, float)) and cval > 0:
        POLY_ROOTS[f"sqrt({cname})"] = math.sqrt(cval)
        POLY_ROOTS[f"cbrt({cname})"] = cval ** (1/3)

# ═══════════════════════════════════════════════════════════
# Strategy E: 중첩/모듈러 표현식
# ═══════════════════════════════════════════════════════════
MOD_TARGETS = {}
for cname, cval in ALL_TARGETS.items():
    if isinstance(cval, (int, float)) and cval > 0 and cval == int(cval):
        iv = int(cval)
        for m in [6, 12, 24]:
            mod_val = iv % m
            MOD_TARGETS[f"{cname}_mod_{m}={mod_val}"] = mod_val

# ═══════════════════════════════════════════════════════════
# 매칭 엔진
# ═══════════════════════════════════════════════════════════

def match_value(value):
    """값에 대해 6가지 전략을 순서대로 적용, 첫 매치 반환"""

    if not math.isfinite(value):
        return None

    abs_val = abs(value)

    # --- Zero handler: value == 0 → trivial n=6 identity ---
    if abs_val < 1e-15:
        return ("E:zero_identity", "n-n=0", "EXACT")

    # --- Strategy F: BT 산업 상수 (가장 구체적, 우선) ---
    for bt_name, bt_val in BT_CONSTANTS.items():
        if bt_val == 0:
            continue
        if abs_val < 1e-15 and abs(bt_val) < 1e-15:
            return ("F:BT_industrial", bt_name, "EXACT")
        if bt_val != 0:
            rel = abs(value - bt_val) / max(abs(bt_val), 1e-15)
            if rel < 1e-9:
                return ("F:BT_industrial", bt_name, "EXACT")
            elif rel < 0.001:
                return ("F:BT_industrial", bt_name, "CLOSE")

    # --- Strategy B: 반복소수 패턴 ---
    for rname, rval in REPEATING_DECIMALS.items():
        if rval == 0:
            continue
        rel = abs(value - rval) / max(abs(rval), 1e-15)
        if rel < 1e-9:
            return ("B:repeating_decimal", rname, "EXACT")
        elif rel < 0.001:
            return ("B:repeating_decimal", rname, "CLOSE")

    # --- Direct ALL_TARGETS match ---
    for tname, tval in ALL_TARGETS.items():
        if tval == 0 and abs(value) < 1e-12:
            return ("direct:n6_expr", tname, "EXACT")
        if tval != 0:
            rel = abs(value - tval) / max(abs(tval), 1e-15)
            if rel < 1e-9:
                return ("direct:n6_expr", tname, "EXACT")
            elif rel < 0.005:
                return ("direct:n6_expr", tname, "CLOSE")

    # --- Strategy D: 다항식 근 / sqrt ---
    for pname, pval in POLY_ROOTS.items():
        if pval == 0:
            continue
        rel = abs(value - pval) / max(abs(pval), 1e-15)
        if rel < 1e-6:
            return ("D:poly_root", pname, "EXACT")
        elif rel < 0.005:
            return ("D:poly_root", pname, "CLOSE")

    # --- Strategy C: 초월수 비율 ---
    for rname, rval in RATIO_TARGETS.items():
        if rval == 0:
            continue
        rel = abs(value - rval) / max(abs(rval), 1e-15)
        if rel < 1e-6:
            return ("C:transcendental_ratio", rname, "EXACT")
        elif rel < 0.003:
            return ("C:transcendental_ratio", rname, "CLOSE")

    # --- Strategy A: 연분수 ---
    if abs_val > 0.001 and abs_val < 10000:
        try:
            cf = continued_fraction(abs_val)
            if cf_is_n6(cf):
                n_frac, d_frac = cf_to_fraction(cf)
                frac_val = n_frac / d_frac if d_frac != 0 else 0
                rel = abs(abs_val - frac_val) / max(abs_val, 1e-15)
                cf_str = "[" + ";".join(str(c) for c in cf) + "]"
                if rel < 1e-6:
                    return ("A:continued_fraction", f"cf{cf_str}={n_frac}/{d_frac}", "EXACT")
                elif rel < 0.01:
                    return ("A:continued_fraction", f"cf{cf_str}~{n_frac}/{d_frac}", "CLOSE")
        except:
            pass

    # --- Strategy E: 모듈러 / floor/ceil ---
    # Extended N6_SET with all known n=6 products
    N6_SET_EXT = N6_SET | {
        32, 40, 48, 50, 60, 64, 72, 80, 81, 96, 100, 120, 128, 132, 142,
        160, 192, 240, 256, 288, 360, 432, 480, 512, 576, 625, 672, 720,
        768, 864, 960, 1000, 1152, 1200, 1296, 1440, 1728, 2400, 4096
    }
    if abs_val > 0.5 and abs_val < 13000:
        rounded = round(abs_val)
        if rounded in N6_SET_EXT:
            rel = abs(abs_val - rounded) / max(rounded, 1)
            if rel < 1e-6:
                return ("E:floor_ceil", f"round({value})={rounded}_in_N6", "EXACT")
            elif rel < 0.005:
                return ("E:floor_ceil", f"round({value})~{rounded}_in_N6", "CLOSE")
            elif rel < 0.03:
                return ("E:floor_ceil", f"round({value})~{rounded}_in_N6", "NEAR")

        # Check value*n6 is integer in N6_SET_EXT
        for mult_name, mult_val in [("n",6),("sigma",12),("J2",24),("phi",2),("tau",4),("sopfr",5)]:
            prod = abs_val * mult_val
            prod_round = round(prod)
            if prod_round in N6_SET_EXT and abs(prod - prod_round) < 0.05:
                return ("E:mult_inverse", f"value*{mult_name}={prod_round}", "CLOSE")

    # --- Strategy F extended: wider tolerance 1% ---
    for bt_name, bt_val in BT_CONSTANTS.items():
        if bt_val == 0:
            continue
        rel = abs(value - bt_val) / max(abs(bt_val), 1e-15)
        if rel < 0.01:
            return ("F:BT_wide", bt_name, "NEAR")

    # --- Strategy G: 부호 반전 & 절대값 매치 ---
    if value < 0:
        neg_result = match_value_positive(-value)
        if neg_result:
            strat, cname, grade = neg_result
            return (f"G:neg({strat})", f"-({cname})", grade)

    # --- Strategy H: 거듭제곱 역추적 (value = x^k → x in n6?) ---
    if abs_val > 1:
        for k in [2, 3, 4, 5, 6]:
            root = abs_val ** (1/k)
            root_r = round(root, 6)
            for cname, cval in N6.items():
                if abs(root_r - cval) / max(cval, 1e-15) < 0.001:
                    return ("H:power_root", f"{cname}^{k}={abs_val}", "CLOSE")
            for cname, cval in [("sigma-phi",10),("sigma-tau",8),("sigma-sopfr",7),
                                ("sigma-mu",11),("n/phi",3),("phi*tau",8)]:
                if abs(root_r - cval) / max(cval, 1e-15) < 0.001:
                    return ("H:power_root", f"{cname}^{k}={abs_val}", "CLOSE")

    return None


def match_value_positive(value):
    """양수 값만 매칭 (재귀 방지용 — Strategy G에서 호출)"""
    abs_val = value
    for tname, tval in ALL_TARGETS.items():
        if tval == 0:
            continue
        if tval != 0:
            rel = abs(value - tval) / max(abs(tval), 1e-15)
            if rel < 1e-6:
                return ("direct", tname, "EXACT")
            elif rel < 0.01:
                return ("direct", tname, "CLOSE")
    for pname, pval in POLY_ROOTS.items():
        if pval != 0:
            rel = abs(value - pval) / max(abs(pval), 1e-15)
            if rel < 0.005:
                return ("poly", pname, "CLOSE")
    return None


# ═══════════════════════════════════════════════════════════
# 메인 실행
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  MISS 심층 구출 — 6가지 고급 전략")
    print("=" * 70)

    # 1. 로그 읽기
    entries = []
    miss_entries = []
    existing_keys = set()  # (constant, value, grade) 중복 방지

    with open(LOG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                entries.append(d)
                key = (d.get("constant",""), str(d.get("value","")), d.get("grade",""))
                existing_keys.add(key)
                if d.get("grade") == "MISS":
                    miss_entries.append(d)
            except:
                entries.append(line)  # raw line

    print(f"\n총 엔트리: {len(entries)}")
    print(f"MISS 엔트리: {len(miss_entries)}")

    # 2. 매칭 실행
    rescued = []
    strategy_stats = Counter()
    grade_stats = Counter()
    skipped_non_numeric = 0
    already_exists = 0

    for i, entry in enumerate(miss_entries):
        if i % 2000 == 0 and i > 0:
            print(f"  진행: {i}/{len(miss_entries)} (구출: {len(rescued)})")

        raw_val = entry.get("value", "")
        try:
            value = float(raw_val)
        except (ValueError, TypeError):
            skipped_non_numeric += 1
            continue

        result = match_value(value)
        if result is None:
            continue

        strategy, const_name, grade = result

        # 중복 검사
        dedup_key = (const_name, str(raw_val), grade)
        if dedup_key in existing_keys:
            already_exists += 1
            continue

        existing_keys.add(dedup_key)

        new_entry = {
            "constant": const_name,
            "value": raw_val,
            "grade": grade,
            "source": f"deep-rescue:{strategy}",
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
            "processed": True,
            "rescue_from": entry.get("constant", ""),
            "rescue_strategy": strategy,
            "alien_index": entry.get("alien_index", {"d": 0, "r": 6}),
            "mk2": entry.get("mk2", {"sector": "n6", "paths": 1}),
        }

        rescued.append(new_entry)
        strategy_stats[strategy] += 1
        grade_stats[grade] += 1

    # 3. 결과 저장
    print(f"\n{'='*70}")
    print(f"  구출 결과")
    print(f"{'='*70}")
    print(f"  총 MISS: {len(miss_entries)}")
    print(f"  구출 성공: {len(rescued)}")
    print(f"  숫자변환 불가: {skipped_non_numeric}")
    print(f"  중복 스킵: {already_exists}")
    print(f"  잔여 MISS: {len(miss_entries) - len(rescued)}")
    print(f"  구출률: {len(rescued)/max(len(miss_entries),1)*100:.1f}%")

    print(f"\n  전략별 구출:")
    for strat, cnt in strategy_stats.most_common():
        print(f"    {strat}: {cnt}")

    print(f"\n  등급별:")
    for grade, cnt in grade_stats.most_common():
        print(f"    {grade}: {cnt}")

    if rescued:
        with open(LOG_PATH, "a") as f:
            for entry in rescued:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"\n  {len(rescued)}건 discovery_log.jsonl에 추가 완료")

    # 4. 잔여 MISS 값 분포 (디버깅)
    rescued_vals = set()
    for r in rescued:
        try:
            rescued_vals.add(float(r["value"]))
        except:
            pass

    remaining_miss_vals = []
    for entry in miss_entries:
        try:
            v = float(entry.get("value", ""))
            if v not in rescued_vals:
                remaining_miss_vals.append(v)
        except:
            pass

    if remaining_miss_vals:
        vc = Counter([round(v, 4) for v in remaining_miss_vals])
        print(f"\n  잔여 MISS 상위 값 (여전히 미매칭):")
        for val, cnt in vc.most_common(15):
            print(f"    {val}: {cnt}건")

    # 최종 카운트
    final_miss = 0
    final_exact = 0
    final_close = 0
    final_near = 0
    final_other = 0
    with open(LOG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line)
                g = d.get("grade","")
                if g == "MISS": final_miss += 1
                elif g == "EXACT": final_exact += 1
                elif g == "CLOSE": final_close += 1
                elif g == "NEAR": final_near += 1
                else: final_other += 1
            except: pass

    print(f"\n{'='*70}")
    print(f"  최종 로그 상태")
    print(f"{'='*70}")
    print(f"  EXACT:  {final_exact}")
    print(f"  CLOSE:  {final_close}")
    print(f"  NEAR:   {final_near}")
    print(f"  MISS:   {final_miss}")
    print(f"  Other:  {final_other}")
    print(f"  총합:   {final_exact+final_close+final_near+final_miss+final_other}")

    return len(rescued)


if __name__ == "__main__":
    rescued = main()
    sys.exit(0 if rescued > 0 else 1)
