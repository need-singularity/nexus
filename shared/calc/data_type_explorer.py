#!/usr/bin/env python3
"""Data Type Explorer — Quickly test repulsion field with new data

Usage:
  python3 data_type_explorer.py --data iris
  python3 data_type_explorer.py --data random --dim 50 --classes 5 --samples 500
  python3 data_type_explorer.py --list
"""
import argparse, time, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import torch, torch.nn as nn, numpy as np
    from model_utils import Expert
    _HAS_DEPS = True
except ImportError as e:
    _HAS_DEPS = False
    _IMPORT_ERR = str(e)

class QuickRepulsionField(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.a = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, output_dim))
        self.g = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, output_dim))
        self.field = nn.Sequential(nn.Linear(output_dim, output_dim), nn.Tanh())
        self.scale = nn.Parameter(torch.tensor(1/3))
    def forward(self, x):
        a, g = self.a(x), self.g(x)
        rep = a - g
        t = (rep**2).sum(-1, keepdim=True)
        eq = (a + g) / 2
        return eq + self.scale * torch.sqrt(t + 1e-8) * self.field(rep), t.squeeze(-1)

class QuickDense(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, output_dim))
    def forward(self, x):
        return self.net(x)

def load_data(name, dim=50, classes=5, samples=500):
    if name == 'random':
        X = torch.randn(samples, dim)
        y = torch.randint(0, classes, (samples,))
        return X, y, dim, classes, f"Random({dim}d,{classes}c,{samples}n)"
    elif name == 'iris':
        from sklearn.datasets import load_iris
        d = load_iris()
        return torch.tensor(d.data, dtype=torch.float32), torch.tensor(d.target), 4, 3, "Iris"
    elif name == 'wine':
        from sklearn.datasets import load_wine
        d = load_wine()
        return torch.tensor(d.data, dtype=torch.float32), torch.tensor(d.target), 13, 3, "Wine"
    elif name == 'digits':
        from sklearn.datasets import load_digits
        d = load_digits()
        return torch.tensor(d.data, dtype=torch.float32), torch.tensor(d.target), 64, 10, "Digits"
    elif name == 'cancer':
        from sklearn.datasets import load_breast_cancer
        d = load_breast_cancer()
        return torch.tensor(d.data, dtype=torch.float32), torch.tensor(d.target), 30, 2, "BreastCancer"
    else:
        raise ValueError(f"Unknown: {name}. Use --list")

def main():
    parser = argparse.ArgumentParser(description='Data Type Explorer')
    parser.add_argument('--data', type=str, default='iris')
    parser.add_argument('--dim', type=int, default=50)
    parser.add_argument('--classes', type=int, default=5)
    parser.add_argument('--samples', type=int, default=500)
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()

    if not _HAS_DEPS:
        print(f"Error: Missing dependency — {_IMPORT_ERR}")
        print("Install with: pip install torch numpy")
        sys.exit(1)

    if args.list:
        print("Available: iris, wine, digits, cancer, random")
        return

    X, y, input_dim, n_classes, desc = load_data(args.data, args.dim, args.classes, args.samples)
    # Normalize
    X = (X - X.mean(0)) / (X.std(0) + 1e-8)

    # Train/test split
    n = len(X)
    idx = torch.randperm(n)
    split = int(0.8 * n)
    X_train, y_train = X[idx[:split]], y[idx[:split]]
    X_test, y_test = X[idx[split:]], y[idx[split:]]

    print(f"{'='*50}")
    print(f"  Data Type Explorer: {desc}")
    print(f"  dim={input_dim}, classes={n_classes}, n={n}")
    print(f"{'='*50}")

    results = {}
    for name, Model in [("Dense", QuickDense), ("Repulsion", QuickRepulsionField)]:
        torch.manual_seed(42)
        model = Model(input_dim, 32, n_classes)
        opt = torch.optim.Adam(model.parameters(), lr=0.01)
        crit = nn.CrossEntropyLoss()

        for ep in range(args.epochs):
            model.train()
            out = model(X_train)
            if isinstance(out, tuple): out = out[0]
            loss = crit(out, y_train)
            opt.zero_grad(); loss.backward(); opt.step()

        model.eval()
        with torch.no_grad():
            out = model(X_test)
            if isinstance(out, tuple):
                logits, tension = out
                mean_t = tension.mean().item()
            else:
                logits = out
                mean_t = 0
            acc = (logits.argmax(1) == y_test).float().mean().item()
        results[name] = (acc, mean_t)
        print(f"  {name:<12}: {acc*100:.1f}%  tension={mean_t:.2f}")

    delta = (results['Repulsion'][0] - results['Dense'][0]) * 100
    print(f"\n  Delta: {delta:+.1f}%")
    print(f"  Verdict: {'Repulsion WINS' if delta > 0.1 else 'TIED' if abs(delta) < 0.1 else 'Dense WINS'}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()