import os
import json
import logging
import re
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from rdkit import Chem
from rdkit.Chem import inchi

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_validation_dir(project_root: Path) -> Path:
    val_dir = project_root / "data" / "interim" / "validation"
    val_dir.mkdir(parents=True, exist_ok=True)
    return val_dir

def run_raw_validation(project_root: Path, val_dir: Path) -> dict:
    logger.info("A. Running Raw Dataset Validation...")
    db_file = project_root / "data" / "raw" / "tdc" / "drugbank.tab"
    ts_file = project_root / "data" / "raw" / "twosides" / "twosides.csv"
    
    report = {
        "drugbank": {"exists": False},
        "twosides": {"exists": False}
    }
    
    # 1. DrugBank Tab Validation
    if db_file.exists():
        report["drugbank"]["exists"] = True
        try:
            # Check delimiter
            with open(db_file, 'r') as f:
                header = f.readline()
            report["drugbank"]["raw_header"] = header.strip()
            
            db_df = pd.read_csv(db_file, sep='\t', quotechar='"')
            db_df.columns = [col.replace("\\t", "").replace("\t", "").strip() for col in db_df.columns]
            
            report["drugbank"]["columns"] = list(db_df.columns)
            report["drugbank"]["row_count"] = len(db_df)
            
            all_drugs = pd.concat([db_df["ID1"], db_df["ID2"]]).dropna().unique()
            report["drugbank"]["unique_drugs_count"] = len(all_drugs)
            
            # Check ID format (DrugBank IDs start with DB)
            invalid_db_ids = [str(did) for did in all_drugs if not str(did).startswith("DB")]
            report["drugbank"]["invalid_id_format_count"] = len(invalid_db_ids)
            report["drugbank"]["invalid_id_format_examples"] = invalid_db_ids[:5]
            
            report["drugbank"]["missing_values"] = db_df.isna().sum().to_dict()
            report["drugbank"]["duplicate_rows"] = int(db_df.duplicated().sum())
            
            # Molecular structures availability
            x1_valid = db_df["X1"].dropna().nunique()
            x2_valid = db_df["X2"].dropna().nunique()
            report["drugbank"]["molecular_structures"] = {
                "unique_X1": x1_valid,
                "unique_X2": x2_valid
            }
        except Exception as e:
            report["drugbank"]["error"] = str(e)
            logger.error(f"Error validating raw DrugBank: {e}")
            
    # 2. TWOSIDES CSV Validation
    if ts_file.exists():
        report["twosides"]["exists"] = True
        try:
            ts_df = pd.read_csv(ts_file, sep=',', quotechar='"')
            ts_df.columns = [col.strip() for col in ts_df.columns]
            
            report["twosides"]["columns"] = list(ts_df.columns)
            report["twosides"]["row_count"] = len(ts_df)
            
            all_ts_drugs = pd.concat([ts_df["ID1"], ts_df["ID2"]]).dropna().unique()
            report["twosides"]["unique_drugs_count"] = len(all_ts_drugs)
            
            # Check ID format (TWOSIDES IDs start with CID)
            invalid_ts_ids = [str(cid) for cid in all_ts_drugs if not str(cid).startswith("CID")]
            report["twosides"]["invalid_id_format_count"] = len(invalid_ts_ids)
            report["twosides"]["invalid_id_format_examples"] = invalid_ts_ids[:5]
            
            report["twosides"]["missing_values"] = ts_df.isna().sum().to_dict()
            report["twosides"]["duplicate_rows"] = int(ts_df.duplicated().sum())
            
            # Side effect stats
            unique_y = ts_df["Y"].dropna().nunique()
            unique_se_name = ts_df["Side Effect Name"].dropna().nunique()
            report["twosides"]["side_effects"] = {
                "unique_Y_ids": unique_y,
                "unique_names": unique_se_name
            }
        except Exception as e:
            report["twosides"]["error"] = str(e)
            logger.error(f"Error validating raw TWOSIDES: {e}")
            
    with open(val_dir / "raw_dataset_validation_report.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

def run_normalized_validation(project_root: Path, val_dir: Path) -> dict:
    logger.info("B. Running Normalized Output Validation...")
    norm_dir = project_root / "data" / "interim" / "normalized"
    
    files_to_check = [
        "drugbank_drugs_normalized.csv",
        "drugbank_interactions_normalized.csv",
        "twosides_drugs_normalized.csv",
        "twosides_side_effects_normalized.csv",
        "twosides_relationships_normalized.csv",
        "integrated_drug_nodes.csv",
        "integrated_drug_source_mappings.csv",
        "integrated_drug_mapping_edges.csv"
    ]
    
    report = {}
    
    loaded_dfs = {}
    
    for fname in files_to_check:
        fpath = norm_dir / fname
        if not fpath.exists():
            report[fname] = {"exists": False}
            continue
            
        try:
            df = pd.read_csv(fpath)
            loaded_dfs[fname] = df
            
            report[fname] = {
                "exists": True,
                "schema": list(df.columns),
                "row_count": len(df),
                "column_count": len(df.columns),
                "missing_values": df.isna().sum().to_dict(),
                "duplicate_count": int(df.duplicated().sum())
            }
            
            # Count unique identifiers
            id_col = df.columns[0]
            report[fname]["unique_primary_keys"] = int(df[id_col].nunique())
            
            # Sample record
            report[fname]["sample"] = df.head(1).to_dict(orient="records")
        except Exception as e:
            report[fname] = {"exists": True, "error": str(e)}
            logger.error(f"Error validating normalized output {fname}: {e}")
            
    # Referential integrity checks
    ref_integrity = {}
    try:
        if "drugbank_interactions_normalized.csv" in loaded_dfs and "drugbank_drugs_normalized.csv" in loaded_dfs:
            db_drugs = set(loaded_dfs["drugbank_drugs_normalized.csv"]["drugbank_id"])
            db_inters = loaded_dfs["drugbank_interactions_normalized.csv"]
            
            missing_source = db_inters[~db_inters["source_drugbank_id"].isin(db_drugs)]
            missing_target = db_inters[~db_inters["target_drugbank_id"].isin(db_drugs)]
            ref_integrity["drugbank_interactions_referential_errors"] = {
                "source_missing_count": len(missing_source),
                "target_missing_count": len(missing_target)
            }
            
        if "twosides_relationships_normalized.csv" in loaded_dfs and "twosides_drugs_normalized.csv" in loaded_dfs:
            ts_drugs = set(loaded_dfs["twosides_drugs_normalized.csv"]["twosides_id"])
            ts_rels = loaded_dfs["twosides_relationships_normalized.csv"]
            
            missing_drug1 = ts_rels[~ts_rels["drug1"].isin(ts_drugs)]
            missing_drug2 = ts_rels[~ts_rels["drug2"].isin(ts_drugs)]
            ref_integrity["twosides_relationships_referential_errors"] = {
                "drug1_missing_count": len(missing_drug1),
                "drug2_missing_count": len(missing_drug2)
            }
            
        if "integrated_drug_source_mappings.csv" in loaded_dfs and "integrated_drug_nodes.csv" in loaded_dfs:
            int_nodes = set(loaded_dfs["integrated_drug_nodes.csv"]["internal_drug_id"])
            int_maps = loaded_dfs["integrated_drug_source_mappings.csv"]
            
            missing_node = int_maps[~int_maps["internal_drug_id"].isin(int_nodes)]
            ref_integrity["integrated_mappings_referential_errors"] = {
                "node_missing_count": len(missing_node)
            }
    except Exception as e:
        ref_integrity["error"] = str(e)
        logger.error(f"Error performing referential integrity checks: {e}")
        
    report["referential_integrity"] = ref_integrity
    
    with open(val_dir / "pipeline_validation_summary.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

def run_db_relationship_audit(project_root: Path, val_dir: Path) -> dict:
    logger.info("C. Running DrugBank DDI Relationship Audit...")
    db_file = project_root / "data" / "raw" / "tdc" / "drugbank.tab"
    
    report = {}
    if not db_file.exists():
        report["error"] = "DrugBank raw file missing."
        return report
        
    try:
        db_df = pd.read_csv(db_file, sep='\t', quotechar='"')
        db_df.columns = [col.replace("\\t", "").replace("\t", "").strip() for col in db_df.columns]
        
        total_records = len(db_df)
        
        # Directed pairs
        directed_pairs = list(zip(db_df["ID1"], db_df["ID2"]))
        unique_directed = len(set(directed_pairs))
        
        # Repeated drug pairs (directed)
        pair_counts = pd.Series(directed_pairs).value_counts()
        repeated_pairs = int((pair_counts > 1).sum())
        
        # Self-interactions
        self_interactions = int((db_df["ID1"] == db_df["ID2"]).sum())
        
        # Reverse-direction pairs
        pair_set = set(directed_pairs)
        reverse_pairs_count = 0
        for u_pair in pair_set:
            rev_pair = (u_pair[1], u_pair[0])
            if rev_pair in pair_set:
                reverse_pairs_count += 1
                
        # Descriptions variation
        desc_counts = db_df.groupby(["ID1", "ID2"])["Map"].nunique()
        desc_variance = int((desc_counts > 1).sum())
        
        report = {
            "total_raw_ddi_records": total_records,
            "unique_directed_pairs": unique_directed,
            "repeated_directed_pairs": repeated_pairs,
            "reverse_pairs_count": reverse_pairs_count,
            "self_interactions": self_interactions,
            "map_descriptions_variance_count": desc_variance,
            "duplicate_rows": int(db_df.duplicated().sum())
        }
        
    except Exception as e:
        report["error"] = str(e)
        logger.error(f"Error in DrugBank relationship audit: {e}")
        
    with open(val_dir / "drugbank_relationship_audit.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

def run_twosides_relationship_audit(project_root: Path, val_dir: Path) -> dict:
    logger.info("D. Running TWOSIDES Relationship Audit...")
    ts_file = project_root / "data" / "raw" / "twosides" / "twosides.csv"
    
    report = {}
    if not ts_file.exists():
        report["error"] = "TWOSIDES raw file missing."
        return report
        
    try:
        ts_df = pd.read_csv(ts_file, sep=',', quotechar='"')
        ts_df.columns = [col.strip() for col in ts_df.columns]
        
        total_records = len(ts_df)
        
        # Unique drug pairs (directed)
        directed_pairs = list(zip(ts_df["ID1"], ts_df["ID2"]))
        unique_directed_drug_pairs = len(set(directed_pairs))
        
        # Unique side effects
        unique_side_effects = ts_df["Y"].dropna().nunique()
        
        # Duplicate rows
        duplicates = int(ts_df.duplicated().sum())
        
        # Repeated drug-pair / side-effect combinations
        combo_counts = ts_df.groupby(["ID1", "ID2", "Y"]).size()
        repeated_combos = int((combo_counts > 1).sum())
        
        # Self-pairs
        self_pairs = int((ts_df["ID1"] == ts_df["ID2"]).sum())
        
        # Side effects per drug pair distribution
        se_per_pair = ts_df.groupby(["ID1", "ID2"])["Y"].count()
        
        report = {
            "total_records": total_records,
            "unique_directed_drug_pairs": unique_directed_drug_pairs,
            "unique_side_effects": unique_side_effects,
            "duplicate_rows": duplicates,
            "repeated_combos": repeated_combos,
            "self_pairs": self_pairs,
            "side_effects_per_pair_distribution": {
                "min": int(se_per_pair.min()) if len(se_per_pair) > 0 else 0,
                "max": int(se_per_pair.max()) if len(se_per_pair) > 0 else 0,
                "mean": float(se_per_pair.mean()) if len(se_per_pair) > 0 else 0,
                "median": float(se_per_pair.median()) if len(se_per_pair) > 0 else 0,
                "std": float(se_per_pair.std()) if len(se_per_pair) > 1 else 0
            }
        }
    except Exception as e:
        report["error"] = str(e)
        logger.error(f"Error in TWOSIDES relationship audit: {e}")
        
    with open(val_dir / "twosides_relationship_audit.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

def run_deep_crosswalk_audit(project_root: Path, val_dir: Path) -> dict:
    logger.info("E. Running Deep Crosswalk Audit...")
    norm_dir = project_root / "data" / "interim" / "normalized"
    unified_f = norm_dir / "drugbank_twosides_unified_crosswalk.csv"
    high_conf_f = norm_dir / "drugbank_twosides_high_confidence_crosswalk.csv"
    
    report = {}
    if not unified_f.exists():
        report["error"] = "Unified crosswalk file missing."
        return report
        
    try:
        unified_df = pd.read_csv(unified_f)
        
        # 1. Counts
        report["unique_mapping_pairs"] = len(unified_df)
        report["unique_drugbank_mapped"] = int(unified_df["drugbank_id"].nunique())
        report["unique_twosides_mapped"] = int(unified_df["twosides_id"].nunique())
        
        # 2. Confidences
        report["confidence_counts"] = unified_df["mapping_confidence"].value_counts().to_dict()
        
        # 3. Canonical-only vs InChIKey-only vs both
        both_count = len(unified_df[(unified_df["canonical_smiles_match"] == True) & (unified_df["inchikey_match"] == True)])
        canonical_only = len(unified_df[(unified_df["canonical_smiles_match"] == True) & (unified_df["inchikey_match"] != True)])
        inchikey_only = len(unified_df[(unified_df["canonical_smiles_match"] != True) & (unified_df["inchikey_match"] == True)])
        
        report["match_breakdown"] = {
            "both_canonical_and_inchikey": both_count,
            "canonical_smiles_only": canonical_only,
            "inchikey_only": inchikey_only
        }
        
        # 4. Save CSV slices
        # High confidence
        high_conf_df = unified_df[unified_df["mapping_confidence"].isin(["HIGH_EXACT", "HIGH_INCHIKEY"])]
        high_conf_df.to_csv(val_dir / "high_confidence_mappings.csv", index=False)
        
        # Canonical only
        canon_only_df = unified_df[(unified_df["canonical_smiles_match"] == True) & (unified_df["inchikey_match"] != True)]
        canon_only_df.to_csv(val_dir / "canonical_only_mappings.csv", index=False)
        
        # Group by drugbank_id to find one-to-many
        db_group_counts = unified_df.groupby("drugbank_id")["twosides_id"].nunique()
        one_to_many_db = db_group_counts[db_group_counts > 1].index.tolist()
        one_to_many_df = unified_df[unified_df["drugbank_id"].isin(one_to_many_db)]
        one_to_many_df.to_csv(val_dir / "one_to_many_mappings.csv", index=False)
        
        # Group by twosides_id to find many-to-one
        ts_group_counts = unified_df.groupby("twosides_id")["drugbank_id"].nunique()
        many_to_one_ts = ts_group_counts[ts_group_counts > 1].index.tolist()
        many_to_one_df = unified_df[unified_df["twosides_id"].isin(many_to_one_ts)]
        many_to_one_df.to_csv(val_dir / "many_to_one_mappings.csv", index=False)
        
        # Find ambiguous mapping components
        # We can reconstruct connected components of mappings to find ambiguous clusters
        adj = defaultdict(set)
        for _, row in unified_df.iterrows():
            db_id = row["drugbank_id"]
            ts_id = row["twosides_id"]
            adj[db_id].add(ts_id)
            adj[ts_id].add(db_id)
            
        visited = set()
        ambiguous_groups = []
        for node in list(adj.keys()):
            if node in visited:
                continue
            
            # BFS
            comp = []
            queue = [node]
            visited.add(node)
            while queue:
                curr = queue.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        
            comp_db = [x for x in comp if x.startswith("DB")]
            comp_ts = [x for x in comp if not x.startswith("DB")]
            
            if len(comp_db) > 1 or len(comp_ts) > 1:
                # Ambiguous cluster
                for db_id in comp_db:
                    for ts_id in comp_ts:
                        ambiguous_groups.append({
                            "drugbank_id": db_id,
                            "twosides_id": ts_id,
                            "component_db_count": len(comp_db),
                            "component_ts_count": len(comp_ts),
                            "component_db_members": ";".join(comp_db),
                            "component_ts_members": ";".join(comp_ts)
                        })
                        
        ambiguous_groups_df = pd.DataFrame(ambiguous_groups)
        ambiguous_groups_df.to_csv(val_dir / "ambiguous_mapping_groups.csv", index=False)
        
        report["mapping_relationships"] = {
            "one_to_many_distinct_db_count": len(one_to_many_db),
            "many_to_one_distinct_ts_count": len(many_to_one_ts),
            "ambiguous_edges_count": len(ambiguous_groups_df)
        }
        
        # Load normalized drugs to determine unmapped coverage
        db_norm_file = norm_dir / "drugbank_drugs_normalized.csv"
        ts_norm_file = norm_dir / "twosides_drugs_normalized.csv"
        
        if db_norm_file.exists() and ts_norm_file.exists():
            db_drugs = pd.read_csv(db_norm_file)
            ts_drugs = pd.read_csv(ts_norm_file)
            
            mapped_db = set(unified_df["drugbank_id"])
            mapped_ts = set(unified_df["twosides_id"])
            
            unmapped_db_df = db_drugs[~db_drugs["drugbank_id"].isin(mapped_db)]
            unmapped_ts_df = ts_drugs[~ts_drugs["twosides_id"].isin(mapped_ts)]
            
            unmapped_db_df.to_csv(val_dir / "unmapped_drugbank.csv", index=False)
            unmapped_ts_df.to_csv(val_dir / "unmapped_twosides.csv", index=False)
            
            report["coverage"] = {
                "drugbank_total": len(db_drugs),
                "drugbank_mapped": len(mapped_db),
                "drugbank_unmapped": len(unmapped_db_df),
                "drugbank_coverage_pct": float(len(mapped_db) / len(db_drugs)) * 100 if len(db_drugs) > 0 else 0.0,
                
                "twosides_total": len(ts_drugs),
                "twosides_mapped": len(mapped_ts),
                "twosides_unmapped": len(unmapped_ts_df),
                "twosides_coverage_pct": float(len(mapped_ts) / len(ts_drugs)) * 100 if len(ts_drugs) > 0 else 0.0,
            }
            
    except Exception as e:
        report["error"] = str(e)
        logger.error(f"Error in deep crosswalk audit: {e}")
        
    with open(val_dir / "crosswalk_validation_report.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

def run_chemical_mapping_validation(project_root: Path, val_dir: Path) -> dict:
    logger.info("F. Running Chemical Mapping Validation...")
    norm_dir = project_root / "data" / "interim" / "normalized"
    unified_f = norm_dir / "drugbank_twosides_unified_crosswalk.csv"
    db_norm_file = norm_dir / "drugbank_drugs_normalized.csv"
    ts_norm_file = norm_dir / "twosides_drugs_normalized.csv"
    
    report = {
        "mismatches": [],
        "invalid_drugbank_structures": []
    }
    
    if not (unified_f.exists() and db_norm_file.exists() and ts_norm_file.exists()):
        report["error"] = "Required normalized files for chemical audit are missing."
        return report
        
    try:
        unified_df = pd.read_csv(unified_f)
        db_drugs = pd.read_csv(db_norm_file)
        ts_drugs = pd.read_csv(ts_norm_file)
        
        # 1. Identify invalid DrugBank structures
        invalid_db = db_drugs[db_drugs["structure_valid"] == False]
        for _, row in invalid_db.iterrows():
            report["invalid_drugbank_structures"].append({
                "drugbank_id": row["drugbank_id"],
                "raw_smiles": row["raw_smiles"]
            })
            
        # 2. Analyze canonical matches vs InChIKey mismatches
        db_lookup = db_drugs.set_index("drugbank_id").to_dict(orient="index")
        ts_lookup = ts_drugs.set_index("twosides_id").to_dict(orient="index")
        
        mismatch_classifications = defaultdict(int)
        
        for _, row in unified_df.iterrows():
            db_id = row["drugbank_id"]
            ts_id = row["twosides_id"]
            
            db_info = db_lookup.get(db_id, {})
            ts_info = ts_lookup.get(ts_id, {})
            
            canon_match = row["canonical_smiles_match"]
            ikey_match = row["inchikey_match"]
            
            if canon_match and not ikey_match:
                # Investigate mismatch
                db_smiles = db_info.get("canonical_smiles")
                ts_smiles = ts_info.get("canonical_smiles")
                
                db_ikey = db_info.get("inchikey")
                ts_ikey = ts_info.get("inchikey")
                
                db_iso_smiles = db_info.get("isomeric_smiles")
                ts_iso_smiles = ts_info.get("isomeric_smiles")
                
                category = "UNRESOLVED_STRUCTURE_DIFFERENCE"
                
                if db_ikey and ts_ikey:
                    # InChIKeys are 27 characters (AAAAA-BBBBB-C)
                    # First block: 14 chars (molecular skeleton/connectivity)
                    # Second block: 10 chars (stereochemistry, isotope variation, protonation)
                    db_ikey_parts = db_ikey.split("-")
                    ts_ikey_parts = ts_ikey.split("-")
                    
                    if len(db_ikey_parts) >= 2 and len(ts_ikey_parts) >= 2:
                        db_block1, db_block2 = db_ikey_parts[0], db_ikey_parts[1]
                        ts_block1, ts_block2 = ts_ikey_parts[0], ts_ikey_parts[1]
                        
                        if db_block1 == ts_block1:
                            # Skeleton is identical, so it must be stereochemistry or isotope or charge difference
                            if db_iso_smiles != ts_iso_smiles:
                                category = "stereochemistry"
                            else:
                                # Check formal charges or molecular formula if needed
                                try:
                                    db_mol = Chem.MolFromSmiles(db_smiles)
                                    ts_mol = Chem.MolFromSmiles(ts_smiles)
                                    if db_mol and ts_mol:
                                        db_charge = Chem.GetFormalCharge(db_mol)
                                        ts_charge = Chem.GetFormalCharge(ts_mol)
                                        if db_charge != ts_charge:
                                            category = "charge_variation"
                                        else:
                                            # Check isotopes
                                            db_has_iso = any(atom.GetIsotope() > 0 for atom in db_mol.GetAtoms())
                                            ts_has_iso = any(atom.GetIsotope() > 0 for atom in ts_mol.GetAtoms())
                                            if db_has_iso or ts_has_iso:
                                                category = "isotope_variation"
                                except Exception:
                                    pass
                        else:
                            # Skeletons differ. Check if multiple components (salts)
                            if "." in str(db_smiles) or "." in str(ts_smiles):
                                category = "salt_variation"
                                
                mismatch_classifications[category] += 1
                report["mismatches"].append({
                    "drugbank_id": db_id,
                    "twosides_id": ts_id,
                    "drugbank_inchikey": db_ikey,
                    "twosides_inchikey": ts_ikey,
                    "drugbank_isomeric_smiles": db_iso_smiles,
                    "twosides_isomeric_smiles": ts_iso_smiles,
                    "classification": category
                })
                
        report["mismatch_summary"] = dict(mismatch_classifications)
        
    except Exception as e:
        report["error"] = str(e)
        logger.error(f"Error running chemical mapping validation: {e}")
        
    with open(val_dir / "chemical_mapping_audit.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

def run_integrated_entity_validation(project_root: Path, val_dir: Path) -> dict:
    logger.info("G. Running Integrated Entity Validation...")
    norm_dir = project_root / "data" / "interim" / "normalized"
    nodes_f = norm_dir / "integrated_drug_nodes.csv"
    mappings_f = norm_dir / "integrated_drug_source_mappings.csv"
    
    report = {
        "files_exist": False
    }
    
    if not (nodes_f.exists() and mappings_f.exists()):
        logger.warning("Integrated entity files do not exist.")
        report["files_exist"] = False
        with open(val_dir / "integrated_entity_validation.json", 'w') as f:
            json.dump(report, f, indent=4)
        return report
        
    try:
        report["files_exist"] = True
        nodes_df = pd.read_csv(nodes_f)
        mappings_df = pd.read_csv(mappings_f)
        
        # 1. Deterministic IDs validation
        pattern = re.compile(r"^DRUG_\d{6}$")
        all_ids_valid = nodes_df["internal_drug_id"].apply(lambda x: bool(pattern.match(str(x)))).all()
        report["deterministic_ids_format_valid"] = bool(all_ids_valid)
        
        # 2. Check duplicate internal IDs
        duplicate_nodes = int(nodes_df["internal_drug_id"].duplicated().sum())
        report["duplicate_internal_ids_count"] = duplicate_nodes
        
        # 3. Check inconsistent source identifier assignments
        # A source drug_id must not map to multiple different internal_drug_ids
        source_groups = mappings_df.groupby(["source_dataset", "source_drug_id"])["internal_drug_id"].nunique()
        inconsistent_sources = source_groups[source_groups > 1].index.tolist()
        
        report["inconsistent_source_identifier_mappings_count"] = len(inconsistent_sources)
        report["inconsistent_source_identifier_mappings"] = [
            {"dataset": x[0], "source_id": x[1], "mapped_internal_count": int(source_groups[x])} for x in inconsistent_sources[:10]
        ]
        
        # 4. Check mapping confidence retained
        confidence_distribution = mappings_df["mapping_confidence"].value_counts().to_dict()
        report["mapping_confidence_retained_distribution"] = confidence_distribution
        
        # 5. Check entity type distribution
        if "entity_type" in nodes_df.columns:
            entity_types = nodes_df["entity_type"].value_counts().to_dict()
            report["entity_type_distribution"] = entity_types
            
    except Exception as e:
        report["error"] = str(e)
        logger.error(f"Error in integrated entity validation: {e}")
        
    with open(val_dir / "integrated_entity_validation.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    return report

def execute_audit(project_root: Path):
    logger.info("Executing comprehensive audit suite...")
    val_dir = setup_validation_dir(project_root)
    
    raw_res = run_raw_validation(project_root, val_dir)
    norm_res = run_normalized_validation(project_root, val_dir)
    db_rel_res = run_db_relationship_audit(project_root, val_dir)
    ts_rel_res = run_twosides_relationship_audit(project_root, val_dir)
    crosswalk_res = run_deep_crosswalk_audit(project_root, val_dir)
    chem_res = run_chemical_mapping_validation(project_root, val_dir)
    integrated_res = run_integrated_entity_validation(project_root, val_dir)
    
    logger.info("All audit checks completed and validated.")

if __name__ == "__main__":
    import sys
    proj_root = Path(__file__).resolve().parent.parent
    execute_audit(proj_root)
