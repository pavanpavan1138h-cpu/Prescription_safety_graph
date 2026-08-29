from typing import List
from src.prescription.trustworthiness.trustworthiness_schema import (
    ReproducibilityProfile,
    InputPerturbationResult,
    StructuralRobustnessProfile,
    SignalRobustnessProfile,
    CrossLayerConsistencyProfile,
    ProvenanceCompletenessProfile,
    ExplanationConsistencyProfile,
    TrustworthinessMetric,
    TrustworthinessLevel
)

class TrustworthinessScoringEngine:
    @staticmethod
    def compute_trustworthiness(
        reproducibility: ReproducibilityProfile,
        perturbations: List[InputPerturbationResult],
        structure: StructuralRobustnessProfile,
        signals: List[SignalRobustnessProfile],
        consistency: CrossLayerConsistencyProfile,
        provenance: ProvenanceCompletenessProfile,
        explanation: ExplanationConsistencyProfile
    ) -> tuple[float, List[TrustworthinessMetric], TrustworthinessLevel]:
        """
        Calculates normalized trustworthiness scores based on weighted averages of sub-metrics.
        """
        metrics: List[TrustworthinessMetric] = []

        # 1. Reproducibility (weight: 0.20)
        rep_score = reproducibility.deterministic_match_ratio
        metrics.append(TrustworthinessMetric(
            metric_id="METRIC_REPRODUCIBILITY",
            metric_name="Deterministic Reproducibility Ratio",
            value=rep_score,
            normalized_value=rep_score,
            classification=reproducibility.classification.value,
            description="Matches between repeat baseline execution outputs"
        ))

        # 2. Input Invariance (weight: 0.15)
        if perturbations:
            inv_count = sum(1 for p in perturbations if p.classification.value == "INVARIANT")
            pert_score = inv_count / len(perturbations)
        else:
            pert_score = 1.0
        
        metrics.append(TrustworthinessMetric(
            metric_id="METRIC_PERTURBATION",
            metric_name="Input Invariance Ratio",
            value=pert_score,
            normalized_value=pert_score,
            classification="HIGH_INVARIANCE" if pert_score >= 0.8 else "SENSITIVE_INVARIANCE",
            description="Output preservation under name perturbations, whitespace, and duplication"
        ))

        # 3. Structural Robustness (weight: 0.15)
        # Average topology, cluster, and central persistence
        struct_score = (structure.topology_persistence_ratio + structure.cluster_persistence_ratio + structure.central_participant_persistence) / 3.0
        metrics.append(TrustworthinessMetric(
            metric_id="METRIC_STRUCT_ROBUST",
            metric_name="Structural Robustness Index",
            value=struct_score,
            normalized_value=struct_score,
            classification=structure.robustness_level.value,
            description="Persistence of topology classification and centrality hubs across scenarios"
        ))

        # 4. Signal Robustness (weight: 0.15)
        if signals:
            sig_score = sum(s.scenario_presence_ratio for s in signals) / len(signals)
        else:
            sig_score = 1.0
        metrics.append(TrustworthinessMetric(
            metric_id="METRIC_SIGNAL_ROBUST",
            metric_name="Signal Robustness Index",
            value=sig_score,
            normalized_value=sig_score,
            classification="ROBUST_SIGNAL_SET" if sig_score >= 0.70 else "SENSITIVE_SIGNAL_SET",
            description="Preservation of identified evidence themes across sub-prescription scenarios"
        ))

        # 5. Cross-Layer Consistency (weight: 0.15)
        cl_map = {
            "CONSISTENT_CONVERGENCE": 1.0,
            "MULTI_DIMENSIONAL_ANALYTICAL_DISTRIBUTION": 0.85,
            "PARTIAL_ALIGNMENT": 0.70,
            "ANALYTICAL_DIVERGENCE": 0.30,
            "INSUFFICIENT_COMPARABLE_DATA": 0.50
        }
        cons_score = cl_map.get(consistency.consistency_level.value, 0.50)
        metrics.append(TrustworthinessMetric(
            metric_id="METRIC_CROSS_LAYER",
            metric_name="Cross-Layer Consistency Score",
            value=cons_score,
            normalized_value=cons_score,
            classification=consistency.consistency_level.value,
            description="Convergence and alignment check of central components across layers"
        ))

        # 6. Provenance Completeness (weight: 0.10)
        prov_score = provenance.traceability_coverage
        metrics.append(TrustworthinessMetric(
            metric_id="METRIC_PROVENANCE",
            metric_name="Provenance Traceability Coverage",
            value=prov_score,
            normalized_value=prov_score,
            classification=provenance.completeness_level,
            description="Evidentiary components grounded back to source identifiers"
        ))

        # 7. Explanation Consistency (weight: 0.10)
        exp_score = explanation.consistency_ratio
        metrics.append(TrustworthinessMetric(
            metric_id="METRIC_EXPLANATION",
            metric_name="Explanation Consistency Index",
            value=exp_score,
            normalized_value=exp_score,
            classification=explanation.classification,
            description="Narrative explanation claims matching structured outputs"
        ))

        # Scoring Formula:
        # 0.20 * Rep + 0.15 * Pert + 0.15 * Struct + 0.15 * Sig + 0.15 * Cons + 0.10 * Prov + 0.10 * Exp
        overall = (
            0.20 * rep_score +
            0.15 * pert_score +
            0.15 * struct_score +
            0.15 * sig_score +
            0.15 * cons_score +
            0.10 * prov_score +
            0.10 * exp_score
        )
        overall = round(max(0.0, min(1.0, overall)), 4)

        if overall >= 0.80:
            level = TrustworthinessLevel.HIGH_COMPUTATIONAL_TRUSTWORTHINESS
        elif overall >= 0.60:
            level = TrustworthinessLevel.MODERATE_COMPUTATIONAL_TRUSTWORTHINESS
        elif overall >= 0.40:
            level = TrustworthinessLevel.LIMITED_COMPUTATIONAL_TRUSTWORTHINESS
        else:
            level = TrustworthinessLevel.INSUFFICIENT_EVALUATION_CONTEXT

        return overall, metrics, level
