"""
src/api/graph_schemas.py

Pydantic schemas for the Interactive Prescription Safety Graph Visualization Layer.
Defines Node, Edge, Metadata, and Subgraph response models for Cytoscape.js rendering.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # Drug, RxNormConcept, DrugPair, SideEffect, ProvenanceSource
    display_category: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    evidence_summary: Optional[str] = None
    is_focal: bool = False

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str  # HAS_RXNORM_CONCEPT, INTERACTS_WITH, MEMBER_OF_PAIR, ASSOCIATED_WITH, DERIVED_FROM
    label: str
    directional: bool = True
    source_dataset: str
    evidence_priority: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

class GraphMetadata(BaseModel):
    graph_type: str  # PRESCRIPTION_OVERVIEW, PAIR_EVIDENCE, PROVENANCE_TRACE, DRUG_NEIGHBORHOOD
    analysis_id: Optional[str] = None
    pair_id: Optional[str] = None
    node_count: int
    edge_count: int
    truncated: bool = False
    hidden_node_count: int = 0
    generated_from: str = "KnowledgeGraph_Phase4"

class SubgraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: GraphMetadata
