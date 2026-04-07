#!/usr/bin/env python3
"""H325 Verification: Fisher Information Geometry and Tension Manifold

Experiment Plan:
1. Train 2-pole RepulsionField on MNIST (15 epochs)
2. Collect class-wise tension fingerprints (10-dimensional vectors)
3. Approximate Fisher information matrix:
   (a) Sample covariance inverse → tr(F_k), det(F_k)
   (b) Gradient-based estimation: d log p / d fp
4. Correlation between Fisher trace vs mean tension (Pearson, Spearman)
5. Verify if high tension classes = high Fisher information

Prediction: r(tr(F), mean_tension) > +0.7
"""

import sys
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import stats

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

np.random.seed(42)
torch.manual_seed(42)


# ═══════════════════════════════════════════════
# 1. RepulsionField Model (2-pole)
# ═══════════════════════════════════════════════

class RepulsionField2Pole(nn.Module):
    """2-pole repulsion field engine with per-class fingerprint."""

    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        super().__init__()
        self.engine_a = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )
        self.engine_g = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )
        self.tension_scale = nn.Parameter(torch.tensor(1.0))

    def forward(self, x):
        out_a = self.engine_a(x)
        out_g = self.engine_g(x)
        repulsion = out_a - out_g
        tension = (repulsion ** 2).mean(dim=-1, keepdim=True)
        direction = F.normalize(repulsion, dim=-1)
        output = self.tension_scale * torch.sqrt(tension + 1e-8) * direction
        return output, tension.squeeze(-1), repulsion

    def get_fingerprint(self, x):
        """Per-class tension fingerprint (10-dim): repulsion^2 per output dim."""
        out_a = self.engine_a(x)
        out_g = self.engine_g(x)
        repulsion = out_a - out_g
        per_class_tension = repulsion ** 2  # (B, 10)
        return per_class_tension


# ═══════════════════════════════════════════════
# 2. Data Loading
# ═══════════════════════════════════════════════

from torchvision import datasets, transforms

def load_mnist():
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x.view(-1))
    ])
    train_ds = datasets.MNIST(root='/tmp/data', train=True, download=True, transform=transform)
    test_ds = datasets.MNIST(root='/tmp/data', train=False, download=True, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=256, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_ds, batch_size=256, shuffle=False)
    return train_loader, test_loader


# ═══════════════════════════════════════════════
# 3. Fisher Information Calculation Utilities
# ═══════════════════════════════════════════════

def compute_fisher_covariance(fps_k):
    """Method A: Covariance inverse-based Fisher information.

    Fisher info for Gaussian: F = Sigma^{-1}
    tr(F) = sum of 1/eigenvalues of covariance
    """
    n_samples, n_dim = fps_k.shape
    if n_samples < n_dim + 5:
        return 0.0, 0.0, np.zeros(n_dim)

    cov = np.cov(fps_k.T)  # (10, 10)
    # Regularize
    cov_reg = cov + np.eye(n_dim) * 1e-6

    eigenvalues = np.linalg.eigvalsh(cov_reg)
    eigenvalues = np.maximum(eigenvalues, 1e-10)

    # Fisher trace = sum(1/lambda_i)
    fisher_trace = np.sum(1.0 / eigenvalues)

    # Fisher log-det = -log(det(cov)) = -sum(log(lambda_i))
    fisher_logdet = -np.sum(np.log(eigenvalues))

    # Per-dimension Fisher (diagonal approximation)
    var_per_dim = np.var(fps_k, axis=0) + 1e-10
    fisher_per_dim = 1.0 / var_per_dim

    return fisher_trace, fisher_logdet, fisher_per_dim


def compute_fisher_gradient(model, data_loader, class_k, n_samples=500):
    """Method B: Gradient-based Fisher information estimation.

    F_k = E[ (d log p(y=k|x) / d theta)^2 ]
    Actual: mean squared gradient of log softmax output
    """
    model.eval()
    grad_norms_sq = []
    count = 0

    for x_batch, y_batch in data_loader:
        mask = y_batch == class_k
        if mask.sum() == 0:
            continue

        x_k = x_batch[mask]
        for i in range(min(len(x_k), n_samples - count)):
            model.zero_grad()
            xi = x_k[i:i+1]
            xi.requires_grad_(False)

            output, _, _ = model(xi)
            log_prob = F.log_softmax(output, dim=-1)[0, class_k]
            log_prob.backward()

            # Collect gradient norms
            total_grad_sq = 0.0
            for p in model.parameters():
                if p.grad is not None:
                    total_grad_sq += (p.grad ** 2).sum().item()
            grad_norms_sq.append(total_grad_sq)

            count += 1
            if count >= n_samples:
                break
        if count >= n_samples:
            break

    if len(grad_norms_sq) == 0:
        return 0.0
    return np.mean(grad_norms_sq)


# ═══════════════════════════════════════════════
# 4. Main Experiment
# ═══════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  H325 Verification: Fisher Information Geometry and Tension Manifold")
    print("  MNIST RepulsionField 2-pole Experiment")
    print("=" * 70)

    train_loader, test_loader = load_mnist()
    class_names = [str(i) for i in range(10)]
    n_classes = 10

    # ── Training ──
    model = RepulsionField2Pole(784, 128, 10)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    print("\n[Phase 1] RepulsionField Training (15 epochs)")
    for epoch in range(15):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        for x_batch, y_batch in train_loader:
            output, tension, _ = model(x_batch)
            loss = F.cross_entropy(output, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(x_batch)
            correct += (output.argmax(dim=-1) == y_batch).sum().item()
            total += len(x_batch)
        if (epoch + 1) % 5 == 0:
            acc = correct / total * 100
            print(f"  Epoch {epoch+1:>2}: loss={total_loss/total:.4f}, acc={acc:.1f}%")

    # Test accuracy
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            output, _, _ = model(x_batch)
            correct += (output.argmax(dim=-1) == y_batch).sum().item()
            total += len(x_batch)
    test_acc = correct / total * 100
    print(f"  Test accuracy: {test_acc:.1f}%")
    print(f"  tension_scale: {model.tension_scale.item():.4f}")

    # ── Fingerprint Collection ──
    print("\n[Phase 2] Collecting Class-wise Fingerprints")
    model.eval()
    all_fps = []
    all_tensions = []
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            fp = model.get_fingerprint(x_batch)
            output, tension, _ = model(x_batch)
            pred = output.argmax(dim=-1)
            all_fps.append(fp.numpy())
            all_tensions.append(tension.numpy())
            all_labels.append(y_batch.numpy())
            all_preds.append(pred.numpy())

    fps = np.concatenate(all_fps)        # (N, 10)
    tensions = np.concatenate(all_tensions)  # (N,)
    labels = np.concatenate(all_labels)      # (N,)
    preds = np.concatenate(all_preds)        # (N,)

    # ── Class-wise Statistics ──
    class_mean_tension = np.zeros(n_classes)
    class_std_tension = np.zeros(n_classes)
    class_accuracy = np.zeros(n_classes)
    class_counts = np.zeros(n_classes, dtype=int)

    for k in range(n_classes):
        mask = labels == k
        class_counts[k] = np.sum(mask)
        class_mean_tension[k] = np.mean(tensions[mask])
        class_std_tension[k] = np.std(tensions[mask])
        class_accuracy[k] = np.mean(preds[mask] == labels[mask]) * 100

    print(f"\n  Class-wise Mean Tension + Accuracy:")
    print(f"  {'Class':>6} | {'N':>5} | {'Mean T':>10} | {'Std T':>10} | {'Acc%':>6} | Bar")
    print(f"  {'─'*6}─┼─{'─'*5}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*6}─┼─{'─'*30}")
    max_t = np.max(class_mean_tension)
    for k in range(n_classes):
        bar_len = int(class_mean_tension[k] / max_t * 30)
        bar = "#" * bar_len
        print(f"  {class_names[k]:>6} | {class_counts[k]:>5} | {class_mean_tension[k]:>10.4f} | {class_std_tension[k]:>10.4f} | {class_accuracy[k]:>5.1f}% | {bar}")

    # ═══════════════════════════════════════════════
    # Phase 3: Fisher Information Matrix Calculation
    # ═══════════════════════════════════════════════

    print("\n[Phase 3] Fisher Information Matrix Calculation")

    # Method A: Covariance inverse
    print("\n  (A) Covariance inverse-based Fisher:")
    fisher_trace_A = np.zeros(n_classes)
    fisher_logdet_A = np.zeros(n_classes)
    fisher_diag_A = np.zeros((n_classes, n_classes))

    for k in range(n_classes):
        mask = labels == k
        fps_k = fps[mask]
        ft, fld, fd = compute_fisher_covariance(fps_k)
        fisher_trace_A[k] = ft
        fisher_logdet_A[k] = fld
        fisher_diag_A[k] = fd

    print(f"\n  {'Class':>6} | {'Mean T':>10} | {'F trace':>12} | {'F logdet':>12} | {'Acc%':>6}")
    print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*12}─┼─{'─'*12}─┼─{'─'*6}")
    for k in range(n_classes):
        print(f"  {class_names[k]:>6} | {class_mean_tension[k]:>10.4f} | {fisher_trace_A[k]:>12.1f} | {fisher_logdet_A[k]:>12.2f} | {class_accuracy[k]:>5.1f}%")

    # Method B: Gradient-based Fisher
    print("\n  (B) Gradient-based Fisher (200 samples per class):")
    fisher_grad_B = np.zeros(n_classes)

    model.train()  # Need gradients
    for k in range(n_classes):
        fg = compute_fisher_gradient(model, test_loader, k, n_samples=200)
        fisher_grad_B[k] = fg
        print(f"    Class {k}: F_grad = {fg:.2f}")

    model.eval()

    # ═══════════════════════════════════════════════
    # Phase 4: Correlation Analysis
    # ═══════════════════════════════════════════════

    print("\n[Phase 4] Correlation Analysis")
    print("=" * 60)

    # Pearson
    r_trace, p_trace = stats.pearsonr(class_mean_tension, fisher_trace_A)
    r_logdet, p_logdet = stats.pearsonr(class_mean_tension, fisher_logdet_A)
    r_grad, p_grad = stats.pearsonr(class_mean_tension, fisher_grad_B)
    r_acc_t, p_acc_t = stats.pearsonr(class_mean_tension, class_accuracy)
    r_acc_f, p_acc_f = stats.pearsonr(fisher_trace_A, class_accuracy)

    # Spearman
    rho_trace, sp_trace = stats.spearmanr(class_mean_tension, fisher_trace_A)
    rho_logdet, sp_logdet = stats.spearmanr(class_mean_tension, fisher_logdet_A)
    rho_grad, sp_grad = stats.spearmanr(class_mean_tension, fisher_grad_B)

    print(f"\n  Pearson Correlation:")
    print(f"  {'Pair':>35} | {'r':>8} | {'p-value':>10} | {'Sig':>5}")
    print(f"  {'─'*35}─┼─{'─'*8}─┼─{'─'*10}─┼─{'─'*5}")
    print(f"  {'tension vs Fisher trace (cov)':>35} | {r_trace:>+8.4f} | {p_trace:>10.4f} | {'***' if p_trace < 0.001 else '**' if p_trace < 0.01 else '*' if p_trace < 0.05 else 'ns':>5}")
    print(f"  {'tension vs Fisher logdet':>35} | {r_logdet:>+8.4f} | {p_logdet:>10.4f} | {'***' if p_logdet < 0.001 else '**' if p_logdet < 0.01 else '*' if p_logdet < 0.05 else 'ns':>5}")
    print(f"  {'tension vs Fisher grad':>35} | {r_grad:>+8.4f} | {p_grad:>10.4f} | {'***' if p_grad < 0.001 else '**' if p_grad < 0.01 else '*' if p_grad < 0.05 else 'ns':>5}")
    print(f"  {'tension vs accuracy':>35} | {r_acc_t:>+8.4f} | {p_acc_t:>10.4f} | {'***' if p_acc_t < 0.001 else '**' if p_acc_t < 0.01 else '*' if p_acc_t < 0.05 else 'ns':>5}")
    print(f"  {'Fisher trace vs accuracy':>35} | {r_acc_f:>+8.4f} | {p_acc_f:>10.4f} | {'***' if p_acc_f < 0.001 else '**' if p_acc_f < 0.01 else '*' if p_acc_f < 0.05 else 'ns':>5}")

    print(f"\n  Spearman Rank Correlation:")
    print(f"  {'Pair':>35} | {'rho':>8} | {'p-value':>10}")
    print(f"  {'─'*35}─┼─{'─'*8}─┼─{'─'*10}")
    print(f"  {'tension vs Fisher trace (cov)':>35} | {rho_trace:>+8.4f} | {sp_trace:>10.4f}")
    print(f"  {'tension vs Fisher logdet':>35} | {rho_logdet:>+8.4f} | {sp_logdet:>10.4f}")
    print(f"  {'tension vs Fisher grad':>35} | {rho_grad:>+8.4f} | {sp_grad:>10.4f}")

    # ═══════════════════════════════════════════════
    # Phase 5: Fisher Information Matrix Eigenvalue Analysis
    # ═══════════════════════════════════════════════

    print("\n[Phase 5] Fisher Matrix Eigenvalue Spectrum")
    print("=" * 60)

    print(f"\n  Class-wise Covariance Eigenvalues (top 3):")
    print(f"  {'Class':>6} | {'lambda_1':>10} | {'lambda_2':>10} | {'lambda_3':>10} | {'cond num':>10}")
    print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*10}")

    class_condition = np.zeros(n_classes)
    for k in range(n_classes):
        mask = labels == k
        fps_k = fps[mask]
        cov_k = np.cov(fps_k.T)
        eigvals = np.sort(np.linalg.eigvalsh(cov_k + np.eye(10) * 1e-8))[::-1]
        class_condition[k] = eigvals[0] / (eigvals[-1] + 1e-10)
        print(f"  {class_names[k]:>6} | {eigvals[0]:>10.4f} | {eigvals[1]:>10.4f} | {eigvals[2]:>10.4f} | {class_condition[k]:>10.1f}")

    r_cond, p_cond = stats.pearsonr(class_mean_tension, class_condition)
    print(f"\n  r(tension, condition_number) = {r_cond:+.4f} (p={p_cond:.4f})")

    # ═══════════════════════════════════════════════
    # Phase 6: ASCII Scatter Plots
    # ═══════════════════════════════════════════════

    print("\n[Phase 6] Scatter Plots")
    print("=" * 60)

    def ascii_scatter(x_vals, y_vals, x_label, y_label, labels_list, width=50, height=20):
        """ASCII scatter plot."""
        x_min, x_max = np.min(x_vals), np.max(x_vals)
        y_min, y_max = np.min(y_vals), np.max(y_vals)
        x_range = x_max - x_min + 1e-10
        y_range = y_max - y_min + 1e-10

        grid = [['.' for _ in range(width)] for _ in range(height)]
        for i in range(len(x_vals)):
            xi = int((x_vals[i] - x_min) / x_range * (width - 1))
            yi = int((y_vals[i] - y_min) / y_range * (height - 1))
            yi = height - 1 - yi
            xi = max(0, min(width - 1, xi))
            yi = max(0, min(height - 1, yi))
            grid[yi][xi] = labels_list[i][0]

        print(f"\n  {y_label} ^")
        for row in grid:
            print(f"  |{''.join(row)}")
        print(f"  +{'─' * width}> {x_label}")

    ascii_scatter(class_mean_tension, fisher_trace_A,
                  "Mean Tension", "Fisher Trace (cov-inv)",
                  class_names)

    ascii_scatter(class_mean_tension, fisher_grad_B,
                  "Mean Tension", "Fisher Grad",
                  class_names)

    ascii_scatter(class_mean_tension, class_accuracy,
                  "Mean Tension", "Accuracy %",
                  class_names)

    # ═══════════════════════════════════════════════
    # Phase 7: Overall Verdict
    # ═══════════════════════════════════════════════

    print("\n\n" + "=" * 70)
    print("  Overall Verdict")
    print("=" * 70)

    print(f"\n  Core Correlation (tension vs Fisher trace via cov-inv):")
    print(f"    Pearson r  = {r_trace:+.4f}  (p = {p_trace:.4f})")
    print(f"    Spearman rho = {rho_trace:+.4f}  (p = {sp_trace:.4f})")

    print(f"\n  Secondary Correlation (tension vs Fisher grad):")
    print(f"    Pearson r  = {r_grad:+.4f}  (p = {p_grad:.4f})")
    print(f"    Spearman rho = {rho_grad:+.4f}  (p = {sp_grad:.4f})")

    print(f"\n  Triangle Verification (tension -> Fisher -> accuracy):")
    print(f"    tension -> accuracy:  r = {r_acc_t:+.4f}")
    print(f"    Fisher  -> accuracy:  r = {r_acc_f:+.4f}")

    # Judgment
    avg_r = (abs(r_trace) + abs(r_grad)) / 2
    sign_consistent = (r_trace > 0) == (r_grad > 0)

    print(f"\n  Average |r| = {avg_r:.4f}")
    print(f"  Sign consistency: {'YES' if sign_consistent else 'NO'}")

    if r_trace > 0.7 and p_trace < 0.05:
        verdict = "STRONG SUPPORT: Fisher trace ~ tension (r > +0.7, p < 0.05)"
        grade = "green"
    elif r_trace > 0.3 and p_trace < 0.05:
        verdict = "PARTIAL SUPPORT: positive correlation but weaker than predicted"
        grade = "orange-star"
    elif r_trace > 0 and p_trace < 0.1:
        verdict = "WEAK SUPPORT: marginal positive trend"
        grade = "orange"
    elif abs(r_trace) < 0.3:
        verdict = "NOT SUPPORTED: no significant correlation"
        grade = "white"
    else:
        verdict = "REFUTED: negative correlation (opposite of prediction)"
        grade = "black"

    # Check direction: H325 predicts HIGH tension = HIGH Fisher
    if r_trace < 0:
        direction_note = "INVERTED: high tension = LOW Fisher (opposite of H325 prediction)"
    else:
        direction_note = "CORRECT DIRECTION: high tension = high Fisher"

    print(f"\n  Direction: {direction_note}")
    print(f"  Verdict: {verdict}")
    print(f"  Grade: {grade}")

    print(f"\n  Notes:")
    print(f"    1. Fisher = 1/Cov approximation (Gaussian assumption)")
    print(f"    2. n=10 classes → df=8, limited statistical power")
    print(f"    3. Only MNIST tested (needs replication with Fashion-MNIST)")
    print(f"    4. Gradient Fisher uses all model parameters → interpret with care")
    print(f"    5. Causal direction unclear: Fisher->tension? tension->Fisher? common cause?")

    # ═══════════════════════════════════════════════
    # Full Data Dump (for README)
    # ═══════════════════════════════════════════════

    print("\n\n" + "=" * 70)
    print("  Full Data (for README documentation)")
    print("=" * 70)

    print(f"\n  | Class | N    | Mean T   | Std T    | F_trace    | F_logdet | F_grad     | Acc%  |")
    print(f"  |-------|------|----------|----------|------------|----------|------------|-------|")
    for k in range(n_classes):
        print(f"  | {class_names[k]:>5} | {class_counts[k]:>4} | {class_mean_tension[k]:>8.4f} | {class_std_tension[k]:>8.4f} | {fisher_trace_A[k]:>10.1f} | {fisher_logdet_A[k]:>8.2f} | {fisher_grad_B[k]:>10.2f} | {class_accuracy[k]:>5.1f} |")

    print(f"\n  Correlation Summary:")
    print(f"  | Metric                        | Pearson r | p-value  | Spearman rho | p-value  |")
    print(f"  |-------------------------------|-----------|----------|--------------|----------|")
    print(f"  | tension vs F_trace (cov-inv)  | {r_trace:>+9.4f} | {p_trace:>8.4f} | {rho_trace:>+12.4f} | {sp_trace:>8.4f} |")
    print(f"  | tension vs F_logdet           | {r_logdet:>+9.4f} | {p_logdet:>8.4f} | {rho_logdet:>+12.4f} | {sp_logdet:>8.4f} |")
    print(f"  | tension vs F_grad             | {r_grad:>+9.4f} | {p_grad:>8.4f} | {rho_grad:>+12.4f} | {sp_grad:>8.4f} |")
    print(f"  | tension vs accuracy           | {r_acc_t:>+9.4f} | {p_acc_t:>8.4f} |              |          |")
    print(f"  | F_trace vs accuracy           | {r_acc_f:>+9.4f} | {p_acc_f:>8.4f} |              |          |")

    print(f"\n  Model Parameters:")
    print(f"    tension_scale = {model.tension_scale.item():.4f}")
    print(f"    test_acc = {test_acc:.1f}%")

    print("\n" + "=" * 70)
    print("  Experiment Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()