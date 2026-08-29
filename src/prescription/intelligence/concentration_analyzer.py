from typing import Any, Dict, List, Optional
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.intelligence.intelligence_schema import EvidenceConcentrationProfile, EvidenceConcentrationType

class ConcentrationAnalyzer:
    @staticmethod
    def analyze(report: PrescriptionSafetyReport, structural_analysis: Any) -> EvidenceConcentrationProfile:
        total_possible = max(1, report.evidence_summary.total_expected_pairs)
        supported_pairs = report.evidence_summary.pairs_with_evidence
        edge_coverage_ratio = round(supported_pairs / total_possible, 3)

        if supported_pairs == 0:
            return EvidenceConcentrationProfile(
                concentration_type=EvidenceConcentrationType.NO_EVIDENCE_CONCENTRATION,
                edge_coverage_ratio=0.0
            )

        # 1. Compute drug-level shares
        drug_edge_counts = {}
        for p in report.pair_results:
            if p.get("evidence_status") != "NO_DIRECT_GRAPH_EVIDENCE":
                da = p["drug_a_id"]
                db = p["drug_b_id"]
                drug_edge_counts[da] = drug_edge_counts.get(da, 0) + 1
                drug_edge_counts[db] = drug_edge_counts.get(db, 0) + 1

        dominant_drug_id = None
        dominant_drug_share = 0.0
        if drug_edge_counts:
            # find max drug
            dom_drug = max(drug_edge_counts, key=drug_edge_counts.get)
            dominant_drug_id = dom_drug
            dominant_drug_share = round(drug_edge_counts[dom_drug] / supported_pairs, 3)

        # 2. Compute cluster-level shares (using Phase 8 clusters)
        dominant_cluster_id = None
        dominant_cluster_edge_share = 0.0
        
        if structural_analysis and hasattr(structural_analysis, "clusters"):
            # find max cluster by edge count
            active_clusters = [c for c in structural_analysis.clusters if not c.is_isolated]
            if active_clusters:
                dom_cluster = max(active_clusters, key=lambda c: c.edge_count)
                dominant_cluster_id = dom_cluster.cluster_id
                dominant_cluster_edge_share = round(dom_cluster.edge_count / supported_pairs, 3)

        # 3. Classify Concentration Type
        # Centralized: one drug participates in >= 60% of all evidence supported pairs
        # Cluster-concentrated: one cluster contains >= 70% of all evidence supported pairs
        if supported_pairs <= 1:
            concentration_type = EvidenceConcentrationType.SPARSE_EVIDENCE
        elif dominant_drug_share >= 0.60:
            concentration_type = EvidenceConcentrationType.CENTRALIZED_EVIDENCE
        elif dominant_cluster_edge_share >= 0.70:
            concentration_type = EvidenceConcentrationType.CLUSTER_CONCENTRATED_EVIDENCE
        elif dominant_drug_share <= 0.35 and dominant_cluster_edge_share <= 0.50:
            concentration_type = EvidenceConcentrationType.DISTRIBUTED_EVIDENCE
        else:
            concentration_type = EvidenceConcentrationType.MIXED_EVIDENCE_DISTRIBUTION

        return EvidenceConcentrationProfile(
            concentration_type=concentration_type,
            edge_coverage_ratio=edge_coverage_ratio,
            dominant_drug_id=dominant_drug_id,
            dominant_drug_share=dominant_drug_share,
            dominant_cluster_id=dominant_cluster_id,
            dominant_cluster_edge_share=dominant_cluster_edge_share
        )
