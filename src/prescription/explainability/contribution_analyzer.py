"""
src/prescription/explainability/contribution_analyzer.py

Computes multi-layer deterministic contribution scores across Phase 6 (Pairs),
Phase 8 (Structure), Phase 9 (Signals), and Phase 10 (Stability).
"""

from typing import List, Dict, Any, Optional
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.explainability.explainability_schema import ContributionProfile, ContributionLevel

class ContributionAnalyzer:
    """
    Analyzes and quantifies how much each individual drug and drug-pair contributed
    to the prescription's aggregate network intelligence conclusions.
    """

    def analyze_contributions(
        self,
        analysis_result: PrescriptionSafetyReport,
        structural_analysis: Optional[Any] = None,
        evidence_intelligence: Optional[Any] = None,
        contextual_stability: Optional[Any] = None
    ) -> List[ContributionProfile]:
        profiles: List[ContributionProfile] = []
        
        # 1. Map drug dependencies from Phase 10 if present
        dep_map: Dict[str, float] = {}
        if contextual_stability and hasattr(contextual_stability, "drug_dependencies"):
            for dep in contextual_stability.drug_dependencies:
                dep_map[dep.drug_id] = float(dep.structural_connectivity_loss_ratio)

        # 2. Map structural participation from Phase 8 if present
        struct_map: Dict[str, float] = {}
        if structural_analysis and hasattr(structural_analysis, "structural_interpretation"):
            highest_drug = structural_analysis.structural_interpretation.highest_participation_drug
            if highest_drug:
                struct_map[highest_drug] = 1.0

        # 3. Map themes participation from Phase 9 if present
        theme_drug_counts: Dict[str, int] = {}
        if evidence_intelligence and hasattr(evidence_intelligence, "evidence_themes"):
            for theme in evidence_intelligence.evidence_themes:
                for d in theme.participating_drugs:
                    theme_drug_counts[d] = theme_drug_counts.get(d, 0) + 1

        total_pairs = len(analysis_result.pair_results)
        resolved_drugs = analysis_result.resolution_summary.resolved_drugs if analysis_result.resolution_summary else []

        # Analyze Drug Entities
        for drug in resolved_drugs:
            drug_id = getattr(drug, "resolved_internal_drug_id", None) or getattr(drug, "canonical_drug_id", "UNKNOWN")
            drug_name = getattr(drug, "display_name", None) or getattr(drug, "canonical_name", "UNKNOWN")

            # Direct Decision Contribution: ratio of positive pairs involving this drug
            def pair_matches_drug(p):
                da = p.get("drug_a_id") if isinstance(p, dict) else getattr(p, "drug_a_id", "")
                db = p.get("drug_b_id") if isinstance(p, dict) else getattr(p, "drug_b_id", "")
                return da == drug_id or db == drug_id

            def is_pair_positive(p):
                st = p.get("evidence_status") if isinstance(p, dict) else getattr(p, "evidence_status", "")
                return st not in ["NO_DIRECT_GRAPH_EVIDENCE", "NO_EVIDENCED_INTERACTION"]

            involving_pairs = [p for p in analysis_result.pair_results if pair_matches_drug(p)]
            positive_pairs = [p for p in involving_pairs if is_pair_positive(p)]
            direct_contrib = len(positive_pairs) / max(len(involving_pairs), 1)

            # Evidence Coverage
            def get_ev_count(p):
                has_d = p.get("ddi_evidence_present", False) if isinstance(p, dict) else getattr(p, "has_direct_ddi", False)
                has_e = p.get("combination_event_evidence_present", False) if isinstance(p, dict) else getattr(p, "has_combination_side_effects", False)
                return (1 if has_d else 0) + (1 if has_e else 0)

            ev_count = sum(get_ev_count(p) for p in involving_pairs)
            evidence_cov = min(1.0, ev_count / 5.0) if involving_pairs else 0.0

            # Cross-Layer Participation
            participating_phases = ["Phase 5/6 (Reasoning)"]
            if drug_name in struct_map or drug_id in struct_map:
                participating_phases.append("Phase 8 (Structure)")
            if drug_name in theme_drug_counts or drug_id in theme_drug_counts:
                participating_phases.append("Phase 9 (Signals)")
            if drug_id in dep_map and dep_map[drug_id] > 0:
                participating_phases.append("Phase 10 (Stability)")
            cross_layer_score = len(participating_phases) / 4.0

            # Dependency Impact
            dep_impact = dep_map.get(drug_id, 0.2 if positive_pairs else 0.0)

            overall_score = round(
                0.35 * direct_contrib +
                0.25 * evidence_cov +
                0.20 * cross_layer_score +
                0.20 * dep_impact,
                4
            )
            overall_score = max(0.0, min(1.0, overall_score))

            if overall_score >= 0.75:
                level = ContributionLevel.PRIMARY_CONTRIBUTOR
            elif overall_score >= 0.50:
                level = ContributionLevel.MAJOR_CONTRIBUTOR
            elif overall_score >= 0.30:
                level = ContributionLevel.SUPPORTING_CONTRIBUTOR
            elif overall_score >= 0.15:
                level = ContributionLevel.MINOR_CONTRIBUTOR
            else:
                level = ContributionLevel.BACKGROUND_CONTEXT

            profiles.append(ContributionProfile(
                entity_id=drug_id,
                entity_label=drug_name,
                entity_type="DRUG_ENTITY",
                direct_decision_contribution=round(direct_contrib, 3),
                evidence_coverage=round(evidence_cov, 3),
                cross_layer_participation=round(cross_layer_score, 3),
                dependency_impact=round(dep_impact, 3),
                overall_contribution_score=overall_score,
                contribution_level=level,
                participating_phases=participating_phases,
                explanation=f"{drug_name} participates across {len(participating_phases)} analytical layers with {len(positive_pairs)} evidenced pairs."
            ))

        # Also Analyze Drug Pairs
        for pair in analysis_result.pair_results:
            pair_id = pair.get("pair_id") if isinstance(pair, dict) else getattr(pair, "pair_id", None)
            drug_a_id = pair.get("drug_a_id") if isinstance(pair, dict) else getattr(pair, "drug_a_id", "")
            drug_b_id = pair.get("drug_b_id") if isinstance(pair, dict) else getattr(pair, "drug_b_id", "")
            drug_a_name = pair.get("drug_a_name") if isinstance(pair, dict) else getattr(pair, "drug_a_name", "")
            drug_b_name = pair.get("drug_b_name") if isinstance(pair, dict) else getattr(pair, "drug_b_name", "")
            
            if not pair_id:
                pair_id = f"{drug_a_id}:{drug_b_id}" if (drug_a_id and drug_b_id) else f"PAIR_{drug_a_name}_{drug_b_name}"

            pair_label = f"{drug_a_name} + {drug_b_name}" if (drug_a_name and drug_b_name) else pair_id
            
            st = pair.get("evidence_status") if isinstance(pair, dict) else getattr(pair, "evidence_status", "")
            conf = pair.get("confidence_score", 0.0) if isinstance(pair, dict) else getattr(pair, "confidence_score", 0.0)
            has_d = pair.get("ddi_evidence_present", False) if isinstance(pair, dict) else getattr(pair, "has_direct_ddi", False)
            has_e = pair.get("combination_event_evidence_present", False) if isinstance(pair, dict) else getattr(pair, "has_combination_side_effects", False)
            
            is_pos = st not in ["NO_DIRECT_GRAPH_EVIDENCE", "NO_EVIDENCED_INTERACTION"]
            is_conv = st == "CONVERGENT_SAFETY_EVIDENCE"
            direct_p = 1.0 if is_conv else (0.7 if is_pos else 0.1)
            ev_p = 1.0 if (has_d and has_e) else (0.5 if is_pos else 0.0)
            cross_p = 0.75 if is_conv else (0.5 if is_pos else 0.25)
            dep_p = 0.5 if is_conv else (0.3 if is_pos else 0.0)

            overall_score = round(0.35 * direct_p + 0.25 * ev_p + 0.20 * cross_p + 0.20 * dep_p, 4)
            overall_score = max(0.0, min(1.0, overall_score))

            if overall_score >= 0.75:
                level = ContributionLevel.PRIMARY_CONTRIBUTOR
            elif overall_score >= 0.50:
                level = ContributionLevel.MAJOR_CONTRIBUTOR
            elif overall_score >= 0.30:
                level = ContributionLevel.SUPPORTING_CONTRIBUTOR
            elif overall_score >= 0.15:
                level = ContributionLevel.MINOR_CONTRIBUTOR
            else:
                level = ContributionLevel.BACKGROUND_CONTEXT

            profiles.append(ContributionProfile(
                entity_id=str(pair_id),
                entity_label=str(pair_label),
                entity_type="DRUG_PAIR",
                direct_decision_contribution=round(direct_p, 3),
                evidence_coverage=round(ev_p, 3),
                cross_layer_participation=round(cross_p, 3),
                dependency_impact=round(dep_p, 3),
                overall_contribution_score=overall_score,
                contribution_level=level,
                participating_phases=["Phase 5/6 (Reasoning)", "Phase 9 (Signals)"],
                explanation=f"Pair combination {pair_label} evaluated as {st} with confidence {conf}."
            ))

        # Sort descending by overall contribution score
        profiles.sort(key=lambda p: p.overall_contribution_score, reverse=True)
        return profiles
