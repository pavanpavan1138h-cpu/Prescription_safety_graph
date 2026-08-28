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
