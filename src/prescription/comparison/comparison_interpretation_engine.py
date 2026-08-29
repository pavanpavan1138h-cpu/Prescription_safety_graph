from src.prescription.comparison.comparison_schema import (
    PrescriptionComparativeIntelligenceProfile
)

class ComparisonInterpretationEngine:
    @staticmethod
    def generate(profile: PrescriptionComparativeIntelligenceProfile) -> str:
        lines = []
        lines.append("=== PRESCRIPTION COMPARATIVE INTELLIGENCE REPORT ===")
        lines.append("")
        
        # 1. Executive Summary
        summary = profile.summary
        med_set = profile.medication_set_comparison
        lines.append(f"Comparison ID: {profile.comparison_id}")
        lines.append(f"Reference A: {profile.analysis_id_a} ({len(med_set.shared_drugs) + len(med_set.a_only_drugs)} drugs)")
        lines.append(f"Reference B: {profile.analysis_id_b} ({len(med_set.shared_drugs) + len(med_set.b_only_drugs)} drugs)")
        lines.append(f"Global Delta Interpretation: {summary.global_delta_interpretation.replace('_', ' ')}")
        lines.append("")

        # 2. Medication Set changes
        lines.append("--- MEDICATION DIFFERENCES ---")
        lines.append(f"Shared Drugs ({len(med_set.shared_drugs)}): {', '.join(med_set.shared_drugs) if med_set.shared_drugs else 'None'}")
        lines.append(f"Drugs in A Only ({len(med_set.a_only_drugs)}): {', '.join(med_set.a_only_drugs) if med_set.a_only_drugs else 'None'}")
        lines.append(f"Drugs in B Only ({len(med_set.b_only_drugs)}): {', '.join(med_set.b_only_drugs) if med_set.b_only_drugs else 'None'}")
        lines.append("")

        # 3. Evidence Changes
        ev = profile.evidence_delta
        lines.append("--- EVIDENCE DELTA ---")
        lines.append(f"Total Evidence status modifications: {summary.total_evidence_changes}")
        lines.append(f"  * Preserved evidence pairs: {ev.preserved_pairs_count}")
        lines.append(f"  * Reclassified evidence pairs: {ev.reclassified_pairs_count}")
        lines.append(f"  * Added evidence pairs: {ev.added_pairs_count}")
        lines.append(f"  * Removed evidence pairs: {ev.removed_pairs_count}")
        
        reclass_pairs = [p for p in ev.pair_comparisons if p.change_type == "EVIDENCE_RECLASSIFIED"]
        if reclass_pairs:
            lines.append("Reclassified Pair Details:")
            for p in reclass_pairs:
                lines.append(f"  - Pair {p.drug_a_name} + {p.drug_b_name}: {p.evidence_status_a.replace('_', ' ')} -> {p.evidence_status_b.replace('_', ' ')}")
        lines.append("")

        # 4. Structural Changes
        st = profile.structural_delta
        lines.append("--- STRUCTURAL DELTA ---")
        lines.append(f"Structural Delta Magnitude: {st.structural_delta_magnitude} / 1.0")
        lines.append(f"  * Node Count: {st.node_count_a} -> {st.node_count_b} (Delta: {st.node_count_delta})")
        lines.append(f"  * Edge Count: {st.edge_count_a} -> {st.edge_count_b} (Delta: {st.edge_count_delta})")
        lines.append(f"  * Network Density: {st.density_a:.4f} -> {st.density_b:.4f} (Delta: {st.density_delta:.4f})")
        lines.append(f"  * Connected Clusters: {st.cluster_count_a} -> {st.cluster_count_b} (Delta: {st.cluster_count_delta})")
        lines.append(f"  * Network Topology Classification: {st.topology_a} -> {st.topology_b}")
        if st.dominant_drug_changed:
            lines.append(f"  * Central Participant Shift: {st.dominant_drug_a} -> {st.dominant_drug_b}")
        else:
            lines.append(f"  * Central Participant Preserved: {st.dominant_drug_a}")
        lines.append("")

        # 5. Signal Changes
        sig = profile.signal_delta
        lines.append("--- CLINICAL SIGNAL DELTA ---")
        lines.append(f"Theme Reinforcement Shifts: {summary.total_signal_changes}")
        lines.append(f"  * Evidence Concentration: {sig.concentration_type_a} -> {sig.concentration_type_b}")
        lines.append(f"  * Structural-Evidence Alignment: {sig.alignment_level_a} -> {sig.alignment_level_b}")
        
        theme_changes = [t for t in sig.theme_comparisons if t.change_type != "THEME_PRESERVED"]
        if theme_changes:
            lines.append("Modified Signal Themes:")
            for tc in theme_changes:
                lines.append(f"  - Theme: {tc.theme_name.replace('_', ' ')} | Change: {tc.change_type.value.replace('_', ' ')}")
                lines.append(f"    * Reinforcement: {tc.reinforcement_level_a} ({tc.reinforcement_score_a}) -> {tc.reinforcement_level_b} ({tc.reinforcement_score_b})")
        lines.append("")

        # 6. Contextual Stability Changes
        stab = profile.stability_delta
        lines.append("--- CONTEXTUAL STABILITY DELTA ---")
        lines.append(f"Interpretation Stability Shift: {stab.stability_change_type.value.replace('_', ' ')}")
        lines.append(f"  * Evidence Stability Score: {stab.stability_score_a} -> {stab.stability_score_b} (Delta: {stab.stability_score_delta:.2f})")
        lines.append(f"  * Context Sensitivity Score: {stab.sensitivity_score_a} -> {stab.sensitivity_score_b} (Delta: {stab.sensitivity_score_delta:.2f})")
        lines.append(f"  * Global Stability Level: {stab.interpretation_stability_a} -> {stab.interpretation_stability_b}")
        lines.append("")

        # 7. Mandatory Warning Guardrails
        lines.append("--- CLINICAL SAFETY NOTICE ---")
        for warning in profile.guardrails:
            lines.append(warning)

        return "\n".join(lines)
