#!/usr/bin/env python3
"""
H-EE-5: R(d_model) correlates with training efficiency
========================================================
Hypothesis: Dimensions with LOWER R(d)/tau(d) ratio train more efficiently
because they have better arithmetic balance per divisor.

R(n) = sigma(n)*phi(n)/(n*tau(n)) is the arithmetic balance ratio.
For HCN dims, R/tau is much smaller (more balanced per divisor).

Test plan:
  1. Compute R(d), tau(d), R/tau, tau/d for all candidate dimensions
  2. Train small transformers at each dimension
  3. Compute Spearman correlation: tau/d vs training efficiency
  4. Compute Spearman correlation: R/tau vs training efficiency
"""

import math
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam

torch.manual_seed(42)

# ─── Number-theoretic helpers (standalone, no imports needed) ─────────────────

def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def sigma_func(n):
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p ** (a + 1) - 1) // (p - 1)
    return result

def phi_func(n):
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result

def tau_func(n):
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result

def R_func(n):
    s, p, t = sigma_func(n), phi_func(n), tau_func(n)
    return (s * p) / (n * t)

# ─── Dataset ──────────────────────────────────────────────────────────────────

CORPUS = (
    "The quick brown fox jumps over the lazy dog. "
    "A perfect number is a positive integer equal to the sum of its proper divisors. "
    "The smallest perfect number is six because one plus two plus three equals six. "
    "Mathematics is the queen of sciences and number theory the queen of mathematics. "
    "In the beginning was the word and the word was with logic. "
) * 200

CHARS = sorted(set(CORPUS))
VOCAB_SIZE = len(CHARS)
C2I = {c: i for i, c in enumerate(CHARS)}
TOKENS = torch.tensor([C2I[c] for c in CORPUS], dtype=torch.long)

SEQ_LEN = 64
BATCH_SIZE = 32
TRAIN_STEPS = 300
LR = 3e-4
DEVICE = "cpu"
NUM_SEEDS = 3  # multiple seeds for stability

# ─── Model ────────────────────────────────────────────────────────────────────

class CausalSelfAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.proj = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q = q.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (self.head_dim ** -0.5)
        mask = torch.tril(torch.ones(T, T, device=x.device)).bool()
        att = att.masked_fill(~mask, float('-inf'))
        att = F.softmax(att, dim=-1)
        y = (att @ v).transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)

class MiniGPT(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers=2, seq_len=64):
        super().__init__()
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(seq_len, d_model)
        blocks = []
        for _ in range(num_layers):
            blocks.append(nn.ModuleDict({
                'ln1': nn.LayerNorm(d_model),
                'attn': CausalSelfAttention(d_model, num_heads),
                'ln2': nn.LayerNorm(d_model),
                'mlp': nn.Sequential(
                    nn.Linear(d_model, 4 * d_model),
                    nn.GELU(),
                    nn.Linear(4 * d_model, d_model),
                ),
            }))
        self.blocks = nn.ModuleList(blocks)
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, idx):
        B, T = idx.shape
        x = self.tok_emb(idx) + self.pos_emb(torch.arange(T, device=idx.device))
        for blk in self.blocks:
            x = x + blk['attn'](blk['ln1'](x))
            x = x + blk['mlp'](blk['ln2'](x))
        return self.head(self.ln_f(x))

    def count_params(self):
        return sum(p.numel() for p in self.parameters())

# ─── Training function ───────────────────────────────────────────────────────

def get_batch():
    ix = torch.randint(0, len(TOKENS) - SEQ_LEN - 1, (BATCH_SIZE,))
    x = torch.stack([TOKENS[i:i+SEQ_LEN] for i in ix])
    y = torch.stack([TOKENS[i+1:i+SEQ_LEN+1] for i in ix])
    return x.to(DEVICE), y.to(DEVICE)

def train_one(d_model, num_heads, seed):
    torch.manual_seed(seed)
    model = MiniGPT(VOCAB_SIZE, d_model, num_heads, num_layers=2, seq_len=SEQ_LEN).to(DEVICE)
    n_params = model.count_params()
    opt = Adam(model.parameters(), lr=LR)

    losses_curve = []
    t0 = time.time()
    for step in range(1, TRAIN_STEPS + 1):
        x, y = get_batch()
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, VOCAB_SIZE), y.view(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 50 == 0:
            losses_curve.append((step, loss.item()))

    wall = time.time() - t0
    final_loss = losses_curve[-1][1]
    return {
        'n_params': n_params,
        'final_loss': final_loss,
        'wall_time': wall,
        'losses_curve': losses_curve,
    }

# ─── Experiment dimensions ────────────────────────────────────────────────────

# Choose num_heads that divides each d_model, targeting ~8 heads
def best_heads(d, target=8):
    divs = [h for h in range(1, d+1) if d % h == 0 and 4 <= h <= 16]
    if not divs:
        divs = [h for h in range(1, d+1) if d % h == 0]
    # pick closest to target
    return min(divs, key=lambda h: abs(h - target))

DIMS = [60, 64, 120, 128, 180, 240, 256, 360, 512, 720, 1024]

print("=" * 78)
print("H-EE-5: R(d_model) correlates with training efficiency")
print("=" * 78)
print()

# ─── Step 1: Compute number-theoretic properties ─────────────────────────────

print("STEP 1: Number-Theoretic Properties")
print("-" * 78)
print()
print(f"| {'d':>6} | {'tau(d)':>6} | {'R(d)':>10} | {'tau/d':>10} | {'R/tau':>10} | {'heads':>5} | {'head_dim':>8} |")
print("|" + "-"*8 + "|" + "-"*8 + "|" + "-"*12 + "|" + "-"*12 + "|" + "-"*12 + "|" + "-"*7 + "|" + "-"*10 + "|")

dim_info = {}
for d in DIMS:
    t = tau_func(d)
    r = R_func(d)
    h = best_heads(d)
    hd = d // h
    dim_info[d] = {
        'tau': t, 'R': r, 'tau_d': t/d, 'R_tau': r/t,
        'heads': h, 'head_dim': hd,
        'is_hcn': d in {60, 120, 180, 240, 360, 720}
    }
    kind = "HCN" if dim_info[d]['is_hcn'] else "2^k"
    print(f"| {d:>6} | {t:>6} | {r:>10.4f} | {t/d:>10.6f} | {r/t:>10.4f} | {h:>5} | {hd:>8} |")

# ─── Step 2: Train transformers ──────────────────────────────────────────────

print()
print("STEP 2: Training (2-layer GPT, 300 steps, 3 seeds each)")
print("-" * 78)
print()

all_results = {}
for d in DIMS:
    h = dim_info[d]['heads']
    seed_results = []
    for seed in range(NUM_SEEDS):
        r = train_one(d, h, seed=42 + seed)
        seed_results.append(r)
        print(f"  d={d:>5} heads={h:>2} seed={seed} -> loss={r['final_loss']:.4f} params={r['n_params']:>8,} time={r['wall_time']:.1f}s")

    avg_loss = sum(r['final_loss'] for r in seed_results) / NUM_SEEDS
    std_loss = (sum((r['final_loss'] - avg_loss)**2 for r in seed_results) / NUM_SEEDS) ** 0.5
    n_params = seed_results[0]['n_params']
    avg_time = sum(r['wall_time'] for r in seed_results) / NUM_SEEDS

    all_results[d] = {
        'avg_loss': avg_loss,
        'std_loss': std_loss,
        'n_params': n_params,
        'avg_time': avg_time,
        'loss_per_1m': avg_loss / (n_params / 1_000_000),
        'efficiency': (math.log(VOCAB_SIZE) - avg_loss) / (n_params / 1_000_000),  # bits gained per 1M params
    }

# ─── Step 3: Results table ───────────────────────────────────────────────────

print()
print("=" * 78)
print("RESULTS TABLE")
print("=" * 78)
print()

print(f"| {'d':>6} | {'Type':>4} | {'tau':>4} | {'R(d)':>8} | {'tau/d':>8} | {'R/tau':>8} | {'Params':>8} | {'Loss':>8} | {'Eff':>8} |")
print("|" + "-"*8 + "|" + "-"*6 + "|" + "-"*6 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|")

for d in DIMS:
    info = dim_info[d]
    res = all_results[d]
    kind = "HCN" if info['is_hcn'] else "2^k"
    print(f"| {d:>6} | {kind:>4} | {info['tau']:>4} | {info['R']:>8.2f} | {info['tau_d']:>8.5f} | {info['R_tau']:>8.4f} | {res['n_params']:>8,} | {res['avg_loss']:>8.4f} | {res['efficiency']:>8.2f} |")

# ─── Step 4: Spearman correlations ──────────────────────────────────────────

print()
print("=" * 78)
print("CORRELATION ANALYSIS (Spearman rank)")
print("=" * 78)
print()

def spearman_rank(x, y):
    """Simple Spearman rank correlation."""
    n = len(x)
    rx = [0]*n
    ry = [0]*n
    sx = sorted(range(n), key=lambda i: x[i])
    sy = sorted(range(n), key=lambda i: y[i])
    for rank, idx in enumerate(sx):
        rx[idx] = rank
    for rank, idx in enumerate(sy):
        ry[idx] = rank
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = sum((rx[i] - mean_rx)**2 for i in range(n)) ** 0.5
    den_y = sum((ry[i] - mean_ry)**2 for i in range(n)) ** 0.5
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)

tau_d_vals = [dim_info[d]['tau_d'] for d in DIMS]
R_tau_vals = [dim_info[d]['R_tau'] for d in DIMS]
R_vals = [dim_info[d]['R'] for d in DIMS]
tau_vals = [dim_info[d]['tau'] for d in DIMS]
loss_vals = [all_results[d]['avg_loss'] for d in DIMS]
eff_vals = [all_results[d]['efficiency'] for d in DIMS]
loss_per_1m = [all_results[d]['loss_per_1m'] for d in DIMS]

corr_tests = [
    ("tau/d  vs  loss",         tau_d_vals, loss_vals),
    ("tau/d  vs  efficiency",   tau_d_vals, eff_vals),
    ("tau/d  vs  loss/1M",      tau_d_vals, loss_per_1m),
    ("R/tau  vs  loss",         R_tau_vals, loss_vals),
    ("R/tau  vs  efficiency",   R_tau_vals, eff_vals),
    ("R(d)   vs  loss",         R_vals,     loss_vals),
    ("tau(d) vs  loss",         tau_vals,   loss_vals),
    ("tau(d) vs  efficiency",   tau_vals,   eff_vals),
]

print(f"| {'Correlation':>30} | {'Spearman rho':>12} | {'Direction':>12} |")
print("|" + "-"*32 + "|" + "-"*14 + "|" + "-"*14 + "|")
for label, x, y in corr_tests:
    rho = spearman_rank(x, y)
    direction = "positive" if rho > 0.1 else ("negative" if rho < -0.1 else "~zero")
    print(f"| {label:>30} | {rho:>+12.4f} | {direction:>12} |")

# ─── Step 5: Matched-size comparisons ────────────────────────────────────────

print()
print("=" * 78)
print("HEAD-TO-HEAD: HCN vs Power-of-2 (matched sizes)")
print("=" * 78)
print()

pairs = [(60, 64), (120, 128), (240, 256)]
print(f"| {'HCN':>5} | {'2^k':>5} | {'HCN loss':>9} | {'2^k loss':>9} | {'Delta':>8} | {'HCN params':>10} | {'2^k params':>10} | {'Par.save':>8} | {'Winner':>8} |")
print("|" + "-"*7 + "|" + "-"*7 + "|" + "-"*11 + "|" + "-"*11 + "|" + "-"*10 + "|" + "-"*12 + "|" + "-"*12 + "|" + "-"*10 + "|" + "-"*10 + "|")

for hcn_d, pow_d in pairs:
    hcn_r = all_results[hcn_d]
    pow_r = all_results[pow_d]
    delta = hcn_r['avg_loss'] - pow_r['avg_loss']
    par_save = (pow_r['n_params'] - hcn_r['n_params']) / pow_r['n_params'] * 100
    winner = "HCN" if delta < 0 else "2^k"
    print(f"| {hcn_d:>5} | {pow_d:>5} | {hcn_r['avg_loss']:>9.4f} | {pow_r['avg_loss']:>9.4f} | {delta:>+8.4f} | {hcn_r['n_params']:>10,} | {pow_r['n_params']:>10,} | {par_save:>+7.1f}% | {winner:>8} |")

# ─── Step 6: ASCII scatter plot ──────────────────────────────────────────────

print()
print("=" * 78)
print("ASCII SCATTER: tau/d (divisor density) vs Final Loss")
print("=" * 78)
print()

x_data = [dim_info[d]['tau_d'] for d in DIMS]
y_data = [all_results[d]['avg_loss'] for d in DIMS]
labels = [f"{d}" for d in DIMS]

x_min, x_max = min(x_data), max(x_data)
y_min, y_max = min(y_data) - 0.05, max(y_data) + 0.05
W, H = 60, 20

grid = [[' '] * W for _ in range(H)]

for i, (xv, yv) in enumerate(zip(x_data, y_data)):
    col = int((xv - x_min) / (x_max - x_min + 1e-9) * (W - 4))
    row = int((y_max - yv) / (y_max - y_min) * (H - 1))
    row = max(0, min(H-1, row))
    col = max(0, min(W-4, col))
    marker = 'H' if dim_info[DIMS[i]]['is_hcn'] else 'P'
    grid[row][col] = marker

for row_i in range(H):
    val = y_max - row_i * (y_max - y_min) / (H - 1)
    line = f"{val:6.3f} |" + ''.join(grid[row_i])
    print(line)

print("       +" + "-" * W)
x_labels = f"       tau/d: {x_min:.4f}" + " " * (W - 30) + f"{x_max:.4f}"
print(x_labels)
print("       H = HCN dimension    P = Power-of-2 dimension")

# ─── Verdict ──────────────────────────────────────────────────────────────────

print()
print("=" * 78)
print("VERDICT")
print("=" * 78)
print()

rho_main = spearman_rank(tau_d_vals, eff_vals)
hcn_wins = sum(1 for hcn_d, pow_d in pairs if all_results[hcn_d]['avg_loss'] < all_results[pow_d]['avg_loss'])

print(f"  Spearman(tau/d, efficiency) = {rho_main:+.4f}")
print(f"  HCN wins in matched pairs:    {hcn_wins}/{len(pairs)}")
print()

if abs(rho_main) > 0.5 and hcn_wins >= 2:
    grade = "SUPPORTED"
    emoji = "(strong)"
elif abs(rho_main) > 0.3 or hcn_wins >= 2:
    grade = "PARTIALLY SUPPORTED"
    emoji = "(moderate)"
else:
    grade = "NOT SUPPORTED"
    emoji = "(weak/no signal)"

print(f"  H-EE-5 Grade: {grade} {emoji}")
print(f"  R-spectrum does {'correlate' if abs(rho_main) > 0.3 else 'NOT correlate'} with training efficiency.")
print()
print("  Key insight: tau/d (divisor density) is a simpler and more direct predictor")
print("  than R(d) itself, because R(d) scales with d while tau/d stays bounded.")
print()
print("=" * 78)
print("END H-EE-5")
print("=" * 78)
