```python
#!/usr/bin/env python3
"""H-CX-7: sigma-phi=n-tau Architecture Optimality Verification
(12,k=4) vs (8,k=2) vs (6,k=3) vs (16,k=4) vs (24,k=6)
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from model_utils import Expert, TopKGate, load_mnist, train_and_evaluate, count_params

class FlexibleMoE(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, n_experts, k):
        super().__init__()
        self.experts = nn.ModuleList([Expert(input_dim, hidden_dim, output_dim) for _ in range(n_experts)])
        self.gate = TopKGate(input_dim, n_experts, k)
        self.n_experts = n_experts
        self.k = k
    def forward(self, x):
        weights = self.gate(x)
        outputs = torch.stack([e(x) for e in self.experts], dim=1)
        return (weights.unsqueeze(-1) * outputs).sum(dim=1)

def main():
    print("="*60)
    print("  H-CX-7: sigma-phi=n-tau Architecture Optimality")
    print("="*60)
    t0 = time.time()
    train_loader, test_loader = load_mnist()

    configs = [
        ("n=6: sigma=12,k=4", 12, 4, True),
        ("sigma=8,k=2", 8, 2, False),
        ("sigma=6,k=3", 6, 3, False),
        ("sigma=16,k=4", 16, 4, False),
        ("sigma=24,k=6", 24, 6, False),
        ("sigma=12,k=3", 12, 3, False),
        ("sigma=12,k=6", 12, 6, False),
    ]

    results = []
    for name, n_exp, k, is_special in configs:
        print(f"\n[{name}] experts={n_exp}, k={k}, sigma/tau={n_exp/k:.2f}")
        accs = []
        for seed in [42, 137, 256]:
            torch.manual_seed(seed)
            model = FlexibleMoE(784, 48, 10, n_exp, k)
            _, acc_list = train_and_evaluate(model, train_loader, test_loader, epochs=10, verbose=False)
            accs.append(acc_list[-1])
        mean_acc = np.mean(accs)
        std_acc = np.std(accs)
        params = count_params(FlexibleMoE(784, 48, 10, n_exp, k))
        results.append((name, n_exp, k, mean_acc, std_acc, params, is_special))
        print(f"  Acc: {mean_acc*100:.2f}% +/- {std_acc*100:.2f}%  Params: {params:,}")

    print(f"\n{'='*60}")
    print(f"  RESULTS (sorted by accuracy)")
    print(f"{'='*60}")
    results.sort(key=lambda x: -x[3])
    print(f"  {'Config':<25} {'Experts':>7} {'k':>3} {'s/t':>5} {'Acc%':>7} {'Std':>5} {'Params':>10} {'sp=nt':>5}")
    print(f"  {'-'*25} {'-'*7} {'-'*3} {'-'*5} {'-'*7} {'-'*5} {'-'*10} {'-'*5}")
    for name, n_exp, k, mean_acc, std_acc, params, is_special in results:
        marker = " YES" if is_special else ""
        print(f"  {name:<25} {n_exp:>7} {k:>3} {n_exp/k:>5.1f} {mean_acc*100:>6.2f}% {std_acc*100:>4.2f} {params:>10,}{marker}")

    best = results[0]
    special = [r for r in results if r[6]][0]
    print(f"\n  Best: {best[0]} ({best[3]*100:.2f}%)")
    print(f"  sp=nt: {special[0]} ({special[3]*100:.2f}%)")
    print(f"  sp=nt is rank {[r[0] for r in results].index(special[0])+1}/{len(results)}")
    print(f"\n  Elapsed: {time.time()-t0:.1f}s")
    print("="*60)

if __name__ == '__main__':
    main()
```