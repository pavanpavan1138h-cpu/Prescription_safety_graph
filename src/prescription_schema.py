"""
prescription_schema.py

Data structures, enums, and models for Phase 6 Multi-Drug Prescription Safety Reasoning.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

class ResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"
    DUPLICATE = "DUPLICATE"

class EvidencePriority(str, Enum):
    CRITICAL_EVIDENCE_PRIORITY = "CRITICAL_EVIDENCE_PRIORITY"
    HIGH_EVIDENCE_PRIORITY = "HIGH_EVIDENCE_PRIORITY"
    MODERATE_EVIDENCE_PRIORITY = "MODERATE_EVIDENCE_PRIORITY"
    LIMITED_EVIDENCE_PRIORITY = "LIMITED_EVIDENCE_PRIORITY"
    NO_EVIDENCE_PRIORITY = "NO_EVIDENCE_PRIORITY"

class PrescriptionStatus(str, Enum):
    MULTI_SIGNAL_EVIDENCE = "MULTI_SIGNAL_EVIDENCE"
    CONVERGENT_EVIDENCE_PRESENT = "CONVERGENT_EVIDENCE_PRESENT"
    SINGLE_CHANNEL_EVIDENCE_PRESENT = "SINGLE_CHANNEL_EVIDENCE_PRESENT"
    LIMITED_GRAPH_EVIDENCE = "LIMITED_GRAPH_EVIDENCE"
    NO_DIRECT_GRAPH_EVIDENCE = "NO_DIRECT_GRAPH_EVIDENCE"

@dataclass
class ResolvedPrescriptionDrug:
    original_input: str
    resolved_internal_drug_id: Optional[str]
    display_name: Optional[str]
    resolution_status: ResolutionStatus
    identifier_type_matched: Optional[str]
    entity_status: Optional[str] = None
    rxcui: Optional[str] = None
    rxnorm_name: Optional[str] = None

@dataclass
class PrescriptionResolutionResult:
    original_inputs: List[str]
    resolved_drugs: List[ResolvedPrescriptionDrug]
    canonical_drug_ids: List[str]
    unresolved_inputs: List[str]
    ambiguous_inputs: List[str]
    duplicate_inputs: List[str]

@dataclass
class PrescriptionPair:
    pair_index: int
    drug_a_id: str
    drug_b_id: str
    drug_a_name: str
    drug_b_name: str
    canonical_pair_key: str

@dataclass
class PrioritizedFinding:
    finding_id: str
    pair_index: int
    drug_a_id: str
    drug_b_id: str
    drug_a_name: str
    drug_b_name: str
    evidence_status: str
    evidence_priority: EvidencePriority
    confidence_level: str
    confidence_score: float
    ddi_present: bool
    ddi_count: int
    events_present: bool
    event_count: int
    inference_id: str
    rule_fired: str
    summary_narrative: str
    supporting_edge_ids: List[str] = field(default_factory=list)
    source_record_ids: List[str] = field(default_factory=list)

@dataclass
class DrugParticipationSummary:
    internal_drug_id: str
    display_name: str
    total_pairs_involved: int
    evidence_supported_pairs: int
    convergent_pairs: int
    ddi_only_pairs: int
    combination_event_pairs: int
    no_evidence_pairs: int

@dataclass
class PrescriptionEvidenceSummary:
    total_input_items: int
    unique_canonical_drugs: int
    unresolved_items_count: int
    ambiguous_items_count: int
    duplicates_collapsed_count: int
    total_expected_pairs: int
    total_analyzed_pairs: int
    pairs_with_evidence: int
    convergent_evidence_pairs: int
    ddi_only_pairs: int
    combination_event_only_pairs: int
    no_direct_evidence_pairs: int
    prescription_status: PrescriptionStatus

@dataclass
class PrescriptionSafetyReport:
    prescription_id: str
    generated_at: str
    resolution_summary: PrescriptionResolutionResult
    evidence_summary: PrescriptionEvidenceSummary
    drug_participation: List[DrugParticipationSummary]
    prioritized_findings: List[PrioritizedFinding]
    pair_results: List[Dict[str, Any]]
    clinical_narrative_report: str
    scientific_limitations: List[str] = field(default_factory=lambda: [
        "Graph evidence priority is not equivalent to patient-specific clinical risk.",
        "Absence of evidence in the current graph is not evidence of medical safety.",
        "Drug interaction assertions and observational adverse event associations do not independently establish causality.",
        "This report is generated strictly from the ingested knowledge graph datasets and does not replace professional clinical judgment."
    ])
