#!/usr/bin/env python3
"""H-SEDI-8: Multi-engine consensus improves ensemble predictions.
Train 5 PureField models with different seeds, compare:
  a) Simple majority vote
  b) SEDI-weighted vote (weight by inverse tension = confidence)
  c) Single best model
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from model_pure_field import PureFieldEngine
from model_utils import load_mnist

def train_model(seed, train_loader, epochs=5):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = PureFieldEngine(784, 128, 10)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    for epoch in range(epochs):
        model.train()
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out, _ = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
    return model

def evaluate_ensemble(models, test_loader):
    """Evaluate individual + ensemble methods."""
    all_logits, all_tensions, all_labels = [], [], []
    for X, y in test_loader:
        X = X.view(X.size(0), -1)
        batch_logits, batch_tensions = [], []
        for m in models:
            m.eval()
            with torch.no_grad():
                out, tension = m(X)
                batch_logits.append(out)
                batch_tensions.append(tension)
        all_logits.append(torch.stack(batch_logits))      # [5, batch, 10]
        all_tensions.append(torch.stack(batch_tensions))   # [5, batch]
        all_labels.append(y)

    logits = torch.cat(all_logits, dim=1)    # [5, N, 10]
    tensions = torch.cat(all_tensions, dim=1) # [5, N]
    labels = torch.cat(all_labels)            # [N]

    # Individual accuracies
    individual_accs = []
    for i in range(5):
        pred = logits[i].argmax(dim=1)
        acc = (pred == labels).float().mean().item()
        individual_accs.append(acc)

    # a) Simple majority vote
    votes = logits.argmax(dim=2)  # [5, N]
    majority = torch.mode(votes, dim=0).values
    majority_acc = (majority == labels).float().mean().item()

    # b) SEDI-weighted vote (weight by 1/tension = confidence)
    weights = 1.0 / (tensions + 1e-6)  # [5, N]
    weights = weights / weights.sum(dim=0, keepdim=True)  # normalize
    weighted_logits = (weights.unsqueeze(-1) * logits).sum(dim=0)  # [N, 10]
    sedi_pred = weighted_logits.argmax(dim=1)
    sedi_acc = (sedi_pred == labels).float().mean().item()

    # c) Average logits (soft ensemble)
    avg_pred = logits.mean(dim=0).argmax(dim=1)
    avg_acc = (avg_pred == labels).float().mean().item()

    return individual_accs, majority_acc, sedi_acc, avg_acc

def main():
    print("=" * 60)
    print("H-SEDI-8: Multi-Engine Consensus Ensemble")
    print("=" * 60)
    train_loader, test_loader = load_mnist(batch_size=64)

    # Train 5 models with different seeds
    seeds = [42, 123, 456, 789, 1337]
    models = []
    for i, seed in enumerate(seeds):
        print(f"  Training model {i+1}/5 (seed={seed})...")
        m = train_model(seed, train_loader, epochs=5)
        models.append(m)

    # Evaluate
    ind_accs, majority_acc, sedi_acc, avg_acc = evaluate_ensemble(models, test_loader)

    print(f"\n{'='*60}")
    print(f"{'Method':<30} {'Accuracy':>10}")
    print(f"{'-'*40}")
    for i, acc in enumerate(ind_accs):
        print(f"  Model {i+1} (seed={seeds[i]}){'':<12} {acc*100:>8.2f}%")
    best_single = max(ind_accs)
    print(f"{'-'*40}")
    print(f"  Best single model{'':<12} {best_single*100:>8.2f}%")
    print(f"  Simple majority vote{'':<9} {majority_acc*100:>8.2f}%")
    print(f"  Average logits{'':<15} {avg_acc*100:>8.2f}%")
    print(f"  SEDI-weighted vote{'':<11} {sedi_acc*100:>8.2f}%")
    print(f"{'='*60}")

    # Analysis
    print(f"\n--- Improvement Analysis ---")
    print(f"  SEDI vs best single: {(sedi_acc - best_single)*100:+.2f}%")
    print(f"  SEDI vs majority:    {(sedi_acc - majority_acc)*100:+.2f}%")
    print(f"  Majority vs best:    {(majority_acc - best_single)*100:+.2f}%")
    print(f"  Avg vs best:         {(avg_acc - best_single)*100:+.2f}%")

    sedi_wins = sedi_acc > majority_acc and sedi_acc > best_single
    ensemble_wins = majority_acc > best_single or sedi_acc > best_single
    print(f"\n  SEDI-weighted beats all = {sedi_wins}")
    print(f"  Any ensemble beats single = {ensemble_wins}")
    status = "SUPPORTED" if sedi_wins else "PARTIAL" if ensemble_wins else "REFUTED"
    print(f"  Status: {status}")

if __name__ == '__main__':
    main()
