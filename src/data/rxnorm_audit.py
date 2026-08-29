import os
import json
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INTERIM_DIR = DATA_DIR / "interim"
NORMALIZED_DIR = INTERIM_DIR / "normalized"
ENRICHED_DIR = INTERIM_DIR / "enriched"
VALIDATION_DIR = INTERIM_DIR / "validation"

def run_audit_suite():
    logger.info("Executing Phase 2 RxNorm audit suite...")
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    
    report = {
        "files_exist": False,
        "schema_valid": False,
        "integrity_passed": False,
        "coverage": {}
    }
    
    # 1. File existence checks
    required_files = [
        "rxnorm_drug_enrichment.csv",
        "rxnorm_candidate_matches.csv",
        "rxnorm_source_identifier_mapping.csv",
        "rxnorm_enrichment_summary.json",
        "rxnorm_enrichment_failures.csv"
    ]
    
    missing_files = [f for f in required_files if not (ENRICHED_DIR / f).exists()]
    if missing_files:
        logger.error(f"Missing required enrichment files: {missing_files}")
        report["missing_files"] = missing_files
        return report
    
    report["files_exist"] = True
    
    # Load files
    enrichment_df = pd.read_csv(ENRICHED_DIR / "rxnorm_drug_enrichment.csv")
    candidates_df = pd.read_csv(ENRICHED_DIR / "rxnorm_candidate_matches.csv")
    src_map_df = pd.read_csv(ENRICHED_DIR / "rxnorm_source_identifier_mapping.csv")
    failures_df = pd.read_csv(ENRICHED_DIR / "rxnorm_enrichment_failures.csv")
    
    # Load Phase 1 target
    p1_nodes = pd.read_csv(NORMALIZED_DIR / "integrated_drug_nodes.csv")
    
    # 2. Schema check
    expected_cols = {
        "rxnorm_drug_enrichment.csv": [
            "internal_drug_id", "entity_status", "name_candidate", "name_source",
            "name_resolution_status", "rxnorm_match_status", "rxnorm_match_method",
            "rxcui", "rxnorm_name", "rxnorm_synonym", "rxnorm_tty", "rxnorm_language",
            "match_score", "enrichment_confidence", "api_status", "error_message"
        ],
        "rxnorm_candidate_matches.csv": [
            "internal_drug_id", "query_name", "candidate_rxcui", "candidate_name",
            "candidate_tty", "match_method", "match_score", "selected_as_final",
            "selection_reason"
        ]
    }
    
    schema_passed = True
    for fname, cols in expected_cols.items():
        loaded_cols = pd.read_csv(ENRICHED_DIR / fname).columns.tolist()
        missing_cols = set(cols) - set(loaded_cols)
        if missing_cols:
            logger.error(f"Schema mismatch in {fname}. Missing: {missing_cols}")
            schema_passed = False
            
    report["schema_valid"] = schema_passed
    
    # 3. Integrity checks
    # A. Every internal_drug_id exists in Phase 1
    p1_ids = set(p1_nodes["internal_drug_id"])
    e_ids = set(enrichment_df["internal_drug_id"])
    invalid_ids = e_ids - p1_ids
    if invalid_ids:
        logger.error(f"Enrichment IDs not matching Phase 1 IDs: {invalid_ids}")
        report["integrity_passed"] = False
        return report
        
    # B. No duplicates
    if len(enrichment_df) != enrichment_df["internal_drug_id"].nunique():
        logger.error("Duplicates found in primary enrichment file!")
        report["integrity_passed"] = False
        return report
        
    # C. RxCUI format is numeric
    invalid_rxcuis = []
    for val in enrichment_df["rxcui"].dropna():
        if not str(val).split('.')[0].isdigit():
            invalid_rxcuis.append(val)
    if invalid_rxcuis:
        logger.error(f"Invalid non-numeric RxCUIs detected: {invalid_rxcuis}")
        report["integrity_passed"] = False
        return report
        
    report["integrity_passed"] = True
    
    # 4. Coverage calculation
    total_entities = len(enrichment_df)
    resolved_entities = enrichment_df["rxcui"].dropna().nunique()
    
    overall_cov = resolved_entities / total_entities if total_entities > 0 else 0.0
    report["coverage"]["overall"] = overall_cov
    
    # Coverage by entity type
    for etype in enrichment_df["entity_status"].unique():
        sub = enrichment_df[enrichment_df["entity_status"] == etype]
        sub_resolved = sub["rxcui"].dropna().nunique()
        sub_total = len(sub)
        report["coverage"][etype] = sub_resolved / sub_total if sub_total > 0 else 0.0
        
    # 5. Generate Manual Review Queue
    manual_review_records = []
    
    # Low confidence approximate matches
    low_conf = enrichment_df[enrichment_df["rxnorm_match_status"] == "LOW_APPROXIMATE"]
    for _, row in low_conf.iterrows():
        manual_review_records.append({
            "internal_drug_id": row["internal_drug_id"],
            "entity_status": row["entity_status"],
            "name_candidate": row["name_candidate"],
            "issue_type": "low_confidence_approximate_match",
            "candidate_rxcui": row["rxcui"],
            "candidate_name": row["rxnorm_name"],
            "match_score": row["match_score"],
            "recommended_action": "Verify if the approximate match represents the correct clinical entity."
        })
        
    # Conflicting mappings
    conflict = enrichment_df[enrichment_df["rxnorm_match_status"] == "AMBIGUOUS_CLINICAL_MAPPING"]
    for _, row in conflict.iterrows():
        manual_review_records.append({
            "internal_drug_id": row["internal_drug_id"],
            "entity_status": row["entity_status"],
            "name_candidate": row["name_candidate"],
            "issue_type": "conflicting_rxnorms_across_source_identifiers",
            "candidate_rxcui": "",
            "candidate_name": "",
            "match_score": 0.0,
            "recommended_action": "Manually resolve source mapping identifier differences."
        })
        
    # Missing names
    missing_names = enrichment_df[enrichment_df["name_resolution_status"] == "NO_NAME_CANDIDATE"]
    for _, row in missing_names.iterrows():
        manual_review_records.append({
            "internal_drug_id": row["internal_drug_id"],
            "entity_status": row["entity_status"],
            "name_candidate": "NO_NAME_CANDIDATE",
            "issue_type": "missing_name_candidate",
            "candidate_rxcui": "",
            "candidate_name": "",
            "match_score": 0.0,
            "recommended_action": "Find chemical registry mapping/clinical name source."
        })
        
    pd.DataFrame(manual_review_records).to_csv(VALIDATION_DIR / "rxnorm_manual_review_queue.csv", index=False)
    logger.info(f"Generated manual review queue with {len(manual_review_records)} items.")
    
    # Save audit report
    with open(VALIDATION_DIR / "rxnorm_audit_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    logger.info("Phase 2 RxNorm audit suite completed successfully!")
    return report

if __name__ == "__main__":
    run_audit_suite()
