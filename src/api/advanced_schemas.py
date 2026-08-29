"""
src/api/advanced_schemas.py

Pydantic schemas for Phase 8 Advanced Clinical Intelligence API endpoints.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from src.api.schemas import PrescriptionAnalysisResponse

class ComplexityProfileSchema(BaseModel):
    complexity_category: str
    unique_drugs_count: int
    generated_pairs_count: int
    positive_pairs_count: int
    convergent_pairs_count: int
    participating_drugs_count: int
    max_single_drug_participation_ratio: float
    unresolved_inputs_count: int
    complexity_score: float
    explanation: str

class DrugParticipationProfileSchema(BaseModel):
    internal_drug_id: str
    display_name: str
    participation_category: str
    total_evaluated_pairs: int
    positive_evidence_pairs: int
    convergent_evidence_pairs: int
    ddi_participation_count: int
    event_participation_count: int
    prescription_findings_ratio: float
    relative_evidence_concentration: float
    explanation: str

class AdverseEventConvergenceSchema(BaseModel):
    side_effect_name: str
    side_effect_id: Optional[str]
    participating_pairs_count: int
    participating_pair_keys: List[str]
    participating_drug_ids: List[str]
    participating_drug_names: List[str]
    convergence_category: str
    explanation: str

class EvidencePatternSchema(BaseModel):
    pattern_id: str
    pattern_type: str
    title: str
    supporting_pair_ids: List[str]
    supporting_drug_ids: List[str]
    supporting_drug_names: List[str]
    evidence_counts: Dict[str, int]
    rule_fired: str
    explanation: str
    provenance_edge_ids: List[str]

class ReviewPriorityFindingSchema(BaseModel):
    finding_id: str
    pair_id: str
    drug_a_name: str
    drug_b_name: str
    review_priority: str
    review_score: float
    deterministic_reasons: List[str]
    evidence_status: str
    confidence_score: float
    inference_id: str
    supporting_edge_ids: List[str]

class UncertaintyProfileSchema(BaseModel):
    uncertainty_categories: List[str]
    has_identity_uncertainty: bool
    unresolved_input_names: List[str]
    unmapped_rxnorm_drugs: List[str]
    single_channel_only_pairs: int
    unsupported_pairs_count: int
    uncertainty_level: str
    explanation_narrative: str

class ClinicalContextRequirementSchema(BaseModel):
    context_category: str
    description: str
    why_it_matters: str
    is_available_in_graph: bool
    is_evaluated_by_system: bool

class AdvancedExplanationSchema(BaseModel):
    executive_summary: str
    key_findings_summary: str
    prescription_patterns_summary: str
    uncertainty_summary: str
    scientific_guardrails: List[str]

# --- Phase 8 Structural Analysis Schemas ---
class PrescriptionEvidenceNodeSchema(BaseModel):
    drug_id: str
    display_name: str

class PrescriptionEvidenceEdgeSchema(BaseModel):
    drug_a_id: str
    drug_b_id: str
    evidence_status: str
    confidence_score: float
    priority_tier: str
    structural_weight: float
    edge_strength: float
    canonical_pair_key: str

class PrescriptionEvidenceNetworkSchema(BaseModel):
    nodes: Dict[str, PrescriptionEvidenceNodeSchema]
    edges: Dict[str, PrescriptionEvidenceEdgeSchema]
    canonical_drug_ids: List[str]

class ClusterMetricsSchema(BaseModel):
    cluster_id: str
    drug_ids: List[str]
    edge_count: int
    density: float
    convergent_edge_count: int
    ddi_only_edge_count: int
    combination_event_edge_count: int
    is_isolated: bool

class DrugStructuralProfileSchema(BaseModel):
    drug_id: str
    display_name: str
    evidence_degree: int
    weighted_evidence_degree: float
    degree_centrality: float
    betweenness_centrality: float
    evidence_channel_diversity: int
    convergent_relationship_count: int
    ddi_only_relationship_count: int
    combination_only_relationship_count: int
    cluster_id: str
    cluster_size: int
    centrality_rank: int
    structural_contribution_level: str
    structural_contribution_score: float
    explanation: str

class TopologyClassificationSchema(BaseModel):
    primary_topology: str
    secondary_characteristics: List[str]

class CounterfactualResultSchema(BaseModel):
    drug_id: str
    display_name: str
    original_edge_count: int
    remaining_edge_count: int
    structural_delta: int
    convergent_edges_removed: int
    clusters_before: int
    clusters_after: int
    largest_cluster_before: int
    largest_cluster_after: int
    contribution_level: str
    explanation: str

class NetworkSummarySchema(BaseModel):
    total_prescription_drugs: int
    evidence_connected_drugs: int
    structurally_isolated_drugs: int
    total_possible_pairs: int
    evidence_supported_pairs: int
    network_density: float
    connected_cluster_count: int
    largest_cluster_size: int
    convergent_edge_count: int
    ddi_only_edge_count: int
    combination_event_edge_count: int

class StructuralInterpretationSchema(BaseModel):
    highest_participation_drug: Optional[str]
    highest_participation_degree: int
    network_connectivity_narration: str
    counterfactual_impact_narration: str
    clinical_warning: str

class PrescriptionStructuralAnalysisSchema(BaseModel):
    analysis_id: str
    generated_at: str
    network_summary: NetworkSummarySchema
    topology: TopologyClassificationSchema
    clusters: List[ClusterMetricsSchema]
    drug_structural_profiles: List[DrugStructuralProfileSchema]
    ranked_structural_contributors: List[DrugStructuralProfileSchema]
    counterfactual_results: List[CounterfactualResultSchema]
    original_network: PrescriptionEvidenceNetworkSchema
    structural_interpretation: StructuralInterpretationSchema
    scientific_guardrails: List[str]

# --- Phase 9 Evidence Intelligence Schemas ---
class EvidenceThemeSchema(BaseModel):
    theme_id: str
    theme_name: str
    description: str
    mapped_events: List[str]
    supporting_pairs: List[str]
    participating_drugs: List[str]
    supporting_evidence_count: int
    convergent_pair_count: int
    source_channels: List[str]

class CrossPairSignalGroupSchema(BaseModel):
    group_id: str
    theme_id: str
    supporting_pairs: List[str]
    participating_drugs: List[str]
    supporting_events: List[str]
    channel_distribution: List[str]
    convergent_pair_count: int
    reinforcement_score: float
    reinforcement_level: str

class EvidenceConcentrationProfileSchema(BaseModel):
    concentration_type: str
    edge_coverage_ratio: float
    dominant_drug_id: Optional[str] = None
    dominant_drug_share: float
    dominant_cluster_id: Optional[str] = None
    dominant_cluster_edge_share: float

class DrugAlignmentProfileSchema(BaseModel):
    drug_id: str
    display_name: str
    structural_rank: int
    evidence_participation_rank: int
    theme_participation_rank: int
    convergent_evidence_rank: int
    alignment_score: float
    alignment_level: str

class StructuralEvidenceAlignmentSchema(BaseModel):
    alignment_level: str
    explanation: str
    drug_alignment_profiles: List[DrugAlignmentProfileSchema]

class EvidenceIntelligenceSummarySchema(BaseModel):
    major_theme_count: int
    reinforced_signal_group_count: int
    dominant_theme: Optional[str] = None
    dominant_evidence_concentration: str
    strongest_reinforcement_level: str
    highest_alignment_level: str
    overall_intelligence_pattern: str

class PrescriptionEvidenceIntelligenceProfileSchema(BaseModel):
    analysis_id: str
    generated_at: str
    themes: List[EvidenceThemeSchema]
    signal_groups: List[CrossPairSignalGroupSchema]
    concentration_profile: Optional[EvidenceConcentrationProfileSchema] = None
    structural_evidence_alignment: Optional[StructuralEvidenceAlignmentSchema] = None
    summary: Optional[EvidenceIntelligenceSummarySchema] = None
    narrative: str
    guardrails: List[str]

# --- Phase 10 Contextual Stability Schemas ---
class ScenarioProfileSchema(BaseModel):
    scenario_id: str
    scenario_type: str
    included_drugs: List[str]
    excluded_drugs: List[str]
    surviving_edges_count: int
    surviving_convergent_edges_count: int
    surviving_themes_count: int
    prescription_status: str
    topology_classification: str
    dominant_theme: Optional[str] = None
    evidence_concentration: str
    reinforcement_level_distribution: Dict[str, int]

class EvidenceStabilityScoreSchema(BaseModel):
    overall_stability_score: float
    pair_preservation_ratio: float
    convergent_preservation_ratio: float
    theme_preservation_ratio: float
    structural_edge_preservation_ratio: float

class SignalPersistenceSchema(BaseModel):
    theme_name: str
    persistence_score: float
    persistence_level: str

class ContextSensitivitySchema(BaseModel):
    overall_sensitivity_score: float
    sensitivity_level: str
    status_change_rate: float
    topology_change_rate: float
    theme_change_rate: float

class DrugDependencyImpactSchema(BaseModel):
    drug_id: str
    display_name: str
    dependency_score: float
    dependency_level: str
    edge_loss_ratio: float
    theme_loss_ratio: float
    structural_connectivity_loss_ratio: float

class ContextualStabilityProfileSchema(BaseModel):
    analysis_id: str
    generated_at: str
    scenarios: List[ScenarioProfileSchema]
    evidence_stability: EvidenceStabilityScoreSchema
    signal_persistences: List[SignalPersistenceSchema]
    context_sensitivity: ContextSensitivitySchema
    drug_dependencies: List[DrugDependencyImpactSchema]
    interpretation_stability: str
    summary_narrative: str
    guardrails: List[str]

# --- Phase 11 Prescription Comparative Intelligence Schemas ---
class MajorChangeSchema(BaseModel):
    category: str
    change_type: str
    affected_entities: List[str]
    magnitude: float
    description: str

class MedicationSetComparisonSchema(BaseModel):
    shared_drugs: List[str]
    a_only_drugs: List[str]
    b_only_drugs: List[str]

class PairComparisonSchema(BaseModel):
    canonical_pair_key: str
    drug_a_id: str
    drug_b_id: str
    drug_a_name: str
    drug_b_name: str
    evidence_status_a: str
    evidence_status_b: str
    change_type: str

class EvidenceDeltaSchema(BaseModel):
    pair_comparisons: List[PairComparisonSchema]
    added_pairs_count: int
    removed_pairs_count: int
    reclassified_pairs_count: int
    preserved_pairs_count: int

class DrugRankComparisonSchema(BaseModel):
    drug_id: str
    display_name: str
    rank_a: Optional[int] = None
    rank_b: Optional[int] = None
    rank_delta: Optional[int] = None
    normalized_position_a: Optional[float] = None
    normalized_position_b: Optional[float] = None
    normalized_position_delta: Optional[float] = None

class StructuralDeltaSchema(BaseModel):
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
    dominant_drug_a: Optional[str] = None
    dominant_drug_b: Optional[str] = None
    dominant_drug_changed: bool
    rank_comparisons: List[DrugRankComparisonSchema]
    structural_delta_magnitude: float

class ThemeComparisonSchema(BaseModel):
    theme_name: str
    reinforcement_score_a: float
    reinforcement_score_b: float
    reinforcement_level_a: str
    reinforcement_level_b: str
    supporting_pairs_a: List[str]
    supporting_pairs_b: List[str]
    participating_drugs_a: List[str]
    participating_drugs_b: List[str]
    change_type: str

class SignalDeltaSchema(BaseModel):
    theme_comparisons: List[ThemeComparisonSchema]
    concentration_type_a: str
    concentration_type_b: str
    concentration_changed: bool
    alignment_level_a: str
    alignment_level_b: str
    alignment_changed: bool

class StabilityDeltaSchema(BaseModel):
    stability_score_a: float
    stability_score_b: float
    stability_score_delta: float
    sensitivity_score_a: float
    sensitivity_score_b: float
    sensitivity_score_delta: float
    interpretation_stability_a: str
    interpretation_stability_b: str
    stability_change_type: str

class ComparisonMetricSchema(BaseModel):
    metric_name: str
    value_a: float
    value_b: float
    raw_difference: float
    normalized_difference: float

class ComparisonSummarySchema(BaseModel):
    total_evidence_changes: int
    total_structural_changes: int
    total_signal_changes: int
    stability_shift: str
    global_delta_interpretation: str

class PrescriptionComparativeIntelligenceProfileSchema(BaseModel):
    comparison_id: str
    analysis_id_a: str
    analysis_id_b: str
    medication_set_comparison: MedicationSetComparisonSchema
    evidence_delta: EvidenceDeltaSchema
    structural_delta: StructuralDeltaSchema
    signal_delta: SignalDeltaSchema
    stability_delta: StabilityDeltaSchema
    comparison_metrics: List[ComparisonMetricSchema]
    major_changes: List[MajorChangeSchema]
    preserved_characteristics: List[str]
    summary: ComparisonSummarySchema
    narrative: str
    guardrails: List[str]

# --- Phase 11 Explainability Schemas ---
class ExplanationNodeSchema(BaseModel):
    node_id: str
    node_type: str
    label: str
    description: str
    phase_origin: str
    source_reference: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExplanationEdgeSchema(BaseModel):
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    contribution_weight: float
    description: str

class ExplanationGraphSchema(BaseModel):
    nodes: List[ExplanationNodeSchema]
    edges: List[ExplanationEdgeSchema]
    root_node_ids: List[str]
    leaf_node_ids: List[str]

class SourceProvenanceRecordSchema(BaseModel):
    source_id: str
    dataset_name: str
    record_type: str
    external_identifier: Optional[str]
    description: str
    is_available: bool

class ContributionProfileSchema(BaseModel):
    entity_id: str
    entity_label: str
    entity_type: str
    direct_decision_contribution: float
    evidence_coverage: float
    cross_layer_participation: float
    dependency_impact: float
    overall_contribution_score: float
    contribution_level: str
    participating_phases: List[str]
    explanation: str

class DependencyNodeSchema(BaseModel):
    entity_id: str
    entity_label: str
    entity_type: str
    depends_on_ids: List[str]
    dependency_weight: float
    critical_dependency: bool

class DecisionDependencyMapSchema(BaseModel):
    target_interpretation_id: str
    dependencies: List[DependencyNodeSchema]
    critical_path_entities: List[str]
    acyclic_verified: bool

class TraceabilityProfileSchema(BaseModel):
    total_components_evaluated: int
    traceable_components_count: int
    traceability_coverage_score: float
    average_provenance_depth: float
    max_provenance_depth: int
    orphaned_components_count: int
    orphaned_component_ids: List[str]
    cross_layer_traceability: str

class StructuredExplanationClaimSchema(BaseModel):
    claim_id: str
    claim_type: str
    claim_text: str
    referenced_entity_ids: List[str]
    is_supported: bool
    supporting_evidence_ids: List[str]

class PrescriptionExplainabilityProfileSchema(BaseModel):
    prescription_id: str
    analysis_id: str
    generated_at: str
    explanation_graph: ExplanationGraphSchema
    contribution_profiles: List[ContributionProfileSchema]
    dependency_map: DecisionDependencyMapSchema
    traceability_profile: TraceabilityProfileSchema
    provenance_records: List[SourceProvenanceRecordSchema]
    structured_claims: List[StructuredExplanationClaimSchema]
    narrative: str
    guardrails: List[str]

# --- Phase 12 Trustworthiness Schemas ---
class ReproducibilityProfileSchema(BaseModel):
    baseline_signature: str
    repeat_run_signatures: List[str]
    deterministic_match_ratio: float
    classification: str
    mismatched_components: List[str]

class InputPerturbationResultSchema(BaseModel):
    perturbation_id: str
    perturbation_type: str
    baseline_signature: str
    perturbed_signature: str
    invariant_components: List[str]
    changed_components: List[str]
    classification: str

class StructuralRobustnessProfileSchema(BaseModel):
    baseline_topology: str
    scenario_topology_distribution: Dict[str, int]
    topology_persistence_ratio: float
    cluster_persistence_ratio: float
    central_participant_persistence: float
    robustness_level: str

class SignalRobustnessProfileSchema(BaseModel):
    theme_id: str
    baseline_present: bool
    scenario_presence_ratio: float
    reinforcement_stability: float
    classification: str

class CrossLayerConsistencyProfileSchema(BaseModel):
    structural_dominant_participants: List[str]
    evidence_dominant_participants: List[str]
    dependency_dominant_participants: List[str]
    primary_contributors: List[str]
    shared_participants: List[str]
    consistency_level: str
    explanation: str

class ProvenanceCompletenessProfileSchema(BaseModel):
    traceability_coverage: float
    average_provenance_depth: float
    orphaned_component_count: int
    cross_layer_traceability: str
    completeness_level: str

class ExplanationConsistencyProfileSchema(BaseModel):
    claims_checked: int
    claims_supported: int
    unsupported_claims: List[str]
    consistency_ratio: float
    classification: str

class TrustworthinessMetricSchema(BaseModel):
    metric_id: str
    metric_name: str
    value: float
    normalized_value: float
    classification: str
    description: str

class PrescriptionTrustworthinessProfileSchema(BaseModel):
    prescription_id: str
    analysis_id: str
    generated_at: str
    reproducibility_profile: ReproducibilityProfileSchema
    input_perturbation_results: List[InputPerturbationResultSchema]
    structural_robustness: StructuralRobustnessProfileSchema
    signal_robustness_profiles: List[SignalRobustnessProfileSchema]
    cross_layer_consistency: CrossLayerConsistencyProfileSchema
    provenance_completeness: ProvenanceCompletenessProfileSchema
    explanation_consistency: ExplanationConsistencyProfileSchema
    trustworthiness_metrics: List[TrustworthinessMetricSchema]
    overall_trustworthiness_level: str
    executive_summary: str
    guardrails: List[str]

# --- Phase 13 Longitudinal Evolution Schemas ---
class PrescriptionSnapshotReferenceSchema(BaseModel):
    analysis_id: str
    prescription_id: str
    snapshot_timestamp: str
    sequence_index: int
    position_type: str
    medications: List[str]

class PersistenceProfileSchema(BaseModel):
    entity_id: str
    entity_type: str
    presence_ratio: float
    longest_consecutive_run: int
    first_seen_index: int
    last_seen_index: int
    persistence_level: str

class EmergenceEventSchema(BaseModel):
    entity_id: str
    entity_type: str
    emergence_index: int
    previously_absent_count: int
    post_emergence_persistence: float
    classification: str

class DisappearanceEventSchema(BaseModel):
    entity_id: str
    entity_type: str
    disappearance_index: int
    previously_present_count: int
    post_disappearance_absence_ratio: float
    classification: str

class LongitudinalChangePointSchema(BaseModel):
    from_snapshot_index: int
    to_snapshot_index: int
    structural_change: float
    signal_change: float
    stability_change: float
    trustworthiness_change: float
    medication_set_change: float
    aggregate_change_score: float
    change_level: str
    contributing_dimensions: List[str]

class StructuralEvolutionProfileSchema(BaseModel):
    topology_sequence: List[str]
    density_sequence: List[float]
    central_participant_sequence: List[List[str]]
    cluster_count_sequence: List[int]
    topology_transition_count: int
    structural_change_points: List[int]
    classification: str

class SignalEvolutionProfileSchema(BaseModel):
    theme_id: str
    presence_sequence: List[bool]
    reinforcement_sequence: List[float]
    rank_sequence: List[int]
    persistence_ratio: float
    emergence_events: List[EmergenceEventSchema]
    disappearance_events: List[DisappearanceEventSchema]
    classification: str

class StabilityEvolutionProfileSchema(BaseModel):
    stability_sequence: List[str]
    sensitivity_sequence: List[float]
    transition_count: int
    classification: str

class TrustworthinessEvolutionProfileSchema(BaseModel):
    score_sequence: List[float]
    level_sequence: List[str]
    score_delta_sequence: List[float]
    mean_score: float
    score_volatility: float
    classification: str

class CrossLayerEvolutionProfileSchema(BaseModel):
    structural_persistence: float
    signal_persistence: float
    stability_persistence: float
    provenance_persistence: float
    trustworthiness_persistence: float
    cross_layer_transition_alignment: List[str]
    classification: str
    explanation: str

class PrescriptionLongitudinalProfileSchema(BaseModel):
    timeline: List[PrescriptionSnapshotReferenceSchema]
    persistence_profiles: List[PersistenceProfileSchema]
    emergence_events: List[EmergenceEventSchema]
    disappearance_events: List[DisappearanceEventSchema]
    change_points: List[LongitudinalChangePointSchema]
    structural_evolution: StructuralEvolutionProfileSchema
    signal_evolution: List[SignalEvolutionProfileSchema]
    stability_evolution: StabilityEvolutionProfileSchema
    trustworthiness_evolution: TrustworthinessEvolutionProfileSchema
    cross_layer_evolution: CrossLayerEvolutionProfileSchema
    overall_evolution_level: str
    longitudinal_summary: str
    guardrails: List[str]

# Input payload schema for triggering longitudinal history resolution
class LongitudinalAnalysisRequest(BaseModel):
    analysis_ids: List[str]

class AdvancedPrescriptionAnalysisResponse(BaseModel):
    prescription_report: PrescriptionAnalysisResponse
    complexity_profile: ComplexityProfileSchema
    drug_participation_profiles: List[DrugParticipationProfileSchema]
    event_convergence_items: List[AdverseEventConvergenceSchema]
    evidence_patterns: List[EvidencePatternSchema]
    review_priorities: List[ReviewPriorityFindingSchema]
    uncertainty_profile: UncertaintyProfileSchema
    clinical_context_requirements: List[ClinicalContextRequirementSchema]
    advanced_explanation: AdvancedExplanationSchema
    scientific_limitations: List[str]
    structural_analysis: Optional[PrescriptionStructuralAnalysisSchema] = None
    evidence_intelligence: Optional[PrescriptionEvidenceIntelligenceProfileSchema] = None
    contextual_stability: Optional[ContextualStabilityProfileSchema] = None
    explainability: Optional[PrescriptionExplainabilityProfileSchema] = None
    trustworthiness: Optional[PrescriptionTrustworthinessProfileSchema] = None

