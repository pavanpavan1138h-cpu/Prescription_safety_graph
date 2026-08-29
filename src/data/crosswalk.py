import logging
import json
from pathlib import Path
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)

def build_connected_components(crosswalk_df: pd.DataFrame, db_drugs: list, ts_drugs: list) -> list:
    """
    Build connected components (clusters) of drug IDs using adjacency list representation.
    
    Returns a list of dicts: [{"db_ids": [...], "ts_ids": [...]}]
    """
    # Build graph adjacency list
    adj = defaultdict(set)
    for _, row in crosswalk_df.iterrows():
        db_id = row["drugbank_id"]
        ts_id = row["twosides_id"]
        adj[db_id].add(ts_id)
        adj[ts_id].add(db_id)
        
    visited = set()
    components = []
    
    # 1. Process all nodes present in the crosswalk mappings
    all_mapped_nodes = set(crosswalk_df["drugbank_id"]).union(set(crosswalk_df["twosides_id"]))
    
    for node in sorted(all_mapped_nodes):
        if node in visited:
            continue
            
        # BFS to find connected component
        comp_db = []
        comp_ts = []
        queue = [node]
        visited.add(node)
        
        while queue:
            curr = queue.pop(0)
            if curr.startswith("DB"):
                comp_db.append(curr)
            else:
                comp_ts.append(curr)
                
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        components.append({
            "db_ids": sorted(comp_db),
            "ts_ids": sorted(comp_ts)
        })
        
    # 2. Add unmapped DrugBank drugs as single-drug components
    mapped_db = set(crosswalk_df["drugbank_id"])
    for db_id in sorted(db_drugs):
        if db_id not in mapped_db:
            components.append({
                "db_ids": [db_id],
                "ts_ids": []
            })
            
    # 3. Add unmapped TWOSIDES drugs as single-drug components
    mapped_ts = set(crosswalk_df["twosides_id"])
    for ts_id in sorted(ts_drugs):
        if ts_id not in mapped_ts:
            components.append({
                "db_ids": [],
                "ts_ids": [ts_id]
            })
            
    # Deterministic sorting of components
    def component_sort_key(comp):
        if comp["db_ids"]:
            return (0, comp["db_ids"][0])
        else:
            return (1, comp["ts_ids"][0])
            
    components.sort(key=component_sort_key)
    return components

def integrate_drug_entities(
    crosswalk_path: Path,
    db_drugs_df: pd.DataFrame,
    ts_drugs_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """
    Integrate drugs using crosswalk file and build mapping validation reports.
    Distinguishes CONFIRMED_INTEGRATED_ENTITY from AMBIGUOUS_MAPPING_COMPONENT.
    """
    if not crosswalk_path.exists():
        raise FileNotFoundError(f"Crosswalk file not found at {crosswalk_path}")
        
    logger.info(f"Loading crosswalk from {crosswalk_path}...")
    crosswalk_df = pd.read_csv(crosswalk_path)
    
    db_ids = db_drugs_df["drugbank_id"].unique().tolist()
    ts_ids = ts_drugs_df["twosides_id"].unique().tolist()
    
    # 1. Build connected components (candidate mapping components)
    components = build_connected_components(crosswalk_df, db_ids, ts_ids)
    logger.info(f"Total candidate mapping components created: {len(components)}")
    
    # Pre-build lookup dictionaries for fast SMILES/InChIKey extraction
    db_lookup = db_drugs_df.set_index("drugbank_id").to_dict(orient="index")
    ts_lookup = ts_drugs_df.set_index("twosides_id").to_dict(orient="index")
    
    # Mapping confidence lookup
    mapping_conf_lookup = {}
    for _, row in crosswalk_df.iterrows():
        mapping_conf_lookup[(row["drugbank_id"], row["twosides_id"])] = row["mapping_confidence"]
        
    integrated_nodes = []
    integrated_mappings = []
    mapping_edges = []
    
    # Mapping stats counts
    one_to_one_count = 0
    one_to_many_count = 0
    many_to_one_count = 0
    ambiguous_count = 0
    
    # Global counter for generating DRUG_XXXXXX IDs
    drug_id_counter = 1
    
    for comp in components:
        db_list = comp["db_ids"]
        ts_list = comp["ts_ids"]
        
        # Check mapping structure type
        is_ambiguous = len(db_list) > 1 or len(ts_list) > 1
        
        if db_list and ts_list:
            if len(db_list) == 1 and len(ts_list) == 1:
                one_to_one_count += 1
            elif len(db_list) == 1 and len(ts_list) > 1:
                one_to_many_count += 1
            elif len(db_list) > 1 and len(ts_list) == 1:
                many_to_one_count += 1
            else:
                ambiguous_count += 1
                
            # Add mapping edges to dedicated table
            for db_id in db_list:
                for ts_id in ts_list:
                    if (db_id, ts_id) in mapping_conf_lookup:
                        mapping_edges.append({
                            "drugbank_id": db_id,
                            "twosides_id": ts_id,
                            "mapping_confidence": mapping_conf_lookup[(db_id, ts_id)]
                        })
                        
        if not is_ambiguous:
            # Unambiguous component: 1-to-1 mapping, or unmapped single drug
            internal_id = f"DRUG_{drug_id_counter:06d}"
            drug_id_counter += 1
            
            source_membership = "both" if (db_list and ts_list) else ("drugbank_only" if db_list else "twosides_only")
            
            # Extract structure
            canonical_smiles = None
            inchikey = None
            if db_list:
                info = db_lookup.get(db_list[0], {})
                canonical_smiles = info.get("canonical_smiles")
                inchikey = info.get("inchikey")
            elif ts_list:
                info = ts_lookup.get(ts_list[0], {})
                canonical_smiles = info.get("canonical_smiles")
                inchikey = info.get("inchikey")
                
            integrated_nodes.append({
                "internal_drug_id": internal_id,
                "entity_type": "CONFIRMED_INTEGRATED_ENTITY",
                "source_membership": source_membership,
                "canonical_smiles": canonical_smiles,
                "inchikey": inchikey
            })
            
            if db_list:
                integrated_mappings.append({
                    "internal_drug_id": internal_id,
                    "source_dataset": "drugbank",
                    "source_drug_id": db_list[0],
                    "mapping_confidence": mapping_conf_lookup.get((db_list[0], ts_list[0]), "unmapped") if ts_list else "unmapped"
                })
            if ts_list:
                integrated_mappings.append({
                    "internal_drug_id": internal_id,
                    "source_dataset": "twosides",
                    "source_drug_id": ts_list[0],
                    "mapping_confidence": mapping_conf_lookup.get((db_list[0], ts_list[0]), "unmapped") if db_list else "unmapped"
                })
                
        else:
            # Ambiguous component: Do NOT merge them into one entity.
            # Create a separate node for each DrugBank drug and each TWOSIDES drug.
            # Flag all of them as AMBIGUOUS_MAPPING_COMPONENT.
            for db_id in db_list:
                internal_id = f"DRUG_{drug_id_counter:06d}"
                drug_id_counter += 1
                
                info = db_lookup.get(db_id, {})
                integrated_nodes.append({
                    "internal_drug_id": internal_id,
                    "entity_type": "AMBIGUOUS_MAPPING_COMPONENT",
                    "source_membership": "drugbank_only",
                    "canonical_smiles": info.get("canonical_smiles"),
                    "inchikey": info.get("inchikey")
                })
                
                integrated_mappings.append({
                    "internal_drug_id": internal_id,
                    "source_dataset": "drugbank",
                    "source_drug_id": db_id,
                    "mapping_confidence": "ambiguous"
                })
                
            for ts_id in ts_list:
                internal_id = f"DRUG_{drug_id_counter:06d}"
                drug_id_counter += 1
                
                info = ts_lookup.get(ts_id, {})
                integrated_nodes.append({
                    "internal_drug_id": internal_id,
                    "entity_type": "AMBIGUOUS_MAPPING_COMPONENT",
                    "source_membership": "twosides_only",
                    "canonical_smiles": info.get("canonical_smiles"),
                    "inchikey": info.get("inchikey")
                })
                
                integrated_mappings.append({
                    "internal_drug_id": internal_id,
                    "source_dataset": "twosides",
                    "source_drug_id": ts_id,
                    "mapping_confidence": "ambiguous"
                })
                
    nodes_df = pd.DataFrame(integrated_nodes)
    mappings_df = pd.DataFrame(integrated_mappings)
    edges_df = pd.DataFrame(mapping_edges)
    
    # Calculate mapping validation reports
    confidence_counts = crosswalk_df["mapping_confidence"].value_counts().to_dict()
    
    validation_report = {
        "total_mappings": len(crosswalk_df),
        "confidence_distribution": confidence_counts,
        "relationship_types": {
            "one_to_one": one_to_one_count,
            "one_to_many": one_to_many_count,
            "many_to_one": many_to_one_count,
            "many_to_many_ambiguous": ambiguous_count
        },
        "coverage": {
            "mapped_drugbank_drugs": int(crosswalk_df["drugbank_id"].nunique()),
            "total_drugbank_drugs": len(db_ids),
            "mapped_twosides_drugs": int(crosswalk_df["twosides_id"].nunique()),
            "total_twosides_drugs": len(ts_ids)
        }
    }
    
    return nodes_df, mappings_df, edges_df, validation_report
