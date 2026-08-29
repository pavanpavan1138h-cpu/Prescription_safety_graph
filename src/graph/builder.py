"""
graph_builder.py

High-performance, provenance-preserving Knowledge Graph Builder for Phase 4.
Constructs canonical graph nodes and edges adhering to the frozen Phase 4 ontology.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
import pandas as pd

from src.graph.schema import (
    NodeType,
    RelationshipType,
    NODE_SCHEMA,
    EDGE_SCHEMA
)

logger = logging.getLogger(__name__)

class GraphBuilder:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.norm_dir = data_dir / "interim" / "normalized"
        self.enr_dir = data_dir / "interim" / "enriched"
        self.graph_dir = data_dir / "interim" / "graph"
        self.graph_dir.mkdir(parents=True, exist_ok=True)

        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []

        # Specific export buckets
        self.rxnorm_edges: List[Dict] = []
        self.interaction_edges: List[Dict] = []
        self.pair_nodes: List[Dict] = []
        self.pair_membership_edges: List[Dict] = []
        self.pair_side_effect_edges: List[Dict] = []

        # Mappings
        self.source_to_internal: Dict[Tuple[str, str], str] = {}
        self.internal_to_drugbank: Dict[str, List[str]] = {}
        self.internal_to_twosides: Dict[str, List[str]] = {}
        self.unmapped_relationships: List[Dict] = []

    def build_all(self):
        logger.info("Initializing Phase 4 Knowledge Graph construction...")
        
        self._load_source_mappings()
        self._build_drug_nodes()
        self._build_rxnorm_nodes_and_edges()
        self._build_side_effect_nodes()
        self._build_drugbank_interaction_edges()
        self._build_twosides_pair_nodes_and_edges()
        
        self._export_all()
        logger.info("Phase 4 Knowledge Graph construction successfully completed.")

    def _load_source_mappings(self):
        logger.info("Loading source identifier crosswalk...")
        src_map_df = pd.read_csv(self.norm_dir / "integrated_drug_source_mappings.csv")
        for _, row in src_map_df.iterrows():
            ds = row["source_dataset"].lower()
            sid = str(row["source_drug_id"]).strip()
            iid = row["internal_drug_id"]
            self.source_to_internal[(ds, sid)] = iid
            
            if ds == "drugbank":
                self.internal_to_drugbank.setdefault(iid, []).append(sid)
            elif ds == "twosides":
                self.internal_to_twosides.setdefault(iid, []).append(sid)
                
        logger.info(f"Loaded {len(self.source_to_internal)} source-to-internal identifier mappings.")

    def _build_drug_nodes(self):
        logger.info("Building Drug nodes...")
        nodes_df = pd.read_csv(self.norm_dir / "integrated_drug_nodes.csv")
        enr_df = pd.read_csv(self.enr_dir / "rxnorm_drug_enrichment.csv")
        
        merged = pd.merge(nodes_df, enr_df, on="internal_drug_id", how="left")
        
        for _, row in merged.iterrows():
            iid = row["internal_drug_id"]
            rx_name = row.get("rxnorm_name")
            cand_name = row.get("name_candidate")
            display_name = rx_name if pd.notna(rx_name) and rx_name != "" else cand_name
            if pd.isna(display_name) or display_name == "NO_NAME_CANDIDATE":
                display_name = None
                
            rxcui_val = row.get("rxcui")
            rxcui_str = str(int(rxcui_val)) if pd.notna(rxcui_val) and str(rxcui_val) != "nan" else None
            
            db_ids = self.internal_to_drugbank.get(iid, [])
            tw_ids = self.internal_to_twosides.get(iid, [])
            primary_src_id = db_ids[0] if db_ids else (tw_ids[0] if tw_ids else None)

            props = {
                "internal_drug_id": iid,
                "canonical_smiles": row.get("canonical_smiles"),
                "inchikey": row.get("inchikey"),
                "source_membership": row.get("source_membership"),
                "drugbank_ids": db_ids,
                "twosides_cids": tw_ids,
                "name_candidate": cand_name,
                "name_source": row.get("name_source"),
                "name_resolution_status": row.get("name_resolution_status"),
                "rxnorm_match_status": row.get("rxnorm_match_status"),
                "rxnorm_match_method": row.get("rxnorm_match_method"),
                "rxcui": rxcui_str,
                "rxnorm_name": rx_name,
                "match_score": row.get("match_score"),
                "enrichment_confidence": row.get("enrichment_confidence")
            }

            node = {
                "node_id": iid,
                "node_type": NodeType.DRUG.value,
                "display_name": display_name,
                "source_identifier": primary_src_id,
                "entity_status": row["entity_type"],
                "confidence": row.get("enrichment_confidence", "UNENRICHED"),
                "properties_json": json.dumps(props)
            }
            self.nodes.append(node)
            
        logger.info(f"Built {len(nodes_df)} Drug nodes.")

    def _build_rxnorm_nodes_and_edges(self):
        logger.info("Building RxNormConcept nodes and HAS_RXNORM_CONCEPT edges...")
        enr_df = pd.read_csv(self.enr_dir / "rxnorm_drug_enrichment.csv")
        resolved = enr_df[enr_df["rxcui"].notna() & (enr_df["rxcui"] != "")].copy()
        
        # Deduplicate concepts
        concepts: Dict[str, Dict] = {}
        for _, row in resolved.iterrows():
            rxcui_str = str(int(row["rxcui"]))
            if rxcui_str not in concepts:
                concepts[rxcui_str] = {
                    "rxcui": rxcui_str,
                    "rxnorm_name": row.get("rxnorm_name"),
                    "rxnorm_tty": row.get("rxnorm_tty"),
                    "rxnorm_synonym": row.get("rxnorm_synonym"),
                    "rxnorm_language": row.get("rxnorm_language")
                }

        for rxcui_str, cdata in concepts.items():
            node = {
                "node_id": f"RXCUI_{rxcui_str}",
                "node_type": NodeType.RXNORM_CONCEPT.value,
                "display_name": cdata["rxnorm_name"],
                "source_identifier": rxcui_str,
                "entity_status": "OFFICIAL_RXNORM_CONCEPT",
                "confidence": "HIGH_EXACT",
                "properties_json": json.dumps(cdata)
            }
            self.nodes.append(node)

        # Build HAS_RXNORM_CONCEPT edges
        edge_idx = 1
        for _, row in resolved.iterrows():
            iid = row["internal_drug_id"]
            rxcui_str = str(int(row["rxcui"]))
            conf = row.get("enrichment_confidence", "HIGH_EXACT")
            
            props = {
                "mapping_method": row.get("rxnorm_match_method"),
                "resolution_status": row.get("rxnorm_match_status"),
                "match_score": row.get("match_score"),
                "source_dataset": "RxNorm",
                "provenance": "rxnorm_drug_enrichment.csv"
            }
            
            edge = {
                "edge_id": f"E_RXN_{edge_idx:06d}",
                "source_node_id": iid,
                "target_node_id": f"RXCUI_{rxcui_str}",
                "relationship_type": RelationshipType.HAS_RXNORM_CONCEPT.value,
                "source_dataset": "RxNorm",
                "source_record_id": f"RXN:{iid}:{rxcui_str}",
                "mapping_confidence": conf,
                "evidence_confidence": "HIGH_AUTHORITATIVE",
                "properties_json": json.dumps(props)
            }
            self.edges.append(edge)
            self.rxnorm_edges.append(edge)
            edge_idx += 1
            
        logger.info(f"Built {len(concepts)} RxNormConcept nodes and {len(self.rxnorm_edges)} HAS_RXNORM_CONCEPT edges.")

    def _build_side_effect_nodes(self):
        logger.info("Building SideEffect nodes...")
        se_df = pd.read_csv(self.norm_dir / "twosides_side_effects_normalized.csv")
        for _, row in se_df.iterrows():
            se_id = str(row["side_effect_id"]).strip()
            se_name = row["side_effect_name"]
            
            node = {
                "node_id": f"SE_{se_id}",
                "node_type": NodeType.SIDE_EFFECT.value,
                "display_name": se_name,
                "source_identifier": se_id,
                "entity_status": "STANDARDIZED_ADVERSE_EVENT",
                "confidence": "HIGH_CONFIRMED",
                "properties_json": json.dumps({
                    "side_effect_id": se_id,
                    "side_effect_name": se_name,
                    "source_dataset": "twosides"
                })
            }
            self.nodes.append(node)
        logger.info(f"Built {len(se_df)} SideEffect nodes.")

    def _build_drugbank_interaction_edges(self):
        logger.info("Building DrugBank INTERACTS_WITH edges...")
        ddi_df = pd.read_csv(self.norm_dir / "drugbank_interactions_normalized.csv")
        
        ddi_df["src_int"] = ddi_df["source_drugbank_id"].astype(str).str.strip().map(lambda x: self.source_to_internal.get(("drugbank", x)))
        ddi_df["tgt_int"] = ddi_df["target_drugbank_id"].astype(str).str.strip().map(lambda x: self.source_to_internal.get(("drugbank", x)))

        valid_ddi = ddi_df.dropna(subset=["src_int", "tgt_int"]).copy()
        unmapped_ddi = ddi_df[ddi_df["src_int"].isna() | ddi_df["tgt_int"].isna()]

        for _, row in unmapped_ddi.iterrows():
            self.unmapped_relationships.append({
                "source_dataset": "drugbank",
                "source_record": f"{row['source_drugbank_id']} -> {row['target_drugbank_id']}",
                "reason": "Source DrugBank identifier unmapped to integrated entity"
            })

        for i, row in enumerate(valid_ddi.to_dict(orient="records"), start=1):
            src_db = row["source_drugbank_id"]
            tgt_db = row["target_drugbank_id"]
            src_int = row["src_int"]
            tgt_int = row["tgt_int"]
            
            props = {
                "source_drugbank_id_1": src_db,
                "source_drugbank_id_2": tgt_db,
                "interaction_label": row["interaction_label"],
                "interaction_description": row["interaction_description"],
                "directionality": "DIRECTED_ASSERTION",
                "provenance": "drugbank_interactions_normalized.csv"
            }
            
            edge = {
                "edge_id": f"E_DDI_{i:06d}",
                "source_node_id": src_int,
                "target_node_id": tgt_int,
                "relationship_type": RelationshipType.INTERACTS_WITH.value,
                "source_dataset": "drugbank",
                "source_record_id": f"DDI:{src_db}:{tgt_db}",
                "mapping_confidence": "HIGH_CONFIRMED",
                "evidence_confidence": "DIRECTED_DDI_RECORD",
                "properties_json": json.dumps(props)
            }
            self.edges.append(edge)
            self.interaction_edges.append(edge)
            
        logger.info(f"Built {len(self.interaction_edges)} INTERACTS_WITH edges (unmapped: {len(unmapped_ddi)}).")

    def _build_twosides_pair_nodes_and_edges(self):
        logger.info("Building DrugPair nodes, MEMBER_OF_PAIR edges, and ASSOCIATED_WITH side effect edges...")
        rel_df = pd.read_csv(self.norm_dir / "twosides_relationships_normalized.csv", usecols=["drug1", "drug2", "side_effect_id"])
        
        unique_pairs = rel_df[["drug1", "drug2"]].drop_duplicates().copy()
        logger.info(f"Processing {len(unique_pairs)} unique TWOSIDES drug pairs...")

        obs_id_map: Dict[Tuple[str, str], str] = {}
        mem_edge_idx = 1

        for _, r in unique_pairs.iterrows():
            d1 = str(r["drug1"]).strip()
            d2 = str(r["drug2"]).strip()
            
            d1_int = self.source_to_internal.get(("twosides", d1))
            d2_int = self.source_to_internal.get(("twosides", d2))
            
            # Deterministic sorted internal pair ID
            if d1_int and d2_int:
                sorted_pair = sorted([d1_int, d2_int])
                pair_node_id = f"PAIR_{sorted_pair[0]}__{sorted_pair[1]}"
            else:
                sorted_cids = sorted([d1, d2])
                pair_node_id = f"PAIR_{sorted_cids[0]}__{sorted_cids[1]}"
                
            obs_id_map[(d1, d2)] = pair_node_id
            
            props = {
                "drug1_twosides_id": d1,
                "drug2_twosides_id": d2,
                "drug1_internal_id": d1_int,
                "drug2_internal_id": d2_int,
                "pair_ordering_semantics": "CANONICAL_UNDIRECTED_PAIR",
                "source_dataset": "twosides"
            }
            
            pair_node = {
                "node_id": pair_node_id,
                "node_type": NodeType.DRUG_PAIR.value,
                "display_name": f"Drug Pair: {d1_int or d1} + {d2_int or d2}",
                "source_identifier": f"{d1}_{d2}",
                "entity_status": "REIFIED_DRUG_PAIR_OBSERVATION",
                "confidence": "HIGH_CONFIRMED",
                "properties_json": json.dumps(props)
            }
            self.nodes.append(pair_node)
            self.pair_nodes.append(pair_node)
            
            # Exactly 2 MEMBER_OF_PAIR edges per pair
            if d1_int:
                mem_edge_1 = {
                    "edge_id": f"E_MEM_{mem_edge_idx:07d}",
                    "source_node_id": d1_int,
                    "target_node_id": pair_node_id,
                    "relationship_type": RelationshipType.MEMBER_OF_PAIR.value,
                    "source_dataset": "twosides",
                    "source_record_id": f"PAIR_MEMBER:{d1_int}:{pair_node_id}",
                    "mapping_confidence": "HIGH_CONFIRMED",
                    "evidence_confidence": "PAIR_CONSTITUENT_MEMBER",
                    "properties_json": json.dumps({"role": "drug1", "source_twosides_id": d1})
                }
                self.edges.append(mem_edge_1)
                self.pair_membership_edges.append(mem_edge_1)
                mem_edge_idx += 1
                
            if d2_int:
                mem_edge_2 = {
                    "edge_id": f"E_MEM_{mem_edge_idx:07d}",
                    "source_node_id": d2_int,
                    "target_node_id": pair_node_id,
                    "relationship_type": RelationshipType.MEMBER_OF_PAIR.value,
                    "source_dataset": "twosides",
                    "source_record_id": f"PAIR_MEMBER:{d2_int}:{pair_node_id}",
                    "mapping_confidence": "HIGH_CONFIRMED",
                    "evidence_confidence": "PAIR_CONSTITUENT_MEMBER",
                    "properties_json": json.dumps({"role": "drug2", "source_twosides_id": d2})
                }
                self.edges.append(mem_edge_2)
                self.pair_membership_edges.append(mem_edge_2)
                mem_edge_idx += 1

        logger.info(f"Built {len(self.pair_nodes)} DrugPair nodes and {len(self.pair_membership_edges)} MEMBER_OF_PAIR edges.")

        logger.info("Connecting DrugPair nodes to SideEffect concepts (ASSOCIATED_WITH)...")
        distinct_events = rel_df.drop_duplicates()
        
        for i, row in enumerate(distinct_events.to_dict(orient="records"), start=1):
            d1 = str(row["drug1"]).strip()
            d2 = str(row["drug2"]).strip()
            se_id = str(row["side_effect_id"]).strip()
            pair_node_id = obs_id_map.get((d1, d2))
            
            if pair_node_id:
                props = {
                    "source_drug_1": d1,
                    "source_drug_2": d2,
                    "side_effect_id": se_id,
                    "provenance": "twosides_relationships_normalized.csv"
                }
                se_edge = {
                    "edge_id": f"E_SE_{i:08d}",
                    "source_node_id": pair_node_id,
                    "target_node_id": f"SE_{se_id}",
                    "relationship_type": RelationshipType.ASSOCIATED_WITH.value,
                    "source_dataset": "twosides",
                    "source_record_id": f"TWOSIDES_EVENT:{d1}:{d2}:{se_id}",
                    "mapping_confidence": "HIGH_CONFIRMED",
                    "evidence_confidence": "OBSERVED_ADVERSE_EVENT",
                    "properties_json": json.dumps(props)
                }
                self.edges.append(se_edge)
                self.pair_side_effect_edges.append(se_edge)
                
        logger.info(f"Built {len(self.pair_side_effect_edges)} ASSOCIATED_WITH side effect edges.")

    def _export_all(self):
        logger.info("Writing canonical graph tables and relationship-specific exports...")
        nodes_df = pd.DataFrame(self.nodes, columns=NODE_SCHEMA)
        edges_df = pd.DataFrame(self.edges, columns=EDGE_SCHEMA)

        # 1. Canonical graph tables
        nodes_df.to_csv(self.graph_dir / "graph_nodes.csv", index=False)
        edges_df.to_csv(self.graph_dir / "graph_edges.csv", index=False)

        # 2. Relationship-specific exports
        pd.DataFrame(self.rxnorm_edges).to_csv(self.graph_dir / "drug_rxnorm_edges.csv", index=False)
        pd.DataFrame(self.interaction_edges).to_csv(self.graph_dir / "drug_interaction_edges.csv", index=False)
        pd.DataFrame(self.pair_nodes).to_csv(self.graph_dir / "drug_pair_nodes.csv", index=False)
        pd.DataFrame(self.pair_membership_edges).to_csv(self.graph_dir / "drug_pair_membership_edges.csv", index=False)
        pd.DataFrame(self.pair_side_effect_edges).to_csv(self.graph_dir / "drug_pair_side_effect_edges.csv", index=False)

        # 3. Schema & summary JSONs
        build_summary = {
            "total_nodes": len(nodes_df),
            "total_edges": len(edges_df),
            "node_type_counts": nodes_df["node_type"].value_counts().to_dict(),
            "relationship_type_counts": edges_df["relationship_type"].value_counts().to_dict(),
            "drug_node_count": int((nodes_df["node_type"] == NodeType.DRUG.value).sum()),
            "rxnorm_concept_count": int((nodes_df["node_type"] == NodeType.RXNORM_CONCEPT.value).sum()),
            "drug_pair_count": int((nodes_df["node_type"] == NodeType.DRUG_PAIR.value).sum()),
            "side_effect_count": int((nodes_df["node_type"] == NodeType.SIDE_EFFECT.value).sum()),
            "has_rxnorm_concept_edge_count": len(self.rxnorm_edges),
            "interacts_with_edge_count": len(self.interaction_edges),
            "member_of_pair_edge_count": len(self.pair_membership_edges),
            "associated_with_edge_count": len(self.pair_side_effect_edges),
            "unmapped_relationship_count": len(self.unmapped_relationships)
        }

        with open(self.graph_dir / "graph_build_summary.json", "w") as f:
            json.dump(build_summary, f, indent=4)

        schema_dict = {
            "node_schema": NODE_SCHEMA,
            "edge_schema": EDGE_SCHEMA,
            "node_types": list(NodeType.__members__.keys()),
            "relationship_types": list(RelationshipType.__members__.keys())
        }
        with open(self.graph_dir / "graph_schema.json", "w") as f:
            json.dump(schema_dict, f, indent=4)

        logger.info(f"Graph successfully exported to {self.graph_dir}. Total Nodes: {len(nodes_df)}, Total Edges: {len(edges_df)}.")
