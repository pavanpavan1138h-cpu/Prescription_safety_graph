from typing import Any, Dict, List, Tuple
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.intelligence.intelligence_schema import CrossPairSignalGroup, ReinforcementLevel

class ReinforcementEngine:
    @staticmethod
    def analyze(
        group: CrossPairSignalGroup,
        report: PrescriptionSafetyReport,
        structural_analysis: Any
    ) -> Tuple[float, ReinforcementLevel]:
        # 1. Pair Coverage
        supported_pairs_count = max(1, report.evidence_summary.pairs_with_evidence)
        pair_coverage = len(group.supporting_pairs) / supported_pairs_count
        pair_coverage = min(1.0, max(0.0, pair_coverage))

        # 2. Drug Diversity
        total_drugs_count = max(1, len(report.resolution_summary.canonical_drug_ids))
        drug_diversity = len(group.participating_drugs) / total_drugs_count
        drug_diversity = min(1.0, max(0.0, drug_diversity))

        # 3. Channel Diversity
        channel_diversity = 0.0
        channels = group.channel_distribution
        if "twosides" in channels and "drugbank" in channels:
            channel_diversity = 1.0
        elif "twosides" in channels or "drugbank" in channels:
            channel_diversity = 0.5

        # 4. Convergent Support
        supporting_pairs_len = max(1, len(group.supporting_pairs))
        convergent_support = group.convergent_pair_count / supporting_pairs_len
        convergent_support = min(1.0, max(0.0, convergent_support))

        # 5. Structural Distribution (using Phase 8 profiles)
        structural_distribution = 0.1
        if structural_analysis and hasattr(structural_analysis, "drug_structural_profiles"):
            profiles = {p.drug_id: p for p in structural_analysis.drug_structural_profiles}
            unique_clusters = set()
            for d_id in group.participating_drugs:
                if d_id in profiles:
                    unique_clusters.add(profiles[d_id].cluster_id)
            
            if len(unique_clusters) > 1:
                structural_distribution = 1.0
            elif len(unique_clusters) == 1:
                structural_distribution = 0.5
        
        # 6. Proposed Deterministic Formula
        score = (
            0.30 * pair_coverage +
            0.20 * drug_diversity +
            0.20 * channel_diversity +
            0.20 * convergent_support +
            0.10 * structural_distribution
        )
        
        # Ensure exact bounds
        score = round(min(1.0, max(0.0, score)), 3)

        # Classify reinforcement level
        if score >= 0.75:
            level = ReinforcementLevel.STRONG_REINFORCEMENT
        elif score >= 0.50:
            level = ReinforcementLevel.MODERATE_REINFORCEMENT
        elif score >= 0.25:
            level = ReinforcementLevel.EMERGING_REINFORCEMENT
        else:
            level = ReinforcementLevel.LIMITED_REINFORCEMENT

        return score, level
