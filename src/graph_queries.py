"""
graph_queries.py

Structured Graph Query & Retrieval Layer for the Prescription Safety Knowledge Graph.
Provides high-level lookup functions for drugs, RxNorm concepts, direct DDIs,
drug-pair side effects, and provenance tracing.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

class GraphQueryEngine:
    def __init__(self, graph_dir: Path):
        self.graph_dir = graph_dir
        self.nodes_df: Optional[pd.DataFrame] = None
        self.edges_df: Optional[pd.DataFrame] = None

        # Lookups
        self._node_by_id: Dict[str, Dict] = {}
        self._drug_by_drugbank: Dict[str, str] = {}
        self._drug_by_twosides: Dict[str, str] = {}
        self._drug_by_rxcui: Dict[str, str] = {}

    def load(self):
        self.nodes_df = pd.read_csv(self.graph_dir / "graph_nodes.csv")
        self.edges_df = pd.read_csv(self.graph_dir / "graph_edges.csv")

        # Build fast in-memory index for demo queries
        for _, r in self.nodes_df.iterrows():
            nid = r["node_id"]
            self._node_by_id[nid] = r.to_dict()
            
            if r["node_type"] == "Drug":
                props = json.loads(r["properties_json"])
                for db in props.get("drugbank_ids", []):
                    self._drug_by_drugbank[db] = nid
                for tw in props.get("twosides_cids", []):
                    self._drug_by_twosides[tw] = nid
                if props.get("rxcui"):
                    self._drug_by_rxcui[props["rxcui"]] = nid

    def get_drug_by_source_identifier(self, dataset: str, identifier: str) -> Optional[Dict]:
        ds = dataset.lower()
        if ds == "drugbank":
            nid = self._drug_by_drugbank.get(identifier)
        elif ds == "twosides":
            nid = self._drug_by_twosides.get(identifier)
        else:
            nid = None
            
        return self._node_by_id.get(nid) if nid else None

    def get_drug_by_rxcui(self, rxcui: str) -> Optional[Dict]:
        nid = self._drug_by_rxcui.get(str(rxcui))
        return self._node_by_id.get(nid) if nid else None

    def get_rxnorm_concept_for_drug(self, internal_drug_id: str) -> Optional[Dict]:
        # Search edge HAS_RXNORM_CONCEPT
        edges = self.edges_df[
            (self.edges_df["source_node_id"] == internal_drug_id) & 
            (self.edges_df["relationship_type"] == "HAS_RXNORM_CONCEPT")
        ]
        if not edges.empty:
            target_id = edges.iloc[0]["target_node_id"]
            edge_props = json.loads(edges.iloc[0]["properties_json"])
            target_node = self._node_by_id.get(target_id, {})
            return {
                "rxnorm_concept_node": target_node,
                "mapping_edge": edges.iloc[0].to_dict(),
                "mapping_properties": edge_props
            }
        return None

    def get_direct_interactions(self, drug_a_id: str, drug_b_id: str) -> List[Dict]:
        # Query directed INTERACTS_WITH edges in either direction
        edges = self.edges_df[
            (self.edges_df["relationship_type"] == "INTERACTS_WITH") &
            (
                ((self.edges_df["source_node_id"] == drug_a_id) & (self.edges_df["target_node_id"] == drug_b_id)) |
                ((self.edges_df["source_node_id"] == drug_b_id) & (self.edges_df["target_node_id"] == drug_a_id))
            )
        ]
        results = []
        for _, erow in edges.iterrows():
            results.append({
                "edge_id": erow["edge_id"],
                "source": erow["source_node_id"],
                "target": erow["target_node_id"],
                "source_dataset": erow["source_dataset"],
                "evidence_confidence": erow["evidence_confidence"],
                "properties": json.loads(erow["properties_json"])
            })
        return results

    def get_drug_pair_and_side_effects(self, drug_a_id: str, drug_b_id: str) -> Optional[Dict]:
        sorted_pair = sorted([drug_a_id, drug_b_id])
        pair_node_id = f"PAIR_{sorted_pair[0]}__{sorted_pair[1]}"
        
        pair_node = self._node_by_id.get(pair_node_id)
        if not pair_node:
            return None

        # Fetch associated side effects
        se_edges = self.edges_df[
            (self.edges_df["source_node_id"] == pair_node_id) &
            (self.edges_df["relationship_type"] == "ASSOCIATED_WITH")
        ]
        
        side_effects = []
        for _, erow in se_edges.head(10).iterrows(): # Sample top 10
            se_node_id = erow["target_node_id"]
            se_node = self._node_by_id.get(se_node_id, {})
            side_effects.append({
                "side_effect_id": se_node.get("source_identifier"),
                "side_effect_name": se_node.get("display_name"),
                "edge_id": erow["edge_id"]
            })

        return {
            "pair_node": pair_node,
            "total_associated_side_effects": len(se_edges),
            "sample_side_effects": side_effects
        }

    def get_provenance_for_edge(self, edge_id: str) -> Optional[Dict]:
        edge_row = self.edges_df[self.edges_df["edge_id"] == edge_id]
        if edge_row.empty:
            return None
        erow = edge_row.iloc[0]
        return {
            "edge_id": erow["edge_id"],
            "relationship_type": erow["relationship_type"],
            "source_node": self._node_by_id.get(erow["source_node_id"]),
            "target_node": self._node_by_id.get(erow["target_node_id"]),
            "source_dataset": erow["source_dataset"],
            "source_record_id": erow["source_record_id"],
            "mapping_confidence": erow["mapping_confidence"],
            "evidence_confidence": erow["evidence_confidence"],
            "properties": json.loads(erow["properties_json"])
        }
