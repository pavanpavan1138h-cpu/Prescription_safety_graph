"""
graph_schema.py

Defines the frozen Phase 4 ontology, node types, relationship types, field schemas,
and validation constraints for the Prescription Safety Knowledge Graph.
"""

from enum import Enum
from typing import Dict, List, Set

class NodeType(str, Enum):
    DRUG = "Drug"
    RXNORM_CONCEPT = "RxNormConcept"
    DRUG_PAIR = "DrugPair"
    SIDE_EFFECT = "SideEffect"

class RelationshipType(str, Enum):
    HAS_RXNORM_CONCEPT = "HAS_RXNORM_CONCEPT"
    INTERACTS_WITH = "INTERACTS_WITH"
    MEMBER_OF_PAIR = "MEMBER_OF_PAIR"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"

# Canonical Node Schema
NODE_SCHEMA: List[str] = [
    "node_id",
    "node_type",
    "display_name",
    "source_identifier",
    "entity_status",
    "confidence",
    "properties_json"
]

# Canonical Edge Schema
EDGE_SCHEMA: List[str] = [
    "edge_id",
    "source_node_id",
    "target_node_id",
    "relationship_type",
    "source_dataset",
    "source_record_id",
    "mapping_confidence",
    "evidence_confidence",
    "properties_json"
]

VALID_NODE_TYPES: Set[str] = {t.value for t in NodeType}
VALID_RELATIONSHIP_TYPES: Set[str] = {t.value for t in RelationshipType}

# Strict endpoint constraints
EDGE_ENDPOINT_CONSTRAINTS: Dict[str, Dict[str, Set[str]]] = {
    RelationshipType.HAS_RXNORM_CONCEPT.value: {
        "source_types": {NodeType.DRUG.value},
        "target_types": {NodeType.RXNORM_CONCEPT.value}
    },
    RelationshipType.INTERACTS_WITH.value: {
        "source_types": {NodeType.DRUG.value},
        "target_types": {NodeType.DRUG.value}
    },
    RelationshipType.MEMBER_OF_PAIR.value: {
        "source_types": {NodeType.DRUG.value},
        "target_types": {NodeType.DRUG_PAIR.value}
    },
    RelationshipType.ASSOCIATED_WITH.value: {
        "source_types": {NodeType.DRUG_PAIR.value},
        "target_types": {NodeType.SIDE_EFFECT.value}
    }
}
