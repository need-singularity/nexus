#!/usr/bin/env python3
"""H-SEDI-9: Entropy of confusion matrix predicts generalization.
Shannon entropy of confusion matrix decreases during training.
Rate of decrease (dH/dt) correlates with final accuracy.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch, torch.nn as nn, numpy as np
from model_pure_field import PureFieldEngine
from model_utils import load_mnist
from sklearn.metrics import confusion_matrix

def confusion_entropy(y_true, y_pred, n_classes=10):
    """Shannon entropy of normalized confusion matrix."""
    cm = confusion_matrix(y_true, y_pred, labels=range(n_classes))
    cm_norm = cm / (cm.sum() + 1e-12)
    cm_flat = cm_norm.flatten()
    cm_flat = cm_flat[cm_flat > 0]
    return -np.sum(cm_flat * np.log(cm_flat))

def train_and_track(seed, train_loader, test_loader, epochs=10):
    torch.manual_seed(seed)
    model = PureFieldEngine(784, 128, 10)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    entropies, accs = [], []

    for epoch in range(epochs):
        model.train()
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out, _ = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        # Evaluate + confusion entropy
        model.eval()
        all_pred, all_true = [], []
        with torch.no_grad():
            for X, y in test_loader:
                X = X.view(X.size(0), -1)
                out, _ = model(X)
                all_pred.extend(out.argmax(1).tolist())
                all_true.extend(y.tolist())
        acc = np.mean(np.array(all_pred) == np.array(all_true))
        h = confusion_entropy(all_true, all_pred)
        entropies.append(h)
        accs.append(acc)
    return entropies, accs

def main():
    print("=" * 60)
    print("H-SEDI-9: Confusion Matrix Entropy Predicts Generalization")
    print("=" * 60)
    train_loader, test_loader = load_mnist(batch_size=128)
    epochs = 10

    # Train multiple models with different seeds
    seeds = [42, 123, 456, 789, 1337, 2024, 3141, 9999]
    all_results = []
    for seed in seeds:
        print(f"  Training seed={seed}...")
        ents, accs = train_and_track(seed, train_loader, test_loader, epochs)
        all_results.append({'seed': seed, 'entropies': ents, 'accs': accs})

    # Display per-epoch entropy for first 3 models
    print(f"\n--- Per-Epoch Confusion Entropy (first 3 models) ---")
    print(f"{'Epoch':>6}", end="")
    for r in all_results[:3]:
        print(f"  H(s={r['seed']:>4})", end="")
    print()
    for ep in range(epochs):
        print(f"{ep+1:>6}", end="")
        for r in all_results[:3]:
            print(f"  {r['entropies'][ep]:>9.4f}", end="")
        print()

    # Compute dH/dt (slope of entropy over epochs)
    print(f"\n--- Entropy Decrease Rate vs Final Accuracy ---")
    print(f"{'Seed':>6} {'H(ep1)':>8} {'H(ep10)':>8} {'dH/dt':>8} {'FinalAcc':>10}")
    print("-" * 45)
    dh_list, final_acc_list = [], []
    for r in all_results:
        h_early = np.mean(r['entropies'][:3])
        h_late = np.mean(r['entropies'][-3:])
        dh = (h_late - h_early) / epochs  # should be negative
        dh_list.append(dh)
        final_acc_list.append(r['accs'][-1])
        print(f"{r['seed']:>6} {r['entropies'][0]:>8.4f} {r['entropies'][-1]:>8.4f} {dh:>8.5f} {r['accs'][-1]*100:>9.2f}%")

    # Correlation
    corr = np.corrcoef(dh_list, final_acc_list)[0, 1]
    print(f"\nCorrelation(dH/dt, final_acc) = {corr:.4f}")

    # Monotonic decrease check
    decreasing = []
    for r in all_results:
        is_dec = all(r['entropies'][i] >= r['entropies'][i+1] for i in range(len(r['entropies'])-1))
        mostly_dec = sum(1 for i in range(len(r['entropies'])-1) if r['entropies'][i] >= r['entropies'][i+1])
        decreasing.append(mostly_dec / (epochs - 1))
    avg_dec = np.mean(decreasing)
    print(f"Average fraction of epochs where H decreases: {avg_dec:.2f}")

    print(f"\n{'='*60}")
    h_decreases = avg_dec > 0.7
    corr_significant = abs(corr) > 0.5
    print(f"VERDICT:")
    print(f"  H(confusion) decreases during training = {h_decreases} ({avg_dec:.0%} epochs)")
    print(f"  dH/dt correlates with final accuracy = {corr_significant} (r={corr:.3f})")
    status = "SUPPORTED" if h_decreases and corr_significant else "PARTIAL" if h_decreases else "REFUTED"
    print(f"  Status: {status}")

if __name__ == '__main__':
    main()
