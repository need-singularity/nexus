#!/usr/bin/env python3
"""
GZ Dropout Rate Prediction Test
================================
Golden Zone predicts optimal inhibition I = 1/e = 0.3679.
In ML, dropout rate = fraction of neurons deactivated = I.
Prediction: dropout ~ 0.37 should be optimal for complex tasks.

Test: Train simple CNN on CIFAR-10 with multiple dropout rates.
Output: accuracy vs dropout table + ASCII graph.

Usage:
    python3 calc/gz_dropout_test.py              # full sweep (GPU recommended)
    python3 calc/gz_dropout_test.py --quick       # fewer epochs for sanity check
    python3 calc/gz_dropout_test.py --seeds 5     # multiple seeds for statistics
"""

import argparse
import time
import sys

# ── Constants ──────────────────────────────────────────────
GZ_CENTER = 0.36787944117  # 1/e
GZ_UPPER = 0.5
GZ_LOWER = 0.2123
DROPOUT_RATES = [0.0, 0.1, 0.2, 0.3, 0.37, 0.4, 0.5, 0.6, 0.7]


def check_torch():
    try:
        import torch
        return torch
    except ImportError:
        print("ERROR: PyTorch not installed. Install with:")
        print("  pip install torch torchvision")
        sys.exit(1)


def build_model(torch, dropout_rate):
    """Simple CNN: 3 conv blocks + 2 FC layers with dropout."""
    import torch.nn as nn

    class SimpleCNN(nn.Module):
        def __init__(self, p=0.5):
            super().__init__()
            # Conv block 1: 3 -> 32
            self.conv1 = nn.Sequential(
                nn.Conv2d(3, 32, 3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(),
                nn.MaxPool2d(2),
            )
            # Conv block 2: 32 -> 64
            self.conv2 = nn.Sequential(
                nn.Conv2d(32, 64, 3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(2),
            )
            # Conv block 3: 64 -> 128
            self.conv3 = nn.Sequential(
                nn.Conv2d(64, 128, 3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(1),
            )
            # FC layers with dropout
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(128, 256),
                nn.ReLU(),
                nn.Dropout(p),
                nn.Linear(256, 128),
                nn.ReLU(),
                nn.Dropout(p),
                nn.Linear(128, 10),
            )

        def forward(self, x):
            x = self.conv1(x)
            x = self.conv2(x)
            x = self.conv3(x)
            x = self.classifier(x)
            return x

    return SimpleCNN(p=dropout_rate)


def get_cifar10(torch, batch_size=128):
    """Load CIFAR-10 with standard augmentation."""
    import torchvision
    import torchvision.transforms as T

    train_transform = T.Compose([
        T.RandomHorizontalFlip(),
        T.RandomCrop(32, padding=4),
        T.ToTensor(),
        T.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    test_transform = T.Compose([
        T.ToTensor(),
        T.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    train_ds = torchvision.datasets.CIFAR10(
        root="./data", train=True, download=True, transform=train_transform
    )
    test_ds = torchvision.datasets.CIFAR10(
        root="./data", train=False, download=True, transform=test_transform
    )

    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=2
    )
    test_loader = torch.utils.data.DataLoader(
        test_ds, batch_size=batch_size, shuffle=False, num_workers=2
    )
    return train_loader, test_loader


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(targets).sum().item()
        total += targets.size(0)
    return total_loss / total, 100.0 * correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    import torch as th
    with th.no_grad():
        for inputs, targets in loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            total_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(targets).sum().item()
            total += targets.size(0)
    return total_loss / total, 100.0 * correct / total


def ascii_bar(value, max_val, width=40):
    """Create ASCII bar for visualization."""
    filled = int(round(value / max_val * width))
    return "#" * filled + "." * (width - filled)


def ascii_graph(rates, accuracies):
    """Print ASCII accuracy vs dropout graph."""
    max_acc = max(accuracies)
    min_acc = min(accuracies)
    best_idx = accuracies.index(max_acc)

    print("\n  Accuracy vs Dropout Rate")
    print("  " + "=" * 60)
    for i, (rate, acc) in enumerate(zip(rates, accuracies)):
        marker = " ***" if i == best_idx else ""
        gz_marker = " <-- 1/e" if rate == 0.37 else ""
        bar = ascii_bar(acc - min_acc + 1, max_acc - min_acc + 1, width=35)
        print(f"  p={rate:.2f} | {bar} | {acc:.2f}%{marker}{gz_marker}")
    print("  " + "=" * 60)
    print(f"  Best: p={rates[best_idx]:.2f} ({max_acc:.2f}%)")
    print(f"  GZ prediction: p=0.37 (1/e={GZ_CENTER:.4f})")
    print(f"  GZ zone: [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]")

    # Check if best is in GZ
    best_rate = rates[best_idx]
    if GZ_LOWER <= best_rate <= GZ_UPPER:
        print(f"  Result: Best dropout {best_rate} IS in Golden Zone [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]")
    else:
        print(f"  Result: Best dropout {best_rate} is OUTSIDE Golden Zone")

    # Distance from 1/e
    dist = abs(rates[best_idx] - GZ_CENTER)
    print(f"  Distance from 1/e: {dist:.4f}")


def run_sweep(epochs=20, seeds=1, quick=False, device_name=None):
    torch = check_torch()
    import torch.nn as nn

    if device_name:
        device = torch.device(device_name)
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"Device: {device}")
    print(f"Epochs: {epochs}, Seeds: {seeds}")
    print(f"Dropout rates: {DROPOUT_RATES}")
    print()

    rates = DROPOUT_RATES
    if quick:
        rates = [0.0, 0.2, 0.37, 0.5, 0.7]
        epochs = 5

    train_loader, test_loader = get_cifar10(torch)
    criterion = nn.CrossEntropyLoss()

    # Results: {rate: [acc_seed1, acc_seed2, ...]}
    results = {r: [] for r in rates}
    train_results = {r: [] for r in rates}

    for seed in range(seeds):
        print(f"\n{'='*60}")
        print(f"  Seed {seed+1}/{seeds}")
        print(f"{'='*60}")

        for rate in rates:
            torch.manual_seed(42 + seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(42 + seed)

            model = build_model(torch, rate).to(device)
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=epochs
            )

            print(f"\n  Dropout={rate:.2f}: ", end="", flush=True)
            t0 = time.time()

            for epoch in range(epochs):
                train_loss, train_acc = train_one_epoch(
                    model, train_loader, optimizer, criterion, device
                )
                scheduler.step()
                if (epoch + 1) % 5 == 0 or epoch == epochs - 1:
                    print(f"E{epoch+1}={train_acc:.1f}% ", end="", flush=True)

            test_loss, test_acc = evaluate(model, test_loader, criterion, device)
            elapsed = time.time() - t0
            print(f"-> Test: {test_acc:.2f}% ({elapsed:.1f}s)")

            results[rate].append(test_acc)
            train_results[rate].append(train_acc)

    # ── Summary ──
    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"\n  {'Dropout':>8}  {'Test Acc':>10}  {'Std':>8}  {'Train Acc':>10}  {'Gap':>8}")
    print(f"  {'-'*8}  {'-'*10}  {'-'*8}  {'-'*10}  {'-'*8}")

    mean_accs = []
    for rate in rates:
        test_mean = sum(results[rate]) / len(results[rate])
        train_mean = sum(train_results[rate]) / len(train_results[rate])
        gap = train_mean - test_mean

        if seeds > 1:
            import math
            test_std = math.sqrt(
                sum((x - test_mean) ** 2 for x in results[rate]) / (seeds - 1)
            )
        else:
            test_std = 0.0

        mean_accs.append(test_mean)
        gz = " <-1/e" if rate == 0.37 else ""
        print(
            f"  {rate:>8.2f}  {test_mean:>9.2f}%  {test_std:>7.2f}%  "
            f"{train_mean:>9.2f}%  {gap:>7.2f}%{gz}"
        )

    ascii_graph(rates, mean_accs)

    # ── Generalization efficiency ──
    print("\n  Generalization Efficiency (Test/Train ratio):")
    for rate in rates:
        test_mean = sum(results[rate]) / len(results[rate])
        train_mean = sum(train_results[rate]) / len(train_results[rate])
        if train_mean > 0:
            eff = test_mean / train_mean
            bar = ascii_bar(eff, 1.0, width=30)
            gz = " <-1/e" if rate == 0.37 else ""
            print(f"  p={rate:.2f} | {bar} | {eff:.4f}{gz}")


def main():
    parser = argparse.ArgumentParser(description="GZ Dropout Prediction Test")
    parser.add_argument("--epochs", type=int, default=20, help="Training epochs")
    parser.add_argument("--seeds", type=int, default=1, help="Number of random seeds")
    parser.add_argument("--quick", action="store_true", help="Quick test (5 epochs, fewer rates)")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda/mps/cpu)")
    args = parser.parse_args()

    print("=" * 70)
    print("  GZ DROPOUT PREDICTION TEST")
    print("  Prediction: Optimal dropout = 1/e = 0.3679")
    print("  Golden Zone: [0.2123, 0.5000]")
    print("=" * 70)

    run_sweep(
        epochs=args.epochs,
        seeds=args.seeds,
        quick=args.quick,
        device_name=args.device,
    )


if __name__ == "__main__":
    main()
