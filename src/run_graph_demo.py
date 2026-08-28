"""
run_graph_demo.py

Demonstration of structured retrieval queries and provenance inspection
on the built Phase 4 Prescription Safety Knowledge Graph.
"""

import json
import logging
from pathlib import Path
from graph_queries import GraphQueryEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent
    graph_dir = project_root / "data" / "interim" / "graph"
    
    logger.info("Initializing Graph Query Engine for Phase 4 Demonstration...")
    engine = GraphQueryEngine(graph_dir)
    engine.load()

    print("\n" + "="*80)
    print("PHASE 4 KNOWLEDGE GRAPH STRUCTURED RETRIEVAL & PROVENANCE DEMONSTRATION")
    print("="*80)

    # Query 1: Given a DrugBank ID, find integrated Drug entity
    db_id = "DB00191"
    drug_1 = engine.get_drug_by_source_identifier("drugbank", db_id)
    print(f"\n[QUERY 1] DrugBank ID '{db_id}' -> Integrated Drug Entity:")
    print(f"  Internal ID:   {drug_1['node_id']}")
    print(f"  Display Name:  {drug_1['display_name']}")
    print(f"  Entity Status: {drug_1['entity_status']}")
    print(f"  Confidence:    {drug_1['confidence']}")

    # Query 2: Given a DrugBank ID, find second drug (e.g. DB00196) and a confirmed RxCUI-mapped drug (DB00006)
    db_id_2 = "DB00196"
    drug_2 = engine.get_drug_by_source_identifier("drugbank", db_id_2)
    drug_with_rxn = engine.get_drug_by_source_identifier("drugbank", "DB00006") # DRUG_000001
    print(f"\n[QUERY 2] DrugBank IDs '{db_id_2}' and 'DB00006' -> Integrated Drug Entities:")
    print(f"  Entity 1: {drug_2['node_id']} ({drug_2['display_name']})")
    print(f"  Entity 2: {drug_with_rxn['node_id']} ({drug_with_rxn['display_name']})")

    # Query 3: Given an integrated drug, retrieve its RxNorm concept
    rxn_info = engine.get_rxnorm_concept_for_drug(drug_with_rxn['node_id'])
    print(f"\n[QUERY 3] Integrated Drug '{drug_with_rxn['node_id']}' -> RxNorm Concept:")
    if rxn_info:
        print(f"  RxCUI Node:      {rxn_info['rxnorm_concept_node']['node_id']}")
        print(f"  RxNorm Name:     {rxn_info['rxnorm_concept_node']['display_name']}")
        print(f"  Mapping Method:  {rxn_info['mapping_properties']['mapping_method']}")
        print(f"  Match Status:    {rxn_info['mapping_properties']['resolution_status']}")
    else:
        print("  Unresolved / No direct RxCUI mapping.")

    # Query 4: Given Drug A and Drug B, retrieve direct DrugBank interaction evidence
    d1_id = drug_1['node_id']
    d2_id = drug_2['node_id']
    interactions = engine.get_direct_interactions(d1_id, d2_id)
    print(f"\n[QUERY 4] Direct DrugBank Interactions between '{d1_id}' ({drug_1['display_name']}) and '{d2_id}' ({drug_2['display_name']}):")
    print(f"  Total Directed Interaction Edges Found: {len(interactions)}")
    for inter in interactions:
        print(f"  - Edge ID:       {inter['edge_id']} ({inter['source']} -> {inter['target']})")
        print(f"    Source Record: {inter['properties']['source_drugbank_id_1']} -> {inter['properties']['source_drugbank_id_2']}")
        print(f"    Description:   {inter['properties']['interaction_description']}")

    # Query 5: Given Drug A and Drug B, retrieve TWOSIDES DrugPair adverse events
    pair_res = engine.get_drug_pair_and_side_effects(d1_id, d2_id)
    print(f"\n[QUERY 5] TWOSIDES DrugPair Adverse Events for Combination of '{d1_id}' + '{d2_id}':")
    if pair_res:
        print(f"  DrugPair Node ID:                {pair_res['pair_node']['node_id']}")
        print(f"  Total Associated Side Effects:   {pair_res['total_associated_side_effects']}")
        print(f"  Sample Side Effects Observed:")
        for se in pair_res['sample_side_effects'][:5]:
            print(f"    * SE_{se['side_effect_id']}: {se['side_effect_name']} (Edge: {se['edge_id']})")
    else:
        print("  No TWOSIDES pair record found.")

    # Query 6: Complete Provenance Tracing for an interaction edge
    sample_edge_id = interactions[0]['edge_id'] if interactions else "E_DDI_000001"
    prov = engine.get_provenance_for_edge(sample_edge_id)
    print(f"\n[QUERY 6] Complete Provenance Trace for Edge '{sample_edge_id}':")
    print(f"  Relationship:        {prov['relationship_type']}")
    print(f"  Source Node:         {prov['source_node']['node_id']} ({prov['source_node']['display_name']})")
    print(f"  Target Node:         {prov['target_node']['node_id']} ({prov['target_node']['display_name']})")
    print(f"  Source Dataset:      {prov['source_dataset']}")
    print(f"  Source Record ID:    {prov['source_record_id']}")
    print(f"  Mapping Confidence:  {prov['mapping_confidence']}")
    print(f"  Evidence Confidence: {prov['evidence_confidence']}")
    print(f"  Provenance File:     {prov['properties']['provenance']}")

    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("="*80)

if __name__ == "__main__":
    main()
