import uuid
from typing import Any, List, Dict
from src.prescription.comparison.comparison_schema import (
    PrescriptionComparativeIntelligenceProfile,
    MedicationSetComparison,
    ComparisonMetric,
    ComparisonSummary,
    MajorChange
)
from src.prescription.comparison.comparison_input_resolver import ComparisonInputResolver
from src.prescription.comparison.evidence_delta_engine import EvidenceDeltaEngine
from src.prescription.comparison.structural_delta_engine import StructuralDeltaEngine
from src.prescription.comparison.signal_delta_engine import SignalDeltaEngine
from src.prescription.comparison.stability_delta_engine import StabilityDeltaEngine
from src.prescription.comparison.normalization_engine import NormalizationEngine
from src.prescription.comparison.comparison_interpretation_engine import ComparisonInterpretationEngine
from src.prescription.comparison.comparison_validation import ComparisonValidator

class PrescriptionComparativeIntelligenceEngine:
    @staticmethod
    def compare(
        analysis_id_a: str,
        analysis_id_b: str,
        service: Any
    ) -> PrescriptionComparativeIntelligenceProfile:
        # 1. Resolve inputs
        report_a, report_b = ComparisonInputResolver.resolve(analysis_id_a, analysis_id_b, service)

        drugs_a = report_a.resolution_summary.canonical_drug_ids
        drugs_b = report_b.resolution_summary.canonical_drug_ids
        drugs_a_set = set(drugs_a)
        drugs_b_set = set(drugs_b)

        # 2. Medication Set Delta
        shared_drugs = sorted(list(drugs_a_set.intersection(drugs_b_set)))
        a_only = sorted(list(drugs_a_set - drugs_b_set))
        b_only = sorted(list(drugs_b_set - drugs_a_set))

        med_comparison = MedicationSetComparison(
            shared_drugs=shared_drugs,
            a_only_drugs=a_only,
            b_only_drugs=b_only
        )

        # 3. Load referenced snapshots A and B
        from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
        from src.prescription.intelligence.intelligence_aggregator import PrescriptionEvidenceIntelligenceAnalyzer
        from src.prescription.contextual.contextual_aggregator import ContextualStabilityAggregator

        struct_a = PrescriptionStructuralAnalyzer.analyze(report_a)
        struct_b = PrescriptionStructuralAnalyzer.analyze(report_b)

        intel_a = PrescriptionEvidenceIntelligenceAnalyzer.analyze(report_a, struct_a, service.reasoner)
        intel_b = PrescriptionEvidenceIntelligenceAnalyzer.analyze(report_b, struct_b, service.reasoner)

        stab_a = ContextualStabilityAggregator.analyze(report_a, struct_a, service.reasoner)
        stab_b = ContextualStabilityAggregator.analyze(report_b, struct_b, service.reasoner)

        # 4. Run Delta Engines
        ev_delta = EvidenceDeltaEngine.compare(report_a, report_b, set(shared_drugs))
        st_delta = StructuralDeltaEngine.compare(struct_a, struct_b, drugs_a_set, drugs_b_set)
        sig_delta = SignalDeltaEngine.compare(intel_a, intel_b)
        stab_delta = StabilityDeltaEngine.compare(stab_a, stab_b)

        # 5. General Normalization Metrics
        cov_a = NormalizationEngine.evidence_coverage(struct_a.network_summary.evidence_supported_pairs, len(drugs_a))
        cov_b = NormalizationEngine.evidence_coverage(struct_b.network_summary.evidence_supported_pairs, len(drugs_b))
        
        conv_cov_a = NormalizationEngine.convergent_coverage(report_a.evidence_summary.convergent_evidence_pairs, len(drugs_a))
        conv_cov_b = NormalizationEngine.convergent_coverage(report_b.evidence_summary.convergent_evidence_pairs, len(drugs_b))

        theme_cov_a = NormalizationEngine.theme_coverage(len([t for t in intel_a.themes if t.theme_name != "UNKNOWN_OR_UNMAPPED_THEME"]))
        theme_cov_b = NormalizationEngine.theme_coverage(len([t for t in intel_b.themes if t.theme_name != "UNKNOWN_OR_UNMAPPED_THEME"]))

        metrics = [
            ComparisonMetric(
                metric_name="Evidence Coverage Ratio",
                value_a=cov_a,
                value_b=cov_b,
                raw_difference=cov_b - cov_a,
                normalized_difference=cov_b - cov_a
            ),
            ComparisonMetric(
                metric_name="Convergent Evidence Coverage",
                value_a=conv_cov_a,
                value_b=conv_cov_b,
                raw_difference=conv_cov_b - conv_cov_a,
                normalized_difference=conv_cov_b - conv_cov_a
            ),
            ComparisonMetric(
                metric_name="Clinical Theme Coverage",
                value_a=theme_cov_a,
                value_b=theme_cov_b,
                raw_difference=theme_cov_b - theme_cov_a,
                normalized_difference=theme_cov_b - theme_cov_a
            )
        ]

        # 6. Structured Major Changes compilation (Addition 2)
        major_changes: List[MajorChange] = []

        if ev_delta.reclassified_pairs_count > 0:
            reclass_pair_names = [f"{p.drug_a_name}+{p.drug_b_name}" for p in ev_delta.pair_comparisons if p.change_type == "EVIDENCE_RECLASSIFIED"]
            major_changes.append(MajorChange(
                category="EVIDENCE",
                change_type="EVIDENCE_RECLASSIFIED",
                affected_entities=reclass_pair_names,
                magnitude=0.7,
                description=f"Evidence status changed for {len(reclass_pair_names)} drug pairs."
            ))
        if ev_delta.added_pairs_count > 0:
            major_changes.append(MajorChange(
                category="EVIDENCE",
                change_type="NEW_EVIDENCE",
                affected_entities=[f"{p.drug_a_name}+{p.drug_b_name}" for p in ev_delta.pair_comparisons if p.change_type == "NEW_EVIDENCE"],
                magnitude=0.6,
                description=f"Identified {ev_delta.added_pairs_count} new drug pairs with safety evidence."
            ))
        if ev_delta.removed_pairs_count > 0:
            major_changes.append(MajorChange(
                category="EVIDENCE",
                change_type="REMOVED_EVIDENCE",
                affected_entities=[f"{p.drug_a_name}+{p.drug_b_name}" for p in ev_delta.pair_comparisons if p.change_type == "REMOVED_EVIDENCE"],
                magnitude=0.6,
                description=f"No longer reporting safety evidence for {ev_delta.removed_pairs_count} pairs."
            ))

        if st_delta.topology_changed:
            major_changes.append(MajorChange(
                category="STRUCTURE",
                change_type="TOPOLOGY_CHANGED",
                affected_entities=[st_delta.topology_a, st_delta.topology_b],
                magnitude=0.8,
                description=f"Graph evidence network topology changed from {st_delta.topology_a} to {st_delta.topology_b}."
            ))
        if abs(st_delta.structural_delta_magnitude) > 0.1:
            major_changes.append(MajorChange(
                category="STRUCTURE",
                change_type="RESTRUCTURED",
                affected_entities=[],
                magnitude=st_delta.structural_delta_magnitude,
                description=f"Structural delta magnitude scored at {st_delta.structural_delta_magnitude} / 1.0."
            ))

        for tc in sig_delta.theme_comparisons:
            if tc.change_type in ["THEME_EMERGED", "THEME_DISAPPEARED", "REINFORCEMENT_INCREASED", "REINFORCEMENT_DECREASED"]:
                major_changes.append(MajorChange(
                    category="SIGNAL",
                    change_type=tc.change_type.value,
                    affected_entities=[tc.theme_name],
                    magnitude=0.65 if "REINFORCEMENT" in tc.change_type.value else 0.8,
                    description=f"Theme {tc.theme_name.replace('_', ' ')}: status shift to {tc.change_type.value.replace('_', ' ')}."
                ))

        if stab_delta.stability_change_type != "UNCHANGED":
            major_changes.append(MajorChange(
                category="STABILITY",
                change_type=stab_delta.stability_change_type.value,
                affected_entities=[stab_delta.interpretation_stability_a, stab_delta.interpretation_stability_b],
                magnitude=abs(stab_delta.stability_score_delta),
                description=f"Computational interpretation stability shifted to {stab_delta.stability_change_type.value.replace('_', ' ')}."
            ))

        # 7. Summary
        tot_ev = ev_delta.reclassified_pairs_count + ev_delta.added_pairs_count + ev_delta.removed_pairs_count
        tot_st = 1 if st_delta.topology_changed else 0
        tot_st += len([rc for rc in st_delta.rank_comparisons if rc.rank_delta and abs(rc.rank_delta) >= 2])
        tot_sig = len([t for t in sig_delta.theme_comparisons if t.change_type != "THEME_PRESERVED"])

        # Determine Global Delta Interpretation
        if len(drugs_a_set ^ drugs_b_set) == 0 and tot_ev == 0 and tot_st == 0 and tot_sig == 0:
            interpretation = "IDENTICAL_SNAPSHOTS"
        elif tot_ev <= 1 and tot_sig <= 1 and st_delta.structural_delta_magnitude <= 0.2:
            interpretation = "MINOR_DIFFERENCES"
        elif tot_ev <= 4 and tot_sig <= 3 and st_delta.structural_delta_magnitude <= 0.5:
            interpretation = "MODERATE_DIFFERENCES"
        else:
            interpretation = "SIGNIFICANT_DIFFERENCES"

        summary = ComparisonSummary(
            total_evidence_changes=tot_ev,
            total_structural_changes=tot_st,
            total_signal_changes=tot_sig,
            stability_shift=stab_delta.stability_change_type.value,
            global_delta_interpretation=interpretation
        )

        # 8. Preserved Characteristics
        preserved = []
        if not st_delta.topology_changed:
            preserved.append(f"Network Topology: {st_delta.topology_a}")
        if not st_delta.dominant_drug_changed:
            preserved.append(f"Central Hub Medication: {st_delta.dominant_drug_a}")
        for tc in sig_delta.theme_comparisons:
            if tc.change_type == "THEME_PRESERVED":
                preserved.append(f"Clinical Safety Theme: {tc.theme_name.replace('_', ' ')}")

        comparison_id = f"COMP_{uuid.uuid4().hex[:8].upper()}"

        profile = PrescriptionComparativeIntelligenceProfile(
            comparison_id=comparison_id,
            analysis_id_a=analysis_id_a,
            analysis_id_b=analysis_id_b,
            medication_set_comparison=med_comparison,
            evidence_delta=ev_delta,
            structural_delta=st_delta,
            signal_delta=sig_delta,
            stability_delta=stab_delta,
            comparison_metrics=metrics,
            major_changes=major_changes,
            preserved_characteristics=preserved,
            summary=summary,
            narrative=""
        )

        # 9. Narrative report generation
        profile.narrative = ComparisonInterpretationEngine.generate(profile)

        # 10. Run structural validators before returns
        v_report = ComparisonValidator.validate(profile, report_a, report_b)
        if not v_report["validation_passed"]:
            raise ValueError(f"Phase 11 validation check failed: {v_report['errors']}")

        return profile
