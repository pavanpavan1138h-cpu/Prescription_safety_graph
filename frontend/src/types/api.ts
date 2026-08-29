export interface ResolvedDrugItem {
  input: string;
  status: string;
  internal_drug_id: string | null;
  canonical_name: string | null;
  identifier_type_matched: string | null;
  rxcui: string | null;
}

export interface DrugResolveResponse {
  input_count: number;
  unique_resolved_drugs: number;
  duplicates_collapsed: number;
  unresolved_count: number;
  results: ResolvedDrugItem[];
}

export interface SystemInfoResponse {
  api_version: string;
  graph_nodes: number;
  graph_edges: number;
  node_breakdown: Record<string, number>;
  edge_breakdown: Record<string, number>;
  supported_identifier_types: string[];
}

export interface PrioritizedFinding {
  finding_id: string;
  pair_id: string;
  priority: string;
  drug_a: { drug_id: string; name: string };
  drug_b: { drug_id: string; name: string };
  evidence_status: string;
  confidence: { level: string; score: number };
  summary_narrative: string;
  evidence_channels: {
    drugbank_ddi: boolean;
    twosides_combination_events: boolean;
  };
  ddi_record_count: number;
  adverse_event_count: number;
  inference_id: string;
  supporting_edge_ids: string[];
}

export interface PairResultRow {
  pair_id: string;
  drug_a_name: string;
  drug_b_name: string;
  evidence_status: string;
  evidence_priority: string;
  confidence_level: string;
  confidence_score: number;
  ddi_evidence_present: boolean;
  combination_event_evidence_present: boolean;
}

export interface DrugParticipationRow {
  drug_id: string;
  drug_name: string;
  total_pairs: number;
  pairs_with_evidence: number;
  convergent_evidence_pairs: number;
  highest_priority: string;
}

export interface UnresolvedItem {
  input_value: string;
  resolution_status: string;
  reason: string;
}

export interface PrescriptionAnalysisResponse {
  metadata: {
    analysis_id: string;
    api_version: string;
    generated_at: string;
    graph_version: string;
    reasoning_engine_version: string;
  };
  input_summary: {
    submitted_medication_count: number;
    submitted_medications: string[];
  };
  resolution_summary: {
    resolved_count: number;
    unique_canonical_drug_count: number;
    duplicate_count: number;
    unresolved_count: number;
    resolved_drugs: Array<{
      canonical_drug_id: string;
      canonical_name: string;
      rxcui: string | null;
      input_values: string[];
    }>;
  };
  prescription_summary: {
    evidence_status: string;
    highest_evidence_priority: string;
    total_unique_drugs: number;
    total_pairs_analyzed: number;
    positive_evidence_pairs: number;
    convergent_evidence_pairs: number;
    ddi_only_pairs: number;
    combination_event_only_pairs: number;
    no_direct_evidence_pairs: number;
  };
  prioritized_findings: PrioritizedFinding[];
  pair_results: PairResultRow[];
  drug_participation: DrugParticipationRow[];
  unresolved_items: UnresolvedItem[];
  limitations: string[];
  provenance: {
    evidence_sources: string[];
    supporting_edge_count: number;
    top_supporting_edge_ids: string[];
  };
  clinical_narrative_report: string;
}

export interface PairDetailResponse {
  pair_id: string;
  drug_a: {
    internal_drug_id: string;
    display_name: string;
    rxcui: string | null;
    rxnorm_name: string | null;
  };
  drug_b: {
    internal_drug_id: string;
    display_name: string;
    rxcui: string | null;
    rxnorm_name: string | null;
  };
  inference: {
    inference_id: string;
    evidence_status: string;
    evidence_priority: string;
    confidence_level: string;
    confidence_score: number;
    rule_fired: string;
  };
  direct_ddi_evidence: Array<{
    edge_id: string;
    direction: string;
    source_dataset: string;
    source_record_id: string;
    interaction_description: string;
  }>;
  combination_adverse_events: {
    total_event_count: number;
    observed_events: Array<{
      edge_id: string;
      side_effect_id: string;
      side_effect_name: string;
      source_dataset: string;
    }>;
  };
  provenance_trace: {
    graph_paths: string[];
    confidence_reasons: string[];
  };
}

// --- Phase 8 Structural Analysis Types ---
export interface PrescriptionEvidenceNode {
  drug_id: string;
  display_name: string;
}

export interface PrescriptionEvidenceEdge {
  drug_a_id: string;
  drug_b_id: string;
  evidence_status: string;
  confidence_score: number;
  priority_tier: string;
  structural_weight: number;
  edge_strength: number;
  canonical_pair_key: string;
}

export interface PrescriptionEvidenceNetwork {
  nodes: Record<string, PrescriptionEvidenceNode>;
  edges: Record<string, PrescriptionEvidenceEdge>;
  canonical_drug_ids: string[];
}

export interface ClusterMetrics {
  cluster_id: string;
  drug_ids: string[];
  edge_count: number;
  density: number;
  convergent_edge_count: number;
  ddi_only_edge_count: number;
  combination_event_edge_count: number;
  is_isolated: boolean;
}

export interface DrugStructuralProfile {
  drug_id: string;
  display_name: string;
  evidence_degree: number;
  weighted_evidence_degree: number;
  degree_centrality: number;
  betweenness_centrality: number;
  evidence_channel_diversity: number;
  convergent_relationship_count: number;
  ddi_only_relationship_count: number;
  combination_only_relationship_count: number;
  cluster_id: string;
  cluster_size: number;
  centrality_rank: number;
  structural_contribution_level: string;
  structural_contribution_score: number;
  explanation: string;
}

export interface TopologyClassification {
  primary_topology: string;
  secondary_characteristics: string[];
}

export interface CounterfactualResult {
  drug_id: string;
  display_name: string;
  original_edge_count: number;
  remaining_edge_count: number;
  structural_delta: number;
  convergent_edges_removed: number;
  clusters_before: number;
  clusters_after: number;
  largest_cluster_before: number;
  largest_cluster_after: number;
  contribution_level: string;
  explanation: string;
}

export interface NetworkSummary {
  total_prescription_drugs: number;
  evidence_connected_drugs: number;
  structurally_isolated_drugs: number;
  total_possible_pairs: number;
  evidence_supported_pairs: number;
  network_density: number;
  connected_cluster_count: number;
  largest_cluster_size: number;
  convergent_edge_count: number;
  ddi_only_edge_count: number;
  combination_event_edge_count: number;
}

export interface StructuralInterpretation {
  highest_participation_drug: string | null;
  highest_participation_degree: number;
  network_connectivity_narration: string;
  counterfactual_impact_narration: string;
  clinical_warning: string;
}

export interface PrescriptionStructuralAnalysis {
  analysis_id: string;
  generated_at: string;
  network_summary: NetworkSummary;
  topology: TopologyClassification;
  clusters: ClusterMetrics[];
  drug_structural_profiles: DrugStructuralProfile[];
  ranked_structural_contributors: DrugStructuralProfile[];
  counterfactual_results: CounterfactualResult[];
  original_network: PrescriptionEvidenceNetwork;
  structural_interpretation: StructuralInterpretation;
  scientific_guardrails: string[];
}

// --- Phase 9 Evidence Intelligence Types ---
export interface EvidenceTheme {
  theme_id: string;
  theme_name: string;
  description: string;
  mapped_events: string[];
  supporting_pairs: string[];
  participating_drugs: string[];
  supporting_evidence_count: number;
  convergent_pair_count: number;
  source_channels: string[];
}

export interface CrossPairSignalGroup {
  group_id: string;
  theme_id: string;
  supporting_pairs: string[];
  participating_drugs: string[];
  supporting_events: string[];
  channel_distribution: string[];
  convergent_pair_count: number;
  reinforcement_score: number;
  reinforcement_level: string;
}

export interface EvidenceConcentrationProfile {
  concentration_type: string;
  edge_coverage_ratio: number;
  dominant_drug_id: string | null;
  dominant_drug_share: number;
  dominant_cluster_id: string | null;
  dominant_cluster_edge_share: number;
}

export interface DrugAlignmentProfile {
  drug_id: string;
  display_name: string;
  structural_rank: number;
  evidence_participation_rank: number;
  theme_participation_rank: number;
  convergent_evidence_rank: number;
  alignment_score: number;
  alignment_level: string;
}

export interface StructuralEvidenceAlignment {
  alignment_level: string;
  explanation: string;
  drug_alignment_profiles: DrugAlignmentProfile[];
}

export interface EvidenceIntelligenceSummary {
  major_theme_count: number;
  reinforced_signal_group_count: number;
  dominant_theme: string | null;
  dominant_evidence_concentration: string;
  strongest_reinforcement_level: string;
  highest_alignment_level: string;
  overall_intelligence_pattern: string;
}

export interface PrescriptionEvidenceIntelligenceProfile {
  analysis_id: string;
  generated_at: string;
  themes: EvidenceTheme[];
  signal_groups: CrossPairSignalGroup[];
  concentration_profile: EvidenceConcentrationProfile | null;
  structural_evidence_alignment: StructuralEvidenceAlignment | null;
  summary: EvidenceIntelligenceSummary | null;
  narrative: string;
  guardrails: string[];
}

// --- Phase 10 Contextual Stability Types ---
export interface ScenarioProfile {
  scenario_id: string;
  scenario_type: string;
  included_drugs: string[];
  excluded_drugs: string[];
  surviving_edges_count: number;
  surviving_convergent_edges_count: number;
  surviving_themes_count: number;
  prescription_status: string;
  topology_classification: string;
  dominant_theme: string | null;
  evidence_concentration: string;
  reinforcement_level_distribution: Record<string, number>;
}

export interface EvidenceStabilityScore {
  overall_stability_score: number;
  pair_preservation_ratio: number;
  convergent_preservation_ratio: number;
  theme_preservation_ratio: number;
  structural_edge_preservation_ratio: number;
}

export interface SignalPersistence {
  theme_name: string;
  persistence_score: number;
  persistence_level: string;
}

export interface ContextSensitivity {
  overall_sensitivity_score: number;
  sensitivity_level: string;
  status_change_rate: number;
  topology_change_rate: number;
  theme_change_rate: number;
}

export interface DrugDependencyImpact {
  drug_id: string;
  display_name: string;
  dependency_score: number;
  dependency_level: string;
  edge_loss_ratio: number;
  theme_loss_ratio: number;
  structural_connectivity_loss_ratio: number;
}

export interface ContextualStabilityProfile {
  analysis_id: string;
  generated_at: string;
  scenarios: ScenarioProfile[];
  evidence_stability: EvidenceStabilityScore;
  signal_persistences: SignalPersistence[];
  context_sensitivity: ContextSensitivity;
  drug_dependencies: DrugDependencyImpact[];
  interpretation_stability: string;
  summary_narrative: string;
  guardrails: string[];
}

// --- Phase 11 Prescription Comparative Intelligence Types ---
export interface MajorChange {
  category: string;
  change_type: string;
  affected_entities: string[];
  magnitude: number;
  description: string;
}

export interface MedicationSetComparison {
  shared_drugs: string[];
  a_only_drugs: string[];
  b_only_drugs: string[];
}

export interface PairComparison {
  canonical_pair_key: string;
  drug_a_id: string;
  drug_b_id: string;
  drug_a_name: string;
  drug_b_name: string;
  evidence_status_a: string;
  evidence_status_b: string;
  change_type: string;
}

export interface EvidenceDelta {
  pair_comparisons: PairComparison[];
  added_pairs_count: number;
  removed_pairs_count: number;
  reclassified_pairs_count: number;
  preserved_pairs_count: number;
}

export interface DrugRankComparison {
  drug_id: string;
  display_name: string;
  rank_a: number | null;
  rank_b: number | null;
  rank_delta: number | null;
  normalized_position_a: number | null;
  normalized_position_b: number | null;
  normalized_position_delta: number | null;
}

export interface StructuralDelta {
  node_count_a: number;
  node_count_b: number;
  node_count_delta: number;
  edge_count_a: number;
  edge_count_b: number;
  edge_count_delta: number;
  density_a: number;
  density_b: number;
  density_delta: number;
  cluster_count_a: number;
  cluster_count_b: number;
  cluster_count_delta: number;
  topology_a: string;
  topology_b: string;
  topology_changed: boolean;
  dominant_drug_a: string | null;
  dominant_drug_b: string | null;
  dominant_drug_changed: boolean;
  rank_comparisons: DrugRankComparison[];
  structural_delta_magnitude: number;
}

export interface ThemeComparison {
  theme_name: string;
  reinforcement_score_a: number;
  reinforcement_score_b: number;
  reinforcement_level_a: string;
  reinforcement_level_b: string;
  supporting_pairs_a: string[];
  supporting_pairs_b: string[];
  participating_drugs_a: string[];
  participating_drugs_b: string[];
  change_type: string;
}

export interface SignalDelta {
  theme_comparisons: ThemeComparison[];
  concentration_type_a: string;
  concentration_type_b: string;
  concentration_changed: boolean;
  alignment_level_a: string;
  alignment_level_b: string;
  alignment_changed: boolean;
}

export interface StabilityDelta {
  stability_score_a: number;
  stability_score_b: number;
  stability_score_delta: number;
  sensitivity_score_a: number;
  sensitivity_score_b: number;
  sensitivity_score_delta: number;
  interpretation_stability_a: string;
  interpretation_stability_b: string;
  stability_change_type: string;
}

export interface ComparisonMetric {
  metric_name: string;
  value_a: number;
  value_b: number;
  raw_difference: number;
  normalized_difference: number;
}

export interface ComparisonSummary {
  total_evidence_changes: number;
  total_structural_changes: number;
  total_signal_changes: number;
  stability_shift: string;
  global_delta_interpretation: string;
}

export interface PrescriptionComparativeIntelligenceProfile {
  comparison_id: string;
  analysis_id_a: string;
  analysis_id_b: string;
  medication_set_comparison: MedicationSetComparison;
  evidence_delta: EvidenceDelta;
  structural_delta: StructuralDelta;
  signal_delta: SignalDelta;
  stability_delta: StabilityDelta;
  comparison_metrics: ComparisonMetric[];
  major_changes: MajorChange[];
  preserved_characteristics: string[];
  summary: ComparisonSummary;
  narrative: string;
  guardrails: string[];
}

// --- Phase 11 Explainability Types ---
export interface ExplanationNode {
  node_id: string;
  node_type: string;
  label: string;
  description: string;
  phase_origin: string;
  source_reference?: string | null;
  metadata?: Record<string, any>;
}

export interface ExplanationEdge {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: string;
  contribution_weight: number;
  description: string;
}

export interface ExplanationGraph {
  nodes: ExplanationNode[];
  edges: ExplanationEdge[];
  root_node_ids: string[];
  leaf_node_ids: string[];
}

export interface SourceProvenanceRecord {
  source_id: string;
  dataset_name: string;
  record_type: string;
  external_identifier?: string | null;
  description: string;
  is_available: boolean;
}

export interface ContributionProfile {
  entity_id: string;
  entity_label: string;
  entity_type: string;
  direct_decision_contribution: number;
  evidence_coverage: number;
  cross_layer_participation: number;
  dependency_impact: number;
  overall_contribution_score: number;
  contribution_level: string;
  participating_phases: string[];
  explanation: string;
}

export interface DependencyNode {
  entity_id: string;
  entity_label: string;
  entity_type: string;
  depends_on_ids: string[];
  dependency_weight: number;
  critical_dependency: boolean;
}

export interface DecisionDependencyMap {
  target_interpretation_id: string;
  dependencies: DependencyNode[];
  critical_path_entities: string[];
  acyclic_verified: boolean;
}

export interface TraceabilityProfile {
  total_components_evaluated: number;
  traceable_components_count: number;
  traceability_coverage_score: number;
  average_provenance_depth: number;
  max_provenance_depth: number;
  orphaned_components_count: number;
  orphaned_component_ids: string[];
  cross_layer_traceability: string;
}

export interface StructuredExplanationClaim {
  claim_id: string;
  claim_type: string;
  claim_text: string;
  referenced_entity_ids: string[];
  is_supported: boolean;
  supporting_evidence_ids: string[];
}

export interface PrescriptionExplainabilityProfile {
  prescription_id: string;
  analysis_id: string;
  generated_at: string;
  explanation_graph: ExplanationGraph;
  contribution_profiles: ContributionProfile[];
  dependency_map: DecisionDependencyMap;
  traceability_profile: TraceabilityProfile;
  provenance_records: SourceProvenanceRecord[];
  structured_claims: StructuredExplanationClaim[];
  narrative: string;
  guardrails: string[];
}

// --- Phase 12 Trustworthiness Types ---
export interface ReproducibilityProfile {
  baseline_signature: string;
  repeat_run_signatures: string[];
  deterministic_match_ratio: number;
  classification: string;
  mismatched_components: string[];
}

export interface InputPerturbationResult {
  perturbation_id: string;
  perturbation_type: string;
  baseline_signature: string;
  perturbed_signature: string;
  invariant_components: string[];
  changed_components: string[];
  classification: string;
}

export interface StructuralRobustnessProfile {
  baseline_topology: string;
  scenario_topology_distribution: Record<string, number>;
  topology_persistence_ratio: number;
  cluster_persistence_ratio: number;
  central_participant_persistence: number;
  robustness_level: string;
}

export interface SignalRobustnessProfile {
  theme_id: string;
  baseline_present: boolean;
  scenario_presence_ratio: number;
  reinforcement_stability: number;
  classification: string;
}

export interface CrossLayerConsistencyProfile {
  structural_dominant_participants: string[];
  evidence_dominant_participants: string[];
  dependency_dominant_participants: string[];
  primary_contributors: string[];
  shared_participants: string[];
  consistency_level: string;
  explanation: string;
}

export interface ProvenanceCompletenessProfile {
  traceability_coverage: number;
  average_provenance_depth: number;
  orphaned_component_count: number;
  cross_layer_traceability: string;
  completeness_level: string;
}

export interface ExplanationConsistencyProfile {
  claims_checked: number;
  claims_supported: number;
  unsupported_claims: string[];
  consistency_ratio: number;
  classification: string;
}

export interface TrustworthinessMetric {
  metric_id: string;
  metric_name: string;
  value: number;
  normalized_value: number;
  classification: string;
  description: string;
}

export interface PrescriptionTrustworthinessProfile {
  prescription_id: string;
  analysis_id: string;
  generated_at: string;
  reproducibility_profile: ReproducibilityProfile;
  input_perturbation_results: InputPerturbationResult[];
  structural_robustness: StructuralRobustnessProfile;
  signal_robustness_profiles: SignalRobustnessProfile[];
  cross_layer_consistency: CrossLayerConsistencyProfile;
  provenance_completeness: ProvenanceCompletenessProfile;
  explanation_consistency: ExplanationConsistencyProfile;
  trustworthiness_metrics: TrustworthinessMetric[];
  overall_trustworthiness_level: string;
  executive_summary: string;
  guardrails: string[];
}

// --- Phase 13 Longitudinal Evolution Types ---
export interface PrescriptionSnapshotReference {
  analysis_id: string;
  prescription_id: string;
  snapshot_timestamp: string;
  sequence_index: number;
  position_type: string;
  medications: string[];
}

export interface PersistenceProfile {
  entity_id: string;
  entity_type: string;
  presence_ratio: number;
  longest_consecutive_run: number;
  first_seen_index: number;
  last_seen_index: number;
  persistence_level: string;
}

export interface EmergenceEvent {
  entity_id: string;
  entity_type: string;
  emergence_index: number;
  previously_absent_count: number;
  post_emergence_persistence: number;
  classification: string;
}

export interface DisappearanceEvent {
  entity_id: string;
  entity_type: string;
  disappearance_index: number;
  previously_present_count: number;
  post_disappearance_absence_ratio: number;
  classification: string;
}

export interface LongitudinalChangePoint {
  from_snapshot_index: number;
  to_snapshot_index: number;
  structural_change: number;
  signal_change: number;
  stability_change: number;
  trustworthiness_change: number;
  medication_set_change: number;
  aggregate_change_score: number;
  change_level: string;
  contributing_dimensions: string[];
}

export interface StructuralEvolutionProfile {
  topology_sequence: string[];
  density_sequence: number[];
  central_participant_sequence: string[][];
  cluster_count_sequence: number[];
  topology_transition_count: number;
  structural_change_points: number[];
  classification: string;
}

export interface SignalEvolutionProfile {
  theme_id: string;
  presence_sequence: boolean[];
  reinforcement_sequence: number[];
  rank_sequence: number[];
  persistence_ratio: number;
  emergence_events: EmergenceEvent[];
  disappearance_events: DisappearanceEvent[];
  classification: string;
}

export interface StabilityEvolutionProfile {
  stability_sequence: string[];
  sensitivity_sequence: number[];
  transition_count: number;
  classification: string;
}

export interface TrustworthinessEvolutionProfile {
  score_sequence: number[];
  level_sequence: string[];
  score_delta_sequence: number[];
  mean_score: number;
  score_volatility: number;
  classification: string;
}

export interface CrossLayerEvolutionProfile {
  structural_persistence: number;
  signal_persistence: number;
  stability_persistence: number;
  provenance_persistence: number;
  trustworthiness_persistence: number;
  cross_layer_transition_alignment: string[];
  classification: string;
  explanation: string;
}

export interface PrescriptionLongitudinalProfile {
  timeline: PrescriptionSnapshotReference[];
  persistence_profiles: PersistenceProfile[];
  emergence_events: EmergenceEvent[];
  disappearance_events: DisappearanceEvent[];
  change_points: LongitudinalChangePoint[];
  structural_evolution: StructuralEvolutionProfile;
  signal_evolution: SignalEvolutionProfile[];
  stability_evolution: StabilityEvolutionProfile;
  trustworthiness_evolution: TrustworthinessEvolutionProfile;
  cross_layer_evolution: CrossLayerEvolutionProfile;
  overall_evolution_level: string;
  longitudinal_summary: string;
  guardrails: string[];
}



