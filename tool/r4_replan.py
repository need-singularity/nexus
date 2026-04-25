#!/usr/bin/env python3
"""r4 schedule_replan() — Python reference impl.
Mirrors tool/roadmap_engine.hexa parse_node L282, vstar L480, schedule L513.
Strategies: soft_drop / parallel_split / seed_inject.
MCTS UCB1 c=sqrt(2), rollouts<=32, wall<=2000ms (hard cap); soft caps 24/1500ms.
In-memory deep_copy snapshot per rollout. Uniform-random default policy. seed=42.
"""
import json, math, time, copy, random, sys
from dataclasses import dataclass, field
from typing import Optional

HARD_ROLLOUTS, HARD_DEPTH, HARD_WALL_MS = 32, 3, 2000
SOFT_ROLLOUTS, SOFT_DEPTH, SOFT_WALL_MS = 24, 2, 1500
UCB1_C, SEED = math.sqrt(2.0), 42

@dataclass
class Node:
    id: str; name: str = ""; ntype: str = "build"
    cost: float = 0.0; p_success: float = 1.0; eta: float = 0.0; n_uses: int = 1
    deps: list = field(default_factory=list); soft_deps: list = field(default_factory=list)
    status: str = "todo"; progress: float = 0.0

@dataclass
class Roadmap:
    id: str = ""; goal: str = ""; start: str = ""
    K_target: float = 1.0; C_channel: float = 1.0
    updated: str = ""; description: str = ""
    nodes: list = field(default_factory=list)

@dataclass
class ReplanBudget:
    max_rollouts: int = HARD_ROLLOUTS; max_depth: int = HARD_DEPTH; max_wall_ms: int = HARD_WALL_MS

@dataclass
class ReplanDelta:
    action: str; target: str; detail: str
    T_pre: float; T_post: float; rollouts_used: int; wall_ms: float
    soft_warnings: list = field(default_factory=list)

def parse_node(d: dict) -> Node:
    nu = d.get("n_uses", 1) or 1
    if nu <= 0: nu = 1
    p = d.get("p_success", 1.0) or 1.0
    if p <= 0.0: p = 1.0
    hd = d.get("hard_deps")
    deps = list(hd) if hd else list(d.get("deps", []))
    return Node(id=d["id"], name=d.get("name") or d["id"], ntype=d.get("type") or "build",
                cost=float(d.get("cost", 0.0)), p_success=float(p), eta=float(d.get("eta", 0.0)),
                n_uses=int(nu), deps=deps, soft_deps=list(d.get("soft_deps", [])),
                status=d.get("status") or "todo", progress=float(d.get("progress", 0.0)))

def parse_roadmap(path: str) -> Roadmap:
    with open(path, "r") as f:
        raw = json.load(f)
    return Roadmap(id=raw.get("id",""), goal=raw.get("goal",""), start=raw.get("start",""),
                   K_target=float(raw.get("K_target",1.0)), C_channel=float(raw.get("C_channel",1.0)),
                   updated=raw.get("updated",""), description=raw.get("description",""),
                   nodes=[parse_node(n) for n in raw.get("nodes",[])])

# ── Cost (mirrors hexa effective_cost L412 / remaining_cost L446) ──────────
def is_done(st): return st in ("done","complete","aborted","skipped")

def effective_cost(n: Node, K: float, C: float) -> float:
    t = n.ntype
    if t == "seed": return 0.0
    if t == "goal": return n.cost
    if t == "exp": return n.cost / (n.p_success if n.p_success > 0 else 1.0)
    if t == "learn": return n.cost * (1.0 - max(0.0, n.eta))
    if t == "boot": return n.cost / float(max(1, n.n_uses))
    if t == "verify":
        k = K if K > 0 else 1.0; c = C if C > 0 else 1.0
        return (k / c) + (n.cost * 0.25)
    return n.cost

def remaining_cost(n: Node, K: float, C: float) -> float:
    if is_done(n.status): return 0.0
    c = effective_cost(n, K, C)
    if n.status == "in_progress":
        p = max(0.0, min(1.0, n.progress))
        return c * (1.0 - p)
    return c

# ── V* with Tarjan SCC contraction (handles soft_dep cycles) ───────────────
def _children(nodes, nid, include_soft):
    out = []
    for n in nodes:
        if nid in n.deps: out.append(n.id)
        elif include_soft and nid in n.soft_deps: out.append(n.id)
    return out

def _tarjan_scc(nodes, include_soft):
    idx = {n.id: -1 for n in nodes}; low = {n.id: 0 for n in nodes}
    on = {n.id: False for n in nodes}; stack = []; scc = {}
    counter = [0]; sidx = [0]
    sys.setrecursionlimit(10000)
    def strong(v):
        idx[v] = counter[0]; low[v] = counter[0]; counter[0] += 1
        stack.append(v); on[v] = True
        for w in _children(nodes, v, include_soft):
            if idx[w] == -1:
                strong(w); low[v] = min(low[v], low[w])
            elif on[w]:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            while True:
                w = stack.pop(); on[w] = False; scc[w] = sidx[0]
                if w == v: break
            sidx[0] += 1
    for n in nodes:
        if idx[n.id] == -1: strong(n.id)
    return scc

def vstar(rm: Roadmap, node_id: str, include_soft: bool = True) -> float:
    """V*(n) — DAG critical path with SCC contraction; SCC members serial-sum."""
    nodes = rm.nodes; K, C = rm.K_target, rm.C_channel
    by_id = {n.id: n for n in nodes}
    if node_id not in by_id: return 0.0
    scc_of = _tarjan_scc(nodes, include_soft)
    super_cost, super_edges = {}, {}
    for nid, sid in scc_of.items():
        super_cost[sid] = super_cost.get(sid, 0.0) + remaining_cost(by_id[nid], K, C)
        super_edges.setdefault(sid, set())
    for n in nodes:
        for child in _children(nodes, n.id, include_soft):
            a, b = scc_of[n.id], scc_of[child]
            if a != b: super_edges[a].add(b)
    memo = {}
    def vsuper(sid):
        if sid in memo: return memo[sid]
        best = 0.0
        for nxt in super_edges[sid]:
            v = vsuper(nxt)
            if v > best: best = v
        memo[sid] = super_cost[sid] + best
        return memo[sid]
    return vsuper(scc_of[node_id])

# ── Strategies (atomic apply on deep_copy snapshot) ────────────────────────
def apply_soft_drop(rm: Roadmap) -> Optional[str]:
    dropped = sum(len(n.soft_deps) for n in rm.nodes)
    if dropped == 0: return None
    for n in rm.nodes: n.soft_deps = []
    return f"dropped {dropped} soft edges"

def apply_parallel_split(rm: Roadmap) -> Optional[str]:
    cands = [n for n in rm.nodes if not is_done(n.status) and n.ntype == "build" and n.cost >= 30.0]
    if not cands: return None
    target = max(cands, key=lambda n: n.cost)
    kids = len(_children(rm.nodes, target.id, include_soft=False))
    k = min(4, max(2, kids)) if kids >= 3 else 3
    target.cost /= float(k)
    return f"split {target.id} k={k}"

def apply_seed_inject(rm: Roadmap) -> Optional[str]:
    blocked = [n for n in rm.nodes if n.ntype == "seed" and (n.status == "blocked" or n.n_uses <= 0)]
    if not blocked: return None
    alts = [n for n in rm.nodes if n.ntype == "seed" and n.n_uses > 0 and n not in blocked]
    if not alts: return None
    bk, alt = blocked[0], alts[0]
    # Taint = nodes whose deps are ALL through blocked seed (no alt path).
    tainted = {bk.id}; changed = True
    while changed:
        changed = False
        for n in rm.nodes:
            if n.id in tainted: continue
            if n.deps and all(d in tainted for d in n.deps):
                tainted.add(n.id); changed = True
    rewrites = 0
    # Mixed-dep nodes: drop tainted branches (alt path exists).
    for n in rm.nodes:
        if n.id in tainted: continue
        nt = [d for d in n.deps if d not in tainted]
        td = [d for d in n.deps if d in tainted]
        if td and nt:
            n.deps = nt; rewrites += len(td)
    # Direct swap of blocked-seed refs to alt.
    for n in rm.nodes:
        if n.id == bk.id: continue
        if bk.id in n.deps:
            n.deps = [alt.id if d == bk.id else d for d in n.deps]
            rewrites += 1
    return f"seed_inject blocked={bk.id} alt={alt.id} rewrites={rewrites}" if rewrites else None

STRATEGIES = {"soft_drop": apply_soft_drop, "parallel_split": apply_parallel_split, "seed_inject": apply_seed_inject}

def _start_id(rm: Roadmap) -> str:
    if rm.start: return rm.start
    for n in rm.nodes:
        if not n.deps: return n.id
    return rm.nodes[0].id if rm.nodes else ""

def _rollout(rm: Roadmap, action: str):
    snap = copy.deepcopy(rm)
    fn = STRATEGIES.get(action)
    if fn is None: return (math.inf, None)
    desc = fn(snap)
    if desc is None: return (math.inf, None)
    return (vstar(snap, _start_id(snap), include_soft=True), desc)

def schedule_replan(rm: Roadmap, budget: ReplanBudget = ReplanBudget()) -> Optional[ReplanDelta]:
    """MCTS UCB1 over 3 strategies; return best delta or None if no improvement."""
    rng = random.Random(SEED)
    T_pre = vstar(rm, _start_id(rm), include_soft=True)
    actions = list(STRATEGIES.keys())
    visits = {a: 0 for a in actions}; rewards = {a: 0.0 for a in actions}
    best_T, best_action, best_desc = math.inf, None, None
    soft_warnings = []
    t0 = time.time(); rollouts = 0
    max_r = min(budget.max_rollouts, HARD_ROLLOUTS)
    max_wall = min(budget.max_wall_ms, HARD_WALL_MS)
    while rollouts < max_r:
        elapsed = (time.time() - t0) * 1000.0
        if elapsed > max_wall: break
        if elapsed > SOFT_WALL_MS and "wall_soft" not in soft_warnings: soft_warnings.append("wall_soft")
        if rollouts >= SOFT_ROLLOUTS and "rollouts_soft" not in soft_warnings: soft_warnings.append("rollouts_soft")
        tv = sum(visits.values())
        if tv < len(actions):
            action = actions[tv]
        else:
            best_ucb, action = -math.inf, actions[0]
            for a in actions:
                ucb = math.inf if visits[a] == 0 else rewards[a]/visits[a] + UCB1_C*math.sqrt(math.log(tv)/visits[a])
                if ucb > best_ucb: best_ucb, action = ucb, a
        T_post, desc = _rollout(rm, action)
        rollouts += 1; visits[action] += 1
        if T_post < math.inf:
            rewards[action] += max(0.0, (T_pre - T_post) / max(T_pre, 1e-9))
            if T_post < best_T: best_T, best_action, best_desc = T_post, action, desc
    wall_ms = (time.time() - t0) * 1000.0
    if best_action is None or best_T >= T_pre: return None
    return ReplanDelta(action=best_action, target="", detail=best_desc or "",
                       T_pre=T_pre, T_post=best_T, rollouts_used=rollouts,
                       wall_ms=wall_ms, soft_warnings=soft_warnings)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        rm = parse_roadmap(sys.argv[1])
        print(f"T*_pre = {vstar(rm, _start_id(rm)):.3f}")
        d = schedule_replan(rm)
        if d is None: print("schedule_replan: None")
        else: print(f"action={d.action} T_pre={d.T_pre:.3f} T_post={d.T_post:.3f} rollouts={d.rollouts_used} wall_ms={d.wall_ms:.1f}")
