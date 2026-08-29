from src.prescription.intelligence.intelligence_schema import (
    PrescriptionEvidenceIntelligenceProfile,
    EvidenceThemeType,
    ReinforcementLevel,
    EvidenceConcentrationType,
    AlignmentLevel
)

class IntelligenceInterpretationEngine:
    @staticmethod
    def generate(profile: PrescriptionEvidenceIntelligenceProfile) -> str:
        lines = []
        lines.append("=== PRESCRIPTION EVIDENCE INTELLIGENCE SYNTHESIS ===")
        lines.append("")

        # 1. Executive Overview
        themes_count = len([t for t in profile.themes if t.theme_name != EvidenceThemeType.UNKNOWN_OR_UNMAPPED_THEME.value])
        has_unknown = any(t.theme_name == EvidenceThemeType.UNKNOWN_OR_UNMAPPED_THEME.value for t in profile.themes)
        
        lines.append(f"Analysis summary: Identified {themes_count} distinct clinical safety themes across drug combinations.")
        if has_unknown:
            lines.append("Supplementary unmapped side-effect events were also retained in the safety profile.")
        lines.append("")

        # 2. Cross-Pair Signal Convergence & Reinforcement
        lines.append("--- CROSS-PAIR CONVERGENCE & REINFORCEMENT ---")
        if not profile.signal_groups:
            lines.append("No recurring cross-pair evidence patterns detected. Safety findings are isolated to pairwise drug combinations.")
        else:
            lines.append(f"Detected {len(profile.signal_groups)} synthesized signal group(s) showing repeated convergence:")
            for sg in profile.signal_groups:
                # Find theme name from themes
                theme_obj = next((t for t in profile.themes if t.theme_id == sg.theme_id), None)
                theme_name = theme_obj.theme_name.replace("_", " ") if theme_obj else sg.theme_id
                
                lines.append(f"- Group {sg.group_id} ({sg.reinforcement_level.value}):")
                lines.append(f"  * Theme: {theme_name}")
                lines.append(f"  * Supporting drug pairs: {', '.join(sg.supporting_pairs)}")
                lines.append(f"  * Participating medications: {', '.join(sg.participating_drugs)}")
                lines.append(f"  * Evidence channels: {', '.join(sg.channel_distribution)}")
                lines.append(f"  * Convergence score: {sg.reinforcement_score}")
        lines.append("")

        # 3. Evidence Concentration
        lines.append("--- EVIDENCE CONCENTRATION SUMMARY ---")
        cp = profile.concentration_profile
        if cp:
            lines.append(f"Evidence distribution: {cp.concentration_type.value}")
            if cp.concentration_type == EvidenceConcentrationType.CENTRALIZED_EVIDENCE:
                lines.append(f"  * Centralized hub: Medication {cp.dominant_drug_id} participates in {int(cp.dominant_drug_share * 100)}% of evidence findings.")
            elif cp.concentration_type == EvidenceConcentrationType.CLUSTER_CONCENTRATED_EVIDENCE:
                lines.append(f"  * Concentrated cluster: Cluster {cp.dominant_cluster_id} contains {int(cp.dominant_cluster_edge_share * 100)}% of evidence edges.")
            elif cp.concentration_type == EvidenceConcentrationType.DISTRIBUTED_EVIDENCE:
                lines.append("  * Safety findings are distributed across independent regions of the medication network.")
            elif cp.concentration_type == EvidenceConcentrationType.MIXED_EVIDENCE_DISTRIBUTION:
                lines.append(f"  * Mixed pattern combining centralized drug hubs with isolated combination safety channels.")
            elif cp.concentration_type == EvidenceConcentrationType.SPARSE_EVIDENCE:
                lines.append("  * Evidence is sparse; minimal drug combinations show safety records.")
        else:
            lines.append("No active evidence concentration calculated.")
        lines.append("")

        # 4. Structural-Evidence Alignment
        lines.append("--- STRUCTURAL ↔ EVIDENCE ALIGNMENT ---")
        al = profile.structural_evidence_alignment
        if al:
            lines.append(f"Alignment category: {al.alignment_level.value}")
            lines.append(f"Explanation: {al.explanation}")
            
            # List top aligned drug
            if al.drug_alignment_profiles:
                top_drug = al.drug_alignment_profiles[0]
                lines.append(f"  * Most aligned: Medication {top_drug.display_name} (Centrality Rank #{top_drug.structural_rank}, Evidence Rank #{top_drug.evidence_participation_rank})")
        else:
            lines.append("No structural-evidence alignment profile computed.")
        lines.append("")

        # 5. Safety Guardrails Notice
        lines.append("--- CLINICAL GUARDRAIL NOTICE ---")
        lines.append("This is a synthesized evidence analysis summarizing repetitions, concentrations, and structural alignments of findings inside the graph. It does NOT establish pharmacological causality, predict patient-specific outcomes, or constitute a clinical recommendation to modify, substitute, or discontinue patient drug therapies.")
        
        return "\n".join(lines)
