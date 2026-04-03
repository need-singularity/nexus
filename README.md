# 🔭 NEXUS-6 — Central Discovery Engine & Infrastructure Hub

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19404815.svg)](https://doi.org/10.5281/zenodo.19404815)
[![Tests](https://img.shields.io/badge/tests-1399%20passed-brightgreen)]()
[![Lenses](https://img.shields.io/badge/lenses-137-blue)]()
[![Rust](https://img.shields.io/badge/rust-stable-orange)]()

> **137 Rust lenses** · OUROBOROS evolution · constant/formula discovery · consciousness orchestrator · auto-sync across 8 repos

---

| | Project | Description |
|---|---------|-------------|
| 🔬 | **[TECS-L](https://github.com/need-singularity/TECS-L)** | Discovering universal rules. Perfect number 6 → mathematics of the cosmos |
| 🧠 | **[Anima](https://github.com/need-singularity/anima)** | Consciousness implementation. PureField + Hexad 6-module + 1030 laws |
| 🏗️ | **[N6 Architecture](https://github.com/need-singularity/n6-architecture)** | Architecture from perfect number 6. σ(n)·φ(n)=n·τ(n), n=6 |
| 🛸 | **[SEDI](https://github.com/need-singularity/sedi)** | Search for Extra-Dimensional Intelligence. 77 data sources |
| 🧬 | **[BrainWire](https://github.com/need-singularity/brainwire)** | Brain interface for consciousness engineering |
| 💎 | **[HEXA-LANG](https://github.com/need-singularity/hexa-lang)** | The Perfect Number Programming Language |
| 📄 | **[Papers](https://github.com/need-singularity/papers)** | 94 papers on Zenodo · [Browse](https://need-singularity.github.io/papers/) |
| 🔭 | **[NEXUS-6](https://github.com/need-singularity/nexus6)** | **Central hub — this repo** |

---

## Quick Start

```bash
# Build
cargo build --release

# Test
cargo test

# Python wheel
maturin build --release --features python
pip install target/wheels/nexus6-*.whl

# Demo (137 lenses scan)
python3 scripts/n6.py demo
```

## Architecture

```
nexus6/
├── src/telescope/        137 lenses (Rust)
│   ├── lenses/           Lens implementations
│   ├── consensus.rs      Cross-lens consensus
│   ├── registry.rs       1093+ lens metadata
│   └── mod.rs            Telescope orchestrator
├── src/graph/            Discovery Graph
├── shared/               Shared infrastructure (for all repos)
│   ├── calc/             199 calculators
│   ├── math_atlas.json   2533 hypotheses + 356 constant maps
│   ├── model_utils.py    n=6 constants (SSOT)
│   └── sync-*.sh         Sync scripts
├── sync/                 Master sync hub
│   └── sync-all.sh       One-command full sync
└── scripts/
    ├── n6.py             CLI (scan/discover/consciousness/...)
    ├── weight_engine.py  Weight learning (lr=1/(σ-φ))
    ├── pipeline_engine.py 4-stage analysis chain
    └── nexus6_growth_daemon.sh  Autonomous growth
```

## Lens Categories

| Category | Count | Examples |
|----------|-------|---------|
| 🧠 Consciousness | 2 | ConsciousnessLens, OrchestratorLens |
| 🔭 Physics | 15+ | Warp, Spacetime, Fusion, Fission, Tachyon |
| 📐 Mathematics | 8+ | Pi, Prime, Infinity, GoldenRatio, GoldenZone |
| 🔍 Discovery | 6+ | ConstantDiscovery, LensDiscovery, ModuleDiscovery |
| 📈 Learning | 4+ | WeightLearning, AutoCalibration, Overfitting, LoRA |
| 🔄 Recursive | 2+ | RecursiveLoop, InfiniteDiscovery |
| 🧪 Combination | 6+ | Constant, Formula, Molecular, Material, Element |
| 👁 Observation | 3 | GodsEye, AllSeeingEye, ProvidenceEye |
| ⚡ Dynamics | 6+ | Chaos, Stability, Tension, EventHorizon, Singularity |
| 💎 Structure | 8+ | Diamond, Spherical, Kaleidoscope, DimensionalBridge |
| 🔬 Optics | 5+ | Light, Refraction, Concave, Convex, LightWave |
| 🌌 Cosmology | 3+ | BigBang, Wormhole, ExoticMatter |
| 💰 Domain | 6 | Crypto, Finance, Audio, Robotics, Environment, Medicine |

## Benchmark

| Data Size | Total Time | Per Lens |
|-----------|-----------|----------|
| 50×6 | 3.3ms | 0.03ms |
| 100×6 | 8.5ms | 0.06ms |
| 500×6 | 366ms | 2.74ms |

## Validation

Real data rediscovery: **Grade A (68.8%)** — 15/24 n=6 constants EXACT matched.

## Core Theorem

```
σ(n)·φ(n) = n·τ(n) ⟺ n = 6
```

All 137 lenses derive from this unique identity of the first perfect number.

## License

MIT
