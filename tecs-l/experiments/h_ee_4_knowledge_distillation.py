"""
H-EE-4: Phi6Simple Knowledge Distillation
============================================
Hypothesis: A Phi6Simple student can distill from a GELU teacher with minimal loss.

Test plan:
  1. Train a GELU teacher MLP to convergence
  2. Train a Phi6Simple student from scratch (baseline)
  3. Distill: train Phi6Simple student to match GELU teacher soft targets
  4. Compare: student-from-scratch vs distilled-student vs teacher
  5. Measure KL divergence between teacher and student predictions

Distillation: minimize KL(teacher_softmax || student_softmax) with temperature T.
"""

import numpy as np
import time
import sys

np.random.seed(42)

# ── Activations ──

def act_gelu(x):
    return 0.5 * x * (1.0 + np.tanh(0.7978845608028654 * (x + 0.044715 * x**3)))

def act_gelu_grad(x):
    c = 0.7978845608028654
    x3 = x**3
    t = np.tanh(c * (x + 0.044715 * x3))
    dt = 1.0 - t*t
    return 0.5 * (1.0 + t) + 0.5 * x * dt * c * (1.0 + 3 * 0.044715 * x**2)

def act_phi6(x):
    xc = np.clip(x, -2.0, 2.0)
    return xc * xc - xc + 1.0

def act_phi6_grad(x):
    mask = ((x >= -2.0) & (x <= 2.0)).astype(x.dtype)
    xc = np.clip(x, -2.0, 2.0)
    return mask * (2.0 * xc - 1.0)


# ── MLP ──

class MLP:
    def __init__(self, d_in, d_hidden, d_out, act_fwd, act_bwd, rng):
        scale = np.sqrt(2.0 / d_in)
        self.W1 = rng.standard_normal((d_in, d_hidden)).astype(np.float64) * scale
        self.b1 = np.zeros(d_hidden)
        self.W2 = rng.standard_normal((d_hidden, d_out)).astype(np.float64) * np.sqrt(2.0 / d_hidden)
        self.b2 = np.zeros(d_out)
        self.act_fwd = act_fwd
        self.act_bwd = act_bwd

    def forward(self, x):
        self._x = x
        self._h_pre = x @ self.W1 + self.b1
        self._h = self.act_fwd(self._h_pre)
        return self._h @ self.W2 + self.b2

    def backward_ce(self, dout, lr):
        """Standard cross-entropy backward."""
        dh = dout @ self.W2.T
        dh_pre = dh * self.act_bwd(self._h_pre)
        dW2 = self._h.T @ dout
        db2 = dout.sum(0)
        dW1 = self._x.T @ dh_pre
        db1 = dh_pre.sum(0)
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2

    def backward_kd(self, dout_kd, dout_ce, alpha, lr):
        """Knowledge distillation backward: alpha * KD_grad + (1-alpha) * CE_grad."""
        dout = alpha * dout_kd + (1 - alpha) * dout_ce
        self.backward_ce(dout, lr)


def softmax_np(x, T=1.0):
    x_scaled = x / T
    ex = np.exp(x_scaled - x_scaled.max(-1, keepdims=True))
    return ex / ex.sum(-1, keepdims=True)

def cross_entropy_and_grad(logits, targets):
    probs = softmax_np(logits)
    N = logits.shape[0]
    loss = -np.log(probs[np.arange(N), targets] + 1e-9).mean()
    dlogits = probs.copy()
    dlogits[np.arange(N), targets] -= 1.0
    dlogits /= N
    return loss, dlogits

def kl_div_and_grad(student_logits, teacher_logits, T=4.0):
    """KL(teacher || student) with temperature scaling."""
    teacher_probs = softmax_np(teacher_logits, T=T)
    student_probs = softmax_np(student_logits, T=T)
    N = student_logits.shape[0]
    # KL = sum(teacher * log(teacher/student))
    kl = np.sum(teacher_probs * np.log((teacher_probs + 1e-9) / (student_probs + 1e-9))) / N
    # Gradient w.r.t. student logits
    dlogits = (student_probs - teacher_probs) * (T ** 2) / N
    return kl, dlogits

def accuracy(logits, targets):
    preds = np.argmax(logits, axis=-1)
    return np.mean(preds == targets)


def make_corpus(d_in=32, n_classes=32, n_batches=200, batch_size=64):
    rng = np.random.default_rng(0)
    batches = []
    patterns = [
        np.arange(n_classes),
        np.roll(np.arange(n_classes), 3),
        (np.arange(n_classes) * 3) % n_classes,
        (np.arange(n_classes) * 5) % n_classes,
    ]
    for _ in range(n_batches):
        pat = rng.integers(0, len(patterns))
        idx = rng.integers(0, n_classes, batch_size)
        targets = patterns[pat][idx]
        x = np.zeros((batch_size, d_in))
        x[np.arange(batch_size), idx % d_in] = 1.0
        x += rng.standard_normal((batch_size, d_in)) * 0.05
        batches.append((x.astype(np.float64), targets.astype(np.int32)))
    return batches


# ── Training functions ──

def train_teacher(corpus, n_steps=1000, lr=0.01):
    """Train GELU teacher to convergence."""
    rng = np.random.default_rng(42)
    model = MLP(32, 128, 32, act_gelu, act_gelu_grad, rng)
    losses = []

    for step in range(n_steps):
        x, targets = corpus[step % len(corpus)]
        logits = model.forward(x)
        loss, dlogits = cross_entropy_and_grad(logits, targets)
        model.backward_ce(dlogits, lr)
        losses.append(loss)

    return model, losses


def train_student_scratch(corpus, n_steps=1000, lr=0.01):
    """Train Phi6 student from scratch."""
    rng = np.random.default_rng(42)
    model = MLP(32, 128, 32, act_phi6, act_phi6_grad, rng)
    losses = []

    for step in range(n_steps):
        x, targets = corpus[step % len(corpus)]
        logits = model.forward(x)
        loss, dlogits = cross_entropy_and_grad(logits, targets)
        model.backward_ce(dlogits, lr)
        losses.append(loss)

    return model, losses


def train_student_distilled(teacher, corpus, n_steps=1000, lr=0.01, T=4.0, alpha=0.7):
    """Train Phi6 student with knowledge distillation from GELU teacher."""
    rng = np.random.default_rng(42)
    student = MLP(32, 128, 32, act_phi6, act_phi6_grad, rng)
    losses_ce = []
    losses_kd = []

    for step in range(n_steps):
        x, targets = corpus[step % len(corpus)]

        # Get teacher logits (no gradient)
        teacher_logits = teacher.forward(x)

        # Forward student
        student_logits = student.forward(x)

        # CE loss
        ce_loss, dlogits_ce = cross_entropy_and_grad(student_logits, targets)

        # KD loss
        kd_loss, dlogits_kd = kl_div_and_grad(student_logits, teacher_logits, T=T)

        # Combined backward
        student.backward_kd(dlogits_kd, dlogits_ce, alpha, lr)

        losses_ce.append(ce_loss)
        losses_kd.append(kd_loss)

    return student, losses_ce, losses_kd


def evaluate_model(model, corpus, n_eval=50):
    """Evaluate model on corpus subset."""
    total_loss = 0
    total_acc = 0
    for i in range(n_eval):
        x, targets = corpus[i % len(corpus)]
        logits = model.forward(x)
        probs = softmax_np(logits)
        loss = -np.log(probs[np.arange(len(targets)), targets] + 1e-9).mean()
        acc = accuracy(logits, targets)
        total_loss += loss
        total_acc += acc
    return total_loss / n_eval, total_acc / n_eval


def measure_kl_divergence(model_a, model_b, corpus, n_eval=50):
    """Measure mean KL(A || B) on corpus."""
    total_kl = 0
    for i in range(n_eval):
        x, _ = corpus[i % len(corpus)]
        logits_a = model_a.forward(x)
        logits_b = model_b.forward(x)
        probs_a = softmax_np(logits_a)
        probs_b = softmax_np(logits_b)
        kl = np.sum(probs_a * np.log((probs_a + 1e-9) / (probs_b + 1e-9))) / len(x)
        total_kl += kl
    return total_kl / n_eval


# ── Main ──

def main():
    SEP = "=" * 78
    corpus = make_corpus()

    print(SEP)
    print("  H-EE-4: Phi6Simple Knowledge Distillation")
    print("  Hypothesis: Phi6 student can distill from GELU teacher with minimal loss")
    print(SEP)

    # 1. Train teacher
    print("\n  [1/5] Training GELU teacher (1000 steps)...")
    teacher, teacher_losses = train_teacher(corpus, n_steps=1000)
    teacher_eval_loss, teacher_eval_acc = evaluate_model(teacher, corpus)
    print(f"    Teacher final loss: {np.mean(teacher_losses[-50:]):.4f}")
    print(f"    Teacher eval loss:  {teacher_eval_loss:.4f}")
    print(f"    Teacher eval acc:   {teacher_eval_acc*100:.1f}%")

    # 2. Train Phi6 student from scratch
    print("\n  [2/5] Training Phi6 student from scratch (1000 steps)...")
    student_scratch, scratch_losses = train_student_scratch(corpus, n_steps=1000)
    scratch_eval_loss, scratch_eval_acc = evaluate_model(student_scratch, corpus)
    print(f"    Scratch final loss: {np.mean(scratch_losses[-50:]):.4f}")
    print(f"    Scratch eval loss:  {scratch_eval_loss:.4f}")
    print(f"    Scratch eval acc:   {scratch_eval_acc*100:.1f}%")

    # 3. Distill with different temperatures and alpha
    print("\n  [3/5] Knowledge distillation experiments...")
    distill_configs = [
        {"T": 2.0, "alpha": 0.5},
        {"T": 4.0, "alpha": 0.5},
        {"T": 4.0, "alpha": 0.7},
        {"T": 4.0, "alpha": 0.9},
        {"T": 8.0, "alpha": 0.7},
    ]

    print(f"\n  {'T':>4s}  {'alpha':>5s}  {'Final CE':>9s}  {'Eval Loss':>10s}  "
          f"{'Eval Acc':>9s}  {'KL(T||S)':>10s}  {'vs Scratch':>10s}")
    print("  " + "-" * 72)

    best_distilled = None
    best_distilled_loss = float('inf')

    for cfg in distill_configs:
        student_d, ce_losses, kd_losses = train_student_distilled(
            teacher, corpus, n_steps=1000, T=cfg["T"], alpha=cfg["alpha"])
        d_eval_loss, d_eval_acc = evaluate_model(student_d, corpus)
        kl = measure_kl_divergence(teacher, student_d, corpus)

        delta = ((d_eval_loss - scratch_eval_loss) / scratch_eval_loss) * 100
        print(f"  {cfg['T']:4.1f}  {cfg['alpha']:5.1f}  {np.mean(ce_losses[-50:]):9.4f}  "
              f"{d_eval_loss:10.4f}  {d_eval_acc*100:8.1f}%  {kl:10.6f}  {delta:+9.1f}%")

        if d_eval_loss < best_distilled_loss:
            best_distilled_loss = d_eval_loss
            best_distilled = student_d
            best_cfg = cfg

    # 4. Summary comparison
    print(f"\n  [4/5] SUMMARY COMPARISON")
    print("  " + "-" * 60)

    best_d_loss, best_d_acc = evaluate_model(best_distilled, corpus)
    kl_teacher_scratch = measure_kl_divergence(teacher, student_scratch, corpus)
    kl_teacher_distilled = measure_kl_divergence(teacher, best_distilled, corpus)

    print(f"\n  {'Model':25s}  {'Eval Loss':>10s}  {'Eval Acc':>9s}  {'KL from Teacher':>15s}")
    print("  " + "-" * 65)
    print(f"  {'GELU Teacher':25s}  {teacher_eval_loss:10.4f}  {teacher_eval_acc*100:8.1f}%  {'0 (reference)':>15s}")
    print(f"  {'Phi6 from scratch':25s}  {scratch_eval_loss:10.4f}  {scratch_eval_acc*100:8.1f}%  {kl_teacher_scratch:15.6f}")
    print(f"  {'Phi6 distilled (best)':25s}  {best_d_loss:10.4f}  {best_d_acc*100:8.1f}%  {kl_teacher_distilled:15.6f}")
    print(f"    Best distillation config: T={best_cfg['T']}, alpha={best_cfg['alpha']}")

    # 5. Gap analysis
    print(f"\n  [5/5] GAP ANALYSIS")
    print("  " + "-" * 60)

    teacher_scratch_gap = scratch_eval_loss - teacher_eval_loss
    teacher_distill_gap = best_d_loss - teacher_eval_loss
    distill_improvement = (kl_teacher_scratch - kl_teacher_distilled) / kl_teacher_scratch * 100 if kl_teacher_scratch > 0 else 0

    print(f"    Teacher-to-Scratch gap:    {teacher_scratch_gap:+.4f} loss")
    print(f"    Teacher-to-Distilled gap:  {teacher_distill_gap:+.4f} loss")
    print(f"    Distillation KL reduction: {distill_improvement:.1f}%")
    print(f"    Gap closed by distillation: {((teacher_scratch_gap - teacher_distill_gap) / teacher_scratch_gap * 100) if teacher_scratch_gap != 0 else 0:.1f}%")

    # ASCII comparison bar
    print(f"\n    Loss comparison (lower = better):")
    ref = max(teacher_eval_loss, scratch_eval_loss, best_d_loss)
    for name, loss in [("GELU Teacher", teacher_eval_loss),
                       ("Phi6 Scratch", scratch_eval_loss),
                       ("Phi6 Distill", best_d_loss)]:
        bar_len = int(loss / ref * 40)
        print(f"    {name:16s} |{'#' * bar_len}{'.' * (40 - bar_len)}| {loss:.4f}")

    # Verdict
    print(f"\n  VERDICT:")
    gap_pct = abs(teacher_distill_gap / teacher_eval_loss * 100) if teacher_eval_loss > 0 else 999

    if best_d_loss <= teacher_eval_loss * 1.05:
        print(f"    SUPPORTED: Distilled Phi6 student matches teacher within 5% ({gap_pct:.1f}% gap)")
        print(f"    Knowledge distillation successfully transfers GELU knowledge to Phi6.")
        grade = "SUPPORTED"
    elif best_d_loss <= teacher_eval_loss * 1.15:
        print(f"    PARTIAL: Distilled Phi6 student within 15% of teacher ({gap_pct:.1f}% gap)")
        print(f"    Distillation helps but gap is significant.")
        grade = "PARTIAL"
    else:
        print(f"    REFUTED: Distilled Phi6 student is {gap_pct:.1f}% worse than teacher")
        grade = "REFUTED"

    if best_d_loss < scratch_eval_loss:
        print(f"    Additionally: Distillation improved over scratch training by {((scratch_eval_loss - best_d_loss) / scratch_eval_loss * 100):.1f}%")
    else:
        print(f"    Note: Distillation did NOT improve over scratch training")

    print(f"\n    Grade: {grade}")
    print(SEP)


if __name__ == "__main__":
    main()
