#!/usr/bin/env python3
"""Mitosis Experiment — One engine splits into two, diversity emerges.

Train one engine, split it, let the halves diverge, then combine in a repulsion field.

Phases:
  1. Parent: Train EngineA on MNIST
  2. Mitosis: deepcopy + mutation -> two children
  3. Divergence: Independent training, track similarity decay
  4. Repulsion field from split: Combine diverged children
  5. Reunion: Average weights back
  6. Multiple splits: 2, 4, 8 children + majority vote
  7. Recognition: Can child_a predict child_b's output?
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import copy
import time
import sys

sys.path.insert(0, '/Users/ghost/Dev/logout')
from model_utils import (
    Expert, load_mnist, train_and_evaluate, count_params
)
from model_meta_engine import EngineA, EngineG, RepulsionFieldEngine


def cosine_similarity_params(model_a, model_b):
    """Cosine similarity between all parameters (flattened)."""
    vec_a = torch.cat([p.detach().flatten() for p in model_a.parameters()])
    vec_b = torch.cat([p.detach().flatten() for p in model_b.parameters()])
    return F.cosine_similarity(vec_a.unsqueeze(0), vec_b.unsqueeze(0)).item()


def compute_tension(model_a, model_b, test_loader, flatten=True, max_batches=10):
    """Tension = mean |out_a - out_b|^2 over test data."""
    model_a.eval()
    model_b.eval()
    total_tension = 0.0
    count = 0
    with torch.no_grad():
        for i, (X, y) in enumerate(test_loader):
            if i >= max_batches:
                break
            if flatten:
                X = X.view(X.size(0), -1)
            out_a = model_a(X)
            out_b = model_b(X)
            if isinstance(out_a, tuple):
                out_a = out_a[0]
            if isinstance(out_b, tuple):
                out_b = out_b[0]
            total_tension += ((out_a - out_b) ** 2).sum(dim=-1).mean().item()
            count += 1
    return total_tension / max(count, 1)


def evaluate_accuracy(model, test_loader, flatten=True):
    """Evaluate model accuracy."""
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for X, y in test_loader:
            if flatten:
                X = X.view(X.size(0), -1)
            out = model(X)
            if isinstance(out, tuple):
                out = out[0]
            correct += (out.argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total


def train_one_epoch(model, train_loader, optimizer, flatten=True):
    """Train for one epoch, return avg loss."""
    model.train()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0
    for X, y in train_loader:
        if flatten:
            X = X.view(X.size(0), -1)
        optimizer.zero_grad()
        out = model(X)
        if isinstance(out, tuple):
            logits, aux = out
            loss = criterion(logits, y) + 0.01 * aux
        else:
            loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(train_loader)


def ascii_graph(values, label, width=50, height=10):
    """Draw ASCII graph."""
    if not values:
        return
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1.0
    print(f"\n  {label}")
    print(f"  {'':>6} {'|'}")
    for row in range(height - 1, -1, -1):
        threshold = mn + (row / (height - 1)) * rng
        line = ""
        for v in values:
            if v >= threshold:
                line += "#"
            else:
                line += " "
        val_label = f"{threshold:.4f}" if rng < 10 else f"{threshold:.1f}"
        print(f"  {val_label:>6} |{line}")
    print(f"  {'':>6} +{''.join(['-' for _ in values])}")
    x_labels = "".join([str(i % 10) for i in range(len(values))])
    print(f"  {'':>6}  {x_labels}")


def print_table(headers, rows, title=""):
    """Print markdown-style table."""
    if title:
        print(f"\n  {title}")
    widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0)) + 2
              for i, h in enumerate(headers)]
    header_line = "|".join(f" {h:^{w-2}} " for h, w in zip(headers, widths))
    sep_line = "|".join("-" * w for w in widths)
    print(f"  |{header_line}|")
    print(f"  |{sep_line}|")
    for row in rows:
        row_line = "|".join(f" {str(row[i]):^{w-2}} " for i, w in enumerate(range(len(headers)))
                            for w in [widths[i]])
        # Simpler approach
        cells = []
        for i, w in enumerate(widths):
            cells.append(f" {str(row[i]):<{w-2}} ")
        print(f"  |{'|'.join(cells)}|")


def main():
    torch.manual_seed(42)
    np.random.seed(42)

    print()
    print("=" * 70)
    print("   MITOSIS EXPERIMENT")
    print("   One engine splits into two, diversity emerges")
    print("=" * 70)

    train_loader, test_loader = load_mnist(batch_size=128)
    input_dim, hidden_dim, output_dim = 784, 48, 10

    # ================================================================
    # PHASE 1: Train Parent Engine
    # ================================================================
    print("\n" + "=" * 70)
    print("  PHASE 1: Train Parent (EngineA, 5 epochs)")
    print("=" * 70)

    parent = EngineA(input_dim, hidden_dim, output_dim)
    parent_params = count_params(parent)
    print(f"  Parameters: {parent_params:,}")

    optimizer = torch.optim.Adam(parent.parameters(), lr=0.001)
    parent_accs = []
    for ep in range(5):
        loss = train_one_epoch(parent, train_loader, optimizer)
        acc = evaluate_accuracy(parent, test_loader)
        parent_accs.append(acc)
        print(f"    Epoch {ep+1}/5: Loss={loss:.4f}, Acc={acc*100:.1f}%")

    parent_acc = parent_accs[-1]
    print(f"\n  Parent final accuracy: {parent_acc*100:.2f}%")

    # ================================================================
    # PHASE 2: Mitosis — Split with different mutation scales
    # ================================================================
    print("\n" + "=" * 70)
    print("  PHASE 2: Mitosis — Split + Mutation")
    print("=" * 70)

    mutation_scales = [0.001, 0.01, 0.1]
    mitosis_results = []

    for scale in mutation_scales:
        torch.manual_seed(42)
        child_a = copy.deepcopy(parent)
        child_b = copy.deepcopy(parent)

        # Add mutation to child_b
        with torch.no_grad():
            for p in child_b.parameters():
                p.add_(torch.randn_like(p) * scale)

        cos_sim = cosine_similarity_params(child_a, child_b)
        tension = compute_tension(child_a, child_b, test_loader)
        acc_a = evaluate_accuracy(child_a, test_loader)
        acc_b = evaluate_accuracy(child_b, test_loader)

        mitosis_results.append({
            'scale': scale,
            'cos_sim': cos_sim,
            'tension': tension,
            'acc_a': acc_a,
            'acc_b': acc_b,
        })

        print(f"\n  Mutation scale = {scale}")
        print(f"    Cosine similarity:  {cos_sim:.6f}")
        print(f"    Tension at birth:   {tension:.4f}")
        print(f"    Child A accuracy:   {acc_a*100:.2f}%")
        print(f"    Child B accuracy:   {acc_b*100:.2f}%")
        print(f"    Acc drop (child B): {(parent_acc - acc_b)*100:.2f}%")

    print_table(
        ["Mutation", "Cos Sim", "Tension", "Acc A%", "Acc B%", "B Drop%"],
        [[f"{r['scale']}", f"{r['cos_sim']:.6f}", f"{r['tension']:.4f}",
          f"{r['acc_a']*100:.1f}", f"{r['acc_b']*100:.1f}",
          f"{(parent_acc - r['acc_b'])*100:.1f}"]
         for r in mitosis_results],
        title="Phase 2 Summary: Mitosis"
    )

    # ================================================================
    # PHASE 3: Divergence — Independent training
    # ================================================================
    print("\n" + "=" * 70)
    print("  PHASE 3: Divergence — Independent Training (10 epochs)")
    print("  Using mutation_scale=0.01")
    print("=" * 70)

    # Use moderate mutation
    torch.manual_seed(42)
    child_a = copy.deepcopy(parent)
    child_b = copy.deepcopy(parent)
    with torch.no_grad():
        for p in child_b.parameters():
            p.add_(torch.randn_like(p) * 0.01)

    opt_a = torch.optim.Adam(child_a.parameters(), lr=0.001)
    opt_b = torch.optim.Adam(child_b.parameters(), lr=0.001)

    divergence_log = []
    diverge_epochs = 10

    for ep in range(diverge_epochs):
        # Train with different data order (different generator seeds)
        g_a = torch.Generator().manual_seed(ep * 1000 + 1)
        g_b = torch.Generator().manual_seed(ep * 1000 + 2)

        # We can't easily change DataLoader seed mid-run, so just train normally
        # The shuffle randomness from DataLoader provides sufficient divergence
        train_one_epoch(child_a, train_loader, opt_a)
        train_one_epoch(child_b, train_loader, opt_b)

        cos_sim = cosine_similarity_params(child_a, child_b)
        tension = compute_tension(child_a, child_b, test_loader)
        acc_a = evaluate_accuracy(child_a, test_loader)
        acc_b = evaluate_accuracy(child_b, test_loader)

        divergence_log.append({
            'epoch': ep + 1,
            'cos_sim': cos_sim,
            'tension': tension,
            'acc_a': acc_a,
            'acc_b': acc_b,
        })

        print(f"    Epoch {ep+1:>2}/10: CosSim={cos_sim:.4f}  Tension={tension:.2f}  "
              f"AccA={acc_a*100:.1f}%  AccB={acc_b*100:.1f}%")

    print_table(
        ["Epoch", "Cos Sim", "Tension", "Acc A%", "Acc B%"],
        [[f"{d['epoch']}", f"{d['cos_sim']:.4f}", f"{d['tension']:.2f}",
          f"{d['acc_a']*100:.1f}", f"{d['acc_b']*100:.1f}"]
         for d in divergence_log],
        title="Phase 3 Summary: Divergence Curve"
    )

    # ASCII graphs
    ascii_graph([d['cos_sim'] for d in divergence_log],
                "Cosine Similarity Decay (params)")
    ascii_graph([d['tension'] for d in divergence_log],
                "Tension Growth")
    ascii_graph([d['acc_a'] for d in divergence_log],
                "Child A Accuracy")
    ascii_graph([d['acc_b'] for d in divergence_log],
                "Child B Accuracy")

    # ================================================================
    # PHASE 4: Repulsion Field from Split
    # ================================================================
    print("\n" + "=" * 70)
    print("  PHASE 4: Repulsion Field from Split Children")
    print("=" * 70)

    # Build a simple repulsion field from the split children
    class SplitRepulsionField(nn.Module):
        """Repulsion field built from mitosis children."""
        def __init__(self, child_a, child_b, output_dim):
            super().__init__()
            self.child_a = child_a
            self.child_b = child_b
            # Freeze children
            for p in self.child_a.parameters():
                p.requires_grad = False
            for p in self.child_b.parameters():
                p.requires_grad = False
            # Learnable field transform
            self.field_linear = nn.Linear(output_dim, output_dim)
            self.field_scale = nn.Parameter(torch.tensor(1/3))

        def forward(self, x):
            out_a = self.child_a(x)
            out_b = self.child_b(x)
            if isinstance(out_a, tuple):
                out_a = out_a[0]
            if isinstance(out_b, tuple):
                out_b = out_b[0]
            avg = (out_a + out_b) / 2
            diff = out_a - out_b
            field = self.field_scale * torch.tanh(self.field_linear(diff))
            return avg + field

    split_field = SplitRepulsionField(child_a, child_b, output_dim)
    field_params = sum(p.numel() for p in split_field.parameters() if p.requires_grad)
    print(f"  Trainable field params: {field_params}")

    # Train field_transform only (5 epochs)
    field_opt = torch.optim.Adam(
        [p for p in split_field.parameters() if p.requires_grad], lr=0.001
    )
    field_accs = []
    for ep in range(5):
        loss = train_one_epoch(split_field, train_loader, field_opt)
        acc = evaluate_accuracy(split_field, test_loader)
        field_accs.append(acc)
        print(f"    Field Epoch {ep+1}/5: Loss={loss:.4f}, Acc={acc*100:.1f}%")

    split_field_acc = field_accs[-1]

    # Designed repulsion field (A vs G, same total epochs = 5+10+5=20)
    print("\n  Training Designed RepulsionField (A vs G, 20 epochs)...")
    designed_field = RepulsionFieldEngine(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(
        designed_field, train_loader, test_loader, epochs=20, aux_lambda=0.01, verbose=True
    )
    designed_field_acc = accs[-1]

    # Summary
    child_a_acc = evaluate_accuracy(child_a, test_loader)
    child_b_acc = evaluate_accuracy(child_b, test_loader)

    print_table(
        ["Model", "Accuracy%", "Note"],
        [
            ["Parent (5 ep)", f"{parent_acc*100:.2f}", "Before split"],
            ["Child A (15 ep)", f"{child_a_acc*100:.2f}", "After divergence"],
            ["Child B (15 ep)", f"{child_b_acc*100:.2f}", "After divergence"],
            ["Split Field", f"{split_field_acc*100:.2f}", "Children frozen + field"],
            ["Designed Field", f"{designed_field_acc*100:.2f}", "A vs G, 20 epochs"],
        ],
        title="Phase 4 Summary: Split Field vs Designed Field"
    )

    # ================================================================
    # PHASE 5: Reunion — Average weights back
    # ================================================================
    print("\n" + "=" * 70)
    print("  PHASE 5: Reunion — Average Weights")
    print("=" * 70)

    merged = copy.deepcopy(child_a)
    with torch.no_grad():
        for p_merged, p_a, p_b in zip(merged.parameters(),
                                        child_a.parameters(),
                                        child_b.parameters()):
            p_merged.copy_((p_a + p_b) / 2)

    merged_acc = evaluate_accuracy(merged, test_loader)

    print(f"  Parent accuracy:    {parent_acc*100:.2f}%")
    print(f"  Child A accuracy:   {child_a_acc*100:.2f}%")
    print(f"  Child B accuracy:   {child_b_acc*100:.2f}%")
    print(f"  Merged accuracy:    {merged_acc*100:.2f}%")
    print(f"  Merged vs Parent:   {(merged_acc - parent_acc)*100:+.2f}%")
    print(f"  Merged vs Best:     {(merged_acc - max(child_a_acc, child_b_acc))*100:+.2f}%")

    if merged_acc > parent_acc:
        print("  --> Reunion IMPROVES on parent!")
    elif merged_acc > min(child_a_acc, child_b_acc):
        print("  --> Reunion better than worst child, worse than best")
    else:
        print("  --> Reunion DEGRADES: diverged too far to simply average")

    # ================================================================
    # PHASE 6: Multiple Splits — 2, 4, 8 children
    # ================================================================
    print("\n" + "=" * 70)
    print("  PHASE 6: Multiple Splits (2, 4, 8 children)")
    print("=" * 70)

    split_counts = [2, 4, 8]
    multi_results = []

    for n_splits in split_counts:
        torch.manual_seed(42)
        children = []
        for i in range(n_splits):
            child = copy.deepcopy(parent)
            if i > 0:  # First child is exact copy
                with torch.no_grad():
                    for p in child.parameters():
                        torch.manual_seed(42 + i * 100)
                        p.add_(torch.randn_like(p) * 0.01)
            children.append(child)

        # Diverge each child for 5 epochs
        child_opts = [torch.optim.Adam(c.parameters(), lr=0.001) for c in children]
        for ep in range(5):
            for ci, (child, opt) in enumerate(zip(children, child_opts)):
                train_one_epoch(child, train_loader, opt)

        # Individual accuracies
        child_accs = [evaluate_accuracy(c, test_loader) for c in children]
        best_single = max(child_accs)
        worst_single = min(child_accs)

        # Majority vote
        def majority_vote(models, loader, flatten=True):
            correct = total = 0
            for X, y in loader:
                if flatten:
                    X = X.view(X.size(0), -1)
                votes = torch.zeros(X.size(0), output_dim)
                for m in models:
                    m.eval()
                    with torch.no_grad():
                        out = m(X)
                        if isinstance(out, tuple):
                            out = out[0]
                        preds = out.argmax(1)
                        for j in range(X.size(0)):
                            votes[j, preds[j]] += 1
                correct += (votes.argmax(1) == y).sum().item()
                total += y.size(0)
            return correct / total

        vote_acc = majority_vote(children, test_loader)

        # Also try soft ensemble (average logits)
        def soft_ensemble(models, loader, flatten=True):
            correct = total = 0
            for X, y in loader:
                if flatten:
                    X = X.view(X.size(0), -1)
                avg_logits = torch.zeros(X.size(0), output_dim)
                for m in models:
                    m.eval()
                    with torch.no_grad():
                        out = m(X)
                        if isinstance(out, tuple):
                            out = out[0]
                        avg_logits += out
                avg_logits /= len(models)
                correct += (avg_logits.argmax(1) == y).sum().item()
                total += y.size(0)
            return correct / total

        ensemble_acc = soft_ensemble(children, test_loader)

        multi_results.append({
            'n': n_splits,
            'best': best_single,
            'worst': worst_single,
            'vote': vote_acc,
            'ensemble': ensemble_acc,
            'accs': child_accs,
        })

        print(f"\n  N={n_splits} splits:")
        print(f"    Individual: {' / '.join(f'{a*100:.1f}%' for a in child_accs)}")
        print(f"    Best single:    {best_single*100:.2f}%")
        print(f"    Majority vote:  {vote_acc*100:.2f}%")
        print(f"    Soft ensemble:  {ensemble_acc*100:.2f}%")
        print(f"    Vote vs Best:   {(vote_acc - best_single)*100:+.2f}%")

    print_table(
        ["N Splits", "Best Single%", "Vote%", "Ensemble%", "Vote-Best%"],
        [[f"{r['n']}", f"{r['best']*100:.1f}", f"{r['vote']*100:.1f}",
          f"{r['ensemble']*100:.1f}", f"{(r['vote']-r['best'])*100:+.1f}"]
         for r in multi_results],
        title="Phase 6 Summary: Multiple Splits"
    )

    # ASCII graph: accuracy vs number of splits
    labels = ["Parent"] + [f"N={r['n']}vote" for r in multi_results] + [f"N={r['n']}ens" for r in multi_results]
    vals = [parent_acc] + [r['vote'] for r in multi_results] + [r['ensemble'] for r in multi_results]
    print("\n  Accuracy vs Strategy:")
    for lbl, v in sorted(zip(labels, vals), key=lambda x: -x[1]):
        bar = "#" * int(v * 50)
        print(f"    {lbl:>14} |{bar} {v*100:.1f}%")

    # ================================================================
    # PHASE 7: Recognition After Split
    # ================================================================
    print("\n" + "=" * 70)
    print("  PHASE 7: Recognition — Can Child A Predict Child B's Output?")
    print("=" * 70)

    # Use the diverged children from Phase 3
    # Train a small predictor: given child_a's output, predict child_b's output

    class OutputPredictor(nn.Module):
        def __init__(self, dim):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(dim, dim * 2),
                nn.ReLU(),
                nn.Linear(dim * 2, dim),
            )
        def forward(self, x):
            return self.net(x)

    # Collect output pairs
    child_a.eval()
    child_b.eval()

    # Also create a "stranger" engine (EngineG, completely different)
    stranger = EngineG(input_dim, hidden_dim, output_dim)
    stranger_opt = torch.optim.Adam(stranger.parameters(), lr=0.001)
    print("  Training stranger engine (EngineG, 15 epochs)...")
    for ep in range(15):
        train_one_epoch(stranger, train_loader, stranger_opt)
    stranger_acc = evaluate_accuracy(stranger, test_loader)
    print(f"  Stranger accuracy: {stranger_acc*100:.1f}%")

    # Collect data for predictor training
    def collect_output_pairs(model_src, model_tgt, loader, max_batches=50):
        src_outputs = []
        tgt_outputs = []
        model_src.eval()
        model_tgt.eval()
        with torch.no_grad():
            for i, (X, y) in enumerate(loader):
                if i >= max_batches:
                    break
                X = X.view(X.size(0), -1)
                out_s = model_src(X)
                out_t = model_tgt(X)
                if isinstance(out_s, tuple):
                    out_s = out_s[0]
                if isinstance(out_t, tuple):
                    out_t = out_t[0]
                src_outputs.append(out_s)
                tgt_outputs.append(out_t)
        return torch.cat(src_outputs), torch.cat(tgt_outputs)

    # Former self: child_a -> child_b
    src_ab, tgt_ab = collect_output_pairs(child_a, child_b, train_loader)
    # Stranger: child_a -> stranger
    src_as, tgt_as = collect_output_pairs(child_a, stranger, train_loader)

    def train_predictor(src, tgt, epochs=20):
        predictor = OutputPredictor(output_dim)
        opt = torch.optim.Adam(predictor.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        ds = torch.utils.data.TensorDataset(src, tgt)
        loader = torch.utils.data.DataLoader(ds, batch_size=256, shuffle=True)
        losses = []
        for ep in range(epochs):
            total_loss = 0
            count = 0
            for s, t in loader:
                opt.zero_grad()
                pred = predictor(s)
                loss = criterion(pred, t)
                loss.backward()
                opt.step()
                total_loss += loss.item()
                count += 1
            losses.append(total_loss / count)
        # Final MSE
        predictor.eval()
        with torch.no_grad():
            final_mse = criterion(predictor(src), tgt).item()
        return final_mse, losses

    print("\n  Training predictor: Child A -> Child B (former self)...")
    mse_sibling, losses_sib = train_predictor(src_ab, tgt_ab)
    print(f"    Final MSE: {mse_sibling:.6f}")

    print("  Training predictor: Child A -> Stranger (EngineG)...")
    mse_stranger, losses_str = train_predictor(src_as, tgt_as)
    print(f"    Final MSE: {mse_stranger:.6f}")

    # Baseline: random predictor
    random_mse = ((tgt_ab - tgt_ab.mean(dim=0)) ** 2).mean().item()
    print(f"  Random baseline MSE: {random_mse:.6f}")

    # Recognition ratio
    recognition_ratio = mse_stranger / max(mse_sibling, 1e-10)
    print(f"\n  Recognition ratio (stranger/sibling MSE): {recognition_ratio:.2f}x")
    print(f"  Sibling recognition MSE:  {mse_sibling:.6f}")
    print(f"  Stranger recognition MSE: {mse_stranger:.6f}")

    if recognition_ratio > 1.5:
        print("  --> Child A recognizes Child B as 'former self' (much easier to predict)")
    elif recognition_ratio > 1.1:
        print("  --> Weak recognition: siblings slightly more predictable")
    else:
        print("  --> No recognition: diverged too far, siblings look like strangers")

    # Compare with C8=94.3% cross-dimension recognition
    sibling_r2 = 1 - mse_sibling / random_mse
    stranger_r2 = 1 - mse_stranger / random_mse
    print(f"\n  Sibling R^2:  {sibling_r2:.4f} ({sibling_r2*100:.1f}%)")
    print(f"  Stranger R^2: {stranger_r2:.4f} ({stranger_r2*100:.1f}%)")
    print(f"  Cross-dim recognition (C8 benchmark): 94.3%")

    ascii_graph(losses_sib, "Sibling Prediction Loss (A->B)")
    ascii_graph(losses_str, "Stranger Prediction Loss (A->Stranger)")

    # ================================================================
    # FINAL SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("  FINAL SUMMARY: MITOSIS EXPERIMENT")
    print("=" * 70)

    print(f"""
  Phase 1 - Parent:           {parent_acc*100:.2f}% (5 epochs)
  Phase 2 - Mutation effect:  scale=0.01 -> cos_sim={mitosis_results[1]['cos_sim']:.4f}
  Phase 3 - After divergence: A={child_a_acc*100:.1f}%, B={child_b_acc*100:.1f}%
            Cos similarity:   {divergence_log[-1]['cos_sim']:.4f} (was ~1.0)
            Tension growth:   {divergence_log[0]['tension']:.2f} -> {divergence_log[-1]['tension']:.2f}
  Phase 4 - Split field:      {split_field_acc*100:.2f}%
            Designed field:   {designed_field_acc*100:.2f}%
            Split vs Design:  {(split_field_acc - designed_field_acc)*100:+.2f}%
  Phase 5 - Reunion (avg):    {merged_acc*100:.2f}%
            vs Parent:        {(merged_acc - parent_acc)*100:+.2f}%
  Phase 6 - Multi-split best: N={multi_results[-1]['n']} ensemble={multi_results[-1]['ensemble']*100:.1f}%
  Phase 7 - Recognition:      sibling={sibling_r2*100:.1f}% vs stranger={stranger_r2*100:.1f}%
            Ratio:            {recognition_ratio:.2f}x
""")

    # Key insights
    print("  KEY INSIGHTS:")
    print("  " + "-" * 50)

    if split_field_acc > designed_field_acc:
        print("  [!] Split field BEATS designed field")
        print("      -> Shared origin helps repulsion field")
    else:
        print("  [ ] Designed field still better than split field")
        print("      -> Different architectures create richer tension")

    if merged_acc > parent_acc:
        print("  [!] Reunion improves on parent")
        print("      -> Divergence found complementary features")
    else:
        print("  [ ] Reunion degrades from parent")
        print("      -> Weight averaging loses specialization")

    if recognition_ratio > 1.5:
        print("  [!] Strong sibling recognition")
        print("      -> Shared origin leaves lasting structural imprint")
    else:
        print("  [ ] Weak/no sibling recognition")
        print("      -> Training overwrites initial structure")

    best_ensemble = max(r['ensemble'] for r in multi_results)
    if best_ensemble > max(child_a_acc, child_b_acc):
        print("  [!] Ensemble > any single child")
        print("      -> Mitosis creates genuine diversity")

    print("\n  " + "=" * 50)
    print("  Mitosis experiment complete.")
    print("  " + "=" * 50)


if __name__ == '__main__':
    main()
