from src.prescription.contextual.contextual_schema import ContextualStabilityProfile

class StabilityInterpreter:
    @staticmethod
    def generate(profile: ContextualStabilityProfile) -> str:
        lines = []
        lines.append("=== PRESCRIPTION CONTEXTUAL STABILITY PROFILE ===")
        lines.append("")

        # 1. Executive Summary
        lines.append(f"Global Interpretation Stability: {profile.interpretation_stability.value.replace('_', ' ')}")
        lines.append(f"Analyzed {len(profile.scenarios)} computational scenarios (1 Baseline, {len(profile.scenarios)-1} Contextual Variants).")
        lines.append("")

        # 2. Overall Stability Scores
        lines.append("--- STABILITY & SENSITIVITY SCORES ---")
        es = profile.evidence_stability
        lines.append(f"Evidence Stability Score: {es.overall_stability_score} / 1.0")
        lines.append(f"  * Pair Preservation Ratio: {es.pair_preservation_ratio}")
        lines.append(f"  * Convergent Preservation Ratio: {es.convergent_preservation_ratio}")
        lines.append(f"  * Theme Preservation Ratio: {es.theme_preservation_ratio}")
        lines.append(f"  * Structural Edge Preservation Ratio: {es.structural_edge_preservation_ratio}")
        
        cs = profile.context_sensitivity
        lines.append(f"Context Sensitivity Score: {cs.overall_sensitivity_score} / 1.0 ({cs.sensitivity_level})")
        lines.append(f"  * Status Change Rate: {int(cs.status_change_rate * 100)}% of scenarios")
        lines.append(f"  * Topology Change Rate: {int(cs.topology_change_rate * 100)}% of scenarios")
        lines.append(f"  * Dominant Theme Change Rate: {int(cs.theme_change_rate * 100)}% of scenarios")
        lines.append("")

        # 3. Drug-level Dependency Insights
        lines.append("--- DRUG-LEVEL EVIDENCE DEPENDENCY IMPACTS ---")
        if not profile.drug_dependencies:
            lines.append("No medication dependencies mapped.")
        else:
            lines.append("Exclusion of individual medications from the analysis impacts the network structure as follows:")
            for dep in profile.drug_dependencies:
                lines.append(f"- Medication {dep.drug_id}: {dep.dependency_level.replace('_', ' ')} (Dependency Score: {dep.dependency_score})")
                lines.append(f"  * Evidence Edge Loss: {int(dep.edge_loss_ratio * 100)}%")
                lines.append(f"  * Theme Loss: {int(dep.theme_loss_ratio * 100)}%")
                lines.append(f"  * Structural Connectivity Loss: {int(dep.structural_connectivity_loss_ratio * 100)}%")
        lines.append("")

        # 4. Signal Persistence Insights
        lines.append("--- CLINICAL SIGNAL PERSISTENCE ---")
        if not profile.signal_persistences:
            lines.append("No persistent safety themes identified.")
        else:
            lines.append("Persistence of baseline clinical safety themes across subset perturbations:")
            for sp in profile.signal_persistences:
                theme_pretty = sp.theme_name.replace('_', ' ')
                lines.append(f"- Theme: {theme_pretty} | Persistence Score: {sp.persistence_score} ({sp.persistence_level})")
        lines.append("")

        # 5. Mandatory Guardrails Wording
        lines.append("--- CLINICAL WARNING NOTICE ---")
        for guardrail in profile.guardrails:
            lines.append(guardrail)
        
        return "\n".join(lines)
