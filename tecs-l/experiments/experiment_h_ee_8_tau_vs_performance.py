#!/usr/bin/env python3
"""
H-EE-8: Optimal d_model follows tau(d) more than d itself
==========================================================
Hypothesis: Among models of similar parameter count, higher tau(d_model)
leads to better performance.

Key idea: Match parameter counts by adjusting depth (num_layers).
Then the ONLY variable is d_model's divisor structure.

Test plan:
  1. For each (d_model, num_layers) pair, compute param count
  2. Find param-matched pairs: d=120 vs d=128, d=240 vs d=256
  3. Adjust num_layers to equalize param count within 5%
  4. Train and compare: does higher tau(d) win at matched params?
"""

import math
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam

torch.manual_seed(42)

# ─── Number theory ────────────────────────────────────────────────────────────

def tau(n):
    count = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            count += 2 if i != n // i else 1
    return count

# ─── Dataset ──────────────────────────────────────────────────────────────────

CORPUS = (
    "The quick brown fox jumps over the lazy dog. "
    "A perfect number is a positive integer equal to the sum of its proper divisors. "
    "The smallest perfect number is six because one plus two plus three equals six. "
    "Mathematics is the queen of sciences and number theory the queen of mathematics. "
    "In the beginning was the word and the word was with logic. "
    "Attention is all you need but the dimension of attention matters too. "
    "The number of divisors determines the flexibility of the architecture. "
    "Highly composite numbers maximize divisor count for their magnitude. "
) * 200

CHARS = sorted(set(CORPUS))
VOCAB_SIZE = len(CHARS)
C2I = {c: i for i, c in enumerate(CHARS)}
TOKENS = torch.tensor([C2I[c] for c in CORPUS], dtype=torch.long)

SEQ_LEN = 64
BATCH_SIZE = 32
TRAIN_STEPS = 400
LR = 3e-4
DEVICE = "cpu"
NUM_SEEDS = 3

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

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_batch():
    ix = torch.randint(0, len(TOKENS) - SEQ_LEN - 1, (BATCH_SIZE,))
    x = torch.stack([TOKENS[i:i+SEQ_LEN] for i in ix])
    y = torch.stack([TOKENS[i+1:i+SEQ_LEN+1] for i in ix])
    return x.to(DEVICE), y.to(DEVICE)

def best_heads(d, target=8):
    divs = [h for h in range(1, min(d+1, 33)) if d % h == 0 and h >= 4]
    return min(divs, key=lambda h: abs(h - target)) if divs else 1

def count_model_params(d_model, num_layers, num_heads):
    """Approximate param count without building model."""
    # Embedding: vocab * d + seq * d
    embed = VOCAB_SIZE * d_model + SEQ_LEN * d_model
    # Per layer: QKV (3*d*d) + proj (d*d) + MLP (4*d*d + 4*d*d) + 2*LN (4*d)
    per_layer = 3 * d_model * d_model + d_model * d_model + 4 * d_model * d_model + 4 * d_model * d_model + 4 * d_model
    # Head: d * vocab
    head = d_model * VOCAB_SIZE
    # Final LN: 2*d
    final_ln = 2 * d_model
    return embed + num_layers * per_layer + head + final_ln

def train_one(d_model, num_heads, num_layers, seed):
    torch.manual_seed(seed)
    model = MiniGPT(VOCAB_SIZE, d_model, num_heads, num_layers=num_layers, seq_len=SEQ_LEN).to(DEVICE)
    n_params = model.count_params()
    opt = Adam(model.parameters(), lr=LR)

    losses = {}
    t0 = time.time()
    for step in range(1, TRAIN_STEPS + 1):
        x, y = get_batch()
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, VOCAB_SIZE), y.view(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 100 == 0:
            losses[step] = loss.item()

    wall = time.time() - t0
    return {
        'd_model': d_model, 'num_heads': num_heads, 'num_layers': num_layers,
        'n_params': n_params, 'final_loss': losses[TRAIN_STEPS],
        'wall_time': wall, 'losses': losses, 'tau': tau(d_model),
    }

# ─── Step 1: Find param-matched configurations ──────────────────────────────

print("=" * 80)
print("H-EE-8: Does tau(d_model) predict performance at matched param count?")
print("=" * 80)
print()

print("STEP 1: Parameter Count Estimation")
print("-" * 80)
print()

# Target pairs: match param count by adjusting depth
PAIRS_TO_TEST = [
    # (d_hcn, d_pow2)
    (60, 64),
    (120, 128),
    (240, 256),
]

matched_configs = []

for d_hcn, d_pow2 in PAIRS_TO_TEST:
    h_hcn = best_heads(d_hcn)
    h_pow2 = best_heads(d_pow2)

    print(f"  Pair: d={d_hcn} (tau={tau(d_hcn)}) vs d={d_pow2} (tau={tau(d_pow2)})")

    # Try different layer counts to find param match
    print(f"    {'d':>5} {'layers':>6} {'heads':>5} {'approx_params':>13}")
    best_match = None
    best_diff = float('inf')

    for layers_hcn in range(1, 8):
        p_hcn = count_model_params(d_hcn, layers_hcn, h_hcn)
        for layers_pow2 in range(1, 8):
            p_pow2 = count_model_params(d_pow2, layers_pow2, h_pow2)
            diff = abs(p_hcn - p_pow2) / max(p_hcn, p_pow2)
            if diff < best_diff:
                best_diff = diff
                best_match = (layers_hcn, layers_pow2, p_hcn, p_pow2, diff)

    l_hcn, l_pow2, p_hcn, p_pow2, diff = best_match
    print(f"    {d_hcn:>5} {l_hcn:>6} {h_hcn:>5} {p_hcn:>13,}")
    print(f"    {d_pow2:>5} {l_pow2:>6} {h_pow2:>5} {p_pow2:>13,}")
    print(f"    Param diff: {diff*100:.1f}%")
    print()

    matched_configs.append({
        'hcn': (d_hcn, h_hcn, l_hcn, p_hcn),
        'pow2': (d_pow2, h_pow2, l_pow2, p_pow2),
        'diff': diff,
    })

# ─── Step 2: Also test at FIXED depth ────────────────────────────────────────

print()
print("STEP 2: Fixed-Depth Comparison (2 layers, same architecture)")
print("-" * 80)
print()

FIXED_DEPTH_DIMS = [60, 64, 96, 120, 128, 180, 240, 256, 360]

print(f"| {'d':>5} | {'tau':>4} | {'heads':>5} | {'layers':>6} | {'params':>8} |")
print("|" + "-"*7 + "|" + "-"*6 + "|" + "-"*7 + "|" + "-"*8 + "|" + "-"*10 + "|")

for d in FIXED_DEPTH_DIMS:
    h = best_heads(d)
    p = count_model_params(d, 2, h)
    print(f"| {d:>5} | {tau(d):>4} | {h:>5} | {2:>6} | {p:>8,} |")

# ─── Step 3: Train everything ────────────────────────────────────────────────

print()
print("STEP 3: Training (multi-seed)")
print("-" * 80)
print()

# Part A: Param-matched pairs
print("Part A: Param-matched pairs")
matched_results = []

for mc in matched_configs:
    pair_results = {}
    for label, (d, h, l, _) in [('hcn', mc['hcn']), ('pow2', mc['pow2'])]:
        seed_losses = []
        for seed in range(NUM_SEEDS):
            r = train_one(d, h, l, seed=42+seed)
            seed_losses.append(r['final_loss'])
            print(f"  d={d:>5} L={l} h={h:>2} seed={seed} loss={r['final_loss']:.4f} params={r['n_params']:>8,}")
        avg = sum(seed_losses) / NUM_SEEDS
        std = (sum((x - avg)**2 for x in seed_losses) / NUM_SEEDS) ** 0.5
        r['final_loss'] = avg
        r['std_loss'] = std
        pair_results[label] = r
    matched_results.append(pair_results)
    print()

# Part B: Fixed-depth sweep
print("Part B: Fixed-depth sweep (2 layers)")
fixed_results = {}

for d in FIXED_DEPTH_DIMS:
    h = best_heads(d)
    seed_losses = []
    for seed in range(NUM_SEEDS):
        r = train_one(d, h, 2, seed=42+seed)
        seed_losses.append(r['final_loss'])
    avg = sum(seed_losses) / NUM_SEEDS
    std = (sum((x - avg)**2 for x in seed_losses) / NUM_SEEDS) ** 0.5
    r['final_loss'] = avg
    r['std_loss'] = std
    fixed_results[d] = r
    print(f"  d={d:>5} tau={tau(d):>3} loss={avg:.4f}+/-{std:.4f} params={r['n_params']:>8,}")

# ─── Step 4: Results ──────────────────────────────────────────────────────────

print()
print("=" * 80)
print("RESULTS A: Param-Matched Pair Comparison")
print("=" * 80)
print()

print(f"| {'d_hcn':>6} | {'d_pow2':>6} | {'tau_hcn':>7} | {'tau_pow2':>7} | {'L_hcn':>5} | {'L_pow2':>5} | {'loss_hcn':>8} | {'loss_pow2':>8} | {'Delta':>8} | {'Winner':>7} |")
print("|" + "-"*8 + "|" + "-"*8 + "|" + "-"*9 + "|" + "-"*9 + "|" + "-"*7 + "|" + "-"*7 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*9 + "|")

hcn_pair_wins = 0
for i, mc in enumerate(matched_configs):
    rh = matched_results[i]['hcn']
    rp = matched_results[i]['pow2']
    delta = rh['final_loss'] - rp['final_loss']
    winner = "HCN" if delta < 0 else "2^k"
    if delta < 0:
        hcn_pair_wins += 1
    print(f"| {mc['hcn'][0]:>6} | {mc['pow2'][0]:>6} | {rh['tau']:>7} | {rp['tau']:>7} | {mc['hcn'][2]:>5} | {mc['pow2'][2]:>5} | {rh['final_loss']:>8.4f} | {rp['final_loss']:>8.4f} | {delta:>+8.4f} | {winner:>7} |")

# ─── Results B: Fixed depth ──────────────────────────────────────────────────

print()
print("=" * 80)
print("RESULTS B: Fixed-Depth (2 layers) — tau(d) vs Loss")
print("=" * 80)
print()

print(f"| {'d':>5} | {'tau(d)':>6} | {'Params':>8} | {'Loss':>8} | {'Std':>7} | {'Loss/1M':>8} |")
print("|" + "-"*7 + "|" + "-"*8 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*9 + "|" + "-"*10 + "|")

for d in FIXED_DEPTH_DIMS:
    r = fixed_results[d]
    l1m = r['final_loss'] / (r['n_params'] / 1_000_000)
    print(f"| {d:>5} | {tau(d):>6} | {r['n_params']:>8,} | {r['final_loss']:>8.4f} | {r['std_loss']:>7.4f} | {l1m:>8.2f} |")

# ─── Correlation: tau vs loss/1M ──────────────────────────────────────────────

print()
print("=" * 80)
print("CORRELATION ANALYSIS")
print("=" * 80)
print()

def spearman_rank(x, y):
    n = len(x)
    rx = [0]*n
    ry = [0]*n
    sx = sorted(range(n), key=lambda i: x[i])
    sy = sorted(range(n), key=lambda i: y[i])
    for rank, idx in enumerate(sx): rx[idx] = rank
    for rank, idx in enumerate(sy): ry[idx] = rank
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = sum((rx[i] - mean_rx)**2 for i in range(n)) ** 0.5
    den_y = sum((ry[i] - mean_ry)**2 for i in range(n)) ** 0.5
    if den_x == 0 or den_y == 0: return 0.0
    return num / (den_x * den_y)

taus = [tau(d) for d in FIXED_DEPTH_DIMS]
losses = [fixed_results[d]['final_loss'] for d in FIXED_DEPTH_DIMS]
params = [fixed_results[d]['n_params'] for d in FIXED_DEPTH_DIMS]
loss_per_1m = [fixed_results[d]['final_loss'] / (fixed_results[d]['n_params'] / 1e6) for d in FIXED_DEPTH_DIMS]

# Also compute at similar size (exclude very different sizes)
# Group: small (60-64-96), medium (120-128), large (240-256)
groups = [
    ("small (60-96)", [60, 64, 96]),
    ("medium (120-128)", [120, 128]),
    ("large (240-256)", [240, 256]),
]

print(f"  Overall Spearman(tau, loss):       {spearman_rank(taus, losses):+.4f}")
print(f"  Overall Spearman(tau, loss/1M):    {spearman_rank(taus, loss_per_1m):+.4f}")
print(f"  Overall Spearman(d, loss):         {spearman_rank(list(FIXED_DEPTH_DIMS), losses):+.4f}")
print()

print("  Within size groups:")
for gname, gdims in groups:
    g_taus = [tau(d) for d in gdims]
    g_losses = [fixed_results[d]['final_loss'] for d in gdims]
    if len(gdims) >= 3:
        rho = spearman_rank(g_taus, g_losses)
        print(f"    {gname}: Spearman(tau, loss) = {rho:+.4f}")
    else:
        # Just compare
        t1, t2 = g_taus
        l1, l2 = g_losses
        higher_tau = gdims[0] if t1 > t2 else gdims[1]
        lower_loss = gdims[0] if l1 < l2 else gdims[1]
        print(f"    {gname}: Higher tau -> d={higher_tau}, Lower loss -> d={lower_loss}  {'MATCH' if higher_tau == lower_loss else 'MISMATCH'}")

# ─── ASCII: tau vs loss ──────────────────────────────────────────────────────

print()
print("=" * 80)
print("ASCII: tau(d) vs Final Loss (fixed 2-layer)")
print("=" * 80)
print()

sorted_by_tau = sorted(FIXED_DEPTH_DIMS, key=lambda d: tau(d))
max_loss = max(fixed_results[d]['final_loss'] for d in sorted_by_tau)
min_loss = min(fixed_results[d]['final_loss'] for d in sorted_by_tau)

for d in sorted_by_tau:
    r = fixed_results[d]
    bar_len = int((r['final_loss'] - min_loss) / (max_loss - min_loss + 1e-9) * 40) + 1
    is_hcn = d in {60, 120, 180, 240, 360, 720}
    marker = 'H' if is_hcn else 'P'
    print(f"  tau={tau(d):>3} d={d:>4} |{'=' * bar_len}{marker} {r['final_loss']:.4f}")

print()
print("  H = HCN    P = non-HCN (power of 2 or other)")

# ─── Verdict ──────────────────────────────────────────────────────────────────

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()

rho_tau_loss = spearman_rank(taus, losses)
rho_tau_eff = spearman_rank(taus, loss_per_1m)

# Check within-group results
pair_match = sum(1 for gname, gdims in groups if len(gdims) == 2
    and (tau(gdims[0]) > tau(gdims[1])) == (fixed_results[gdims[0]]['final_loss'] < fixed_results[gdims[1]]['final_loss']))

total_pairs = sum(1 for _, gdims in groups if len(gdims) == 2)

print(f"  Spearman(tau, loss) overall:    {rho_tau_loss:+.4f}")
print(f"  Spearman(tau, loss/1M) overall: {rho_tau_eff:+.4f}")
print(f"  Matched-param HCN wins:         {hcn_pair_wins}/{len(matched_configs)}")
print(f"  Within-group tau->loss matches:  {pair_match}/{total_pairs}")
print()

if rho_tau_loss < -0.3 and hcn_pair_wins >= 2:
    grade = "SUPPORTED"
    detail = "Higher tau(d) consistently predicts lower loss"
elif rho_tau_loss < -0.1 or hcn_pair_wins >= 2:
    grade = "PARTIALLY SUPPORTED"
    detail = "tau(d) shows some predictive power but confounded by d"
else:
    grade = "NOT SUPPORTED"
    detail = "tau(d) does not predict loss independently of d"

print(f"  H-EE-8 Grade: {grade}")
print(f"  Detail: {detail}")
print()
print("  Note: Overall correlation is confounded because larger d has both more params")
print("  AND higher tau. The matched-param comparison is the cleaner test.")
print()
print("=" * 80)
print("END H-EE-8")
print("=" * 80)
