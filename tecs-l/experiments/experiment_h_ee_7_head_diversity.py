"""H-EE-7: Head dimension diversity — d=120 allows more head configs than d=128.
Train with d=120, varying num_heads={6,8,10,12} and compare losses."""
import torch, torch.nn as nn, time

torch.manual_seed(42)
text = "".join(chr(32 + (i * 7 + 13) % 95) for i in range(20000))
chars = sorted(set(text))
stoi = {c: i for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in text], dtype=torch.long)
vocab, seq_len, batch = len(chars), 32, 32

def make_batches(data):
    n = len(data) - seq_len - 1
    xs, ys = [], []
    for _ in range(batch * 50):
        i = torch.randint(0, n, (1,)).item()
        xs.append(data[i:i+seq_len]); ys.append(data[i+1:i+seq_len+1])
    return torch.stack(xs).reshape(-1, batch, seq_len), torch.stack(ys).reshape(-1, batch, seq_len)

xs, ys = make_batches(data)

class TinyLM(nn.Module):
    def __init__(self, d, nh, nl=2):
        super().__init__()
        self.emb = nn.Embedding(vocab, d)
        self.pos = nn.Embedding(seq_len, d)
        layer = nn.TransformerEncoderLayer(d, nh, d*4, dropout=0, batch_first=True)
        self.tf = nn.TransformerEncoder(layer, nl)
        self.out = nn.Linear(d, vocab)
    def forward(self, x):
        pos = torch.arange(x.size(1), device=x.device)
        h = self.emb(x) + self.pos(pos)
        mask = nn.Transformer.generate_square_subsequent_mask(x.size(1), device=x.device)
        return self.out(self.tf(h, mask=mask))

print("=" * 60)
print("H-EE-7: Head Dimension Diversity (d=120)")
print("=" * 60)
print(f"d=120 divisors: {[d for d in range(1,121) if 120%d==0]}")
print(f"d=128 divisors: {[d for d in range(1,129) if 128%d==0]}")
print()

# d=120 with varying heads
configs_120 = [(120, nh) for nh in [6, 8, 10, 12]]
# d=128 with varying heads (only powers of 2 work well)
configs_128 = [(128, nh) for nh in [4, 8, 16, 32]]

all_configs = configs_120 + configs_128
results = []
loss_fn = nn.CrossEntropyLoss()

for d, nh in all_configs:
    head_dim = d // nh
    model = TinyLM(d, nh)
    nparams = sum(p.numel() for p in model.parameters())
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    t0 = time.time()
    losses = []
    for step in range(300):
        bi = step % xs.size(0)
        logits = model(xs[bi])
        loss = loss_fn(logits.reshape(-1, vocab), ys[bi].reshape(-1))
        opt.zero_grad(); loss.backward(); opt.step()
        if step >= 250: losses.append(loss.item())
    avg_loss = sum(losses) / len(losses)
    elapsed = time.time() - t0
    results.append((d, nh, head_dim, nparams, avg_loss, elapsed))
    print(f"d={d:>4} nh={nh:>2} head_dim={head_dim:>3} params={nparams:>8} loss={avg_loss:.4f} time={elapsed:.1f}s")

print("\n" + "=" * 60)
print("COMPARISON: d=120 vs d=128")
print("=" * 60)
r120 = [r for r in results if r[0] == 120]
r128 = [r for r in results if r[0] == 128]
best120 = min(r120, key=lambda r: r[4])
best128 = min(r128, key=lambda r: r[4])
print(f"Best d=120: nh={best120[1]}, head_dim={best120[2]}, loss={best120[4]:.4f}")
print(f"Best d=128: nh={best128[1]}, head_dim={best128[2]}, loss={best128[4]:.4f}")
print(f"d=120 configs tested: {len(r120)}, d=128 configs tested: {len(r128)}")
print(f"d=120 valid heads (4-60): {[d for d in range(4,61) if 120%d==0]}")
print(f"d=128 valid heads (4-64): {[d for d in range(4,65) if 128%d==0]}")
avg120 = sum(r[4] for r in r120) / len(r120)
avg128 = sum(r[4] for r in r128) / len(r128)
print(f"Avg loss d=120: {avg120:.4f}, Avg loss d=128: {avg128:.4f}")
std120 = (sum((r[4]-avg120)**2 for r in r120)/len(r120))**0.5
std128 = (sum((r[4]-avg128)**2 for r in r128)/len(r128))**0.5
print(f"Std loss d=120: {std120:.4f}, Std loss d=128: {std128:.4f}")
print(f"Lower std = more robust across head configs")
