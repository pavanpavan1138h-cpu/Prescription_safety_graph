"""
src/api/schemas.py

Pydantic schemas and public contracts for Phase 7 REST API.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# 1. System Schemas
class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "prescription-safety-graph-api"
    graph_loaded: bool = True
    reasoning_engine_available: bool = True

class SystemInfoResponse(BaseModel):
    api_version: str = "v1.0.0"
    graph_nodes: int = 68223
    graph_edges: int = 4969811
    node_breakdown: Dict[str, int]
    edge_breakdown: Dict[str, int]
    supported_identifier_types: List[str]

# 2. Drug Resolution Schemas
class DrugResolveRequest(BaseModel):
    drugs: List[str] = Field(..., min_length=1, max_length=50, description="List of medication identifiers to resolve")

class ResolvedDrugItem(BaseModel):
    input: str
    status: str
    internal_drug_id: Optional[str] = None
    canonical_name: Optional[str] = None
    identifier_type_matched: Optional[str] = None
    rxcui: Optional[str] = None

class DrugResolveResponse(BaseModel):
    input_count: int
    unique_resolved_drugs: int
    duplicates_collapsed: int
    unresolved_count: int
    results: List[ResolvedDrugItem]

class DrugEntityCardResponse(BaseModel):
    internal_drug_id: str
    display_name: Optional[str]
    entity_status: str
    source_membership: Optional[str]
    rxcui: Optional[str]
    rxnorm_name: Optional[str]
    rxnorm_match_status: Optional[str]
    drugbank_ids: List[str]
    twosides_cids: List[str]

# 3. Pairwise Schemas
class PairSafetyRequest(BaseModel):
    drug_a: str
    drug_b: str

class PairSafetyResponse(BaseModel):
    inference_id: str
    drug_a: Dict[str, Any]
    drug_b: Dict[str, Any]
    evidence_status: str
    confidence: Dict[str, Any]
    evidence_summary: Dict[str, Any]
    clinical_interpretation: str

# 4. Master Prescription Analysis Schemas
class PrescriptionAnalyzeRequest(BaseModel):
    medications: List[str] = Field(default_factory=list, description="List of medications to analyze")
    prescription_id: Optional[str] = None

class AnalysisMetadata(BaseModel):
    analysis_id: str
    api_version: str
    generated_at: str
    graph_version: str
    reasoning_engine_version: str

class InputSummary(BaseModel):
    submitted_medication_count: int
    submitted_medications: List[str]

class ResolvedDrugCanonicalItem(BaseModel):
    canonical_drug_id: str
    canonical_name: str
    rxcui: Optional[str] = None
    input_values: List[str]

class ResolutionSummary(BaseModel):
    resolved_count: int
    unique_canonical_drug_count: int
    duplicate_count: int
    unresolved_count: int
    resolved_drugs: List[ResolvedDrugCanonicalItem]

class PrescriptionSummary(BaseModel):
    evidence_status: str
    highest_evidence_priority: str
    total_unique_drugs: int
    total_pairs_analyzed: int
    positive_evidence_pairs: int
    convergent_evidence_pairs: int
    ddi_only_pairs: int
    combination_event_only_pairs: int
    no_direct_evidence_pairs: int

class PrioritizedFindingCard(BaseModel):
    finding_id: str
    pair_id: str
    priority: str
    drug_a: Dict[str, str]
    drug_b: Dict[str, str]
    evidence_status: str
    confidence: Dict[str, Any]
    summary_narrative: str
    evidence_channels: Dict[str, bool]
    ddi_record_count: int
    adverse_event_count: int
    inference_id: str
    supporting_edge_ids: List[str]

class PairResultRow(BaseModel):
    pair_id: str
    drug_a_name: str
    drug_b_name: str
    evidence_status: str
    evidence_priority: str
    confidence_level: str
    confidence_score: float
    ddi_evidence_present: bool
    combination_event_evidence_present: bool

class DrugParticipationRow(BaseModel):
    drug_id: str
    drug_name: str
    total_pairs: int
    pairs_with_evidence: int
    convergent_evidence_pairs: int
    highest_priority: str

class UnresolvedItemRow(BaseModel):
    input_value: str
    resolution_status: str
    reason: str

class ProvenanceSummary(BaseModel):
    evidence_sources: List[str]
    supporting_edge_count: int
    top_supporting_edge_ids: List[str]

class PrescriptionAnalysisResponse(BaseModel):
    metadata: AnalysisMetadata
    input_summary: InputSummary
    resolution_summary: ResolutionSummary
    prescription_summary: PrescriptionSummary
    prioritized_findings: List[PrioritizedFindingCard]
    pair_results: List[PairResultRow]
    drug_participation: List[DrugParticipationRow]
    unresolved_items: List[UnresolvedItemRow]
    limitations: List[str]
    provenance: ProvenanceSummary
    clinical_narrative_report: str

# 5. Granular Pair Detail Drilldown
class DirectDDIItem(BaseModel):
    edge_id: str
    direction: str
    source_dataset: str
    source_record_id: str
    interaction_description: str

class AdverseEventItem(BaseModel):
    edge_id: str
    side_effect_id: str
    side_effect_name: str
    source_dataset: str

class CombinationAdverseEventsDetail(BaseModel):
    total_event_count: int
    observed_events: List[AdverseEventItem]

class ProvenanceTraceDetail(BaseModel):
    graph_paths: List[str]
    confidence_reasons: List[str]

class PairDetailResponse(BaseModel):
    pair_id: str
    drug_a: Dict[str, Any]
    drug_b: Dict[str, Any]
    inference: Dict[str, Any]
    direct_ddi_evidence: List[DirectDDIItem]
    combination_adverse_events: CombinationAdverseEventsDetail
    provenance_trace: ProvenanceTraceDetail

# 6. Error Schema
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail
