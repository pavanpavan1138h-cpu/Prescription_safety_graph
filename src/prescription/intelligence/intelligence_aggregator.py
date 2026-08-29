from datetime import datetime
from typing import Any, List, Optional
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.intelligence.intelligence_schema import (
    PrescriptionEvidenceIntelligenceProfile,
    EvidenceTheme,
    CrossPairSignalGroup,
    EvidenceConcentrationProfile,
    StructuralEvidenceAlignment,
    EvidenceIntelligenceSummary,
    EvidenceThemeType,
    ReinforcementLevel,
    AlignmentLevel
)
from src.prescription.intelligence.signal_grouping_engine import SignalGroupingEngine
from src.prescription.intelligence.reinforcement_engine import ReinforcementEngine
from src.prescription.intelligence.concentration_analyzer import ConcentrationAnalyzer
from src.prescription.intelligence.alignment_engine import AlignmentEngine
from src.prescription.intelligence.intelligence_interpretation_engine import IntelligenceInterpretationEngine

class PrescriptionEvidenceIntelligenceAnalyzer:
    @staticmethod
    def analyze(
        report: PrescriptionSafetyReport,
        structural_analysis: Any,
        reasoner: Any
    ) -> PrescriptionEvidenceIntelligenceProfile:
        analysis_id = report.prescription_id
        generated_at = datetime.now().isoformat()

        # 1. Themes and Signal Groups mapping
        themes, signal_groups = SignalGroupingEngine.analyze(report, reasoner)

        # 2. Reinforcement scoring for each signal group
        for sg in signal_groups:
            score, level = ReinforcementEngine.analyze(sg, report, structural_analysis)
            sg.reinforcement_score = score
            sg.reinforcement_level = level

        # Sort signal groups by reinforcement score descending
        signal_groups.sort(key=lambda x: x.reinforcement_score, reverse=True)

        # 3. Evidence Concentration Profile
        concentration_profile = ConcentrationAnalyzer.analyze(report, structural_analysis)

        # 4. Structural-Evidence Alignment
        alignment = AlignmentEngine.analyze(report, structural_analysis, themes)

        # 5. Compile Summary Stats
        major_themes = [t for t in themes if t.theme_name != EvidenceThemeType.UNKNOWN_OR_UNMAPPED_THEME.value]
        major_theme_count = len(major_themes)
        
        reinforced_groups = [g for g in signal_groups if g.reinforcement_level != ReinforcementLevel.LIMITED_REINFORCEMENT]
        reinforced_count = len(reinforced_groups)

        # Dominant theme (theme with the highest supporting pair count)
        dominant_theme = None
        if major_themes:
            dom_t = max(major_themes, key=lambda t: len(t.supporting_pairs))
            dominant_theme = dom_t.theme_name

        # Strongest reinforcement level
        strongest_reinforcement = ReinforcementLevel.LIMITED_REINFORCEMENT
        if signal_groups:
            # Ranks: STRONG > MODERATE > EMERGING > LIMITED
            level_rank = {
                ReinforcementLevel.STRONG_REINFORCEMENT: 4,
                ReinforcementLevel.MODERATE_REINFORCEMENT: 3,
                ReinforcementLevel.EMERGING_REINFORCEMENT: 2,
                ReinforcementLevel.LIMITED_REINFORCEMENT: 1
            }
            max_sg = max(signal_groups, key=lambda sg: level_rank.get(sg.reinforcement_level, 1))
            strongest_reinforcement = max_sg.reinforcement_level

        # Compile Summary Object
        summary = EvidenceIntelligenceSummary(
            major_theme_count=major_theme_count,
            reinforced_signal_group_count=reinforced_count,
            dominant_theme=dominant_theme,
            dominant_evidence_concentration=concentration_profile.concentration_type,
            strongest_reinforcement_level=strongest_reinforcement,
            highest_alignment_level=alignment.alignment_level,
            overall_intelligence_pattern=f"{major_theme_count} themes | {reinforced_count} reinforced signals | {concentration_profile.concentration_type.value}"
        )

        # Assemble core Profile container
        profile = PrescriptionEvidenceIntelligenceProfile(
            analysis_id=analysis_id,
            generated_at=generated_at,
            themes=themes,
            signal_groups=signal_groups,
            concentration_profile=concentration_profile,
            structural_evidence_alignment=alignment,
            summary=summary,
            narrative="",
            guardrails=[
                "Evidence reinforcement represents consistency within the graph and is not a prediction of clinical patient outcome.",
                "Adverse-event theme mappings are deterministic classifications based on raw observed data.",
                "Alignment levels indicate structural correlation and do not establish pharmacological causality.",
                "This engine acts as a query aggregator and does not constitute medical advice or therapy recommendations."
            ]
        )

        # 6. Generate clinical interpretation narrative
        profile.narrative = IntelligenceInterpretationEngine.generate(profile)

        return profile
