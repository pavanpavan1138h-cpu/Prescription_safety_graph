from typing import Dict, List, Tuple, Any, Optional
from src.prescription.contextual.contextual_schema import (
    ScenarioProfile,
    EvidenceStabilityScore,
    SignalPersistence,
    ContextSensitivity,
    DrugDependencyImpact,
    ScenarioType,
    InterpretationStabilityLevel
)

class MetricsAnalyzer:
    @staticmethod
    def analyze(
        scenarios: List[ScenarioProfile],
        baseline_profile: ScenarioProfile,
        baseline_struct: Any,
        baseline_intel: Any,
        scenario_map: Dict[str, Tuple[ScenarioProfile, Any, Any]]
    ) -> Tuple[
        EvidenceStabilityScore,
        List[SignalPersistence],
        ContextSensitivity,
        List[DrugDependencyImpact],
        InterpretationStabilityLevel
    ]:
        single_drug_scenarios = [s for s in scenarios if s.scenario_type == ScenarioType.SINGLE_DRUG_PERTURBATION]
        
        # Default fallback values for single-drug prescription context
        if not single_drug_scenarios:
            stability = EvidenceStabilityScore(1.0, 1.0, 1.0, 1.0, 1.0)
            persistences = []
            for theme in baseline_intel.themes:
                if theme.theme_name != "UNKNOWN_OR_UNMAPPED_THEME":
                    persistences.append(SignalPersistence(
                        theme_name=theme.theme_name,
                        persistence_score=1.0,
                        persistence_level="HIGHLY_PERSISTENT"
                    ))
            sensitivity = ContextSensitivity(0.0, "LOW_CONTEXT_SENSITIVITY", 0.0, 0.0, 0.0)
            dependencies = []
            for did in baseline_profile.included_drugs:
                dependencies.append(DrugDependencyImpact(
                    drug_id=did,
                    display_name=did,
                    dependency_score=0.0,
                    dependency_level="LOW_EVIDENCE_DEPENDENCY",
                    edge_loss_ratio=0.0,
                    theme_loss_ratio=0.0,
                    structural_connectivity_loss_ratio=0.0
                ))
            return stability, persistences, sensitivity, dependencies, InterpretationStabilityLevel.HIGH_INTERPRETATION_STABILITY

        # ----------------------------------------------------
        # 1. Evidence Stability Score Calculation
        # ----------------------------------------------------
        pair_ratios = []
        conv_ratios = []
        theme_ratios = []
        struct_ratios = []
        scenario_scores = []

        baseline_edges = baseline_profile.surviving_edges_count
        baseline_conv = baseline_profile.surviving_convergent_edges_count
        baseline_themes = baseline_profile.surviving_themes_count
        baseline_struct_edges = len(baseline_struct.original_network.edges)

        for s in single_drug_scenarios:
            p_pairs = s.surviving_edges_count / max(1, baseline_edges)
            p_conv = s.surviving_convergent_edges_count / max(1, baseline_conv)
            p_themes = s.surviving_themes_count / max(1, baseline_themes)

            # Get structural edges count
            _, s_struct, _ = scenario_map[s.scenario_id]
            s_struct_edges = len(s_struct.original_network.edges)
            p_struct = s_struct_edges / max(1, baseline_struct_edges)

            pair_ratios.append(p_pairs)
            conv_ratios.append(p_conv)
            theme_ratios.append(p_themes)
            struct_ratios.append(p_struct)

            # Compute scenario-specific stability score
            w_sum = 0.35
            num_term = 0.35 * p_pairs
            
            if baseline_conv > 0:
                w_sum += 0.25
                num_term += 0.25 * p_conv
            if baseline_themes > 0:
                w_sum += 0.20
                num_term += 0.20 * p_themes
            if baseline_struct_edges > 0:
                w_sum += 0.20
                num_term += 0.20 * p_struct

            scenario_scores.append(num_term / w_sum)

        avg_pairs = round(sum(pair_ratios) / len(pair_ratios), 3)
        avg_conv = round(sum(conv_ratios) / len(conv_ratios), 3)
        avg_themes = round(sum(theme_ratios) / len(theme_ratios), 3)
        avg_struct = round(sum(struct_ratios) / len(struct_ratios), 3)
        overall_stability = round(sum(scenario_scores) / len(scenario_scores), 3)

        stability_score_obj = EvidenceStabilityScore(
            overall_stability_score=overall_stability,
            pair_preservation_ratio=avg_pairs,
            convergent_preservation_ratio=avg_conv,
            theme_preservation_ratio=avg_themes,
            structural_edge_preservation_ratio=avg_struct
        )

        # ----------------------------------------------------
        # 2. Signal Persistence
        # ----------------------------------------------------
        persistences = []
        for baseline_t in baseline_intel.themes:
            if baseline_t.theme_name == "UNKNOWN_OR_UNMAPPED_THEME":
                continue
            
            # Count scenarios retaining this theme
            retaining_count = 0
            for s in single_drug_scenarios:
                _, _, s_intel = scenario_map[s.scenario_id]
                has_theme = any(
                    t.theme_name == baseline_t.theme_name and len(t.supporting_pairs) > 0
                    for t in s_intel.themes
                )
                if has_theme:
                    retaining_count += 1
            
            score = round(retaining_count / len(single_drug_scenarios), 3)
            
            if score >= 0.80:
                lvl = "HIGHLY_PERSISTENT"
            elif score >= 0.60:
                lvl = "PERSISTENT"
            elif score >= 0.40:
                lvl = "MODERATELY_PERSISTENT"
            elif score >= 0.20:
                lvl = "CONTEXT_SENSITIVE"
            else:
                lvl = "HIGHLY_CONTEXT_DEPENDENT"

            persistences.append(SignalPersistence(
                theme_name=baseline_t.theme_name,
                persistence_score=score,
                persistence_level=lvl
            ))

        # Sort persistences by score descending
        persistences.sort(key=lambda x: x.persistence_score, reverse=True)

        # ----------------------------------------------------
        # 3. Context Sensitivity
        # ----------------------------------------------------
        sensitivities = []
        status_changes = 0
        topology_changes = 0
        theme_changes = 0

        for s in single_drug_scenarios:
            d_status = 1.0 if s.prescription_status != baseline_profile.prescription_status else 0.0
            d_topology = 1.0 if s.topology_classification != baseline_profile.topology_classification else 0.0
            d_theme = 1.0 if s.dominant_theme != baseline_profile.dominant_theme else 0.0
            
            # Check reinforcement change
            d_reinforcement = 0.0
            if s.reinforcement_level_distribution != baseline_profile.reinforcement_level_distribution:
                d_reinforcement = 1.0
                
            # Check concentration change
            d_concentration = 0.0
            if s.evidence_concentration != baseline_profile.evidence_concentration:
                d_concentration = 1.0

            if d_status > 0:
                status_changes += 1
            if d_topology > 0:
                topology_changes += 1
            if d_theme > 0:
                theme_changes += 1

            sens_val = (
                0.30 * d_status +
                0.20 * d_topology +
                0.20 * d_theme +
                0.15 * d_reinforcement +
                0.15 * d_concentration
            )
            sensitivities.append(sens_val)

        overall_sens = round(sum(sensitivities) / len(sensitivities), 3)
        
        if overall_sens < 0.20:
            sens_lvl = "LOW_CONTEXT_SENSITIVITY"
        elif overall_sens < 0.40:
            sens_lvl = "MODERATE_CONTEXT_SENSITIVITY"
        elif overall_sens < 0.60:
            sens_lvl = "HIGH_CONTEXT_SENSITIVITY"
        else:
            sens_lvl = "VERY_HIGH_CONTEXT_SENSITIVITY"

        sensitivity_obj = ContextSensitivity(
            overall_sensitivity_score=overall_sens,
            sensitivity_level=sens_lvl,
            status_change_rate=round(status_changes / len(single_drug_scenarios), 3),
            topology_change_rate=round(topology_changes / len(single_drug_scenarios), 3),
            theme_change_rate=round(theme_changes / len(single_drug_scenarios), 3)
        )

        # ----------------------------------------------------
        # 4. Drug Dependency Impacts
        # ----------------------------------------------------
        dependencies = []
        for did in baseline_profile.included_drugs:
            scen_id = f"SCENARIO_EXCLUDE_{did}"
            if scen_id in scenario_map:
                s_profile, s_struct, _ = scenario_map[scen_id]
                
                loss_e = round(1.0 - (s_profile.surviving_edges_count / max(1, baseline_edges)), 3)
                loss_c = round(1.0 - (s_profile.surviving_convergent_edges_count / max(1, baseline_conv)), 3)
                loss_t = round(1.0 - (s_profile.surviving_themes_count / max(1, baseline_themes)), 3)
                
                s_struct_edges = len(s_struct.original_network.edges)
                loss_s = round(1.0 - (s_struct_edges / max(1, baseline_struct_edges)), 3)

                # Compute weighted dependency score
                w_sum = 0.35 + 0.15
                num_term = 0.35 * loss_e + 0.15 * loss_s
                
                if baseline_conv > 0:
                    w_sum += 0.30
                    num_term += 0.30 * loss_c
                if baseline_themes > 0:
                    w_sum += 0.20
                    num_term += 0.20 * loss_t
                    
                dep_score = round(num_term / w_sum, 3)

                if dep_score >= 0.75:
                    dep_lvl = "HIGH_EVIDENCE_DEPENDENCY"
                elif dep_score >= 0.50:
                    dep_lvl = "MODERATE_EVIDENCE_DEPENDENCY"
                elif dep_score >= 0.25:
                    dep_lvl = "LIMITED_EVIDENCE_DEPENDENCY"
                else:
                    dep_lvl = "LOW_EVIDENCE_DEPENDENCY"

                # Find drug display name
                drug_display = did
                for drug_obj in baseline_intel.themes:
                    # Look up from theme participating drugs or we can search resolved drugs
                    pass

                dependencies.append(DrugDependencyImpact(
                    drug_id=did,
                    display_name=did,  # Service level mapper will pretty print if needed
                    dependency_score=dep_score,
                    dependency_level=dep_lvl,
                    edge_loss_ratio=loss_e,
                    theme_loss_ratio=loss_t,
                    structural_connectivity_loss_ratio=loss_s
                ))
            else:
                dependencies.append(DrugDependencyImpact(
                    drug_id=did,
                    display_name=did,
                    dependency_score=0.0,
                    dependency_level="LOW_EVIDENCE_DEPENDENCY",
                    edge_loss_ratio=0.0,
                    theme_loss_ratio=0.0,
                    structural_connectivity_loss_ratio=0.0
                ))

        # Sort dependencies by score descending
        dependencies.sort(key=lambda x: x.dependency_score, reverse=True)

        # ----------------------------------------------------
        # 5. Interpretation Stability
        # ----------------------------------------------------
        stable_count = 0
        partial_count = 0
        for sens_val in sensitivities:
            if sens_val <= 0.15:
                stable_count += 1
            elif sens_val <= 0.45:
                partial_count += 1

        stable_ratio = stable_count / len(single_drug_scenarios)
        stable_or_partial_ratio = (stable_count + partial_count) / len(single_drug_scenarios)

        if stable_ratio >= 0.80:
            global_stability = InterpretationStabilityLevel.HIGH_INTERPRETATION_STABILITY
        elif stable_or_partial_ratio >= 0.60:
            global_stability = InterpretationStabilityLevel.MODERATE_INTERPRETATION_STABILITY
        elif stable_or_partial_ratio >= 0.30:
            global_stability = InterpretationStabilityLevel.LOW_INTERPRETATION_STABILITY
        else:
            global_stability = InterpretationStabilityLevel.FRAGILE_INTERPRETATION

        return stability_score_obj, persistences, sensitivity_obj, dependencies, global_stability
