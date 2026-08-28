"""
src/api/advanced_schemas.py

Pydantic schemas for Phase 8 Advanced Clinical Intelligence API endpoints.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from api.schemas import PrescriptionAnalysisResponse

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
