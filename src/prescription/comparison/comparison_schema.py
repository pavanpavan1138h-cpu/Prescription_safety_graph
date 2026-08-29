from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional

class ComparisonChangeType(str, Enum):
    PRESERVED = "PRESERVED"
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    INCREASED = "INCREASED"
    DECREASED = "DECREASED"
    RECLASSIFIED = "RECLASSIFIED"
    RESTRUCTURED = "RESTRUCTURED"
    RANK_SHIFTED = "RANK_SHIFTED"
    UNCHANGED = "UNCHANGED"

class EvidenceChangeType(str, Enum):
    PRESERVED_EVIDENCE = "PRESERVED_EVIDENCE"
    NEW_EVIDENCE = "NEW_EVIDENCE"
    REMOVED_EVIDENCE = "REMOVED_EVIDENCE"
    EVIDENCE_RECLASSIFIED = "EVIDENCE_RECLASSIFIED"

class StructuralChangeType(str, Enum):
    TOPOLOGY_CHANGED = "TOPOLOGY_CHANGED"
    CLUSTER_EXPANDED = "CLUSTER_EXPANDED"
    CLUSTER_CONTRACTED = "CLUSTER_CONTRACTED"
    DENSITY_INCREASED = "DENSITY_INCREASED"
    DENSITY_DECREASED = "DENSITY_DECREASED"
    CENTRAL_PARTICIPANT_SHIFTED = "CENTRAL_PARTICIPANT_SHIFTED"
    STRUCTURAL_RANK_SHIFTED = "STRUCTURAL_RANK_SHIFTED"

class SignalChangeType(str, Enum):
    THEME_PRESERVED = "THEME_PRESERVED"
    THEME_EMERGED = "THEME_EMERGED"
    THEME_DISAPPEARED = "THEME_DISAPPEARED"
    REINFORCEMENT_INCREASED = "REINFORCEMENT_INCREASED"
    REINFORCEMENT_DECREASED = "REINFORCEMENT_DECREASED"
    CONCENTRATION_SHIFTED = "CONCENTRATION_SHIFTED"
    ALIGNMENT_CHANGED = "ALIGNMENT_CHANGED"

class StabilityChangeType(str, Enum):
    STABILITY_INCREASED = "STABILITY_INCREASED"
    STABILITY_DECREASED = "STABILITY_DECREASED"
    CONTEXT_DEPENDENCY_CHANGED = "CONTEXT_DEPENDENCY_CHANGED"
    SIGNAL_PERSISTENCE_CHANGED = "SIGNAL_PERSISTENCE_CHANGED"
    UNCHANGED = "UNCHANGED"

@dataclass
class MajorChange:
    category: str  # EVIDENCE, STRUCTURE, SIGNAL, STABILITY
    change_type: str
    affected_entities: List[str]
    magnitude: float  # 0.0 to 1.0
    description: str

@dataclass
class MedicationSetComparison:
    shared_drugs: List[str]
    a_only_drugs: List[str]
    b_only_drugs: List[str]

@dataclass
class PairComparison:
    canonical_pair_key: str
    drug_a_id: str
    drug_b_id: str
    drug_a_name: str
    drug_b_name: str
    evidence_status_a: str
    evidence_status_b: str
    change_type: EvidenceChangeType

@dataclass
class EvidenceDelta:
    pair_comparisons: List[PairComparison]
    added_pairs_count: int
    removed_pairs_count: int
    reclassified_pairs_count: int
    preserved_pairs_count: int

@dataclass
class DrugRankComparison:
    drug_id: str
    display_name: str
    rank_a: Optional[int]
    rank_b: Optional[int]
    rank_delta: Optional[int]
    normalized_position_a: Optional[float]
    normalized_position_b: Optional[float]
    normalized_position_delta: Optional[float]

@dataclass
class StructuralDelta:
    node_count_a: int
    node_count_b: int
    node_count_delta: int
    edge_count_a: int
    edge_count_b: int
    edge_count_delta: int
    density_a: float
    density_b: float
    density_delta: float
    cluster_count_a: int
    cluster_count_b: int
    cluster_count_delta: int
    topology_a: str
    topology_b: str
    topology_changed: bool
    dominant_drug_a: Optional[str]
    dominant_drug_b: Optional[str]
    dominant_drug_changed: bool
    rank_comparisons: List[DrugRankComparison]
    structural_delta_magnitude: float

@dataclass
class ThemeComparison:
    theme_name: str
    reinforcement_score_a: float
    reinforcement_score_b: float
    reinforcement_level_a: str
    reinforcement_level_b: str
    supporting_pairs_a: List[str]
    supporting_pairs_b: List[str]
    participating_drugs_a: List[str]
    participating_drugs_b: List[str]
    change_type: SignalChangeType

@dataclass
class SignalDelta:
    theme_comparisons: List[ThemeComparison]
    concentration_type_a: str
    concentration_type_b: str
    concentration_changed: bool
    alignment_level_a: str
    alignment_level_b: str
    alignment_changed: bool

@dataclass
class StabilityDelta:
    stability_score_a: float
    stability_score_b: float
    stability_score_delta: float
    sensitivity_score_a: float
    sensitivity_score_b: float
    sensitivity_score_delta: float
    interpretation_stability_a: str
    interpretation_stability_b: str
    stability_change_type: StabilityChangeType

@dataclass
class ComparisonMetric:
    metric_name: str
    value_a: float
    value_b: float
    raw_difference: float
    normalized_difference: float

@dataclass
class ComparisonSummary:
    total_evidence_changes: int
    total_structural_changes: int
    total_signal_changes: int
    stability_shift: str
    global_delta_interpretation: str

@dataclass
class PrescriptionComparativeIntelligenceProfile:
    comparison_id: str
    analysis_id_a: str
    analysis_id_b: str
    medication_set_comparison: MedicationSetComparison
    evidence_delta: EvidenceDelta
    structural_delta: StructuralDelta
    signal_delta: SignalDelta
    stability_delta: StabilityDelta
    comparison_metrics: List[ComparisonMetric]
    major_changes: List[MajorChange]
    preserved_characteristics: List[str]
    summary: ComparisonSummary
    narrative: str
    guardrails: List[str] = field(default_factory=lambda: [
        "This comparison describes differences between computational evidence states and does not determine whether one prescription is safer, better, or clinically preferable than another. It does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
    ])
