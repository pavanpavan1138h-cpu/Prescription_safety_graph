import os
import json
import logging
import pandas as pd
from pathlib import Path
from src.data.rxnorm_enrichment import RxNormCache, RxNavClient, DrugNameResolver, RxNormMatcher

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INTERIM_DIR = DATA_DIR / "interim"
NORMALIZED_DIR = INTERIM_DIR / "normalized"
ENRICHED_DIR = INTERIM_DIR / "enriched"
CACHE_DIR = INTERIM_DIR / "rxnorm_cache"

def run_enrichment():
    logger.info("Initializing RxNorm clinical enrichment pipeline...")
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load input tables
    nodes_path = NORMALIZED_DIR / "integrated_drug_nodes.csv"
    mappings_path = NORMALIZED_DIR / "integrated_drug_source_mappings.csv"
    
    if not nodes_path.exists() or not mappings_path.exists():
        logger.error("Required Phase 1 input files are missing from normalized directory.")
        return

    nodes_df = pd.read_csv(nodes_path)
    mappings_df = pd.read_csv(mappings_path)
    
    # Initialize cache and client
    cache = RxNormCache(CACHE_DIR)
    client = RxNavClient(cache)
    name_resolver = DrugNameResolver(client)
    matcher = RxNormMatcher(client)
    
    # Results accumulators
    enrichment_records = []
    candidate_matches = []
    source_identifier_mappings = []
    failures_records = []
    
    # Stats
    stats = {
        "total_entities": len(nodes_df),
        "entities_with_name": 0,
        "entities_without_name": 0,
        "exact_identifier_matches": 0,
        "exact_name_matches": 0,
        "normalized_name_matches": 0,
        "approximate_matches": 0,
        "ambiguous_matches": 0,
        "no_matches": 0,
        "api_errors": 0,
        "cache_hits": 0,
        "cache_misses": 0
    }
    
    logger.info(f"Processing {len(nodes_df)} integrated drug entities...")
    
    for idx, row in nodes_df.iterrows():
        internal_id = row["internal_drug_id"]
        entity_status = row["entity_type"] # CONFIRMED_INTEGRATED_ENTITY, AMBIGUOUS_MAPPING_COMPONENT
        
        # 1. Resolve Name Candidate
        resolved = name_resolver.resolve_name(row, mappings_df)
        name_candidate = resolved["name_candidate"]
        name_source = resolved["name_source"]
        name_res_status = resolved["name_resolution_status"]
        
        if name_candidate:
            stats["entities_with_name"] += 1
        else:
            stats["entities_without_name"] += 1
            
        # 2. Source-level multi-identifier enrichment route routing
        entity_mappings = mappings_df[mappings_df["internal_drug_id"] == internal_id]
        
        resolved_rxcuis = {}
        provenance_records = []
        
        for _, m_row in entity_mappings.iterrows():
            src_dataset = m_row["source_dataset"]
            src_id = m_row["source_drug_id"]
            
            rxcui = None
            method = "none"
            match_status = "NO_MATCH"
            api_status = "success"
            error_msg = ""
            
            # Lookup route based on source dataset
            if src_dataset == "drugbank":
                res = client.lookup_by_drugbank_id(src_id)
                if res and "idGroup" in res and "rxnormId" in res["idGroup"]:
                    rxcuis = res["idGroup"]["rxnormId"]
                    if rxcuis:
                        rxcui = rxcuis[0]
                        method = "exact_identifier_based"
                        match_status = "HIGH_EXACT"
                else:
                    api_status = "error"
                    error_msg = "DrugBank ID lookup failed or empty"
            elif src_dataset == "twosides" and name_candidate:
                # Use name matching
                match_res = matcher.match(name_candidate)
                rxcui = match_res["rxcui"]
                method = match_res["rxnorm_match_method"]
                match_status = match_res["rxnorm_match_status"]
                
                # Keep all alternate candidates if any
                for cand in match_res["candidates"]:
                    candidate_matches.append({
                        "internal_drug_id": internal_id,
                        "query_name": name_candidate,
                        "candidate_rxcui": cand["rxcui"],
                        "candidate_name": cand["name"],
                        "candidate_tty": cand["tty"],
                        "match_method": cand["match_method"],
                        "match_score": cand["match_score"],
                        "selected_as_final": 1 if cand["rxcui"] == rxcui else 0,
                        "selection_reason": "Top matching score candidate" if cand["rxcui"] == rxcui else "Alternative candidate"
                    })
            
            if rxcui:
                resolved_rxcuis[src_id] = (rxcui, match_status, method)
                source_identifier_mappings.append({
                    "internal_drug_id": internal_id,
                    "source_dataset": src_dataset,
                    "source_drug_id": src_id,
                    "rxcui": rxcui,
                    "mapping_status": match_status
                })
            else:
                source_identifier_mappings.append({
                    "internal_drug_id": internal_id,
                    "source_dataset": src_dataset,
                    "source_drug_id": src_id,
                    "rxcui": "",
                    "mapping_status": "UNRESOLVED"
                })
                
        # 3. Conflict resolution & integrated entity match assignment
        final_rxcui = None
        final_match_status = "NO_MATCH"
        final_method = "none"
        final_name = ""
        final_synonym = ""
        final_tty = ""
        final_lang = ""
        final_score = 0.0
        final_api_status = "success"
        final_error = ""
        
        unique_rxcuis = set([val[0] for val in resolved_rxcuis.values()])
        
        if len(unique_rxcuis) == 1:
            final_rxcui = list(unique_rxcuis)[0]
            # Retrieve properties
            props = client.get_rxcui_properties(final_rxcui)
            if props and "properties" in props:
                p = props["properties"]
                final_name = p.get("name", "")
                final_synonym = p.get("synonym", "")
                final_tty = p.get("tty", "")
                final_lang = p.get("language", "")
            
            # Inherit method and status from the mapping route
            first_val = list(resolved_rxcuis.values())[0]
            final_match_status = first_val[1]
            final_method = first_val[2]
            final_score = 100.0 if "exact" in final_method else 75.0
            
            if final_match_status == "HIGH_EXACT":
                stats["exact_identifier_matches"] += 1
            elif final_match_status == "LOW_APPROXIMATE":
                stats["approximate_matches"] += 1
            else:
                stats["exact_name_matches"] += 1
                
        elif len(unique_rxcuis) > 1:
            final_match_status = "AMBIGUOUS_CLINICAL_MAPPING"
            final_method = "conflict_resolution"
            final_error = f"Conflict: mapped to multiple different RxCUIs: {list(unique_rxcuis)}"
            stats["ambiguous_matches"] += 1
            
            # Save failures/review log
            failures_records.append({
                "internal_drug_id": internal_id,
                "name_candidate": name_candidate or "NO_NAME_CANDIDATE",
                "failure_type": "AMBIGUOUS_CLINICAL_MAPPING",
                "failure_stage": "conflict_resolution",
                "error_message": final_error
            })
        else:
            final_match_status = "NO_MATCH"
            stats["no_matches"] += 1
            failures_records.append({
                "internal_drug_id": internal_id,
                "name_candidate": name_candidate or "NO_NAME_CANDIDATE",
                "failure_type": "NO_MATCH",
                "failure_stage": "matching",
                "error_message": "No matching concept found in RxNorm API."
            })
            
        enrichment_records.append({
            "internal_drug_id": internal_id,
            "entity_status": entity_status,
            "name_candidate": name_candidate or "NO_NAME_CANDIDATE",
            "name_source": name_source,
            "name_resolution_status": name_res_status,
            "rxnorm_match_status": final_match_status,
            "rxnorm_match_method": final_method,
            "rxcui": final_rxcui or "",
            "rxnorm_name": final_name,
            "rxnorm_synonym": final_synonym,
            "rxnorm_tty": final_tty,
            "rxnorm_language": final_lang,
            "match_score": final_score,
            "enrichment_confidence": final_match_status,
            "api_status": final_api_status,
            "error_message": final_error
        })
        
    # Write files
    pd.DataFrame(enrichment_records).to_csv(ENRICHED_DIR / "rxnorm_drug_enrichment.csv", index=False)
    pd.DataFrame(candidate_matches).to_csv(ENRICHED_DIR / "rxnorm_candidate_matches.csv", index=False)
    pd.DataFrame(source_identifier_mappings).to_csv(ENRICHED_DIR / "rxnorm_source_identifier_mapping.csv", index=False)
    pd.DataFrame(failures_records).to_csv(ENRICHED_DIR / "rxnorm_enrichment_failures.csv", index=False)
    
    # Save statistics
    with open(ENRICHED_DIR / "rxnorm_enrichment_summary.json", "w") as f:
        json.dump(stats, f, indent=4)
        
    logger.info("RxNorm Clinical Enrichment pipeline executed successfully and outputs saved!")

if __name__ == "__main__":
    run_enrichment()
