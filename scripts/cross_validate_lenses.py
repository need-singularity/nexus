#!/usr/bin/env python3
"""NEXUS-6 렌즈 교차검증 — 3+ 렌즈 합의 = 확정"""
import numpy as np
try:
    import nexus6
except ImportError:
    print("nexus6 미설치"); exit(1)

np.random.seed(6)
data = np.random.randn(100, 6)
data[:, 0] *= 12; data[:, 1] *= 4; data[:, 2] *= 6  # n=6 constants

result = nexus6.scan(data.flatten().tolist(), 100, 6)
names = result.lens_names

# Collect all scalar metrics across lenses
all_metrics = {}
for nm in names:
    m = result.get_lens(nm)
    if not m: continue
    for k, v in m.items():
        if v and len(v) == 1:  # scalar metric
            all_metrics.setdefault(k, []).append((nm, v[0]))

# Find consensus: metrics reported by 3+ lenses
print("🔍 교차검증 결과 (3+ 렌즈 합의)\n")
consensus = {}
for metric, sources in sorted(all_metrics.items()):
    if len(sources) >= 3:
        vals = [v for _, v in sources]
        mean = np.mean(vals)
        std = np.std(vals)
        cv = std / abs(mean) if abs(mean) > 1e-12 else float('inf')
        consensus[metric] = (len(sources), mean, std, cv)

for metric, (count, mean, std, cv) in sorted(consensus.items(), key=lambda x: -x[1][0]):
    agreement = "✅ 강합의" if cv < 0.1 else "🟡 약합의" if cv < 0.5 else "🔴 불일치"
    print(f"  {metric}: {count}렌즈, mean={mean:.4f}, CV={cv:.2f} {agreement}")

# Cross-domain resonance
print(f"\n📊 요약: {len(consensus)} 교차검증 메트릭, "
      f"{sum(1 for _,(c,_,_,cv) in consensus.items() if cv<0.1)} 강합의")
