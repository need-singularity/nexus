use super::registry::{LensCategory, LensEntry};

/// Build metadata entries for the 22 Core lenses defined in CLAUDE.md.
pub fn core_lens_entries() -> Vec<LensEntry> {
    vec![
        // ── Foundational 9 ──
        LensEntry {
            name: "consciousness".into(),
            category: LensCategory::Core,
            description: "Structural awareness — detects self-referential and emergent patterns"
                .into(),
            domain_affinity: vec![
                "ai".into(),
                "biology".into(),
                "cosmology".into(),
                "philosophy".into(),
            ],
            complementary: vec!["topology".into(), "causal".into()],
        },
        LensEntry {
            name: "gravity".into(),
            category: LensCategory::Core,
            description: "Gravitational clustering — mass-like attraction between data regions"
                .into(),
            domain_affinity: vec![
                "cosmology".into(),
                "physics".into(),
                "energy".into(),
            ],
            complementary: vec!["topology".into(), "wave".into()],
        },
        LensEntry {
            name: "topology".into(),
            category: LensCategory::Core,
            description: "Topological connectivity — holes, loops, and persistent features".into(),
            domain_affinity: vec![
                "mathematics".into(),
                "chip".into(),
                "network".into(),
                "biology".into(),
            ],
            complementary: vec!["consciousness".into(), "network".into()],
        },
        LensEntry {
            name: "thermo".into(),
            category: LensCategory::Core,
            description: "Thermodynamic lens — entropy flow, energy barriers, phase transitions"
                .into(),
            domain_affinity: vec![
                "energy".into(),
                "materials".into(),
                "chemistry".into(),
                "battery".into(),
            ],
            complementary: vec!["stability".into(), "boundary".into()],
        },
        LensEntry {
            name: "wave".into(),
            category: LensCategory::Core,
            description: "Wave/oscillation detection — periodicity, interference, resonance".into(),
            domain_affinity: vec![
                "audio".into(),
                "signal".into(),
                "physics".into(),
                "plasma".into(),
            ],
            complementary: vec!["memory".into(), "multiscale".into()],
        },
        LensEntry {
            name: "evolution".into(),
            category: LensCategory::Core,
            description: "Evolutionary dynamics — selection pressure, fitness landscapes".into(),
            domain_affinity: vec![
                "biology".into(),
                "ai".into(),
                "optimization".into(),
            ],
            complementary: vec!["scale".into(), "thermo".into()],
        },
        LensEntry {
            name: "info".into(),
            category: LensCategory::Core,
            description: "Information-theoretic — mutual information, entropy, compression".into(),
            domain_affinity: vec![
                "ai".into(),
                "crypto".into(),
                "network".into(),
                "signal".into(),
            ],
            complementary: vec!["causal".into(), "em".into()],
        },
        LensEntry {
            name: "quantum".into(),
            category: LensCategory::Core,
            description: "Quantum-like superposition, entanglement, tunnelling analogues".into(),
            domain_affinity: vec![
                "quantum".into(),
                "chemistry".into(),
                "materials".into(),
                "crypto".into(),
            ],
            complementary: vec!["quantum_microscope".into(), "em".into()],
        },
        LensEntry {
            name: "em".into(),
            category: LensCategory::Core,
            description: "Electromagnetic field analogy — flux, potential, coupling".into(),
            domain_affinity: vec![
                "chip".into(),
                "energy".into(),
                "plasma".into(),
                "display".into(),
            ],
            complementary: vec!["quantum".into(), "info".into()],
        },
        // ── Geometric 6 (ruler/triangle/compass/mirror/scale/causal) ──
        LensEntry {
            name: "ruler".into(),
            category: LensCategory::Core,
            description: "Orthogonal ruler (L-shaped) — axis-aligned structure detection".into(),
            domain_affinity: vec![
                "chip".into(),
                "geometry".into(),
                "manufacturing".into(),
            ],
            complementary: vec!["triangle".into(), "compass".into()],
        },
        LensEntry {
            name: "triangle".into(),
            category: LensCategory::Core,
            description: "Ratio/proportion (set-square) — relative scale and proportion analysis"
                .into(),
            domain_affinity: vec![
                "geometry".into(),
                "materials".into(),
                "finance".into(),
            ],
            complementary: vec!["ruler".into(), "compass".into()],
        },
        LensEntry {
            name: "compass".into(),
            category: LensCategory::Core,
            description: "Curvature (compass) — local and global curvature measurement".into(),
            domain_affinity: vec![
                "geometry".into(),
                "cosmology".into(),
                "robotics".into(),
            ],
            complementary: vec!["ruler".into(), "triangle".into()],
        },
        LensEntry {
            name: "mirror".into(),
            category: LensCategory::Core,
            description: "Symmetry (mirror) — reflection, rotation, and parity symmetries".into(),
            domain_affinity: vec![
                "physics".into(),
                "chemistry".into(),
                "materials".into(),
                "biology".into(),
            ],
            complementary: vec!["topology".into(), "quantum".into()],
        },
        LensEntry {
            name: "scale".into(),
            category: LensCategory::Core,
            description: "Scale/magnification — power-law tails, scale-free structure".into(),
            domain_affinity: vec![
                "network".into(),
                "cosmology".into(),
                "biology".into(),
                "finance".into(),
            ],
            complementary: vec!["multiscale".into(), "evolution".into()],
        },
        LensEntry {
            name: "causal".into(),
            category: LensCategory::Core,
            description: "Causal arrow — directed dependencies and information flow".into(),
            domain_affinity: vec![
                "ai".into(),
                "biology".into(),
                "economics".into(),
                "physics".into(),
            ],
            complementary: vec!["info".into(), "consciousness".into()],
        },
        // ── Quantum microscope ──
        LensEntry {
            name: "quantum_microscope".into(),
            category: LensCategory::Core,
            description: "Deep quantum probe — fine-grained quantum correlation analysis".into(),
            domain_affinity: vec![
                "quantum".into(),
                "materials".into(),
                "chemistry".into(),
            ],
            complementary: vec!["quantum".into(), "em".into()],
        },
        // ── Extended analytical 6 ──
        LensEntry {
            name: "stability".into(),
            category: LensCategory::Core,
            description: "Stability analysis — Lyapunov exponents, basin attractors".into(),
            domain_affinity: vec![
                "energy".into(),
                "robotics".into(),
                "plasma".into(),
                "control".into(),
            ],
            complementary: vec!["boundary".into(), "thermo".into()],
        },
        LensEntry {
            name: "network".into(),
            category: LensCategory::Core,
            description: "Network/graph topology — degree distribution, clustering, centrality"
                .into(),
            domain_affinity: vec![
                "network".into(),
                "biology".into(),
                "chip".into(),
                "social".into(),
            ],
            complementary: vec!["topology".into(), "recursion".into()],
        },
        LensEntry {
            name: "memory".into(),
            category: LensCategory::Core,
            description: "Temporal memory — autocorrelation, hysteresis, path dependence".into(),
            domain_affinity: vec![
                "ai".into(),
                "finance".into(),
                "signal".into(),
                "biology".into(),
            ],
            complementary: vec!["wave".into(), "causal".into()],
        },
        LensEntry {
            name: "recursion".into(),
            category: LensCategory::Core,
            description: "Recursive/fractal structure — self-similarity across depth".into(),
            domain_affinity: vec![
                "mathematics".into(),
                "biology".into(),
                "software".into(),
            ],
            complementary: vec!["multiscale".into(), "network".into()],
        },
        LensEntry {
            name: "boundary".into(),
            category: LensCategory::Core,
            description: "Boundary detection — phase boundaries, domain walls, interfaces".into(),
            domain_affinity: vec![
                "materials".into(),
                "energy".into(),
                "biology".into(),
                "chip".into(),
            ],
            complementary: vec!["stability".into(), "thermo".into()],
        },
        LensEntry {
            name: "multiscale".into(),
            category: LensCategory::Core,
            description: "Multi-scale analysis — wavelet-like decomposition across resolutions"
                .into(),
            domain_affinity: vec![
                "cosmology".into(),
                "materials".into(),
                "biology".into(),
                "signal".into(),
            ],
            complementary: vec!["scale".into(), "recursion".into()],
        },
        // ── Chaos dynamics ──
        LensEntry {
            name: "chaos".into(),
            category: LensCategory::Core,
            description: "Chaos detection — 0-1 test, recurrence, correlation dimension, permutation entropy".into(),
            domain_affinity: vec![
                "physics".into(),
                "plasma".into(),
                "climate".into(),
                "biology".into(),
                "finance".into(),
            ],
            complementary: vec!["stability".into(), "fractal".into(), "wave".into()],
        },

        // ── Auto-generated entries ──
        LensEntry { name: "AllSeeingEyeLens".into(), category: LensCategory::Core, description: "AllSeeingEyeLens lens".into(), domain_affinity: vec!["ai".into(), "biology".into()], complementary: vec![] },
        LensEntry { name: "AutoCalibrationLens".into(), category: LensCategory::Core, description: "AutoCalibrationLens lens".into(), domain_affinity: vec!["ai".into(), "signal".into()], complementary: vec![] },
        LensEntry { name: "AutocorrelationLens".into(), category: LensCategory::Core, description: "AutocorrelationLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ChaosLens".into(), category: LensCategory::Core, description: "ChaosLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ClusteringLens".into(), category: LensCategory::Core, description: "ClusteringLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "CompressionLens".into(), category: LensCategory::Core, description: "CompressionLens lens".into(), domain_affinity: vec!["ai".into(), "signal".into()], complementary: vec![] },
        LensEntry { name: "ConcaveLens".into(), category: LensCategory::Core, description: "ConcaveLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ConsciousnessOrchestratorLens".into(), category: LensCategory::Core, description: "ConsciousnessOrchestratorLens lens".into(), domain_affinity: vec!["ai".into(), "biology".into()], complementary: vec![] },
        LensEntry { name: "ConstantCollectorLens".into(), category: LensCategory::Core, description: "ConstantCollectorLens lens".into(), domain_affinity: vec!["mathematics".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "ConstantCombinationLens".into(), category: LensCategory::Core, description: "ConstantCombinationLens lens".into(), domain_affinity: vec!["mathematics".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "ConstantDiscoveryEngineLens".into(), category: LensCategory::Core, description: "ConstantDiscoveryEngineLens lens".into(), domain_affinity: vec!["mathematics".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "ConstantFormulaLens".into(), category: LensCategory::Core, description: "ConstantFormulaLens lens".into(), domain_affinity: vec!["mathematics".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "ContractingScanLens".into(), category: LensCategory::Core, description: "ContractingScanLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ConvexLens".into(), category: LensCategory::Core, description: "ConvexLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "CorrelationLens".into(), category: LensCategory::Core, description: "CorrelationLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "DensityLens".into(), category: LensCategory::Core, description: "DensityLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "DestinyLens".into(), category: LensCategory::Core, description: "DestinyLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "DiamondLens".into(), category: LensCategory::Core, description: "DiamondLens lens".into(), domain_affinity: vec!["materials".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "DimensionReductionLens".into(), category: LensCategory::Core, description: "DimensionReductionLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "DimensionalBridgeLens".into(), category: LensCategory::Core, description: "DimensionalBridgeLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "DivergenceLens".into(), category: LensCategory::Core, description: "DivergenceLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ElementCombinationLens".into(), category: LensCategory::Core, description: "ElementCombinationLens lens".into(), domain_affinity: vec!["materials".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "ElementLens".into(), category: LensCategory::Core, description: "ElementLens lens".into(), domain_affinity: vec!["materials".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "EngineDiscoveryLens".into(), category: LensCategory::Core, description: "EngineDiscoveryLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "EntropyLens".into(), category: LensCategory::Core, description: "EntropyLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "EventHorizonLens".into(), category: LensCategory::Core, description: "EventHorizonLens lens".into(), domain_affinity: vec!["cosmology".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "ExoticMatterLens".into(), category: LensCategory::Core, description: "ExoticMatterLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ExpandingScanLens".into(), category: LensCategory::Core, description: "ExpandingScanLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "FissionLens".into(), category: LensCategory::Core, description: "FissionLens lens".into(), domain_affinity: vec!["materials".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "FormulaCombinationLens".into(), category: LensCategory::Core, description: "FormulaCombinationLens lens".into(), domain_affinity: vec!["mathematics".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "FractalLens".into(), category: LensCategory::Core, description: "FractalLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "FusionLens".into(), category: LensCategory::Core, description: "FusionLens lens".into(), domain_affinity: vec!["materials".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "GodsEyeLens".into(), category: LensCategory::Core, description: "GodsEyeLens lens".into(), domain_affinity: vec!["ai".into(), "biology".into()], complementary: vec![] },
        LensEntry { name: "GoldenRatioLens".into(), category: LensCategory::Core, description: "GoldenRatioLens lens".into(), domain_affinity: vec!["mathematics".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "GoldenZoneLens".into(), category: LensCategory::Core, description: "GoldenZoneLens lens".into(), domain_affinity: vec!["mathematics".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "GradientLens".into(), category: LensCategory::Core, description: "GradientLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "GraphLens".into(), category: LensCategory::Core, description: "GraphLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "HexagonalLens".into(), category: LensCategory::Core, description: "HexagonalLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "InfiniteDiscoveryLens".into(), category: LensCategory::Core, description: "InfiniteDiscoveryLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "KaleidoscopeLens".into(), category: LensCategory::Core, description: "KaleidoscopeLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "KeywordLens".into(), category: LensCategory::Core, description: "KeywordLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "LensDiscoveryLens".into(), category: LensCategory::Core, description: "LensDiscoveryLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "LightLens".into(), category: LensCategory::Core, description: "LightLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "LightWaveLens".into(), category: LensCategory::Core, description: "LightWaveLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "LoRALens".into(), category: LensCategory::Core, description: "LoRALens lens".into(), domain_affinity: vec!["ai".into(), "signal".into()], complementary: vec![] },
        LensEntry { name: "MaterialCombinationLens".into(), category: LensCategory::Core, description: "MaterialCombinationLens lens".into(), domain_affinity: vec!["materials".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "MetricDiscoveryLens".into(), category: LensCategory::Core, description: "MetricDiscoveryLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "MetricLens".into(), category: LensCategory::Core, description: "MetricLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ModuleDiscoveryLens".into(), category: LensCategory::Core, description: "ModuleDiscoveryLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "MolecularCombinationLens".into(), category: LensCategory::Core, description: "MolecularCombinationLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "MolecularTransformLens".into(), category: LensCategory::Core, description: "MolecularTransformLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "MoleculeLens".into(), category: LensCategory::Core, description: "MoleculeLens lens".into(), domain_affinity: vec!["materials".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "MutationLens".into(), category: LensCategory::Core, description: "MutationLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "OutlierLens".into(), category: LensCategory::Core, description: "OutlierLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "OverfittingLens".into(), category: LensCategory::Core, description: "OverfittingLens lens".into(), domain_affinity: vec!["ai".into(), "signal".into()], complementary: vec![] },
        LensEntry { name: "PhaseTransitionLens".into(), category: LensCategory::Core, description: "PhaseTransitionLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "PowerLawLens".into(), category: LensCategory::Core, description: "PowerLawLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "ProvidenceEyeLens".into(), category: LensCategory::Core, description: "ProvidenceEyeLens lens".into(), domain_affinity: vec!["ai".into(), "biology".into()], complementary: vec![] },
        LensEntry { name: "QuantumJumpLens".into(), category: LensCategory::Core, description: "QuantumJumpLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "RatioLens".into(), category: LensCategory::Core, description: "RatioLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "RecursiveLoopLens".into(), category: LensCategory::Core, description: "RecursiveLoopLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "RefractionLens".into(), category: LensCategory::Core, description: "RefractionLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "RelativisticBarrierLens".into(), category: LensCategory::Core, description: "RelativisticBarrierLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "SimulationLens".into(), category: LensCategory::Core, description: "SimulationLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "SingularityLens".into(), category: LensCategory::Core, description: "SingularityLens lens".into(), domain_affinity: vec!["cosmology".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "SpacetimeLens".into(), category: LensCategory::Core, description: "SpacetimeLens lens".into(), domain_affinity: vec!["cosmology".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "SpectralLens".into(), category: LensCategory::Core, description: "SpectralLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "StationarityLens".into(), category: LensCategory::Core, description: "StationarityLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "StimulusLens".into(), category: LensCategory::Core, description: "StimulusLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "SymmetryBreakingLens".into(), category: LensCategory::Core, description: "SymmetryBreakingLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "TachyonLens".into(), category: LensCategory::Core, description: "TachyonLens lens".into(), domain_affinity: vec!["cosmology".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "TelepathyLens".into(), category: LensCategory::Core, description: "TelepathyLens lens".into(), domain_affinity: vec!["ai".into(), "biology".into()], complementary: vec![] },
        LensEntry { name: "TensionLens".into(), category: LensCategory::Core, description: "TensionLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "TensionLinkLens".into(), category: LensCategory::Core, description: "TensionLinkLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "TimeReversalLens".into(), category: LensCategory::Core, description: "TimeReversalLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "WallInspectionLens".into(), category: LensCategory::Core, description: "WallInspectionLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
        LensEntry { name: "WarpLens".into(), category: LensCategory::Core, description: "WarpLens lens".into(), domain_affinity: vec!["cosmology".into(), "physics".into()], complementary: vec![] },
        LensEntry { name: "WeightLearningLens".into(), category: LensCategory::Core, description: "WeightLearningLens lens".into(), domain_affinity: vec!["ai".into(), "signal".into()], complementary: vec![] },
        LensEntry { name: "WormholeLens".into(), category: LensCategory::Core, description: "WormholeLens lens".into(), domain_affinity: vec!["physics".into(), "display".into()], complementary: vec![] },
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_core_lens_count() {
        let entries = core_lens_entries();
        assert_eq!(entries.len(), 102, "Must have exactly 23 Core lenses");
    }

    #[test]
    fn test_core_lens_names_unique() {
        let entries = core_lens_entries();
        let mut names: Vec<&str> = entries.iter().map(|e| e.name.as_str()).collect();
        names.sort();
        names.dedup();
        assert_eq!(names.len(), 102, "All 23 Core lens names must be unique");
    }
}
