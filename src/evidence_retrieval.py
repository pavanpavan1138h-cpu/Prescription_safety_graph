"""
evidence_retrieval.py (chunked fast streaming for side effects)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import pandas as pd

from reasoning_schema import (
    DrugIdentity,
    DDIEvidenceRecord,
    SideEffectRecord,
    PairEvidenceBundle
)

logger = logging.getLogger(__name__)

class EvidenceRetriever:
    def __init__(self, graph_dir: Path):
        self.graph_dir = graph_dir

        self.drug_by_id: Dict[str, DrugIdentity] = {}
        self.drug_by_drugbank: Dict[str, str] = {}
        self.drug_by_twosides: Dict[str, str] = {}
        self.drug_by_rxcui: Dict[str, str] = {}
        self.drug_by_name: Dict[str, str] = {}

        self.ddi_index: Dict[Tuple[str, str], List[DDIEvidenceRecord]] = {}
        self.pair_id_index: Dict[Tuple[str, str], str] = {}
        self.side_effects: Dict[str, str] = {}
        
        # Lazy/on-demand or grouped side effect counts
        self.pair_side_effects_counts: Dict[str, int] = {}
        self.pair_side_effects_samples: Dict[str, List[SideEffectRecord]] = {}

        self.loaded = False

    def load(self):
        if self.loaded:
            return

        logger.info("Loading Phase 4 graph indexes into EvidenceRetriever...")
        
        # 1. Load Nodes
        nodes_df = pd.read_csv(self.graph_dir / "graph_nodes.csv")
        for _, row in nodes_df.iterrows():
            nid = row["node_id"]
            ntype = row["node_type"]
            dname = row["display_name"]
            
            if ntype == "Drug":
                props = json.loads(row["properties_json"])
                drug_obj = DrugIdentity(
                    internal_drug_id=nid,
                    display_name=dname if pd.notna(dname) else None,
                    entity_status=row["entity_status"],
                    source_membership=props.get("source_membership"),
                    rxcui=props.get("rxcui"),
                    rxnorm_name=props.get("rxnorm_name"),
                    rxnorm_match_status=props.get("rxnorm_match_status"),
                    drugbank_ids=props.get("drugbank_ids", []),
                    twosides_cids=props.get("twosides_cids", [])
                )
                self.drug_by_id[nid] = drug_obj

                if dname and pd.notna(dname):
                    self.drug_by_name[dname.lower().strip()] = nid
                if props.get("name_candidate"):
                    self.drug_by_name[props["name_candidate"].lower().strip()] = nid

                for db in props.get("drugbank_ids", []):
                    self.drug_by_drugbank[db.strip()] = nid
                for tw in props.get("twosides_cids", []):
                    self.drug_by_twosides[tw.strip()] = nid
                if props.get("rxcui"):
                    self.drug_by_rxcui[str(props["rxcui"]).strip()] = nid

            elif ntype == "SideEffect":
                self.side_effects[nid] = dname if pd.notna(dname) else nid

            elif ntype == "DrugPair":
                props = json.loads(row["properties_json"])
                d1 = props.get("drug1_internal_id")
                d2 = props.get("drug2_internal_id")
                if d1 and d2:
                    sorted_pair = tuple(sorted([d1, d2]))
                    self.pair_id_index[sorted_pair] = nid

        logger.info(f"Loaded {len(self.drug_by_id)} Drug nodes and {len(self.side_effects)} SideEffect concepts.")

        # 2. Load DDI Edges
        ddi_df = pd.read_csv(self.graph_dir / "drug_interaction_edges.csv")
        for row in ddi_df.to_dict(orient="records"):
            s = row["source_node_id"]
            t = row["target_node_id"]
            props = json.loads(row["properties_json"])
            
            rec = DDIEvidenceRecord(
                edge_id=row["edge_id"],
                source_drug_id=s,
                target_drug_id=t,
                source_drugbank_id_1=props.get("source_drugbank_id_1", ""),
                source_drugbank_id_2=props.get("source_drugbank_id_2", ""),
                interaction_description=props.get("interaction_description", ""),
                interaction_label=props.get("interaction_label"),
                directionality=props.get("directionality", "DIRECTED_ASSERTION"),
                mapping_confidence=row["mapping_confidence"],
                evidence_confidence=row["evidence_confidence"]
            )
            self.ddi_index.setdefault((s, t), []).append(rec)
            
        logger.info(f"Indexed {len(ddi_df)} DDI edges.")

        # 3. Stream/Group Side Effect counts and sample top records in chunks for high performance
        logger.info("Indexing TWOSIDES combination side effects in streaming chunks...")
        chunk_size = 500000
        for chunk in pd.read_csv(self.graph_dir / "drug_pair_side_effect_edges.csv", usecols=["edge_id", "source_node_id", "target_node_id", "properties_json"], chunksize=chunk_size):
            for row in chunk.to_dict(orient="records"):
                pair_nid = row["source_node_id"]
                self.pair_side_effects_counts[pair_nid] = self.pair_side_effects_counts.get(pair_nid, 0) + 1
                
                # Keep up to 10 sample records per pair for fast reasoning traces
                samples = self.pair_side_effects_samples.setdefault(pair_nid, [])
                if len(samples) < 10:
                    se_nid = row["target_node_id"]
                    props = json.loads(row["properties_json"])
                    se_name = self.side_effects.get(se_nid, se_nid)
                    samples.append(SideEffectRecord(
                        edge_id=row["edge_id"],
                        side_effect_id=props.get("side_effect_id", se_nid.replace("SE_", "")),
                        side_effect_name=se_name,
                        drug_pair_id=pair_nid,
                        source_drug_1=props.get("source_drug_1", ""),
                        source_drug_2=props.get("source_drug_2", "")
                    ))

        logger.info(f"Indexed side effects across {len(self.pair_side_effects_counts)} DrugPair combinations.")
        self.loaded = True

    def resolve_drug(self, identifier: str) -> Optional[DrugIdentity]:
        self.load()
        q = str(identifier).strip()
        
        if q in self.drug_by_id:
            return self.drug_by_id[q]
        if q in self.drug_by_drugbank:
            return self.drug_by_id[self.drug_by_drugbank[q]]
        if q in self.drug_by_twosides:
            return self.drug_by_id[self.drug_by_twosides[q]]
        if q in self.drug_by_rxcui:
            return self.drug_by_id[self.drug_by_rxcui[q]]
            
        q_lower = q.lower()
        if q_lower in self.drug_by_name:
            return self.drug_by_id[self.drug_by_name[q_lower]]
            
        return None

    def retrieve_pair_evidence(self, drug_a_id: str, drug_b_id: str) -> PairEvidenceBundle:
        self.load()
        
        drug_a = self.drug_by_id.get(drug_a_id) or DrugIdentity(internal_drug_id=drug_a_id, display_name=None, entity_status="UNKNOWN")
        drug_b = self.drug_by_id.get(drug_b_id) or DrugIdentity(internal_drug_id=drug_b_id, display_name=None, entity_status="UNKNOWN")

        fwd_ddi = self.ddi_index.get((drug_a_id, drug_b_id), [])
        rev_ddi = self.ddi_index.get((drug_b_id, drug_a_id), [])

        sorted_pair = tuple(sorted([drug_a_id, drug_b_id]))
        pair_node_id = self.pair_id_index.get(sorted_pair)

        side_effects_samples = []
        total_count = 0
        if pair_node_id:
            total_count = self.pair_side_effects_counts.get(pair_node_id, 0)
            side_effects_samples = self.pair_side_effects_samples.get(pair_node_id, [])

        return PairEvidenceBundle(
            drug_a=drug_a,
            drug_b=drug_b,
            drug_pair_node_id=pair_node_id,
            ddi_records_forward=fwd_ddi,
            ddi_records_reverse=rev_ddi,
            side_effect_records=side_effects_samples,
            total_side_effects_count=total_count
        )
