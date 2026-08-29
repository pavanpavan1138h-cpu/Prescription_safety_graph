from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional

class ScenarioType(str, Enum):
    BASELINE = "BASELINE"
    SINGLE_DRUG_PERTURBATION = "SINGLE_DRUG_PERTURBATION"
    CLUSTER_CONTEXT = "CLUSTER_CONTEXT"
    DOMINANT_PARTICIPANT_CONTEXT = "DOMINANT_PARTICIPANT_CONTEXT"

class InterpretationStabilityLevel(str, Enum):
    HIGH_INTERPRETATION_STABILITY = "HIGH_INTERPRETATION_STABILITY"
    MODERATE_INTERPRETATION_STABILITY = "MODERATE_INTERPRETATION_STABILITY"
    LOW_INTERPRETATION_STABILITY = "LOW_INTERPRETATION_STABILITY"
    FRAGILE_INTERPRETATION = "FRAGILE_INTERPRETATION"

@dataclass
class ScenarioContext:
    scenario_id: str
    scenario_type: ScenarioType
    baseline_analysis_id: str
    included_drugs: List[str]
    excluded_drugs: List[str]
    included_clusters: List[str] = field(default_factory=list)
    excluded_clusters: List[str] = field(default_factory=list)

@dataclass
class ScenarioProfile:
    scenario_id: str
    scenario_type: ScenarioType
    included_drugs: List[str]
    excluded_drugs: List[str]
    surviving_edges_count: int
    surviving_convergent_edges_count: int
    surviving_themes_count: int
    prescription_status: str
    topology_classification: str
    dominant_theme: Optional[str]
    evidence_concentration: str
    reinforcement_level_distribution: Dict[str, int]

@dataclass
class EvidenceStabilityScore:
    overall_stability_score: float
    pair_preservation_ratio: float
    convergent_preservation_ratio: float
    theme_preservation_ratio: float
    structural_edge_preservation_ratio: float

@dataclass
class SignalPersistence:
    theme_name: str
    persistence_score: float
    persistence_level: str

@dataclass
class ContextSensitivity:
    overall_sensitivity_score: float
    sensitivity_level: str
    status_change_rate: float
    topology_change_rate: float
    theme_change_rate: float

@dataclass
class DrugDependencyImpact:
    drug_id: str
    display_name: str
    dependency_score: float
    dependency_level: str
    edge_loss_ratio: float
    theme_loss_ratio: float
    structural_connectivity_loss_ratio: float

@dataclass
class ContextualStabilityProfile:
    analysis_id: str
    generated_at: str
    scenarios: List[ScenarioProfile]
    evidence_stability: EvidenceStabilityScore
    signal_persistences: List[SignalPersistence]
    context_sensitivity: ContextSensitivity
    drug_dependencies: List[DrugDependencyImpact]
    interpretation_stability: InterpretationStabilityLevel
    summary_narrative: str
    guardrails: List[str] = field(default_factory=lambda: [
        "This analysis computationally changes the graph context for structural and evidential comparison only. It does not recommend discontinuing, removing, substituting, or modifying any medication.",
        "Changes observed between scenarios describe changes in available graph-derived evidence, not changes in actual patient risk or clinical outcome."
    ])
