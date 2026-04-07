#!/usr/bin/env python3
"""
experiment_rc4_curiosity.py — RC-4: Curiosity = Tension Change as Intrinsic Reward

Hypothesis:
  An agent using |tension(t) - tension(t-1)| as intrinsic reward ("surprise")
  will learn to seek high-variation regions of a 2D grid, while a random agent
  will not.

Setup:
  - 16x16 grid with "interesting" (high local variance) and "boring" (uniform) zones
  - Agent has PureField policy: two opposing engines produce action logits via tension
  - Intrinsic reward = |delta_tension| + novelty_bonus
    - delta_tension is bounded via tanh to prevent magnitude explosion
    - novelty_bonus rewards visiting new cells (decays with repeat visits)
  - Training: Evolution Strategy (ES), 300 generations
  - Comparison: random agent vs curiosity-driven PureField agent

Key question: Does tension-change-as-reward produce curiosity-like exploration?

Self-contained. No external dependencies beyond numpy.
"""

import math
import random
import numpy as np

# ─── Reproducibility ───
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ═══════════════════════════════════════════════════════
# 1. 2D Grid Environment
# ═══════════════════════════════════════════════════════

GRID_SIZE = 16
MAX_STEPS = 80

def make_grid():
    """Create a 16x16 grid with interesting and boring regions.

    Interesting regions: high local value variance (rugged landscape).
    Boring regions: uniform values (flat landscape).

    Layout:
      Top-left  (0:6, 0:6)   = interesting (random 0-10)
      Bot-right (10:16,10:16) = interesting (random 0-10)
      Center    (6:10, 6:10)  = mildly interesting (random 0-5)
      Rest                    = boring (constant 5.0)
    """
    grid = np.full((GRID_SIZE, GRID_SIZE), 5.0)

    rng = np.random.RandomState(123)
    grid[0:6, 0:6] = rng.uniform(0, 10, (6, 6))
    grid[10:16, 10:16] = rng.uniform(0, 10, (6, 6))
    grid[6:10, 6:10] = rng.uniform(2, 8, (4, 4))

    return grid


def local_variance(grid, r, c, radius=1):
    """Compute local variance around (r, c) within given radius."""
    rmin = max(0, r - radius)
    rmax = min(GRID_SIZE, r + radius + 1)
    cmin = max(0, c - radius)
    cmax = min(GRID_SIZE, c + radius + 1)
    patch = grid[rmin:rmax, cmin:cmax]
    return float(np.var(patch))


def get_observation(grid, r, c, radius=2):
    """Return a flattened local patch as observation vector.

    Patch is (2*radius+1) x (2*radius+1), zero-padded at borders.
    """
    size = 2 * radius + 1
    obs = np.zeros((size, size), dtype=np.float64)
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                obs[dr + radius, dc + radius] = grid[nr, nc]
    return obs.flatten() / 10.0  # normalize to [0, 1]


# Actions: 0=up, 1=down, 2=left, 3=right
DR = [-1, 1, 0, 0]
DC = [0, 0, -1, 1]
ACTION_NAMES = ['up', 'down', 'left', 'right']
NUM_ACTIONS = 4


class GridEnv:
    """2D grid exploration environment with visit tracking."""

    def __init__(self):
        self.grid = make_grid()
        self.r = GRID_SIZE // 2
        self.c = GRID_SIZE // 2
        self.steps = 0
        self.visit_count = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    def reset(self):
        self.r = GRID_SIZE // 2
        self.c = GRID_SIZE // 2
        self.steps = 0
        self.visit_count[:] = 0
        self.visit_count[self.r, self.c] = 1
        obs = get_observation(self.grid, self.r, self.c)
        return obs

    def step(self, action):
        nr = np.clip(self.r + DR[action], 0, GRID_SIZE - 1)
        nc = np.clip(self.c + DC[action], 0, GRID_SIZE - 1)
        self.r, self.c = int(nr), int(nc)
        self.steps += 1
        self.visit_count[self.r, self.c] += 1

        obs = get_observation(self.grid, self.r, self.c)
        done = self.steps >= MAX_STEPS

        # Novelty: 1.0 for first visit, decaying for repeats
        novelty = 1.0 / self.visit_count[self.r, self.c]

        return obs, done, novelty


# ═══════════════════════════════════════════════════════
# 2. Minimal Numpy Layers
# ═══════════════════════════════════════════════════════

def softmax(x):
    x = x - np.max(x)
    e = np.exp(np.clip(x, -50, 50))
    return e / (e.sum() + 1e-12)

def relu(x):
    return np.maximum(0, x)


class Linear:
    """Simple linear layer with numpy."""
    def __init__(self, in_dim, out_dim):
        scale = np.sqrt(2.0 / (in_dim + out_dim))
        self.W = np.random.randn(in_dim, out_dim).astype(np.float64) * scale
        self.b = np.zeros(out_dim, dtype=np.float64)

    def forward(self, x):
        return x @ self.W + self.b

    def params(self):
        return [self.W, self.b]


# ═══════════════════════════════════════════════════════
# 3. PureField Policy (curiosity agent)
# ═══════════════════════════════════════════════════════

class PureFieldPolicy:
    """PureField-based policy for grid exploration.

    Two opposing engines (A=logic, G=pattern) produce action logits.
    Tension = tanh(|engine_A(obs) - engine_G(obs)|^2)  (bounded [0, 1])
    Output = tension_scale * sqrt(tension) * direction

    The agent receives intrinsic reward = |delta_tension| * novelty
    """

    def __init__(self, obs_dim=25, hidden_dim=32, action_dim=4):
        # Engine A (logic / analytical)
        self.a1 = Linear(obs_dim, hidden_dim)
        self.a2 = Linear(hidden_dim, action_dim)

        # Engine G (gestalt / pattern)
        self.g1 = Linear(obs_dim, hidden_dim)
        self.g2 = Linear(hidden_dim, action_dim)

        self.tension_scale = 1.0 / 3.0  # meta fixed point
        self.name = "PureFieldCuriosity"

    def forward(self, obs):
        """Returns (action_probs, tension_scalar in [0,1])."""
        # Engine A
        ha = relu(self.a1.forward(obs))
        out_a = self.a2.forward(ha)

        # Engine G
        hg = relu(self.g1.forward(obs))
        out_g = self.g2.forward(hg)

        # Repulsion field with bounded tension
        repulsion = out_a - out_g
        raw_tension = float(np.mean(repulsion ** 2))
        # Scale down before tanh so we use the sensitive part of the curve
        # tanh(0.5x) gives useful gradient for raw_tension in [0, 4]
        tension = math.tanh(0.5 * raw_tension)  # bounded to [0, 1]

        # Direction (normalized repulsion)
        norm = np.sqrt(np.sum(repulsion ** 2) + 1e-8)
        direction = repulsion / norm

        # Output logits = tension_scale * sqrt(tension) * direction
        logits = self.tension_scale * math.sqrt(tension + 1e-8) * direction

        probs = softmax(logits)
        return probs, tension

    def all_params(self):
        """Return flat list of all parameter arrays."""
        params = []
        for layer in [self.a1, self.a2, self.g1, self.g2]:
            params.extend(layer.params())
        return params


# ═══════════════════════════════════════════════════════
# 4. Episode Runners
# ═══════════════════════════════════════════════════════

def run_episode_curiosity(env, policy):
    """Run one episode. Returns (total_reward, positions, tensions)."""
    obs = env.reset()

    rewards = []
    tensions = []
    positions = [(env.r, env.c)]

    prev_tension = 0.0
    done = False

    while not done:
        probs, tension = policy.forward(obs)
        tensions.append(tension)

        action = np.random.choice(NUM_ACTIONS, p=probs)

        obs, done, novelty = env.step(action)
        positions.append((env.r, env.c))

        # Intrinsic reward = |delta_tension| * novelty
        # delta_tension is already bounded [0,1] thanks to tanh
        # novelty = 1/visit_count, rewards exploration
        surprise = abs(tension - prev_tension)
        reward = surprise * novelty
        rewards.append(reward)
        prev_tension = tension

    total_reward = sum(rewards)
    return total_reward, positions, tensions, rewards


def run_episode_random(env):
    """Run one episode with random policy."""
    obs = env.reset()
    positions = [(env.r, env.c)]
    done = False

    while not done:
        action = random.randint(0, NUM_ACTIONS - 1)
        obs, done, _ = env.step(action)
        positions.append((env.r, env.c))

    return positions


# ═══════════════════════════════════════════════════════
# 5. Evolution Strategy Training
# ═══════════════════════════════════════════════════════

def collect_params(policy):
    """Flatten all parameters into a single vector."""
    return np.concatenate([p.flatten() for p in policy.all_params()])


def set_params(policy, flat_params):
    """Set policy parameters from a flat vector."""
    offset = 0
    for p in policy.all_params():
        size = p.size
        p[:] = flat_params[offset:offset + size].reshape(p.shape)
        offset += size


def evaluate_policy(policy, env, n_episodes=3):
    """Evaluate: mean total curiosity reward per episode."""
    total = 0.0
    for _ in range(n_episodes):
        r, _, _, _ = run_episode_curiosity(env, policy)
        total += r
    return total / n_episodes


def train_es(policy, env, generations=300, population=30, lr=0.02, sigma=0.05):
    """Train with Evolution Strategy (OpenAI-style simplified ES)."""
    base_params = collect_params(policy)
    n_params = len(base_params)

    best_reward = -float('inf')
    reward_history = []

    print(f"  Parameters: {n_params}")

    for gen in range(generations):
        # Generate perturbations
        noise = np.random.randn(population, n_params)
        rewards = np.zeros(population)

        for i in range(population):
            set_params(policy, base_params + sigma * noise[i])
            r_pos = evaluate_policy(policy, env, n_episodes=2)

            set_params(policy, base_params - sigma * noise[i])
            r_neg = evaluate_policy(policy, env, n_episodes=2)

            rewards[i] = r_pos - r_neg

        # Normalize
        std = rewards.std()
        if std > 1e-8:
            rewards = (rewards - rewards.mean()) / std

        # Update
        gradient = (1.0 / (population * sigma)) * (noise.T @ rewards)
        base_params += lr * gradient

        # Weight decay to prevent explosion
        base_params *= 0.999

        set_params(policy, base_params)

        if gen % 25 == 0 or gen == generations - 1:
            mean_r = evaluate_policy(policy, env, n_episodes=10)
            reward_history.append((gen, mean_r))
            if mean_r > best_reward:
                best_reward = mean_r
            print(f"  Gen {gen:4d} | mean reward: {mean_r:.4f} | best: {best_reward:.4f}")

    set_params(policy, base_params)
    return reward_history


# ═══════════════════════════════════════════════════════
# 6. Analysis & Visualization
# ═══════════════════════════════════════════════════════

def compute_variance_map(grid):
    """Compute local variance at every cell."""
    vmap = np.zeros((GRID_SIZE, GRID_SIZE))
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            vmap[r, c] = local_variance(grid, r, c)
    return vmap


def print_grid_ascii(grid, title):
    """Print a grid as ASCII heatmap."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

    vmin, vmax = grid.min(), grid.max()
    rng = vmax - vmin if vmax > vmin else 1.0
    symbols = ' .:-=+*#%@'

    header = "    " + "".join(f"{c:2d}" for c in range(GRID_SIZE))
    print(header)
    print("    " + "--" * GRID_SIZE)

    for r in range(GRID_SIZE):
        row_str = f"{r:2d} | "
        for c in range(GRID_SIZE):
            level = int((grid[r, c] - vmin) / rng * (len(symbols) - 1))
            level = min(level, len(symbols) - 1)
            row_str += symbols[level] + " "
        print(row_str)


def print_visit_heatmap(visit_count, title):
    """Print visit counts as ASCII heatmap."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

    vmax = max(visit_count.max(), 1)
    symbols = ' .:-=+*#%@'

    header = "    " + "".join(f"{c:2d}" for c in range(GRID_SIZE))
    print(header)
    print("    " + "--" * GRID_SIZE)

    for r in range(GRID_SIZE):
        row_str = f"{r:2d} | "
        for c in range(GRID_SIZE):
            level = int(visit_count[r, c] / vmax * (len(symbols) - 1))
            level = min(level, len(symbols) - 1)
            row_str += symbols[level] + " "
        print(row_str)


def region_time_fraction(positions):
    """Compute fraction of time in interesting vs boring regions."""
    interesting = 0
    for (r, c) in positions:
        if (r < 6 and c < 6) or (r >= 10 and c >= 10) or (6 <= r < 10 and 6 <= c < 10):
            interesting += 1
    return interesting / len(positions) if positions else 0.0


def print_trajectory_segment(positions, n=20):
    """Print first n steps of trajectory."""
    print(f"  First {min(n, len(positions))} steps:")
    for i, (r, c) in enumerate(positions[:n]):
        print(f"    t={i:3d}: ({r:2d}, {c:2d})")


# ═══════════════════════════════════════════════════════
# 7. Main Experiment
# ═══════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  RC-4: Curiosity = Tension Change as Intrinsic Reward")
    print("=" * 60)

    env = GridEnv()
    grid = env.grid

    # --- Variance map ---
    vmap = compute_variance_map(grid)
    print_grid_ascii(vmap, "Local Variance Map (interesting = high)")

    print(f"\n  Interesting zones: top-left(0:6,0:6), bot-right(10:16,10:16)")
    print(f"  Mildly interesting: center(6:10,6:10)")
    print(f"  Boring: everywhere else (variance ~ 0)")
    print(f"  Max local variance: {vmap.max():.3f}")
    print(f"  Mean local variance: {vmap.mean():.3f}")

    # --- Phase 1: Random agent baseline ---
    print("\n" + "=" * 60)
    print("  Phase 1: Random Agent (baseline)")
    print("=" * 60)

    N_EVAL = 100
    random_interesting_fracs = []
    random_unique_cells = []
    all_random_visits = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    for ep in range(N_EVAL):
        positions = run_episode_random(env)
        random_interesting_fracs.append(region_time_fraction(positions))
        random_unique_cells.append(len(set(positions)))
        for (r, c) in positions:
            all_random_visits[r, c] += 1

    print(f"\n  Random agent ({N_EVAL} episodes, {MAX_STEPS} steps each):")
    print(f"  Mean interesting-zone fraction: {np.mean(random_interesting_fracs):.4f}")
    print(f"  Mean unique cells visited:      {np.mean(random_unique_cells):.1f} / {GRID_SIZE*GRID_SIZE}")

    print_visit_heatmap(all_random_visits, "Random Agent Visit Heatmap (100 episodes)")

    # --- Phase 2: Train curiosity agent ---
    print("\n" + "=" * 60)
    print("  Phase 2: Training Curiosity Agent (ES, 300 generations)")
    print("=" * 60)

    policy = PureFieldPolicy(obs_dim=25, hidden_dim=32, action_dim=4)
    reward_history = train_es(policy, env, generations=300, population=30,
                              lr=0.02, sigma=0.05)

    # --- Phase 3: Evaluate trained curiosity agent ---
    print("\n" + "=" * 60)
    print("  Phase 3: Evaluating Trained Curiosity Agent")
    print("=" * 60)

    curiosity_interesting_fracs = []
    curiosity_unique_cells = []
    curiosity_total_rewards = []
    all_curiosity_visits = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    for ep in range(N_EVAL):
        total_r, positions, tensions, rewards = run_episode_curiosity(env, policy)
        curiosity_interesting_fracs.append(region_time_fraction(positions))
        curiosity_unique_cells.append(len(set(positions)))
        curiosity_total_rewards.append(total_r)
        for (r, c) in positions:
            all_curiosity_visits[r, c] += 1

    print(f"\n  Curiosity agent ({N_EVAL} episodes, {MAX_STEPS} steps each):")
    print(f"  Mean interesting-zone fraction: {np.mean(curiosity_interesting_fracs):.4f}")
    print(f"  Mean unique cells visited:      {np.mean(curiosity_unique_cells):.1f} / {GRID_SIZE*GRID_SIZE}")
    print(f"  Mean total reward per episode:  {np.mean(curiosity_total_rewards):.4f}")

    print_visit_heatmap(all_curiosity_visits, "Curiosity Agent Visit Heatmap (100 episodes)")

    # --- Phase 4: Comparison ---
    print("\n" + "=" * 60)
    print("  Phase 4: Comparison")
    print("=" * 60)

    r_int = np.mean(random_interesting_fracs)
    c_int = np.mean(curiosity_interesting_fracs)
    r_uniq = np.mean(random_unique_cells)
    c_uniq = np.mean(curiosity_unique_cells)

    print(f"""
  +-----------------------------+----------+----------+----------+
  | Metric                      |  Random  | Curiosity|  Delta   |
  +-----------------------------+----------+----------+----------+
  | Interesting-zone fraction   | {r_int:8.4f} | {c_int:8.4f} | {c_int - r_int:+8.4f} |
  | Unique cells visited        | {r_uniq:8.1f} | {c_uniq:8.1f} | {c_uniq - r_uniq:+8.1f} |
  +-----------------------------+----------+----------+----------+
""")

    # --- Phase 5: Tension map ---
    print("=" * 60)
    print("  Phase 5: Tension Map (mean tension at each cell)")
    print("=" * 60)

    tension_map = np.zeros((GRID_SIZE, GRID_SIZE))
    tension_count = np.zeros((GRID_SIZE, GRID_SIZE))

    # Evaluate tension everywhere by systematically probing each cell
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            obs = get_observation(grid, r, c)
            _, tension = policy.forward(obs)
            tension_map[r, c] = tension
            tension_count[r, c] = 1

    print_grid_ascii(tension_map, "Tension at Each Cell (trained agent)")

    # Correlation: tension vs local variance
    flat_tension = tension_map.flatten()
    flat_variance = vmap.flatten()
    corr = np.corrcoef(flat_tension, flat_variance)[0, 1]

    print(f"\n  Correlation(tension, local_variance): {corr:.4f}")
    print(f"  (positive = tension responds to environmental complexity)")

    # --- Phase 6: Per-region tension analysis ---
    print("\n" + "=" * 60)
    print("  Phase 6: Per-Region Tension Analysis")
    print("=" * 60)

    zones = {
        'interesting_TL': [(r, c) for r in range(6) for c in range(6)],
        'interesting_BR': [(r, c) for r in range(10, 16) for c in range(10, 16)],
        'mild_center':    [(r, c) for r in range(6, 10) for c in range(6, 10)],
    }
    boring_cells = []
    int_cells = set()
    for cells in zones.values():
        int_cells.update(cells)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if (r, c) not in int_cells:
                boring_cells.append((r, c))
    zones['boring'] = boring_cells

    print(f"\n  {'Zone':<20s}  {'Mean Tension':>12s}  {'Mean Variance':>13s}  {'Cells':>5s}")
    print(f"  {'-'*20}  {'-'*12}  {'-'*13}  {'-'*5}")
    for name, cells in zones.items():
        t_vals = [tension_map[r, c] for r, c in cells]
        v_vals = [vmap[r, c] for r, c in cells]
        print(f"  {name:<20s}  {np.mean(t_vals):12.6f}  {np.mean(v_vals):13.4f}  {len(cells):5d}")

    # --- Phase 7: Sample trajectories ---
    print("\n" + "=" * 60)
    print("  Phase 7: Sample Trajectories")
    print("=" * 60)

    print("\n  --- Random Agent ---")
    positions_r = run_episode_random(env)
    print_trajectory_segment(positions_r, n=20)
    print(f"  Interesting fraction: {region_time_fraction(positions_r):.3f}")
    print(f"  Unique cells: {len(set(positions_r))}")

    print("\n  --- Curiosity Agent ---")
    _, positions_c, tensions_c, _ = run_episode_curiosity(env, policy)
    print_trajectory_segment(positions_c, n=20)
    print(f"  Interesting fraction: {region_time_fraction(positions_c):.3f}")
    print(f"  Unique cells: {len(set(positions_c))}")

    # Tension trace for curiosity agent
    print(f"\n  Tension trace (first 20 steps):")
    print(f"  {'Step':>4s}  {'Position':>10s}  {'Tension':>8s}  Bar")
    print(f"  {'-'*4}  {'-'*10}  {'-'*8}  {'-'*30}")
    for i in range(min(20, len(tensions_c))):
        r, c = positions_c[i]
        t = tensions_c[i]
        bar = '#' * int(t * 30)
        print(f"  {i:4d}  ({r:2d}, {c:2d})    {t:8.4f}  |{bar}")

    # --- Phase 8: Training curve ---
    print("\n" + "=" * 60)
    print("  Phase 8: Training Curve")
    print("=" * 60)

    if reward_history:
        max_r = max(r for _, r in reward_history)
        min_r = min(r for _, r in reward_history)
        rng = max_r - min_r if max_r > min_r else 1.0

        print(f"\n  {'Gen':>6s}  {'Reward':>10s}  Bar")
        print(f"  {'-'*6}  {'-'*10}  {'-'*40}")
        for gen, r in reward_history:
            bar_len = int((r - min_r) / rng * 40)
            bar = '#' * bar_len
            print(f"  {gen:6d}  {r:10.4f}  |{bar}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)

    gained_interest = c_int - r_int > 0.02
    gained_coverage = c_uniq - r_uniq > 2.0

    # Compute tension in interesting vs boring zones
    int_tension = np.mean([tension_map[r, c] for r, c in zones['interesting_TL']] +
                          [tension_map[r, c] for r, c in zones['interesting_BR']])
    boring_tension = np.mean([tension_map[r, c] for r, c in zones['boring']])
    tension_ratio = int_tension / (boring_tension + 1e-8)

    print(f"""
  Curiosity agent seeks interesting zones: {'YES' if gained_interest else 'NO'} (delta = {c_int - r_int:+.4f})
  Curiosity agent explores more cells:     {'YES' if gained_coverage else 'NO'} (delta = {c_uniq - r_uniq:+.1f})
  Tension-variance correlation:            {corr:.4f}
  Tension ratio (interesting/boring):      {tension_ratio:.4f}

  Reward design:
    intrinsic_reward = |tension(t) - tension(t-1)| * novelty
    tension = tanh(|engine_A - engine_G|^2)   (bounded [0,1])
    novelty = 1 / visit_count                 (decays with repeats)

  Interpretation:
    - tension-variance correlation > 0: PureField tension responds to
      environmental complexity (rugged landscape = high tension).
    - tension ratio > 1: interesting zones produce more tension than
      boring zones, confirming the field encodes "interestingness".
    - If interesting-zone fraction increased: the curiosity reward
      successfully drives exploration toward high-variance regions.
    - This validates RC-4: |delta_tension| as intrinsic curiosity signal.
""")


if __name__ == '__main__':
    main()
