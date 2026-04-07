#!/usr/bin/env python3
"""H-CX-21: PPL analog vs Tension correlation analysis"""
import sys; sys.path.insert(0, '/Users/ghost/Dev/logout')
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, math
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

class RepulsionAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.ea = nn.Sequential(nn.Linear(784,128), nn.ReLU(), nn.Linear(128,10))
        self.eg = nn.Sequential(nn.Linear(784,128), nn.ReLU(), nn.Linear(128,10))
        self.eq = nn.Linear(784, 10)
        self.ts = nn.Parameter(torch.tensor(0.3))
    def forward(self, x):
        a, g = self.ea(x), self.eg(x)
        rep = a - g
        t = (rep**2).mean(-1, keepdim=True)
        d = F.normalize(rep, dim=-1)
        return self.eq(x) + self.ts * torch.sqrt(t+1e-8) * d, t.squeeze(), a, g

transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
tl = DataLoader(datasets.MNIST('/tmp/data', train=True, download=True, transform=transform), batch_size=128, shuffle=True)
te = DataLoader(datasets.MNIST('/tmp/data', train=False, transform=transform), batch_size=256)

model = RepulsionAE()
opt = torch.optim.Adam(model.parameters(), lr=0.001)
for ep in range(10):
    model.train()
    for x, y in tl:
        opt.zero_grad()
        out, _, _, _ = model(x.view(-1,784))
        nn.CrossEntropyLoss()(out, y).backward()
        opt.step()

# Analyze: per-sample PPL analog vs tension
model.eval()
all_tension, all_ppl, all_correct = [], [], []
with torch.no_grad():
    for x, y in te:
        x = x.view(-1,784)
        out, tension, _, _ = model(x)
        ce = F.cross_entropy(out, y, reduction='none')
        ppl = torch.exp(ce)
        correct = (out.argmax(1) == y).float()
        all_tension.append(tension)
        all_ppl.append(ppl)
        all_correct.append(correct)

T = torch.cat(all_tension).numpy()
P = torch.cat(all_ppl).numpy()
C = torch.cat(all_correct).numpy()

print("="*60)
print("H-CX-21: PPL analog vs Tension correlation")
print("="*60)

r = np.corrcoef(T, P)[0,1]
print(f"\n  Overall correlation:")
print(f"    r(tension, PPL) = {r:+.4f}")
print(f"    N = {len(T)}")

# Per-class
print(f"\n  Correct/Wrong answer separation:")
t_correct = T[C==1]; p_correct = P[C==1]
t_wrong = T[C==0]; p_wrong = P[C==0]
print(f"    Correct answer: tension={t_correct.mean():.3f}±{t_correct.std():.3f}, PPL={p_correct.mean():.3f}±{p_correct.std():.3f}")
print(f"    Wrong answer: tension={t_wrong.mean():.3f}±{t_wrong.std():.3f}, PPL={p_wrong.mean():.3f}±{p_wrong.std():.3f}")
print(f"    tension ratio (correct/wrong): {t_correct.mean()/t_wrong.mean():.3f}")
print(f"    PPL ratio (wrong/correct):     {p_wrong.mean()/p_correct.mean():.3f}")

# ASCII scatter (binned)
print(f"\n  Binned scatter (tension vs PPL):")
n_bins = 10
t_edges = np.linspace(T.min(), np.percentile(T, 95), n_bins+1)
for i in range(n_bins):
    mask = (T >= t_edges[i]) & (T < t_edges[i+1])
    if mask.sum() > 0:
        mean_p = P[mask].mean()
        bar = '#' * int(mean_p / 2)
        print(f"    T[{t_edges[i]:.1f}-{t_edges[i+1]:.1f}]: PPL={mean_p:.2f} |{bar}")

# Key test: does high tension = high PPL?
q_low = np.percentile(T, 25); q_high = np.percentile(T, 75)
ppl_low_t = P[T < q_low].mean()
ppl_high_t = P[T > q_high].mean()
print(f"\n  PPL in low-tension quartile:  {ppl_low_t:.3f}")
print(f"  PPL in high-tension quartile: {ppl_high_t:.3f}")
print(f"  Ratio: {ppl_high_t/ppl_low_t:.3f}")

if r > 0.1:
    print(f"\n  → Positive correlation! High tension = high PPL = uncertainty")
    print(f"  → H-CX-21 supported: tension ∝ PPL")
elif r < -0.1:
    print(f"\n  → Negative correlation! High tension = low PPL = confidence")
    print(f"  → H-CX-21 refuted (reversal)")
else:
    print(f"\n  → Weak correlation. Direction unclear.")

print(f"\nComplete")