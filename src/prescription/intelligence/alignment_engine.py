from typing import Any, Dict, List
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.intelligence.intelligence_schema import DrugAlignmentProfile, StructuralEvidenceAlignment, AlignmentLevel, EvidenceTheme

class AlignmentEngine:
    @staticmethod
    def _compute_ranks(val_map: Dict[str, float]) -> Dict[str, int]:
        sorted_items = sorted(val_map.items(), key=lambda x: x[1], reverse=True)
        ranks = {}
        prev_val = None
        curr_rank = 1
        for idx, (k, val) in enumerate(sorted_items):
            if val != prev_val:
                curr_rank = idx + 1
                prev_val = val
            ranks[k] = curr_rank
        return ranks

    @classmethod
    def analyze(
        cls,
        report: PrescriptionSafetyReport,
        structural_analysis: Any,
        themes: List[EvidenceTheme]
    ) -> StructuralEvidenceAlignment:
        canonical_ids = report.resolution_summary.canonical_drug_ids
        drug_names = {d.resolved_internal_drug_id: d.display_name for d in report.resolution_summary.resolved_drugs if d.resolved_internal_drug_id}

        # If empty or minimal, return neutral alignment
        if not canonical_ids:
            return StructuralEvidenceAlignment(
                alignment_level=AlignmentLevel.NO_MEANINGFUL_ALIGNMENT,
                explanation="No drugs present in prescription."
            )

        # 1. Gather raw evidence metrics per drug
        evidence_counts = {did: 0.0 for did in canonical_ids}
        theme_counts = {did: 0.0 for did in canonical_ids}
        convergent_counts = {did: 0.0 for did in canonical_ids}

        # Evidence edge counts
        for p in report.pair_results:
            if p.get("evidence_status") != "NO_DIRECT_GRAPH_EVIDENCE":
                da = p["drug_a_id"]
                db = p["drug_b_id"]
                if da in evidence_counts:
                    evidence_counts[da] += 1
                if db in evidence_counts:
                    evidence_counts[db] += 1
                
                if p.get("evidence_status") == "CONVERGENT_SAFETY_EVIDENCE":
                    if da in convergent_counts:
                        convergent_counts[da] += 1
                    if db in convergent_counts:
                        convergent_counts[db] += 1

        # Theme participation counts
        for t in themes:
            for did in t.participating_drugs:
                if did in theme_counts:
                    theme_counts[did] += 1

        # 2. Compute ranks (lower rank = higher count)
        evidence_ranks = cls._compute_ranks(evidence_counts)
        theme_ranks = cls._compute_ranks(theme_counts)
        convergent_ranks = cls._compute_ranks(convergent_counts)

        # Map structural ranks from Phase 8
        structural_ranks = {}
        if structural_analysis and hasattr(structural_analysis, "drug_structural_profiles"):
            for profile in structural_analysis.drug_structural_profiles:
                structural_ranks[profile.drug_id] = profile.centrality_rank
        else:
            # Fallback if Phase 8 rank is missing
            structural_ranks = {did: 1 for did in canonical_ids}

        # 3. Compute alignment profiles per drug
        profiles: List[DrugAlignmentProfile] = []
        total_score = 0.0
        active_drugs_count = 0

        for did in canonical_ids:
            name = drug_names.get(did, did)
            s_rank = structural_ranks.get(did, len(canonical_ids))
            e_rank = evidence_ranks.get(did, len(canonical_ids))
            t_rank = theme_ranks.get(did, len(canonical_ids))
            c_rank = convergent_ranks.get(did, len(canonical_ids))

            # Compute delta average rank difference
            avg_evidence_rank = (e_rank + t_rank + c_rank) / 3.0
            delta = abs(s_rank - avg_evidence_rank)
            
            # alignment_score in range (0.0, 1.0]
            alignment_score = round(1.0 / (1.0 + delta), 3)

            # Classify drug-level alignment level
            if alignment_score >= 0.85:
                level = AlignmentLevel.HIGH_ALIGNMENT
            elif alignment_score >= 0.60:
                level = AlignmentLevel.MODERATE_ALIGNMENT
            elif alignment_score >= 0.35:
                level = AlignmentLevel.LOW_ALIGNMENT
            else:
                level = AlignmentLevel.NO_MEANINGFUL_ALIGNMENT

            profiles.append(DrugAlignmentProfile(
                drug_id=did,
                display_name=name,
                structural_rank=s_rank,
                evidence_participation_rank=e_rank,
                theme_participation_rank=t_rank,
                convergent_evidence_rank=c_rank,
                alignment_score=alignment_score,
                alignment_level=level
            ))

            total_score += alignment_score
            active_drugs_count += 1

        avg_score = (total_score / active_drugs_count) if active_drugs_count > 0 else 0.0
        avg_score = round(avg_score, 3)

        # Classify global prescription-level alignment
        if avg_score >= 0.75:
            global_level = AlignmentLevel.HIGH_ALIGNMENT
            explanation = "Structural centrality correlates strongly with evidence participation and theme diversity."
        elif avg_score >= 0.50:
            global_level = AlignmentLevel.MODERATE_ALIGNMENT
            explanation = "Moderate alignment between network hubs and evidence-supported safety channels."
        elif avg_score >= 0.30:
            global_level = AlignmentLevel.LOW_ALIGNMENT
            explanation = "Structural hubs exhibit rank divergence compared to raw evidence counts."
        else:
            global_level = AlignmentLevel.NO_MEANINGFUL_ALIGNMENT
            explanation = "No meaningful alignment between centrality metrics and safety evidence findings."

        return StructuralEvidenceAlignment(
            alignment_level=global_level,
            explanation=explanation,
            drug_alignment_profiles=sorted(profiles, key=lambda x: x.alignment_score, reverse=True)
        )
