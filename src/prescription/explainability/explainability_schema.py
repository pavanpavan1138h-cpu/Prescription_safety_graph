"""
src/prescription/explainability/explainability_schema.py

Data schemas, enums, and structures for Phase 11 Evidence Provenance, Traceability
and Explainability Intelligence Engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class ExplanationNodeType(str, Enum):
    FINAL_INTERPRETATION = "FINAL_INTERPRETATION"
    CONTEXTUAL_STABILITY_RESULT = "CONTEXTUAL_STABILITY_RESULT"
    EVIDENCE_INTELLIGENCE_RESULT = "EVIDENCE_INTELLIGENCE_RESULT"
    STRUCTURAL_RESULT = "STRUCTURAL_RESULT"
    PAIR_REASONING_RESULT = "PAIR_REASONING_RESULT"
    REASONING_RULE = "REASONING_RULE"
    DRUG_PAIR = "DRUG_PAIR"
    DRUG_ENTITY = "DRUG_ENTITY"
    SIGNAL_THEME = "SIGNAL_THEME"
    EVIDENCE_ASSERTION = "EVIDENCE_ASSERTION"
    GRAPH_RELATIONSHIP = "GRAPH_RELATIONSHIP"
    SOURCE_DATASET = "SOURCE_DATASET"
    SOURCE_RECORD = "SOURCE_RECORD"

class ExplanationRelationType(str, Enum):
    DERIVED_FROM = "DERIVED_FROM"
    SUPPORTED_BY = "SUPPORTED_BY"
    COMPUTED_FROM = "COMPUTED_FROM"
    TRIGGERED_BY = "TRIGGERED_BY"
    CONTRIBUTED_TO = "CONTRIBUTED_TO"
    VALIDATED_BY = "VALIDATED_BY"
    DEPENDS_ON = "DEPENDS_ON"
    TRACES_TO = "TRACES_TO"

class ContributionLevel(str, Enum):
    PRIMARY_CONTRIBUTOR = "PRIMARY_CONTRIBUTOR"
    MAJOR_CONTRIBUTOR = "MAJOR_CONTRIBUTOR"
    SUPPORTING_CONTRIBUTOR = "SUPPORTING_CONTRIBUTOR"
    MINOR_CONTRIBUTOR = "MINOR_CONTRIBUTOR"
    BACKGROUND_CONTEXT = "BACKGROUND_CONTEXT"

class CrossLayerTraceabilityLevel(str, Enum):
    FULL_CROSS_LAYER_TRACEABILITY = "FULL_CROSS_LAYER_TRACEABILITY"
    PARTIAL_CROSS_LAYER_TRACEABILITY = "PARTIAL_CROSS_LAYER_TRACEABILITY"
    LIMITED_TRACEABILITY = "LIMITED_TRACEABILITY"

@dataclass
class ExplanationNode:
    node_id: str
    node_type: ExplanationNodeType
    label: str
    description: str
    phase_origin: str
    source_reference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExplanationEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: ExplanationRelationType
    contribution_weight: float = 1.0
    description: str = ""

@dataclass
class ExplanationGraph:
    nodes: List[ExplanationNode] = field(default_factory=list)
    edges: List[ExplanationEdge] = field(default_factory=list)
    root_node_ids: List[str] = field(default_factory=list)
    leaf_node_ids: List[str] = field(default_factory=list)

@dataclass
class SourceProvenanceRecord:
    source_id: str
    dataset_name: str
    record_type: str
    external_identifier: Optional[str]
    description: str
    is_available: bool = True

@dataclass
class ContributionProfile:
    entity_id: str
    entity_label: str
    entity_type: str
    direct_decision_contribution: float
    evidence_coverage: float
    cross_layer_participation: float
    dependency_impact: float
    overall_contribution_score: float
    contribution_level: ContributionLevel
    participating_phases: List[str] = field(default_factory=list)
    explanation: str = ""

@dataclass
class DependencyNode:
    entity_id: str
    entity_label: str
    entity_type: str
    depends_on_ids: List[str] = field(default_factory=list)
    dependency_weight: float = 1.0
    critical_dependency: bool = False

@dataclass
class DecisionDependencyMap:
    target_interpretation_id: str
    dependencies: List[DependencyNode] = field(default_factory=list)
    critical_path_entities: List[str] = field(default_factory=list)
    acyclic_verified: bool = True

@dataclass
class TraceabilityProfile:
    total_components_evaluated: int
    traceable_components_count: int
    traceability_coverage_score: float
    average_provenance_depth: float
    max_provenance_depth: int
    orphaned_components_count: int
    orphaned_component_ids: List[str] = field(default_factory=list)
    cross_layer_traceability: CrossLayerTraceabilityLevel = CrossLayerTraceabilityLevel.FULL_CROSS_LAYER_TRACEABILITY

@dataclass
class StructuredExplanationClaim:
    claim_id: str
    claim_type: str
    claim_text: str
    referenced_entity_ids: List[str] = field(default_factory=list)
    is_supported: bool = True
    supporting_evidence_ids: List[str] = field(default_factory=list)

@dataclass
class PrescriptionExplainabilityProfile:
    prescription_id: str
    analysis_id: str
    generated_at: str
    explanation_graph: ExplanationGraph
    contribution_profiles: List[ContributionProfile]
    dependency_map: DecisionDependencyMap
    traceability_profile: TraceabilityProfile
    provenance_records: List[SourceProvenanceRecord]
    structured_claims: List[StructuredExplanationClaim]
    narrative: str
    guardrails: List[str] = field(default_factory=list)
