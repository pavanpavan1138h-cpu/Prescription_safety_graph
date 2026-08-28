"""
reasoning_schema.py

Defines core data structures, enums, and types for Phase 5 Prescription Safety Graph Reasoning.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

class EvidenceStatus(str, Enum):
    CONVERGENT_SAFETY_EVIDENCE = "CONVERGENT_SAFETY_EVIDENCE"
    DDI_EVIDENCE_ONLY = "DDI_EVIDENCE_ONLY"
    COMBINATION_EVENT_EVIDENCE_ONLY = "COMBINATION_EVENT_EVIDENCE_ONLY"
    NO_DIRECT_GRAPH_EVIDENCE = "NO_DIRECT_GRAPH_EVIDENCE"

class ConfidenceLevel(str, Enum):
    HIGH_EVIDENCE_CONFIDENCE = "HIGH_EVIDENCE_CONFIDENCE"
    MODERATE_EVIDENCE_CONFIDENCE = "MODERATE_EVIDENCE_CONFIDENCE"
    LIMITED_EVIDENCE_CONFIDENCE = "LIMITED_EVIDENCE_CONFIDENCE"
    AMBIGUOUS_EVIDENCE = "AMBIGUOUS_EVIDENCE"

@dataclass
class DrugIdentity:
    internal_drug_id: str
    display_name: Optional[str]
    entity_status: str
    source_membership: Optional[str] = None
    rxcui: Optional[str] = None
    rxnorm_name: Optional[str] = None
    rxnorm_match_status: Optional[str] = None
    drugbank_ids: List[str] = field(default_factory=list)
    twosides_cids: List[str] = field(default_factory=list)

@dataclass
class DDIEvidenceRecord:
    edge_id: str
    source_drug_id: str
    target_drug_id: str
    source_drugbank_id_1: str
    source_drugbank_id_2: str
    interaction_description: str
    interaction_label: Optional[str]
    directionality: str
    mapping_confidence: str
    evidence_confidence: str
    source_dataset: str = "drugbank"
    provenance: str = "drugbank_interactions_normalized.csv"

@dataclass
class SideEffectRecord:
    edge_id: str
    side_effect_id: str
    side_effect_name: str
    drug_pair_id: str
    source_drug_1: str
    source_drug_2: str
    source_dataset: str = "twosides"
    provenance: str = "twosides_relationships_normalized.csv"

@dataclass
class PairEvidenceBundle:
    drug_a: DrugIdentity
    drug_b: DrugIdentity
    drug_pair_node_id: Optional[str]
    ddi_records_forward: List[DDIEvidenceRecord] = field(default_factory=list)
    ddi_records_reverse: List[DDIEvidenceRecord] = field(default_factory=list)
    side_effect_records: List[SideEffectRecord] = field(default_factory=list)
    total_side_effects_count: int = 0

@dataclass
class ReasoningTrace:
    inference_id: str
    graph_paths: List[str] = field(default_factory=list)
    supporting_edge_ids: List[str] = field(default_factory=list)
    source_record_ids: List[str] = field(default_factory=list)
    rule_fired: str = ""
    confidence_reasons: List[str] = field(default_factory=list)
    explanation_text: str = ""

@dataclass
class SafetyInferenceResult:
    inference_id: str
    drug_a_id: str
    drug_b_id: str
    drug_pair_id: Optional[str]
    evidence_status: EvidenceStatus
    confidence_score: float
    confidence_level: ConfidenceLevel
    ddi_evidence_present: bool
    ddi_forward_count: int
    ddi_reverse_count: int
    combination_event_present: bool
    combination_event_count: int
    identity_status_summary: str
    inference_rule: str
    reasoning_trace: Optional[ReasoningTrace] = None
    clinical_interpretation: str = (
        "This evaluation reflects structured graph evidence strength. "
        "It is not a clinical risk probability or medical diagnosis."
    )
