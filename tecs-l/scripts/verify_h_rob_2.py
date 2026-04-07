#!/usr/bin/env python3
"""H-ROB-2: Tension = Torque Optimization verification script
Simulates 2-DOF planar robot, trains neural net, correlates tension with torque.
"""

import numpy as np
import math

np.random.seed(42)

print("=" * 70)
print("H-ROB-2: Tension = Torque Optimization Verification")
print("=" * 70)

# === 1. 2-DOF Planar Robot Setup ===
print("\n### 1. 2-DOF Planar Robot Parameters ###")
print()

L1, L2 = 1.0, 0.8  # link lengths
print(f"  Link 1: L1 = {L1}")
print(f"  Link 2: L2 = {L2}")
print(f"  Workspace: annulus r_min={abs(L1-L2):.1f}, r_max={L1+L2:.1f}")

# === 2. Forward Kinematics ===
def forward_kinematics(theta1, theta2):
    """Compute end-effector position from joint angles"""
    x = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2)
    y = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2)
    return x, y

# === 3. Jacobian ===
def jacobian(theta1, theta2):
    """2x2 Jacobian matrix"""
    J = np.array([
        [-L1*np.sin(theta1) - L2*np.sin(theta1+theta2), -L2*np.sin(theta1+theta2)],
        [ L1*np.cos(theta1) + L2*np.cos(theta1+theta2),  L2*np.cos(theta1+theta2)]
    ])
    return J

# === 4. Inverse Kinematics ===
def inverse_kinematics(x, y):
    """Compute joint angles for target position (elbow-up solution)"""
    r2 = x**2 + y**2
    cos_theta2 = (r2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_theta2 = np.clip(cos_theta2, -1, 1)
    theta2 = np.arccos(cos_theta2)  # elbow-up

    k1 = L1 + L2 * np.cos(theta2)
    k2 = L2 * np.sin(theta2)
    theta1 = np.arctan2(y, x) - np.arctan2(k2, k1)
    return theta1, theta2

# === 5. Generate workspace samples ===
print("\n### 2. Generating Workspace Samples ###")
print()

N_SAMPLES = 2000
r_min = abs(L1 - L2) + 0.05
r_max = L1 + L2 - 0.05

# Sample in polar coordinates for uniform workspace coverage
angles = np.random.uniform(0, 2*np.pi, N_SAMPLES)
radii = np.sqrt(np.random.uniform(r_min**2, r_max**2, N_SAMPLES))

targets_x = radii * np.cos(angles)
targets_y = radii * np.sin(angles)

# Compute IK and torques
joint_angles = []
torques = []
manipulabilities = []
valid_targets_x = []
valid_targets_y = []
distances = []

gravity = np.array([0, -9.81])  # gravity pointing down
m1, m2 = 1.0, 0.8  # link masses

for i in range(N_SAMPLES):
    try:
        t1, t2 = inverse_kinematics(targets_x[i], targets_y[i])
        if np.isnan(t1) or np.isnan(t2):
            continue

        J = jacobian(t1, t2)
        det_J = abs(np.linalg.det(J))

        if det_J < 1e-6:  # near singularity
            continue

        # Gravity torque computation
        # Torque to hold position against gravity
        # Joint 1 torque: m1*g*L1/2*cos(t1) + m2*g*(L1*cos(t1) + L2/2*cos(t1+t2))
        # Joint 2 torque: m2*g*L2/2*cos(t1+t2)
        tau1 = m1*9.81*(L1/2)*np.cos(t1) + m2*9.81*(L1*np.cos(t1) + L2/2*np.cos(t1+t2))
        tau2 = m2*9.81*(L2/2)*np.cos(t1+t2)

        total_torque = np.sqrt(tau1**2 + tau2**2)

        # Manipulability = |det(J)| = sqrt(det(J*J^T))
        manip = det_J

        joint_angles.append((t1, t2))
        torques.append(total_torque)
        manipulabilities.append(manip)
        valid_targets_x.append(targets_x[i])
        valid_targets_y.append(targets_y[i])
        distances.append(radii[i])
    except:
        continue

N_VALID = len(torques)
print(f"  Total samples: {N_SAMPLES}")
print(f"  Valid (non-singular): {N_VALID}")

torques = np.array(torques)
manipulabilities = np.array(manipulabilities)
distances = np.array(distances)

print(f"  Torque range: [{torques.min():.3f}, {torques.max():.3f}] Nm")
print(f"  Manipulability range: [{manipulabilities.min():.4f}, {manipulabilities.max():.4f}]")

# === 6. Simple Neural Network (from scratch) ===
print("\n### 3. Training Neural Network (IK prediction) ###")
print()

X = np.column_stack([valid_targets_x, valid_targets_y])
Y = np.array(joint_angles)

# Normalize
X_mean, X_std = X.mean(axis=0), X.std(axis=0)
Y_mean, Y_std = Y.mean(axis=0), Y.std(axis=0)
X_norm = (X - X_mean) / X_std
Y_norm = (Y - Y_mean) / Y_std

# Simple 2-layer neural network
HIDDEN = 64
LR = 0.005
EPOCHS = 500

# Initialize weights
W1 = np.random.randn(2, HIDDEN) * 0.1
b1 = np.zeros(HIDDEN)
W2 = np.random.randn(HIDDEN, 32) * 0.1
b2 = np.zeros(32)
W3 = np.random.randn(32, 2) * 0.1
b3 = np.zeros(2)

def relu(x):
    return np.maximum(0, x)

def relu_grad(x):
    return (x > 0).astype(float)

# Split train/test
N_train = int(0.8 * N_VALID)
idx = np.random.permutation(N_VALID)
train_idx, test_idx = idx[:N_train], idx[N_train:]

X_train, Y_train = X_norm[train_idx], Y_norm[train_idx]
X_test, Y_test = X_norm[test_idx], Y_norm[test_idx]

losses = []
for epoch in range(EPOCHS):
    # Forward
    h1 = relu(X_train @ W1 + b1)
    h2 = relu(h1 @ W2 + b2)
    pred = h2 @ W3 + b3

    # Loss
    diff = pred - Y_train
    loss = np.mean(diff**2)
    losses.append(loss)

    # Backward
    grad_pred = 2 * diff / len(X_train)

    grad_W3 = h2.T @ grad_pred
    grad_b3 = grad_pred.sum(axis=0)

    grad_h2 = grad_pred @ W3.T * relu_grad(h1 @ W2 + b2)
    grad_W2 = h1.T @ grad_h2
    grad_b2 = grad_h2.sum(axis=0)

    grad_h1 = grad_h2 @ W2.T * relu_grad(X_train @ W1 + b1)
    grad_W1 = X_train.T @ grad_h1
    grad_b1 = grad_h1.sum(axis=0)

    # Update
    W3 -= LR * grad_W3
    b3 -= LR * grad_b3
    W2 -= LR * grad_W2
    b2 -= LR * grad_b2
    W1 -= LR * grad_W1
    b1 -= LR * grad_b1

print(f"  Architecture: 2 → {HIDDEN} → 32 → 2")
print(f"  Training samples: {N_train}")
print(f"  Test samples: {N_VALID - N_train}")
print(f"  Final train loss: {losses[-1]:.6f}")

# Test
h1_t = relu(X_test @ W1 + b1)
h2_t = relu(h1_t @ W2 + b2)
pred_test = h2_t @ W3 + b3
test_loss = np.mean((pred_test - Y_test)**2)
print(f"  Test loss: {test_loss:.6f}")

# === 7. Compute Tension ===
print("\n### 4. Computing Neural Network Tension ###")
print()

# Tension = prediction uncertainty proxy
# Using variance of hidden activations as tension measure
# High variance in hidden layer = high tension (network is "uncertain")

def compute_tension(x_input):
    """Compute tension as normalized activation variance"""
    h1 = relu(x_input @ W1 + b1)
    h2 = relu(h1 @ W2 + b2)
    pred = h2 @ W3 + b3

    # Tension measures:
    # 1. Activation sparsity (fraction of dead neurons)
    sparsity1 = np.mean(h1 == 0, axis=1)
    sparsity2 = np.mean(h2 == 0, axis=1)

    # 2. Activation magnitude variance (per sample)
    act_var1 = np.var(h1, axis=1)
    act_var2 = np.var(h2, axis=1)

    # 3. Prediction confidence (inverse of output magnitude)
    pred_magnitude = np.sqrt(np.sum(pred**2, axis=1))

    # Combined tension: high sparsity + high variance = high tension
    tension = 0.3 * sparsity1 + 0.3 * sparsity2 + 0.2 * (act_var1 / (act_var1.max() + 1e-8)) + 0.2 * (act_var2 / (act_var2.max() + 1e-8))

    return tension, pred

tensions_test, preds_test = compute_tension(X_test)
tensions_all, preds_all = compute_tension(X_norm)

print(f"  Tension range: [{tensions_all.min():.4f}, {tensions_all.max():.4f}]")
print(f"  Tension mean:  {tensions_all.mean():.4f}")
print(f"  Tension std:   {tensions_all.std():.4f}")

# === 8. Correlate Tension with Torque ===
print("\n### 5. Tension vs Torque Correlation ###")
print()

# Correlation
from numpy import corrcoef

torques_test = torques[test_idx]
manip_test = manipulabilities[test_idx]
dist_test = distances[test_idx]

corr_tension_torque = corrcoef(tensions_test, torques_test)[0, 1]
corr_tension_manip = corrcoef(tensions_test, manip_test)[0, 1]
corr_tension_dist = corrcoef(tensions_test, dist_test)[0, 1]
corr_torque_dist = corrcoef(torques_test, dist_test)[0, 1]
corr_torque_manip = corrcoef(torques_test, manip_test)[0, 1]

print(f"  Correlation Matrix:")
print(f"  {'':>15s} {'Tension':>10s} {'Torque':>10s} {'Manip.':>10s} {'Distance':>10s}")
print(f"  {'Tension':>15s} {'1.000':>10s} {corr_tension_torque:>10.4f} {corr_tension_manip:>10.4f} {corr_tension_dist:>10.4f}")
print(f"  {'Torque':>15s} {corr_tension_torque:>10.4f} {'1.000':>10s} {corr_torque_manip:>10.4f} {corr_torque_dist:>10.4f}")
print(f"  {'Manipulability':>15s} {corr_tension_manip:>10.4f} {corr_torque_manip:>10.4f} {'1.000':>10s} {'—':>10s}")

# === 9. Bin analysis ===
print("\n### 6. Binned Analysis — Torque Quintiles vs Tension ###")
print()

# Sort by torque, divide into quintiles
sorted_idx = np.argsort(torques_test)
quintile_size = len(sorted_idx) // 5

print(f"  {'Quintile':>10s} {'Torque Range':>20s} {'Mean Torque':>12s} {'Mean Tension':>13s} {'Tension Std':>12s}")
print(f"  {'-'*10} {'-'*20} {'-'*12} {'-'*13} {'-'*12}")

quintile_torques = []
quintile_tensions = []

for q in range(5):
    start = q * quintile_size
    end = (q + 1) * quintile_size if q < 4 else len(sorted_idx)
    q_idx = sorted_idx[start:end]

    t_range = f"[{torques_test[q_idx].min():.2f}, {torques_test[q_idx].max():.2f}]"
    mean_t = torques_test[q_idx].mean()
    mean_ten = tensions_test[q_idx].mean()
    std_ten = tensions_test[q_idx].std()

    quintile_torques.append(mean_t)
    quintile_tensions.append(mean_ten)

    label = f"Q{q+1}"
    if q == 0:
        label += " (low τ)"
    elif q == 4:
        label += " (high τ)"
    print(f"  {label:>10s} {t_range:>20s} {mean_t:>12.3f} {mean_ten:>13.4f} {std_ten:>12.4f}")

# === 10. Manipulability analysis ===
print("\n### 7. Manipulability Quintiles vs Tension ###")
print()

sorted_manip_idx = np.argsort(manip_test)

print(f"  {'Quintile':>10s} {'Manip Range':>20s} {'Mean Manip':>12s} {'Mean Tension':>13s} {'Near Singul.':>13s}")
print(f"  {'-'*10} {'-'*20} {'-'*12} {'-'*13} {'-'*13}")

for q in range(5):
    start = q * quintile_size
    end = (q + 1) * quintile_size if q < 4 else len(sorted_manip_idx)
    q_idx = sorted_manip_idx[start:end]

    m_range = f"[{manip_test[q_idx].min():.3f}, {manip_test[q_idx].max():.3f}]"
    mean_m = manip_test[q_idx].mean()
    mean_ten = tensions_test[q_idx].mean()
    near_sing = "YES" if mean_m < 0.1 else "no"

    label = f"Q{q+1}"
    if q == 0:
        label += " (sing.)"
    elif q == 4:
        label += " (free)"
    print(f"  {label:>10s} {m_range:>20s} {mean_m:>12.4f} {mean_ten:>13.4f} {near_sing:>13s}")

# === 11. ASCII Workspace Heatmap ===
print("\n### 8. ASCII Workspace — Tension Heatmap ###")
print()

GRID = 20
x_min, x_max = -2.0, 2.0
y_min, y_max = -2.0, 2.0

# Bin all samples into grid
grid_tension = np.full((GRID, GRID), np.nan)
grid_count = np.zeros((GRID, GRID))
grid_torque = np.full((GRID, GRID), np.nan)

for i in range(N_VALID):
    xi = int((valid_targets_x[i] - x_min) / (x_max - x_min) * GRID)
    yi = int((valid_targets_y[i] - y_min) / (y_max - y_min) * GRID)
    if 0 <= xi < GRID and 0 <= yi < GRID:
        if np.isnan(grid_tension[yi, xi]):
            grid_tension[yi, xi] = 0
            grid_torque[yi, xi] = 0
        grid_tension[yi, xi] += tensions_all[i]
        grid_torque[yi, xi] += torques[i]
        grid_count[yi, xi] += 1

# Average
mask = grid_count > 0
grid_tension[mask] /= grid_count[mask]
grid_torque[mask] /= grid_count[mask]

# Normalize tension for display
t_min = np.nanmin(grid_tension)
t_max = np.nanmax(grid_tension)
chars = " ·░▒▓█"

print("  Tension Heatmap (darker = higher tension):")
print(f"  X: [{x_min:.1f}, {x_max:.1f}]  Y: [{y_min:.1f}, {y_max:.1f}]")
print("  " + "+" + "-" * GRID + "+")
for row in range(GRID - 1, -1, -1):
    line = "  |"
    for col in range(GRID):
        if np.isnan(grid_tension[row, col]):
            line += " "
        else:
            norm_val = (grid_tension[row, col] - t_min) / (t_max - t_min + 1e-8)
            idx = min(int(norm_val * (len(chars) - 1)), len(chars) - 1)
            line += chars[idx]
    line += "|"
    print(line)
print("  " + "+" + "-" * GRID + "+")
print(f"  Legend: ' '=outside, '·'=low, '░▒▓█'=increasing tension")

# Torque heatmap
t_min_t = np.nanmin(grid_torque)
t_max_t = np.nanmax(grid_torque)

print()
print("  Torque Heatmap (darker = higher torque):")
print("  " + "+" + "-" * GRID + "+")
for row in range(GRID - 1, -1, -1):
    line = "  |"
    for col in range(GRID):
        if np.isnan(grid_torque[row, col]):
            line += " "
        else:
            norm_val = (grid_torque[row, col] - t_min_t) / (t_max_t - t_min_t + 1e-8)
            idx = min(int(norm_val * (len(chars) - 1)), len(chars) - 1)
            line += chars[idx]
    line += "|"
    print(line)
print("  " + "+" + "-" * GRID + "+")
print(f"  Legend: ' '=outside, '·'=low, '░▒▓█'=increasing torque")

# === 12. Training loss curve ===
print("\n### 9. Training Loss Curve (ASCII) ###")
print()

# Subsample losses for display
display_epochs = [0, 10, 25, 50, 100, 150, 200, 300, 400, 499]
max_bar = 50
max_loss = max(losses[e] for e in display_epochs)

print(f"  {'Epoch':>6s} | {'Loss':>10s} | Graph")
print(f"  {'-'*6}-+-{'-'*10}-+-{'-'*50}")
for e in display_epochs:
    bar_len = int(losses[e] / max_loss * max_bar)
    bar = "█" * bar_len
    print(f"  {e:>6d} | {losses[e]:>10.6f} | {bar}")

# === 13. Statistical significance ===
print("\n### 10. Statistical Significance ###")
print()

# Permutation test for correlation
n_perms = 10000
observed_corr = abs(corr_tension_torque)
count_exceed = 0
for _ in range(n_perms):
    perm_tensions = np.random.permutation(tensions_test)
    perm_corr = abs(corrcoef(perm_tensions, torques_test)[0, 1])
    if perm_corr >= observed_corr:
        count_exceed += 1

perm_p_value = count_exceed / n_perms

print(f"  Observed |corr(tension, torque)| = {observed_corr:.4f}")
print(f"  Permutation test (n={n_perms}):")
print(f"    p-value = {perm_p_value:.4f}")
if perm_p_value < 0.05:
    print(f"    → Significant at alpha=0.05  ✓")
elif perm_p_value < 0.10:
    print(f"    → Marginally significant (0.05 < p < 0.10)")
else:
    print(f"    → NOT significant (p > 0.10)")

# Also test tension vs manipulability
observed_corr_m = abs(corr_tension_manip)
count_exceed_m = 0
for _ in range(n_perms):
    perm_tensions = np.random.permutation(tensions_test)
    perm_corr = abs(corrcoef(perm_tensions, manip_test)[0, 1])
    if perm_corr >= observed_corr_m:
        count_exceed_m += 1

perm_p_value_m = count_exceed_m / n_perms
print(f"\n  Observed |corr(tension, manipulability)| = {observed_corr_m:.4f}")
print(f"  Permutation p-value = {perm_p_value_m:.4f}")

# === 14. Golden Zone connection ===
print("\n### 11. Golden Zone Connection ###")
print()

golden_center = 1 / math.e
golden_lower = 0.5 - math.log(4/3)
golden_upper = 0.5

# What fraction of tensions fall in Golden Zone?
tensions_rescaled = (tensions_all - tensions_all.min()) / (tensions_all.max() - tensions_all.min() + 1e-8)
in_golden = np.sum((tensions_rescaled >= golden_lower) & (tensions_rescaled <= golden_upper)) / len(tensions_rescaled)
print(f"  Golden Zone: [{golden_lower:.4f}, {golden_upper:.4f}]")
print(f"  Fraction of rescaled tensions in Golden Zone: {in_golden:.4f} ({in_golden*100:.1f}%)")
print(f"  Expected if uniform: {golden_upper - golden_lower:.4f} ({(golden_upper - golden_lower)*100:.1f}%)")
print(f"  Ratio: {in_golden / (golden_upper - golden_lower):.2f}x")

# Tension at optimal manipulability
best_manip_idx = np.argmax(manipulabilities)
worst_manip_idx = np.argmin(manipulabilities)
print(f"\n  At best manipulability point:")
print(f"    Tension = {tensions_all[best_manip_idx]:.4f}")
print(f"    Torque  = {torques[best_manip_idx]:.3f} Nm")
print(f"  At worst manipulability point:")
print(f"    Tension = {tensions_all[worst_manip_idx]:.4f}")
print(f"    Torque  = {torques[worst_manip_idx]:.3f} Nm")

# === Summary ===
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print(f"  corr(tension, torque)         = {corr_tension_torque:+.4f} (p={perm_p_value:.4f})")
print(f"  corr(tension, manipulability) = {corr_tension_manip:+.4f} (p={perm_p_value_m:.4f})")
print(f"  corr(tension, distance)       = {corr_tension_dist:+.4f}")
print()
print("  Interpretation:")
if abs(corr_tension_torque) > 0.3:
    print("  → STRONG: Neural tension correlates with physical torque")
    print("  → Tension as torque proxy is viable")
elif abs(corr_tension_torque) > 0.1:
    print("  → MODERATE: Some correlation exists between tension and torque")
    print("  → Tension partially captures physical difficulty")
else:
    print("  → WEAK: Tension does not strongly correlate with torque")
    print("  → With this simple architecture, tension ≠ torque")

print()
print("  Prediction check:")
print(f"  → High torque = high tension? corr = {corr_tension_torque:+.4f}")
print(f"  → Near singularity = high tension? corr(tension,manip) = {corr_tension_manip:+.4f}")
if corr_tension_manip < -0.1:
    print("     Low manipulability → high tension ✓ (negative correlation expected)")
elif corr_tension_manip > 0.1:
    print("     UNEXPECTED: high manipulability → high tension")
else:
    print("     No clear relationship with singularity proximity")

print()
print("  Grade assessment:")
if abs(corr_tension_torque) > 0.3 and perm_p_value < 0.05:
    print("  → 🟧★ Structural connection confirmed")
elif abs(corr_tension_torque) > 0.1 and perm_p_value < 0.10:
    print("  → 🟧 Weak evidence of connection")
else:
    print("  → ⚪ No significant connection found with this setup")
    print("  → May need: deeper network, learned tension, or different tension definition")
