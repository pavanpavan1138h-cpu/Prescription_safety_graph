"""
src/advanced_intelligence_schema.py

Analytical ontology, dataclasses, and Enums for Phase 8:
Advanced Clinical Intelligence, Prescription Complexity, Event Convergence,
Evidence Patterns, Review Prioritization, Uncertainty, and Context Requirements.
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field

class ComplexityCategory(str, Enum):
    LOW_COMPLEXITY = "LOW_COMPLEXITY"
    MODERATE_COMPLEXITY = "MODERATE_COMPLEXITY"
    HIGH_COMPLEXITY = "HIGH_COMPLEXITY"
    VERY_HIGH_COMPLEXITY = "VERY_HIGH_COMPLEXITY"

class DrugParticipationCategory(str, Enum):
    PRIMARY_SIGNAL_PARTICIPANT = "PRIMARY_SIGNAL_PARTICIPANT"
    RECURRING_SIGNAL_PARTICIPANT = "RECURRING_SIGNAL_PARTICIPANT"
    LIMITED_SIGNAL_PARTICIPANT = "LIMITED_SIGNAL_PARTICIPANT"
    NO_DIRECT_SIGNAL_PARTICIPATION = "NO_DIRECT_SIGNAL_PARTICIPATION"

class EventConvergenceCategory(str, Enum):
    STRONG_EVENT_CONVERGENCE = "STRONG_EVENT_CONVERGENCE"
    MODERATE_EVENT_CONVERGENCE = "MODERATE_EVENT_CONVERGENCE"
    ISOLATED_EVENT_SIGNAL = "ISOLATED_EVENT_SIGNAL"
    NO_EVENT_CONVERGENCE = "NO_EVENT_CONVERGENCE"

class PatternType(str, Enum):
    CONVERGENT_EVIDENCE_CLUSTER = "CONVERGENT_EVIDENCE_CLUSTER"
    CENTRAL_DRUG_SIGNAL_PATTERN = "CENTRAL_DRUG_SIGNAL_PATTERN"
    DISTRIBUTED_MULTI_PAIR_EVIDENCE = "DISTRIBUTED_MULTI_PAIR_EVIDENCE"
    EVENT_CONVERGENCE_PATTERN = "EVENT_CONVERGENCE_PATTERN"
    SINGLE_DOMINANT_FINDING = "SINGLE_DOMINANT_FINDING"
    IDENTITY_UNCERTAINTY_PATTERN = "IDENTITY_UNCERTAINTY_PATTERN"
    LIMITED_EVIDENCE_COVERAGE = "LIMITED_EVIDENCE_COVERAGE"

class ReviewPriorityTier(str, Enum):
    IMMEDIATE_REVIEW_PRIORITY = "IMMEDIATE_REVIEW_PRIORITY"
    HIGH_REVIEW_PRIORITY = "HIGH_REVIEW_PRIORITY"
    MODERATE_REVIEW_PRIORITY = "MODERATE_REVIEW_PRIORITY"
    ROUTINE_EVIDENCE_REVIEW = "ROUTINE_EVIDENCE_REVIEW"
    LIMITED_EVIDENCE_REVIEW = "LIMITED_EVIDENCE_REVIEW"

class UncertaintyCategory(str, Enum):
    IDENTITY_UNCERTAINTY = "IDENTITY_UNCERTAINTY"
    EVIDENCE_COVERAGE_LIMITATION = "EVIDENCE_COVERAGE_LIMITATION"
    SINGLE_CHANNEL_EVIDENCE_LIMITATION = "SINGLE_CHANNEL_EVIDENCE_LIMITATION"
    OBSERVATIONAL_ASSOCIATION_LIMITATION = "OBSERVATIONAL_ASSOCIATION_LIMITATION"
    GRAPH_ABSENCE_LIMITATION = "GRAPH_ABSENCE_LIMITATION"

@dataclass
class PrescriptionComplexityProfile:
    complexity_category: ComplexityCategory
    unique_drugs_count: int
    generated_pairs_count: int
    positive_pairs_count: int
    convergent_pairs_count: int
    participating_drugs_count: int
    max_single_drug_participation_ratio: float
    unresolved_inputs_count: int
    complexity_score: float
    explanation: str

@dataclass
class DrugParticipationProfile:
    internal_drug_id: str
    display_name: str
    participation_category: DrugParticipationCategory
    total_evaluated_pairs: int
    positive_evidence_pairs: int
    convergent_evidence_pairs: int
    ddi_participation_count: int
    event_participation_count: int
    prescription_findings_ratio: float
    relative_evidence_concentration: float
    explanation: str

@dataclass
class AdverseEventConvergenceItem:
    side_effect_name: str
    side_effect_id: Optional[str]
    participating_pairs_count: int
    participating_pair_keys: List[str]
    participating_drug_ids: List[str]
    participating_drug_names: List[str]
    convergence_category: EventConvergenceCategory
    explanation: str

@dataclass
class EvidencePatternItem:
    pattern_id: str
    pattern_type: PatternType
    title: str
    supporting_pair_ids: List[str]
    supporting_drug_ids: List[str]
    supporting_drug_names: List[str]
    evidence_counts: Dict[str, int]
    rule_fired: str
    explanation: str
    provenance_edge_ids: List[str]

@dataclass
class ReviewPriorityFinding:
    finding_id: str
    pair_id: str
    drug_a_name: str
    drug_b_name: str
    review_priority: ReviewPriorityTier
    review_score: float
    deterministic_reasons: List[str]
    evidence_status: str
    confidence_score: float
    inference_id: str
    supporting_edge_ids: List[str]

@dataclass
class UncertaintyProfile:
    uncertainty_categories: List[UncertaintyCategory]
    has_identity_uncertainty: bool
    unresolved_input_names: List[str]
    unmapped_rxnorm_drugs: List[str]
    single_channel_only_pairs: int
    unsupported_pairs_count: int
    uncertainty_level: str
    explanation_narrative: str

@dataclass
class ClinicalContextRequirement:
    context_category: str  # Dosage, Administration Timing, Renal/Hepatic Function, Patient Age, Comorbidities
    description: str
    why_it_matters: str
    is_available_in_graph: bool = False
    is_evaluated_by_system: bool = False

@dataclass
class AdvancedExplanationSummary:
    executive_summary: str
    key_findings_summary: str
    prescription_patterns_summary: str
    uncertainty_summary: str
    scientific_guardrails: List[str]

@dataclass
class AdvancedPrescriptionIntelligenceReport:
    analysis_id: str
    generated_at: str
    complexity_profile: PrescriptionComplexityProfile
    drug_participation_profiles: List[DrugParticipationProfile]
    event_convergence_items: List[AdverseEventConvergenceItem]
    evidence_patterns: List[EvidencePatternItem]
    review_priorities: List[ReviewPriorityFinding]
    uncertainty_profile: UncertaintyProfile
    clinical_context_requirements: List[ClinicalContextRequirement]
    advanced_explanation: AdvancedExplanationSummary
    scientific_limitations: List[str]
