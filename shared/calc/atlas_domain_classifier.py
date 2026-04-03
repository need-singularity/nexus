#!/usr/bin/env python3
"""
Atlas Domain Classifier — 도메인 없는 가설에 키워드 기반 도메인 부여
"""

import sqlite3
import re

DB = '.shared/math_atlas.db'

# 키워드 → 도메인 매핑 (우선순위 순)
RULES = [
    # 물리
    (r'quark|lepton|gauge|standard.model|higgs|boson|particle|fermion', 'PH'),
    (r'string.theory|extra.dimension|calabi.yau|compactif', 'PH'),
    (r'black.hole|hawking|schwarzschild|ISCO|event.horizon', 'PH'),
    (r'phase.transition|critical|ising|percolation|SLE', 'PH'),
    (r'quantum.field|QFT|renormalization|feynman', 'PH'),
    (r'superconductor|BCS|cooper.pair|meissner', 'PH'),
    (r'fusion|plasma|tokamak|stellarator|MHD', 'EE'),
    (r'nuclear|fission|binding.energy|nuclide|isotope', 'PH'),

    # 의식/GZ
    (r'consciousness|conscious|awareness|qualia', 'CX'),
    (r'golden.zone|GZ|inhibition|plasticity|deficit', 'CX'),
    (r'genius|G.?=.?D|brain|neural|EEG|gamma', 'CX'),
    (r'compass|convergence.engine|meta.engine', 'CX'),
    (r'MoE|mixture.of.expert|gating|router|expert', 'CX'),
    (r'edge.of.chaos|langton|lyapunov|critical', 'CX'),

    # 수론
    (r'perfect.number|sigma\(|phi\(|tau\(|sopfr|divisor|squarefree', 'NT'),
    (r'riemann.zeta|zeta\(|basel|bernoulli|euler.product', 'NT'),
    (r'prime|mersenne|fermat.prime|goldbach', 'NT'),
    (r'modular.form|ramanujan|moonshine|j.invariant', 'MOD'),
    (r'elliptic.curve|BSD|mordell|weil', 'ELPT'),
    (r'partition.function|p\(\d+\)|young.tableau|stirling', 'PART'),
    (r'fibonacci|lucas|catalan.number|bell.number', 'SEQ'),

    # 대수/군론
    (r'group.theory|symmetric.group|S_[0-9]|automorphism|outer', 'GRP'),
    (r'lie.algebra|E_[678]|exceptional|root.system', 'LIE'),
    (r'representation|character|schur|young', 'REPR'),
    (r'galois|field.extension|cyclotomic', 'CYCL'),

    # 위상/기하
    (r'topology|homology|homotopy|betti|euler.char', 'TOP'),
    (r'knot|trefoil|jones.poly|alexander', 'TOP'),
    (r'manifold|cobordism|surgery|exotic.sphere', 'TOP'),
    (r'lattice|sphere.packing|kissing.number|leech', 'LATT'),
    (r'polyhedron|platonic|polytope|regular.solid', 'GEO'),

    # 생물
    (r'DNA|codon|genetic.code|amino.acid|nucleotide', 'DNA'),
    (r'biology|cell|organism|evolution|life', 'BIO'),
    (r'EEG|brainwave|cortex|neuron|synapse', 'NEURO'),

    # 공학
    (r'chip|semiconductor|transistor|moore|MOSFET', 'CHIP'),
    (r'robot|autonomous|actuator|sensor', 'ROB'),
    (r'energy|solar|battery|grid|power', 'EE'),
    (r'infrastructure|data.center|cooling', 'INFRA'),

    # 정보/CS
    (r'entropy|information|shannon|channel.capacity|coding', 'INFO'),
    (r'algorithm|complexity|NP|turing|computation', 'CS'),
    (r'machine.learning|deep.learning|transformer|attention|LLM', 'AI'),
    (r'training|fine.tun|loss|gradient|backprop', 'AI'),

    # 의학
    (r'medical|clinical|disease|therapy|drug|anesthesia', 'MED'),

    # 화학
    (r'chemistry|periodic.table|element|orbital|bond', 'CHEM'),
    (r'crystal|lattice.parameter|space.group|bravais', 'CHEM'),

    # 천문
    (r'cosmolog|universe|dark.matter|dark.energy|CMB|BBN', 'COSMO'),
    (r'star|stellar|supernova|neutron.star|pulsar', 'ASTRO'),

    # 확률/통계
    (r'probability|random|stochastic|markov|monte.carlo', 'PROB'),
    (r'statistic|distribution|chi.squared|p.value|hypothesis.test', 'STAT'),

    # 수학 기타
    (r'graph.theory|chromatic|clique|adjacency|petersen', 'GRAPH'),
    (r'combinatorial|binomial|permutation|arrangement', 'COMB'),
    (r'ergodic|mixing|recurrence|measure.preserv', 'ERGODIC'),
    (r'fractal|self.similar|mandelbrot|hausdorff', 'CHAOS'),
    (r'category.theory|functor|natural.transform|monad', 'CAT'),
    (r'differential.equation|ODE|PDE|painlev', 'DE'),
    (r'operator|spectral|eigenvalue|hilbert.space', 'SPEC'),
    (r'continued.fraction|convergent|khinchin|gauss.map', 'CF'),
]

def classify(title, current_domain):
    """타이틀 기반으로 도메인 분류"""
    if current_domain:
        return current_domain

    title_lower = title.lower() if title else ''
    for pattern, domain in RULES:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return domain
    return None

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 도메인 없는 가설 가져오기
    cur.execute("SELECT id, title, domain FROM hypotheses WHERE domain IS NULL OR domain = ''")
    rows = cur.fetchall()
    print(f"도메인 없는 가설: {len(rows)}개")

    classified = 0
    domain_counts = {}
    updates = []

    for hid, title, domain in rows:
        new_domain = classify(title, domain)
        if new_domain:
            updates.append((new_domain, hid))
            domain_counts[new_domain] = domain_counts.get(new_domain, 0) + 1
            classified += 1

    print(f"\n분류 성공: {classified}개 / {len(rows)}개")
    print(f"분류 실패: {len(rows) - classified}개")

    print(f"\n도메인별 분류 결과:")
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"  {d:>10}: {c:>4}개")

    # DB 업데이트
    for new_domain, hid in updates:
        cur.execute("UPDATE hypotheses SET domain=? WHERE id=?", (new_domain, hid))

    conn.commit()

    # 최종 통계
    cur.execute("SELECT COUNT(*) FROM hypotheses WHERE domain IS NULL OR domain = ''")
    remaining = cur.fetchone()[0]
    print(f"\n업데이트 후 도메인 없는 가설: {remaining}개")

    # 전체 도메인 분포
    cur.execute("SELECT domain, COUNT(*) FROM hypotheses WHERE domain IS NOT NULL AND domain != '' GROUP BY domain ORDER BY COUNT(*) DESC LIMIT 20")
    print(f"\n최종 도메인 분포 (Top 20):")
    for domain, cnt in cur.fetchall():
        print(f"  {domain:>10}: {cnt:>4}개")

    conn.close()

if __name__ == '__main__':
    main()
