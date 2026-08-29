from typing import Any, List, Dict, Set
from src.prescription.comparison.comparison_schema import (
    SignalDelta,
    ThemeComparison,
    SignalChangeType
)

class SignalDeltaEngine:
    @staticmethod
    def compare(
        intel_a: Any,
        intel_b: Any
    ) -> SignalDelta:
        themes_a = {t.theme_name: t for t in intel_a.themes if t.theme_name != "UNKNOWN_OR_UNMAPPED_THEME"}
        themes_b = {t.theme_name: t for t in intel_b.themes if t.theme_name != "UNKNOWN_OR_UNMAPPED_THEME"}

        all_themes = set(themes_a.keys()).union(themes_b.keys())
        theme_comparisons: List[ThemeComparison] = []

        for theme in sorted(all_themes):
            ta = themes_a.get(theme)
            tb = themes_b.get(theme)

            if ta and tb:
                score_a = ta.supporting_evidence_count
                score_b = tb.supporting_evidence_count
                # Retrieve matching signal group reinforcement scores if available
                # or default to supporting evidence count as scores
                # Wait, reinforcement_score inside signal groups could be compared if the group is found.
                # Let's check matching signal groups in signal_groups list for that theme.
                sg_a = next((g for g in intel_a.signal_groups if g.theme_id == ta.theme_id), None)
                sg_b = next((g for g in intel_b.signal_groups if g.theme_id == tb.theme_id), None)

                r_score_a = sg_a.reinforcement_score if sg_a else float(ta.supporting_evidence_count)
                r_score_b = sg_b.reinforcement_score if sg_b else float(tb.supporting_evidence_count)
                r_level_a = sg_a.reinforcement_level.value if sg_a else "UNREINFORCED"
                r_level_b = sg_b.reinforcement_level.value if sg_b else "UNREINFORCED"

                if r_score_b > r_score_a:
                    change = SignalChangeType.REINFORCEMENT_INCREASED
                elif r_score_b < r_score_a:
                    change = SignalChangeType.REINFORCEMENT_DECREASED
                else:
                    change = SignalChangeType.THEME_PRESERVED

                theme_comparisons.append(ThemeComparison(
                    theme_name=theme,
                    reinforcement_score_a=r_score_a,
                    reinforcement_score_b=r_score_b,
                    reinforcement_level_a=r_level_a,
                    reinforcement_level_b=r_level_b,
                    supporting_pairs_a=ta.supporting_pairs,
                    supporting_pairs_b=tb.supporting_pairs,
                    participating_drugs_a=ta.participating_drugs,
                    participating_drugs_b=tb.participating_drugs,
                    change_type=change
                ))
            
            elif ta:
                sg_a = next((g for g in intel_a.signal_groups if g.theme_id == ta.theme_id), None)
                r_score_a = sg_a.reinforcement_score if sg_a else float(ta.supporting_evidence_count)
                r_level_a = sg_a.reinforcement_level.value if sg_a else "UNREINFORCED"

                theme_comparisons.append(ThemeComparison(
                    theme_name=theme,
                    reinforcement_score_a=r_score_a,
                    reinforcement_score_b=0.0,
                    reinforcement_level_a=r_level_a,
                    reinforcement_level_b="NO_REINFORCEMENT",
                    supporting_pairs_a=ta.supporting_pairs,
                    supporting_pairs_b=[],
                    participating_drugs_a=ta.participating_drugs,
                    participating_drugs_b=[],
                    change_type=SignalChangeType.THEME_DISAPPEARED
                ))
            
            else:
                sg_b = next((g for g in intel_b.signal_groups if g.theme_id == tb.theme_id), None)
                r_score_b = sg_b.reinforcement_score if sg_b else float(tb.supporting_evidence_count)
                r_level_b = sg_b.reinforcement_level.value if sg_b else "UNREINFORCED"

                theme_comparisons.append(ThemeComparison(
                    theme_name=theme,
                    reinforcement_score_a=0.0,
                    reinforcement_score_b=r_score_b,
                    reinforcement_level_a="NO_REINFORCEMENT",
                    reinforcement_level_b=r_level_b,
                    supporting_pairs_a=[],
                    supporting_pairs_b=tb.supporting_pairs,
                    participating_drugs_a=[],
                    participating_drugs_b=tb.participating_drugs,
                    change_type=SignalChangeType.THEME_EMERGED
                ))

        conc_a = intel_a.concentration_profile.concentration_type.value if intel_a.concentration_profile else "UNKNOWN_CONCENTRATION"
        conc_b = intel_b.concentration_profile.concentration_type.value if intel_b.concentration_profile else "UNKNOWN_CONCENTRATION"
        conc_changed = conc_a != conc_b

        align_a = intel_a.structural_evidence_alignment.alignment_level.value if intel_a.structural_evidence_alignment else "NO_ALIGNMENT"
        align_b = intel_b.structural_evidence_alignment.alignment_level.value if intel_b.structural_evidence_alignment else "NO_ALIGNMENT"
        align_changed = align_a != align_b

        return SignalDelta(
            theme_comparisons=theme_comparisons,
            concentration_type_a=conc_a,
            concentration_type_b=conc_b,
            concentration_changed=conc_changed,
            alignment_level_a=align_a,
            alignment_level_b=align_b,
            alignment_changed=align_changed
        )
