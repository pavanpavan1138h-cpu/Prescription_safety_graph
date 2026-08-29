import logging
import json
from pathlib import Path
import pandas as pd

from src.loaders import load_drugbank_ddi, load_twosides
from src.normalization import normalize_drugbank, normalize_twosides
from src.crosswalk import integrate_drug_entities

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_data_pipeline(project_root: Path):
    """
    Orchestrate and run all stages of the data processing pipeline.
    """
    logger.info("Initializing Prescription Safety Graph Pipeline...")
    
    # 1. Define Paths
    data_dir = project_root / "data"
    raw_dir = data_dir / "raw"
    interim_dir = data_dir / "interim"
    normalized_dir = interim_dir / "normalized"
    
    # Raw Files
    drugbank_file = raw_dir / "tdc" / "drugbank.tab"
    twosides_file = raw_dir / "twosides" / "twosides.csv"
    crosswalk_file = normalized_dir / "drugbank_twosides_unified_crosswalk.csv"
    
    # Output Files
    db_drugs_out = normalized_dir / "drugbank_drugs_normalized.csv"
    db_inter_out = normalized_dir / "drugbank_interactions_normalized.csv"
    ts_drugs_out = normalized_dir / "twosides_drugs_normalized.csv"
    ts_se_out = normalized_dir / "twosides_side_effects_normalized.csv"
    ts_rel_out = normalized_dir / "twosides_relationships_normalized.csv"
    int_nodes_out = normalized_dir / "integrated_drug_nodes.csv"
    int_mappings_out = normalized_dir / "integrated_drug_source_mappings.csv"
    int_edges_out = normalized_dir / "integrated_drug_mapping_edges.csv"
    
    summary_out = normalized_dir / "normalization_summary.json"
    report_out = normalized_dir / "mapping_validation_report.json"
    
    # Ensure directory exists
    normalized_dir.mkdir(parents=True, exist_ok=True)
    
    # --- STAGE 1: Load Data ---
    db_df = load_drugbank_ddi(drugbank_file)
    ts_df = load_twosides(twosides_file)
    
    # --- STAGE 2: DrugBank Normalization ---
    db_drugs_norm, db_inter_norm = normalize_drugbank(db_df)
    
    # --- STAGE 3: TWOSIDES Normalization ---
    ts_drugs_norm, ts_se_norm, ts_rel_norm = normalize_twosides(ts_df)
    
    # --- STAGE 4 & 5: Integration & Entity Resolution ---
    int_nodes_df, int_mappings_df, int_edges_df, validation_report = integrate_drug_entities(
        crosswalk_file,
        db_drugs_norm,
        ts_drugs_norm
    )
    
    # --- STAGE 6 & 7: Verification & Generating reports ---
    logger.info("Verifying outputs and generating statistics...")
    
    normalization_summary = {
        "drugbank": {
            "input_row_count": len(db_df),
            "output_drugs_count": len(db_drugs_norm),
            "output_interactions_count": len(db_inter_norm),
            "unique_drugs": int(db_drugs_norm["drugbank_id"].nunique()),
            "missing_smiles": int(db_drugs_norm["raw_smiles"].isna().sum()),
            "invalid_structures": int((~db_drugs_norm["structure_valid"]).sum()),
            "duplicate_drugs": int(db_drugs_norm["drugbank_id"].duplicated().sum())
        },
        "twosides": {
            "input_row_count": len(ts_df),
            "output_drugs_count": len(ts_drugs_norm),
            "output_side_effects_count": len(ts_se_norm),
            "output_relationships_count": len(ts_rel_norm),
            "unique_drugs": int(ts_drugs_norm["twosides_id"].nunique()),
            "unique_side_effects": int(ts_se_norm["side_effect_id"].nunique()),
            "missing_smiles": int(ts_drugs_norm["raw_smiles"].isna().sum()),
            "invalid_structures": int((~ts_drugs_norm["structure_valid"]).sum()),
            "duplicate_drugs": int(ts_drugs_norm["twosides_id"].duplicated().sum())
        },
        "integrated": {
            "total_drug_entities": len(int_nodes_df),
            "entity_type_distribution": int_nodes_df["entity_type"].value_counts().to_dict(),
            "source_membership_distribution": int_nodes_df["source_membership"].value_counts().to_dict(),
            "mappings_count": len(int_mappings_df),
            "mapping_edges_count": len(int_edges_df),
            "uniqueness_check_passed": bool(int_nodes_df["internal_drug_id"].is_unique)
        }
    }
    
    # --- STAGE 8: Save Outputs ---
    logger.info("Saving processed files...")
    
    db_drugs_norm.to_csv(db_drugs_out, index=False)
    db_inter_norm.to_csv(db_inter_out, index=False)
    ts_drugs_norm.to_csv(ts_drugs_out, index=False)
    ts_se_norm.to_csv(ts_se_out, index=False)
    ts_rel_norm.to_csv(ts_rel_out, index=False)
    int_nodes_df.to_csv(int_nodes_out, index=False)
    int_mappings_df.to_csv(int_mappings_out, index=False)
    int_edges_df.to_csv(int_edges_out, index=False)
    
    with open(summary_out, 'w') as f:
        json.dump(normalization_summary, f, indent=4)
        
    with open(report_out, 'w') as f:
        json.dump(validation_report, f, indent=4)
        
    logger.info("Pipeline executed successfully and all outputs saved!")
    
    return normalization_summary, validation_report
