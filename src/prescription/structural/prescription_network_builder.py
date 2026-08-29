"""
src/prescription/structural/prescription_network_builder.py

Builds the PrescriptionEvidenceNetwork from a PrescriptionSafetyReport.
"""

import logging
from typing import Dict, Any, List
from src.prescription.structural.prescription_network_schema import (
    PrescriptionEvidenceNetwork,
    PrescriptionEvidenceNode,
    PrescriptionEvidenceEdge
)
from src.prescription.schemas import PrescriptionSafetyReport

logger = logging.getLogger(__name__)

class PrescriptionNetworkBuilder:
    @staticmethod
    def build_network(report: PrescriptionSafetyReport) -> PrescriptionEvidenceNetwork:
        """
        Translates a Phase 6 PrescriptionSafetyReport into a PrescriptionEvidenceNetwork.
        Ensures isolated drugs are explicitly registered as nodes.
        """
        network = PrescriptionEvidenceNetwork()
        network.canonical_drug_ids = report.resolution_summary.canonical_drug_ids
        
        # 1. Build nodes for all unique canonical drugs
        # (even if they have no evidence, they must exist in the network as isolated nodes)
        for drug in report.resolution_summary.resolved_drugs:
            did = drug.resolved_internal_drug_id
            if did:
                network.nodes[did] = PrescriptionEvidenceNode(
                    drug_id=did,
                    display_name=drug.display_name or did
                )
                
        # 2. Add edges for pair results that have direct evidence
        for p in report.pair_results:
            status = p.get("evidence_status")
            if status and status != "NO_DIRECT_GRAPH_EVIDENCE":
                da = p.get("drug_a_id")
                db = p.get("drug_b_id")
                if not da or not db:
                    continue
                    
                # Ensure nodes exist (precautionary)
                if da not in network.nodes:
                    network.nodes[da] = PrescriptionEvidenceNode(drug_id=da, display_name=p.get("drug_a_name", da))
                if db not in network.nodes:
                    network.nodes[db] = PrescriptionEvidenceNode(drug_id=db, display_name=p.get("drug_b_name", db))
                    
                # Edge weighting model
                if status == "CONVERGENT_SAFETY_EVIDENCE":
                    weight = 1.0
                elif status in ("DDI_EVIDENCE_ONLY", "COMBINATION_EVENT_EVIDENCE_ONLY"):
                    weight = 0.7
                else:
                    weight = 0.0
                    
                confidence = float(p.get("confidence_score", 1.0))
                strength = round(weight * confidence, 3)
                
                pair_key = p.get("canonical_pair_key") or f"{da}+{db}"
                
                # Determine priority tier (defaulting to MODERATE if not specified)
                priority = p.get("evidence_priority") or "MODERATE_EVIDENCE_PRIORITY"
                
                network.edges[pair_key] = PrescriptionEvidenceEdge(
                    drug_a_id=da,
                    drug_b_id=db,
                    evidence_status=status,
                    confidence_score=confidence,
                    priority_tier=priority,
                    structural_weight=weight,
                    edge_strength=strength,
                    canonical_pair_key=pair_key
                )
                
        return network
