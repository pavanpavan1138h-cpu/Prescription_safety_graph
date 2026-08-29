"""
src/prescription/structural/prescription_network_schema.py

Analytical schemas, dataclasses, and Enums for Phase 8:
Prescription-Level Network Intelligence & Structural Safety Analysis.
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

class TopologyType(str, Enum):
    NO_EVIDENCE_NETWORK = "NO_EVIDENCE_NETWORK"
    ISOLATED_PAIR_EVIDENCE = "ISOLATED_PAIR_EVIDENCE"
    SINGLE_CONNECTED_CLUSTER = "SINGLE_CONNECTED_CLUSTER"
    MULTIPLE_EVIDENCE_CLUSTERS = "MULTIPLE_EVIDENCE_CLUSTERS"
    STAR_CENTRIC_STRUCTURE = "STAR_CENTRIC_STRUCTURE"
    DENSE_EVIDENCE_CLUSTER = "DENSE_EVIDENCE_CLUSTER"

class StructuralImpactLevel(str, Enum):
    HIGH_STRUCTURAL_IMPACT = "HIGH_STRUCTURAL_IMPACT"
    MODERATE_STRUCTURAL_IMPACT = "MODERATE_STRUCTURAL_IMPACT"
    LOW_STRUCTURAL_IMPACT = "LOW_STRUCTURAL_IMPACT"
    NO_STRUCTURAL_IMPACT = "NO_STRUCTURAL_IMPACT"

@dataclass
class PrescriptionEvidenceNode:
    drug_id: str
    display_name: str

@dataclass
class PrescriptionEvidenceEdge:
    drug_a_id: str
    drug_b_id: str
    evidence_status: str
    confidence_score: float
    priority_tier: str
    structural_weight: float
    edge_strength: float  # weight * confidence_score
    canonical_pair_key: str

@dataclass
class PrescriptionEvidenceNetwork:
    nodes: Dict[str, PrescriptionEvidenceNode] = field(default_factory=dict)
    edges: Dict[str, PrescriptionEvidenceEdge] = field(default_factory=dict)
    canonical_drug_ids: List[str] = field(default_factory=list)

@dataclass
class ClusterMetrics:
    cluster_id: str
    drug_ids: List[str]
    edge_count: int
    density: float
    convergent_edge_count: int
    ddi_only_edge_count: int
    combination_event_edge_count: int
    is_isolated: bool = False

@dataclass
class DrugStructuralProfile:
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

@dataclass
class TopologyClassification:
    primary_topology: TopologyType
    secondary_characteristics: List[str] = field(default_factory=list)

@dataclass
class CounterfactualResult:
    drug_id: str
    display_name: str
    original_edge_count: int
    remaining_edge_count: int
    structural_delta: int  # edges removed
    convergent_edges_removed: int
    clusters_before: int
    clusters_after: int
    largest_cluster_before: int
    largest_cluster_after: int
    contribution_level: StructuralImpactLevel
    explanation: str

@dataclass
class NetworkSummary:
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

@dataclass
class StructuralInterpretation:
    highest_participation_drug: Optional[str]
    highest_participation_degree: int
    network_connectivity_narration: str
    counterfactual_impact_narration: str
    clinical_warning: str = "This is a structural counterfactual analysis and is not a recommendation to discontinue, remove, substitute, or modify medication therapy."

@dataclass
class PrescriptionStructuralAnalysis:
    analysis_id: str
    generated_at: str
    network_summary: NetworkSummary
    topology: TopologyClassification
    clusters: List[ClusterMetrics]
    drug_structural_profiles: List[DrugStructuralProfile]
    ranked_structural_contributors: List[DrugStructuralProfile]
    counterfactual_results: List[CounterfactualResult]
    original_network: PrescriptionEvidenceNetwork
    structural_interpretation: StructuralInterpretation
    scientific_guardrails: List[str] = field(default_factory=lambda: [
        "Structural participation and centrality metrics do not correlate with absolute clinical severity or patient risk.",
        "A high structural centrality status indicates evidence connectivity in the knowledge graph, not that a drug is the root cause of risk.",
        "Counterfactual exclusion is a computational simulation only and must never be interpreted as a prescribing suggestion.",
        "Isolated node status indicates absence of direct safety database evidence in the current ingested graph, not clinical safety."
    ])
