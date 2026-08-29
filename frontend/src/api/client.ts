import {
  DrugResolveResponse,
  SystemInfoResponse,
  PrescriptionAnalysisResponse,
  PairDetailResponse,
  PrescriptionStructuralAnalysis,
  PrescriptionEvidenceIntelligenceProfile,
  ContextualStabilityProfile,
  PrescriptionComparativeIntelligenceProfile,
  PrescriptionExplainabilityProfile,
  ExplanationGraph,
  PrescriptionTrustworthinessProfile,
  PrescriptionLongitudinalProfile
} from '../types/api';

export interface GraphNode {
  id: string;
  label: string;
  node_type: string;
  display_category: string;
  properties: Record<string, any>;
  evidence_summary?: string;
  is_focal: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  label: string;
  directional: boolean;
  source_dataset: string;
  evidence_priority?: string;
  properties: Record<string, any>;
}

export interface GraphMetadata {
  graph_type: string;
  analysis_id?: string;
  pair_id?: string;
  node_count: number;
  edge_count: number;
  truncated: boolean;
  hidden_node_count: number;
  generated_from: string;
}

export interface SubgraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: GraphMetadata;
}

const API_BASE = '/api/v1';

export const prescriptionApi = {
  async getHealth(): Promise<{ status: string; graph_loaded: boolean }> {
    const res = await fetch('/health');
    if (!res.ok) throw new Error('System health check failed');
    return res.json();
  },

  async getSystemInfo(): Promise<SystemInfoResponse> {
    const res = await fetch(`${API_BASE}/system/info`);
    if (!res.ok) throw new Error('Failed to fetch system info');
    return res.json();
  },

  async resolveDrugs(drugs: string[]): Promise<DrugResolveResponse> {
    const res = await fetch(`${API_BASE}/drugs/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ drugs })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to resolve drug identifiers');
    }
    return res.json();
  },

  async analyzePrescription(medications: string[], prescriptionId?: string): Promise<PrescriptionAnalysisResponse> {
    const res = await fetch(`${API_BASE}/prescriptions/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ medications, prescription_id: prescriptionId })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to analyze prescription');
    }
    return res.json();
  },

  async getPairDetail(analysisId: string, pairId: string): Promise<PairDetailResponse> {
    const res = await fetch(`${API_BASE}/analyses/${analysisId}/pairs/${pairId}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to fetch pair details');
    }
    return res.json();
  },

  async getPrescriptionGraph(analysisId: string, sideEffectLimit: number = 5): Promise<SubgraphResponse> {
    const res = await fetch(`${API_BASE}/analyses/${analysisId}/graph?side_effect_limit=${sideEffectLimit}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load prescription graph');
    }
    return res.json();
  },

  async getPairEvidenceGraph(analysisId: string, pairId: string, sideEffectLimit: number = 25): Promise<SubgraphResponse> {
    const res = await fetch(`${API_BASE}/analyses/${analysisId}/pairs/${pairId}/graph?side_effect_limit=${sideEffectLimit}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load pair graph');
    }
    return res.json();
  },

  async getProvenanceGraph(analysisId: string, pairId: string): Promise<SubgraphResponse> {
    const res = await fetch(`${API_BASE}/analyses/${analysisId}/pairs/${pairId}/provenance-graph`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load provenance graph');
    }
    return res.json();
  },

  async analyzePrescriptionAdvanced(medications: string[], prescriptionId?: string): Promise<AdvancedPrescriptionAnalysisResponse> {
    const res = await fetch(`${API_BASE}/prescriptions/analyze-advanced`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ medications, prescription_id: prescriptionId })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to perform advanced clinical intelligence analysis');
    }
    return res.json();
  },

  async comparePrescriptions(analysisIdA: string, analysisIdB: string): Promise<PrescriptionComparativeIntelligenceProfile> {
    const res = await fetch(`${API_BASE}/prescriptions/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysis_id_a: analysisIdA, analysis_id_b: analysisIdB })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to compare prescription snapshots');
    }
    return res.json();
  },

  async getComparisonProfile(comparisonId: string): Promise<PrescriptionComparativeIntelligenceProfile> {
    const res = await fetch(`${API_BASE}/comparisons/${comparisonId}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load comparison profile');
    }
    return res.json();
  },

  async getExplainabilityProfile(analysisId: string): Promise<PrescriptionExplainabilityProfile> {
    const res = await fetch(`${API_BASE}/analyses/${analysisId}/explainability`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load explainability profile');
    }
    return res.json();
  },

  async getExplainabilityGraph(analysisId: string): Promise<ExplanationGraph> {
    const res = await fetch(`${API_BASE}/analyses/${analysisId}/explainability/graph`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load explanation graph');
    }
    return res.json();
  },

  async getTrustworthinessProfile(analysisId: string): Promise<PrescriptionTrustworthinessProfile> {
    const res = await fetch(`${API_BASE}/analyses/${analysisId}/trustworthiness`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load trustworthiness profile');
    }
    return res.json();
  },

  async triggerLongitudinalAnalysis(analysisIds: string[]): Promise<{ longitudinal_id: string }> {
    const res = await fetch(`${API_BASE}/analyses/longitudinal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysis_ids: analysisIds })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to trigger longitudinal evolution');
    }
    return res.json();
  },

  async getLongitudinalProfile(longitudinalId: string): Promise<PrescriptionLongitudinalProfile> {
    const res = await fetch(`${API_BASE}/longitudinal/${longitudinalId}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err?.error?.message || 'Failed to load longitudinal evolution profile');
    }
    return res.json();
  }
};

export interface ComplexityProfile {
  complexity_category: string;
  unique_drugs_count: number;
  generated_pairs_count: number;
  positive_pairs_count: number;
  convergent_pairs_count: number;
  participating_drugs_count: number;
  max_single_drug_participation_ratio: number;
  unresolved_inputs_count: number;
  complexity_score: number;
  explanation: string;
}

export interface DrugParticipationProfile {
  internal_drug_id: string;
  display_name: string;
  participation_category: string;
  total_evaluated_pairs: number;
  positive_evidence_pairs: number;
  convergent_evidence_pairs: number;
  ddi_participation_count: number;
  event_participation_count: number;
  prescription_findings_ratio: number;
  relative_evidence_concentration: number;
  explanation: string;
}

export interface AdverseEventConvergenceItem {
  side_effect_name: string;
  side_effect_id?: string;
  participating_pairs_count: number;
  participating_pair_keys: string[];
  participating_drug_ids: string[];
  participating_drug_names: string[];
  convergence_category: string;
  explanation: string;
}

export interface EvidencePatternItem {
  pattern_id: string;
  pattern_type: string;
  title: string;
  supporting_pair_ids: string[];
  supporting_drug_ids: string[];
  supporting_drug_names: string[];
  evidence_counts: Record<string, number>;
  rule_fired: string;
  explanation: string;
  provenance_edge_ids: string[];
}

export interface ReviewPriorityFinding {
  finding_id: string;
  pair_id: string;
  drug_a_name: string;
  drug_b_name: string;
  review_priority: string;
  review_score: number;
  deterministic_reasons: string[];
  evidence_status: string;
  confidence_score: number;
  inference_id: string;
  supporting_edge_ids: string[];
}

export interface UncertaintyProfile {
  uncertainty_categories: string[];
  has_identity_uncertainty: boolean;
  unresolved_input_names: string[];
  unmapped_rxnorm_drugs: string[];
  single_channel_only_pairs: number;
  unsupported_pairs_count: number;
  uncertainty_level: string;
  explanation_narrative: string;
}

export interface ClinicalContextRequirement {
  context_category: string;
  description: string;
  why_it_matters: string;
  is_available_in_graph: boolean;
  is_evaluated_by_system: boolean;
}

export interface AdvancedExplanationSummary {
  executive_summary: string;
  key_findings_summary: string;
  prescription_patterns_summary: string;
  uncertainty_summary: string;
  scientific_guardrails: string[];
}

export interface AdvancedPrescriptionAnalysisResponse {
  prescription_report: PrescriptionAnalysisResponse;
  complexity_profile: ComplexityProfile;
  drug_participation_profiles: DrugParticipationProfile[];
  event_convergence_items: AdverseEventConvergenceItem[];
  evidence_patterns: EvidencePatternItem[];
  review_priorities: ReviewPriorityFinding[];
  uncertainty_profile: UncertaintyProfile;
  clinical_context_requirements: ClinicalContextRequirement[];
  advanced_explanation: AdvancedExplanationSummary;
  scientific_limitations: string[];
  structural_analysis?: PrescriptionStructuralAnalysis;
  evidence_intelligence?: PrescriptionEvidenceIntelligenceProfile;
  contextual_stability?: ContextualStabilityProfile;
  explainability?: PrescriptionExplainabilityProfile;
  trustworthiness?: PrescriptionTrustworthinessProfile;
}
