#!/usr/bin/env python3
"""
experiment_rl_repulsion.py — Repulsion Field for RL Decision Making

CartPole environment (manual, no gym dependency).
State = [position, velocity, angle, angular_velocity] (4-dim).
Actions = {left=0, right=1}.

Two policies compared:
  1. Dense policy: standard 2-layer MLP
  2. RepulsionField policy: two opposing poles generate action via tension

Key question: Does tension correlate with decision difficulty?

Algorithm: REINFORCE (policy gradient), 200 episodes each.
"""

import math
import random
import numpy as np

# ─── Reproducibility ───
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ═══════════════════════════════════════════════════════
# 1. Manual CartPole Environment
# ═══════════════════════════════════════════════════════

class CartPole:
    """Manual CartPole physics. No gym dependency."""

    GRAVITY = 9.8
    CART_MASS = 1.0
    POLE_MASS = 0.1
    TOTAL_MASS = CART_MASS + POLE_MASS
    POLE_HALF_LENGTH = 0.5
    FORCE_MAG = 10.0
    DT = 0.02

    X_THRESHOLD = 2.4
    THETA_THRESHOLD = 12 * math.pi / 180  # 12 degrees
    MAX_STEPS = 200

    def __init__(self):
        self.state = None
        self.steps = 0

    def reset(self):
        # Small random initial state
        self.state = np.array([
            random.uniform(-0.05, 0.05),
            random.uniform(-0.05, 0.05),
            random.uniform(-0.05, 0.05),
            random.uniform(-0.05, 0.05),
        ], dtype=np.float64)
        self.steps = 0
        return self.state.copy()

    def step(self, action):
        x, v, theta, omega = self.state
        force = self.FORCE_MAG if action == 1 else -self.FORCE_MAG

        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # Physics equations (simplified Euler)
        temp = (force + self.POLE_MASS * self.POLE_HALF_LENGTH * omega**2 * sin_t) / self.TOTAL_MASS
        alpha = (self.GRAVITY * sin_t - cos_t * temp) / (
            self.POLE_HALF_LENGTH * (4.0/3.0 - self.POLE_MASS * cos_t**2 / self.TOTAL_MASS)
        )
        a = temp - self.POLE_MASS * self.POLE_HALF_LENGTH * alpha * cos_t / self.TOTAL_MASS

        # Euler integration
        x += self.DT * v
        v += self.DT * a
        theta += self.DT * omega
        omega += self.DT * alpha

        self.state = np.array([x, v, theta, omega], dtype=np.float64)
        self.steps += 1

        done = (
            x < -self.X_THRESHOLD or x > self.X_THRESHOLD or
            theta < -self.THETA_THRESHOLD or theta > self.THETA_THRESHOLD or
            self.steps >= self.MAX_STEPS
        )
        reward = 1.0 if not done or self.steps >= self.MAX_STEPS else 0.0
        # Give reward=1 at max steps too
        if self.steps >= self.MAX_STEPS:
            reward = 1.0
            done = True

        return self.state.copy(), reward, done


# ═══════════════════════════════════════════════════════
# 2. Minimal Autograd (numpy-based, no torch)
# ═══════════════════════════════════════════════════════

def sigmoid(x):
    x = np.clip(x, -500, 500)
    return 1.0 / (1.0 + np.exp(-x))

def softmax(x):
    x = x - np.max(x)
    e = np.exp(x)
    return e / (e.sum() + 1e-12)

def relu(x):
    return np.maximum(0, x)

def tanh(x):
    return np.tanh(x)


class Linear:
    """Simple linear layer with numpy."""
    def __init__(self, in_dim, out_dim):
        # Xavier init
        scale = np.sqrt(2.0 / (in_dim + out_dim))
        self.W = np.random.randn(in_dim, out_dim).astype(np.float64) * scale
        self.b = np.zeros(out_dim, dtype=np.float64)
        # Gradients
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        # Cache for backward
        self.input = None

    def forward(self, x):
        self.input = x.copy()
        return x @ self.W + self.b

    def zero_grad(self):
        self.dW[:] = 0
        self.db[:] = 0

    def params(self):
        return [(self.W, self.dW), (self.b, self.db)]


# ═══════════════════════════════════════════════════════
# 3. Dense Policy (baseline)
# ═══════════════════════════════════════════════════════

class DensePolicy:
    """Standard 2-layer MLP policy."""
    def __init__(self, state_dim=4, hidden_dim=32, action_dim=2):
        self.fc1 = Linear(state_dim, hidden_dim)
        self.fc2 = Linear(hidden_dim, action_dim)
        self.name = "DensePolicy"

    def forward(self, state):
        h = relu(self.fc1.forward(state))
        logits = self.fc2.forward(h)
        probs = softmax(logits)
        return probs, {}

    def all_layers(self):
        return [self.fc1, self.fc2]


# ═══════════════════════════════════════════════════════
# 4. Repulsion Field Policy
# ═══════════════════════════════════════════════════════

class RepulsionFieldPolicy:
    """
    Two opposing poles generate action probabilities through tension.

    Pole+ (excitatory): state -> hidden -> action logits
    Pole- (inhibitory): state -> hidden -> action logits

    Repulsion = pole+ output - pole- output
    Tension = ||repulsion||^2
    Equilibrium = (pole+ + pole-) / 2
    Output = equilibrium + tension_scale * sqrt(tension) * field_direction

    High tension = poles disagree = difficult decision
    Low tension = poles agree = easy/automatic decision
    """
    def __init__(self, state_dim=4, hidden_dim=32, action_dim=2):
        # Pole+ (excitatory / generative)
        self.pole_plus_1 = Linear(state_dim, hidden_dim)
        self.pole_plus_2 = Linear(hidden_dim, action_dim)

        # Pole- (inhibitory / corrective)
        self.pole_minus_1 = Linear(state_dim, hidden_dim)
        self.pole_minus_2 = Linear(hidden_dim, action_dim)

        # Field transform: repulsion -> direction
        self.field_transform = Linear(action_dim, action_dim)

        # Tension scale (fixed at 1/3 = meta fixed point)
        self.tension_scale = 1.0 / 3.0

        self.name = "RepulsionFieldPolicy"

    def forward(self, state):
        # Pole+
        h_plus = tanh(self.pole_plus_1.forward(state))
        out_plus = self.pole_plus_2.forward(h_plus)

        # Pole-
        h_minus = tanh(self.pole_minus_1.forward(state))
        out_minus = self.pole_minus_2.forward(h_minus)

        # Repulsion
        repulsion = out_plus - out_minus
        tension = np.sum(repulsion ** 2)

        # Equilibrium
        equilibrium = (out_plus + out_minus) / 2.0

        # Field direction
        field_dir = tanh(self.field_transform.forward(repulsion))

        # Output = equilibrium + tension_scale * sqrt(tension) * direction
        output = equilibrium + self.tension_scale * math.sqrt(tension + 1e-8) * field_dir

        probs = softmax(output)

        info = {
            'tension': tension,
            'pole_plus': out_plus.copy(),
            'pole_minus': out_minus.copy(),
        }
        return probs, info

    def all_layers(self):
        return [
            self.pole_plus_1, self.pole_plus_2,
            self.pole_minus_1, self.pole_minus_2,
            self.field_transform,
        ]


# ═══════════════════════════════════════════════════════
# 5. REINFORCE Training (numerical gradient for simplicity)
# ═══════════════════════════════════════════════════════

def collect_episode(env, policy):
    """Run one episode, collect trajectory."""
    state = env.reset()
    states, actions, rewards, infos = [], [], [], []
    done = False

    while not done:
        probs, info = policy.forward(state)
        # Sample action
        action = 0 if random.random() < probs[0] else 1

        states.append(state.copy())
        actions.append(action)
        infos.append(info)

        state, reward, done = env.step(action)
        rewards.append(reward)

    return states, actions, rewards, infos


def compute_returns(rewards, gamma=0.99):
    """Compute discounted returns."""
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    returns = np.array(returns)
    if len(returns) > 1:
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
    return returns


def reinforce_update(policy, states, actions, returns, lr=0.005, eps=1e-4):
    """
    REINFORCE with numerical gradient estimation.
    For each parameter, estimate grad via finite difference on log_prob * return.
    """
    layers = policy.all_layers()

    for layer in layers:
        for param, grad in layer.params():
            flat = param.flatten()
            grad_flat = np.zeros_like(flat)

            # Sample a subset of params to perturb (for speed)
            n_params = len(flat)
            # Perturb up to 30 params per layer for speed
            indices = np.random.choice(n_params, min(30, n_params), replace=False)

            for idx in indices:
                original = flat[idx]

                # f(theta + eps)
                flat[idx] = original + eps
                param[:] = flat.reshape(param.shape)
                total_plus = 0.0
                for s, a, G in zip(states, actions, returns):
                    probs, _ = policy.forward(s)
                    log_prob = math.log(probs[a] + 1e-12)
                    total_plus += log_prob * G

                # f(theta - eps)
                flat[idx] = original - eps
                param[:] = flat.reshape(param.shape)
                total_minus = 0.0
                for s, a, G in zip(states, actions, returns):
                    probs, _ = policy.forward(s)
                    log_prob = math.log(probs[a] + 1e-12)
                    total_minus += log_prob * G

                grad_flat[idx] = (total_plus - total_minus) / (2 * eps)

                # Restore
                flat[idx] = original
                param[:] = flat.reshape(param.shape)

            # Update with gradient ascent (maximize expected return)
            param += lr * grad_flat.reshape(param.shape)


def reinforce_update_analytic(policy, states, actions, returns, lr=0.01):
    """
    REINFORCE with score-function trick (analytic gradient for softmax policy).

    For softmax policy: d/d_logit[a'] log pi(a|s) = 1(a=a') - pi(a'|s)
    Chain rule through the network using simple backprop.
    """
    layers = policy.all_layers()

    # Zero grads
    for layer in layers:
        layer.zero_grad()

    # Accumulate gradients over trajectory
    for s, a, G in zip(states, actions, returns):
        probs, _ = policy.forward(s)

        # d log pi(a|s) / d logits = (one_hot(a) - probs)
        d_logits = -probs.copy()
        d_logits[a] += 1.0
        d_logits *= G  # Scale by return

        # Backprop through the network
        _backprop(policy, d_logits, s)

    # Apply gradients (gradient ascent)
    for layer in layers:
        for param, grad in layer.params():
            param += lr * grad / max(len(states), 1)


def _backprop(policy, d_logits, state):
    """Manual backprop for both policy types."""
    if isinstance(policy, DensePolicy):
        # Backprop through fc2
        h = relu(policy.fc1.forward(state))
        policy.fc2.dW += np.outer(h, d_logits)
        policy.fc2.db += d_logits

        # Backprop through relu + fc1
        d_h = d_logits @ policy.fc2.W.T
        d_h = d_h * (h > 0).astype(np.float64)  # relu grad
        policy.fc1.dW += np.outer(state, d_h)
        policy.fc1.db += d_h

    elif isinstance(policy, RepulsionFieldPolicy):
        # Forward pass to get intermediates
        h_plus = tanh(policy.pole_plus_1.forward(state))
        out_plus = policy.pole_plus_2.forward(h_plus)

        h_minus = tanh(policy.pole_minus_1.forward(state))
        out_minus = policy.pole_minus_2.forward(h_minus)

        repulsion = out_plus - out_minus
        tension = np.sum(repulsion ** 2)
        equilibrium = (out_plus + out_minus) / 2.0

        raw_field = policy.field_transform.forward(repulsion)
        field_dir = tanh(raw_field)

        sqrt_tension = math.sqrt(tension + 1e-8)
        scale = policy.tension_scale

        # d_output = d_logits (from softmax grad)
        d_out = d_logits

        # output = equilibrium + scale * sqrt_tension * field_dir
        # d_equilibrium
        d_eq = d_out.copy()

        # d_field_dir
        d_field_dir = d_out * scale * sqrt_tension

        # d_raw_field (tanh grad)
        d_raw_field = d_field_dir * (1 - field_dir ** 2)

        # field_transform backprop
        policy.field_transform.dW += np.outer(repulsion, d_raw_field)
        policy.field_transform.db += d_raw_field

        # d_repulsion from field_transform
        d_repulsion_from_field = d_raw_field @ policy.field_transform.W.T

        # d_repulsion from sqrt(tension) * field_dir term via tension
        # d_sqrt_tension = scale * sum(d_out * field_dir)
        if tension > 1e-8:
            d_sqrt_tension = scale * np.sum(d_out * field_dir)
            d_tension = d_sqrt_tension / (2 * sqrt_tension)
            d_repulsion_from_tension = 2 * repulsion * d_tension
        else:
            d_repulsion_from_tension = np.zeros_like(repulsion)

        d_repulsion = d_repulsion_from_field + d_repulsion_from_tension

        # repulsion = out_plus - out_minus
        # equilibrium = (out_plus + out_minus) / 2
        d_out_plus = d_eq / 2 + d_repulsion
        d_out_minus = d_eq / 2 - d_repulsion

        # Backprop pole+
        policy.pole_plus_2.dW += np.outer(h_plus, d_out_plus)
        policy.pole_plus_2.db += d_out_plus
        d_h_plus = d_out_plus @ policy.pole_plus_2.W.T
        d_h_plus = d_h_plus * (1 - h_plus ** 2)  # tanh grad
        policy.pole_plus_1.dW += np.outer(state, d_h_plus)
        policy.pole_plus_1.db += d_h_plus

        # Backprop pole-
        policy.pole_minus_2.dW += np.outer(h_minus, d_out_minus)
        policy.pole_minus_2.db += d_out_minus
        d_h_minus = d_out_minus @ policy.pole_minus_2.W.T
        d_h_minus = d_h_minus * (1 - h_minus ** 2)  # tanh grad
        policy.pole_minus_1.dW += np.outer(state, d_h_minus)
        policy.pole_minus_1.db += d_h_minus


# ═══════════════════════════════════════════════════════
# 6. Training Loop
# ═══════════════════════════════════════════════════════

def train(policy, env, n_episodes=200, lr=0.01, verbose=True):
    """Train a policy using REINFORCE."""
    episode_rewards = []
    episode_tensions = []  # Only for RepulsionField

    for ep in range(n_episodes):
        states, actions, rewards, infos = collect_episode(env, policy)
        returns = compute_returns(rewards)

        total_reward = sum(rewards)
        episode_rewards.append(total_reward)

        # Track tension
        if infos and 'tension' in infos[0]:
            tensions = [info['tension'] for info in infos]
            mean_tension = np.mean(tensions)
            episode_tensions.append(mean_tension)

        # Update
        reinforce_update_analytic(policy, states, actions, returns, lr=lr)

        if verbose and (ep + 1) % 20 == 0:
            recent = np.mean(episode_rewards[-20:])
            tension_str = ""
            if episode_tensions:
                tension_str = f"  tension={np.mean(episode_tensions[-20:]):.4f}"
            print(f"  [{policy.name}] Episode {ep+1:3d}  avg_reward={recent:6.1f}{tension_str}")

    return episode_rewards, episode_tensions


# ═══════════════════════════════════════════════════════
# 7. Analysis: Tension vs Decision Difficulty
# ═══════════════════════════════════════════════════════

def analyze_tension_difficulty(policy, env, n_episodes=50):
    """
    Measure tension at each step and correlate with decision difficulty.

    Decision difficulty proxy: entropy of action probabilities.
    High entropy = uncertain = difficult decision.
    """
    tensions = []
    entropies = []
    angles = []

    for _ in range(n_episodes):
        state = env.reset()
        done = False
        while not done:
            probs, info = policy.forward(state)

            # Entropy as difficulty proxy
            ent = -sum(p * math.log(p + 1e-12) for p in probs)

            if 'tension' in info:
                tensions.append(info['tension'])
                entropies.append(ent)
                angles.append(abs(state[2]))  # |theta| = physical difficulty

            action = 0 if random.random() < probs[0] else 1
            state, _, done = env.step(action)

    return np.array(tensions), np.array(entropies), np.array(angles)


def pearson_correlation(x, y):
    """Compute Pearson correlation coefficient."""
    if len(x) < 2:
        return 0.0
    x_m = x - x.mean()
    y_m = y - y.mean()
    num = np.sum(x_m * y_m)
    den = math.sqrt(np.sum(x_m**2) * np.sum(y_m**2) + 1e-12)
    return num / den


# ═══════════════════════════════════════════════════════
# 8. Main Experiment
# ═══════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print(" Repulsion Field for RL Decision Making")
    print(" CartPole (manual physics, no gym)")
    print(" REINFORCE, 200 episodes")
    print("=" * 65)

    env = CartPole()
    N_EPISODES = 200
    LR = 0.01

    # ─── Train Dense Policy ───
    print("\n[1] Training Dense Policy (baseline)...")
    np.random.seed(SEED)
    random.seed(SEED)
    dense = DensePolicy(state_dim=4, hidden_dim=32, action_dim=2)
    dense_rewards, _ = train(dense, env, n_episodes=N_EPISODES, lr=LR)

    # ─── Train Repulsion Field Policy ───
    print(f"\n[2] Training Repulsion Field Policy...")
    np.random.seed(SEED)
    random.seed(SEED)
    repulsion = RepulsionFieldPolicy(state_dim=4, hidden_dim=32, action_dim=2)
    repulsion_rewards, repulsion_tensions = train(repulsion, env, n_episodes=N_EPISODES, lr=LR)

    # ─── Compare Performance ───
    print("\n" + "=" * 65)
    print(" PERFORMANCE COMPARISON")
    print("=" * 65)

    # Last 50 episodes average
    last_n = 50
    dense_final = np.mean(dense_rewards[-last_n:])
    repulsion_final = np.mean(repulsion_rewards[-last_n:])

    dense_max = np.max(dense_rewards)
    repulsion_max = np.max(repulsion_rewards)

    print(f"\n  {'Metric':<30s} {'Dense':>10s} {'Repulsion':>12s}")
    print(f"  {'-'*54}")
    print(f"  {'Last 50 ep avg reward':<30s} {dense_final:10.1f} {repulsion_final:12.1f}")
    print(f"  {'Max episode reward':<30s} {dense_max:10.1f} {repulsion_max:12.1f}")
    print(f"  {'First 50 ep avg':<30s} {np.mean(dense_rewards[:50]):10.1f} {np.mean(repulsion_rewards[:50]):12.1f}")
    print(f"  {'Improvement (last 50)':<30s} {'':>10s} {repulsion_final - dense_final:+12.1f}")

    # ─── Tension Analysis ───
    print("\n" + "=" * 65)
    print(" TENSION vs DECISION DIFFICULTY ANALYSIS")
    print("=" * 65)

    print("\n  Collecting tension data from trained RepulsionField policy...")
    tensions, entropies, angles = analyze_tension_difficulty(repulsion, env, n_episodes=50)

    if len(tensions) > 0:
        # Correlation: tension vs entropy (decision difficulty)
        corr_tension_entropy = pearson_correlation(tensions, entropies)
        # Correlation: tension vs |angle| (physical difficulty)
        corr_tension_angle = pearson_correlation(tensions, angles)
        # Correlation: entropy vs |angle| (sanity check)
        corr_entropy_angle = pearson_correlation(entropies, angles)

        print(f"\n  Samples collected: {len(tensions)}")
        print(f"\n  Correlation Analysis:")
        print(f"  {'Pair':<45s} {'Pearson r':>10s}")
        print(f"  {'-'*56}")
        print(f"  {'Tension vs Entropy (decision difficulty)':<45s} {corr_tension_entropy:+10.4f}")
        print(f"  {'Tension vs |Angle| (physical difficulty)':<45s} {corr_tension_angle:+10.4f}")
        print(f"  {'Entropy vs |Angle| (sanity check)':<45s} {corr_entropy_angle:+10.4f}")

        # Tension statistics
        print(f"\n  Tension Statistics:")
        print(f"    Mean:   {np.mean(tensions):.4f}")
        print(f"    Std:    {np.std(tensions):.4f}")
        print(f"    Min:    {np.min(tensions):.4f}")
        print(f"    Max:    {np.max(tensions):.4f}")
        print(f"    Median: {np.median(tensions):.4f}")

        # Bin analysis: high vs low tension decisions
        median_t = np.median(tensions)
        high_mask = tensions > median_t
        low_mask = ~high_mask

        print(f"\n  Decision Quality by Tension Level:")
        print(f"    Low tension  (< median): entropy={np.mean(entropies[low_mask]):.4f}, "
              f"|angle|={np.mean(angles[low_mask]):.4f}")
        print(f"    High tension (> median): entropy={np.mean(entropies[high_mask]):.4f}, "
              f"|angle|={np.mean(angles[high_mask]):.4f}")

        # Quartile analysis
        q1, q2, q3 = np.percentile(tensions, [25, 50, 75])
        bins = [
            ("Q1 (lowest tension)", tensions <= q1),
            ("Q2", (tensions > q1) & (tensions <= q2)),
            ("Q3", (tensions > q2) & (tensions <= q3)),
            ("Q4 (highest tension)", tensions > q3),
        ]

        print(f"\n  Quartile Analysis (Tension -> Entropy):")
        print(f"    {'Quartile':<25s} {'Mean Tension':>14s} {'Mean Entropy':>14s} {'Mean |Angle|':>14s}")
        print(f"    {'-'*68}")
        for name, mask in bins:
            if mask.sum() > 0:
                print(f"    {name:<25s} {np.mean(tensions[mask]):14.4f} "
                      f"{np.mean(entropies[mask]):14.4f} {np.mean(angles[mask]):14.4f}")

    # ─── Tension Evolution During Training ───
    if repulsion_tensions:
        print(f"\n  Tension Evolution During Training:")
        window = 20
        for i in range(0, len(repulsion_tensions), window):
            chunk = repulsion_tensions[i:i+window]
            ep_range = f"Ep {i+1:3d}-{min(i+window, len(repulsion_tensions)):3d}"
            print(f"    {ep_range}: tension={np.mean(chunk):.4f} +/- {np.std(chunk):.4f}")

    # ─── Interpretation ───
    print("\n" + "=" * 65)
    print(" INTERPRETATION")
    print("=" * 65)

    if len(tensions) > 0:
        if abs(corr_tension_entropy) > 0.3:
            direction = "positively" if corr_tension_entropy > 0 else "negatively"
            print(f"\n  [FINDING] Tension {direction} correlates with decision entropy")
            print(f"            (r={corr_tension_entropy:+.4f})")
            if corr_tension_entropy > 0:
                print(f"            -> High tension = uncertain decision = difficult state")
                print(f"            -> Tension IS a marker of decision difficulty")
            else:
                print(f"            -> High tension = confident decision = easy state")
                print(f"            -> Tension is a marker of decision CONFIDENCE")
        else:
            print(f"\n  [FINDING] Tension weakly correlated with decision entropy")
            print(f"            (r={corr_tension_entropy:+.4f})")
            print(f"            -> Tension encodes something OTHER than difficulty")

        if abs(corr_tension_angle) > 0.3:
            direction = "positively" if corr_tension_angle > 0 else "negatively"
            print(f"\n  [FINDING] Tension {direction} correlates with physical danger (|angle|)")
            print(f"            (r={corr_tension_angle:+.4f})")
            if corr_tension_angle > 0:
                print(f"            -> Poles disagree more when pole angle is large")
                print(f"            -> Repulsion field senses physical urgency")

        # Performance comparison interpretation
        if repulsion_final > dense_final + 5:
            print(f"\n  [RESULT] RepulsionField outperforms Dense by {repulsion_final-dense_final:.1f} reward")
        elif dense_final > repulsion_final + 5:
            print(f"\n  [RESULT] Dense outperforms RepulsionField by {dense_final-repulsion_final:.1f} reward")
        else:
            print(f"\n  [RESULT] Performance roughly comparable "
                  f"(Dense={dense_final:.1f}, Repulsion={repulsion_final:.1f})")

    print(f"\n{'=' * 65}")
    print(f" Experiment complete.")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
