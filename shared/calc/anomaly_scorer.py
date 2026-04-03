#!/usr/bin/env python3
"""Anomaly Score Calculator — Anomaly Detection via Tension

Usage:
  python3 anomaly_scorer.py --data random --anomaly-ratio 0.1
  python3 anomaly_scorer.py --data cancer
"""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch.nn as nn, numpy as np

class AnomalyRepulsionField(nn.Module):
    def __init__(self, input_dim, hidden_dim=32):
        super().__init__()
        self.a = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, hidden_dim))
        self.g = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, hidden_dim))
    def forward(self, x):
        return (self.a(x) - self.g(x)).pow(2).sum(-1)  # tension = anomaly score

def main():
    parser = argparse.ArgumentParser(description='Anomaly Score Calculator')
    parser.add_argument('--data', default='random')
    parser.add_argument('--anomaly-ratio', type=float, default=0.1)
    parser.add_argument('--dim', type=int, default=20)
    args = parser.parse_args()

    if args.data == 'random':
        n_normal, n_anomaly = 500, int(500 * args.anomaly_ratio)
        X_normal = torch.randn(n_normal, args.dim)
        X_anomaly = torch.randn(n_anomaly, args.dim) * 3 + 5
        X = torch.cat([X_normal, X_anomaly])
        y = torch.cat([torch.zeros(n_normal), torch.ones(n_anomaly)])
    elif args.data == 'cancer':
        from sklearn.datasets import load_breast_cancer
        d = load_breast_cancer()
        X = torch.tensor(d.data, dtype=torch.float32)
        X = (X - X.mean(0)) / (X.std(0) + 1e-8)
        y = torch.tensor(d.target, dtype=torch.float32)
        # 0=malignant(anomaly), 1=benign(normal) → flip
        y = 1 - y
        args.dim = 30

    model = AnomalyRepulsionField(args.dim if args.data == 'random' else 30)
    opt = torch.optim.Adam(model.parameters(), lr=0.01)

    # Train only on normal data (reconstruction-free!)
    normal_mask = y == 0
    X_train = X[normal_mask]

    print(f"{'='*50}")
    print(f"  Anomaly Scorer (Tension-based)")
    print(f"  Normal: {normal_mask.sum().item()}, Anomaly: {(~normal_mask).sum().item()}")
    print(f"{'='*50}")

    for ep in range(50):
        model.train()
        tension = model(X_train)
        loss = tension.mean()  # minimize tension on normal
        opt.zero_grad(); loss.backward(); opt.step()

    model.eval()
    with torch.no_grad():
        scores = model(X).numpy()
        labels = y.numpy()

    # AUROC
    from itertools import combinations
    n_pos = labels.sum()
    n_neg = len(labels) - n_pos
    correct = sum(1 for i, j in zip(range(len(labels)), range(len(labels)))
                  if labels[i] == 1 and labels[j] == 0 and scores[i] > scores[j])
    # Simple AUROC
    pos_scores = scores[labels == 1]
    neg_scores = scores[labels == 0]
    auroc = sum(1 for p in pos_scores for n in neg_scores if p > n) / (len(pos_scores) * len(neg_scores))

    print(f"  AUROC: {auroc:.4f}")
    print(f"  Normal tension:  {scores[labels==0].mean():.4f} ± {scores[labels==0].std():.4f}")
    print(f"  Anomaly tension: {scores[labels==1].mean():.4f} ± {scores[labels==1].std():.4f}")
    print(f"  Ratio: {scores[labels==1].mean()/max(scores[labels==0].mean(), 1e-8):.1f}x")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()