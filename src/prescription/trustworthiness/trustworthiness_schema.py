from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class ReproducibilityLevel(str, Enum):
    EXACTLY_REPRODUCIBLE = "EXACTLY_REPRODUCIBLE"
    HIGHLY_REPRODUCIBLE = "HIGHLY_REPRODUCIBLE"
    PARTIALLY_REPRODUCIBLE = "PARTIALLY_REPRODUCIBLE"
    NON_REPRODUCIBLE = "NON_REPRODUCIBLE"

class InputPerturbationType(str, Enum):
    MEDICATION_ORDER_PERMUTATION = "MEDICATION_ORDER_PERMUTATION"
    CASE_NORMALIZATION_VARIATION = "CASE_NORMALIZATION_VARIATION"
    WHITESPACE_VARIATION = "WHITESPACE_VARIATION"
    DUPLICATE_INPUT_VARIATION = "DUPLICATE_INPUT_VARIATION"
    PAIR_ORDER_VARIATION = "PAIR_ORDER_VARIATION"
    NORMALIZED_EQUIVALENCE_VARIATION = "NORMALIZED_EQUIVALENCE_VARIATION"

class PerturbationResultType(str, Enum):
    INVARIANT = "INVARIANT"
    MINOR_OUTPUT_VARIATION = "MINOR_OUTPUT_VARIATION"
    MAJOR_OUTPUT_VARIATION = "MAJOR_OUTPUT_VARIATION"
    FAILED_NORMALIZATION = "FAILED_NORMALIZATION"
    NOT_EVALUABLE = "NOT_EVALUABLE"

class StructuralRobustnessLevel(str, Enum):
    HIGHLY_ROBUST_STRUCTURE = "HIGHLY_ROBUST_STRUCTURE"
    ROBUST_STRUCTURE = "ROBUST_STRUCTURE"
    MODERATELY_SENSITIVE_STRUCTURE = "MODERATELY_SENSITIVE_STRUCTURE"
    FRAGILE_STRUCTURE = "FRAGILE_STRUCTURE"
    INSUFFICIENT_STRUCTURAL_CONTEXT = "INSUFFICIENT_STRUCTURAL_CONTEXT"

class SignalRobustnessLevel(str, Enum):
    HIGHLY_ROBUST_SIGNAL = "HIGHLY_ROBUST_SIGNAL"
    ROBUST_SIGNAL = "ROBUST_SIGNAL"
    MODERATELY_SENSITIVE_SIGNAL = "MODERATELY_SENSITIVE_SIGNAL"
    FRAGILE_SIGNAL = "FRAGILE_SIGNAL"
    NON_PERSISTENT_SIGNAL = "NON_PERSISTENT_SIGNAL"

class CrossLayerConsistencyLevel(str, Enum):
    CONSISTENT_CONVERGENCE = "CONSISTENT_CONVERGENCE"
    MULTI_DIMENSIONAL_ANALYTICAL_DISTRIBUTION = "MULTI_DIMENSIONAL_ANALYTICAL_DISTRIBUTION"
    PARTIAL_ALIGNMENT = "PARTIAL_ALIGNMENT"
    ANALYTICAL_DIVERGENCE = "ANALYTICAL_DIVERGENCE"
    INSUFFICIENT_COMPARABLE_DATA = "INSUFFICIENT_COMPARABLE_DATA"

class TrustworthinessLevel(str, Enum):
    HIGH_COMPUTATIONAL_TRUSTWORTHINESS = "HIGH_COMPUTATIONAL_TRUSTWORTHINESS"
    MODERATE_COMPUTATIONAL_TRUSTWORTHINESS = "MODERATE_COMPUTATIONAL_TRUSTWORTHINESS"
    LIMITED_COMPUTATIONAL_TRUSTWORTHINESS = "LIMITED_COMPUTATIONAL_TRUSTWORTHINESS"
    INSUFFICIENT_EVALUATION_CONTEXT = "INSUFFICIENT_EVALUATION_CONTEXT"

@dataclass
class ReproducibilityProfile:
    baseline_signature: str
    repeat_run_signatures: List[str]
    deterministic_match_ratio: float
    classification: ReproducibilityLevel
    mismatched_components: List[str] = field(default_factory=list)

@dataclass
class InputPerturbationResult:
    perturbation_id: str
    perturbation_type: InputPerturbationType
    baseline_signature: str
    perturbed_signature: str
    classification: PerturbationResultType
    invariant_components: List[str] = field(default_factory=list)
    changed_components: List[str] = field(default_factory=list)

@dataclass
class StructuralRobustnessProfile:
    baseline_topology: str
    scenario_topology_distribution: Dict[str, int] = field(default_factory=dict)
    topology_persistence_ratio: float = 1.0
    cluster_persistence_ratio: float = 1.0
    central_participant_persistence: float = 1.0
    robustness_level: StructuralRobustnessLevel = StructuralRobustnessLevel.INSUFFICIENT_STRUCTURAL_CONTEXT

@dataclass
class SignalRobustnessProfile:
    theme_id: str
    baseline_present: bool
    scenario_presence_ratio: float
    reinforcement_stability: float
    classification: SignalRobustnessLevel

@dataclass
class CrossLayerConsistencyProfile:
    structural_dominant_participants: List[str] = field(default_factory=list)
    evidence_dominant_participants: List[str] = field(default_factory=list)
    dependency_dominant_participants: List[str] = field(default_factory=list)
    primary_contributors: List[str] = field(default_factory=list)
    shared_participants: List[str] = field(default_factory=list)
    consistency_level: CrossLayerConsistencyLevel = CrossLayerConsistencyLevel.INSUFFICIENT_COMPARABLE_DATA
    explanation: str = ""

@dataclass
class ProvenanceCompletenessProfile:
    traceability_coverage: float
    average_provenance_depth: float
    orphaned_component_count: int
    cross_layer_traceability: str
    completeness_level: str

@dataclass
class ExplanationConsistencyProfile:
    claims_checked: int
    claims_supported: int
    consistency_ratio: float
    classification: str
    unsupported_claims: List[str] = field(default_factory=list)

@dataclass
class TrustworthinessMetric:
    metric_id: str
    metric_name: str
    value: float
    normalized_value: float
    classification: str
    description: str

@dataclass
class PrescriptionTrustworthinessProfile:
    prescription_id: str
    analysis_id: str
    generated_at: str
    reproducibility_profile: ReproducibilityProfile
    input_perturbation_results: List[InputPerturbationResult]
    structural_robustness: StructuralRobustnessProfile
    signal_robustness_profiles: List[SignalRobustnessProfile]
    cross_layer_consistency: CrossLayerConsistencyProfile
    provenance_completeness: ProvenanceCompletenessProfile
    explanation_consistency: ExplanationConsistencyProfile
    trustworthiness_metrics: List[TrustworthinessMetric]
    overall_trustworthiness_level: TrustworthinessLevel
    executive_summary: str
    guardrails: List[str] = field(default_factory=list)
