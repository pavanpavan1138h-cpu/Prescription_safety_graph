"""
src/advanced_intelligence_service.py

Orchestrator integrating Phase 6 PrescriptionSafetyReasoner with all Phase 8
Advanced Clinical Intelligence engines.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

from src.prescription.reasoning import PrescriptionSafetyReasoner
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.advanced_intelligence_schema import (
    AdvancedPrescriptionIntelligenceReport,
    PrescriptionComplexityProfile,
    DrugParticipationProfile,
    AdverseEventConvergenceItem,
    EvidencePatternItem,
    ReviewPriorityFinding,
    UncertaintyProfile,
    ClinicalContextRequirement,
    AdvancedExplanationSummary,
    PatientContext,
    DrugRiskAssessment,
)
from src.prescription.advanced_intelligence_engines import (
    PrescriptionComplexityEngine,
    DrugParticipationEngine,
    CrossPairEventConvergenceEngine,
    EvidencePatternEngine,
    ReviewPrioritizationEngine,
    UncertaintyEngine,
    ContextRequirementsEngine,
    AdvancedExplanationEngine
)

class AdvancedIntelligenceService:
    def __init__(self, reasoner: Optional[PrescriptionSafetyReasoner] = None):
        if reasoner is None:
            self.reasoner = PrescriptionSafetyReasoner()
        else:
            self.reasoner = reasoner

    def analyze_advanced(
        self,
        medications: List[str],
        prescription_id: Optional[str] = None,
        patient_context: Optional[PatientContext] = None
    ) -> Tuple[PrescriptionSafetyReport, AdvancedPrescriptionIntelligenceReport]:
        # 1. Run canonical Phase 6 Multi-Drug Analysis
        report = self.reasoner.analyze_prescription(medications, prescription_id)

        # Classify drug risks for resolved drugs
        from src.prescription.risk.risk_classifier import DrugRiskClassifier
        classifier = DrugRiskClassifier()
        drug_risk_assessments = []
        for d in report.resolution_summary.resolved_drugs:
            if d.resolved_internal_drug_id:
                dra = classifier.classify_drug(
                    internal_drug_id=d.resolved_internal_drug_id,
                    rxcui=d.rxcui,
                    drug_name=d.display_name or d.original_input
                )
                drug_risk_assessments.append(dra)

        # 2. Part 2: Prescription Complexity Profile
        complexity = PrescriptionComplexityEngine.analyze(report)

        # 3. Part 3: Drug Participation Profiles
        part_profiles = DrugParticipationEngine.analyze(report)

        # 4. Part 4: Cross-Pair Adverse Event Convergence
        event_conv_items = CrossPairEventConvergenceEngine.analyze(report, self.reasoner)

        # 5. Part 5: Evidence Pattern Detection
        patterns = EvidencePatternEngine.analyze(report, part_profiles, event_conv_items)

        # 6. Part 6: Review Prioritization (with Box 9 Modifiers)
        priorities = ReviewPrioritizationEngine.analyze(
            report, part_profiles, event_conv_items,
            patient_context=patient_context,
            drug_risk_assessments=drug_risk_assessments
        )

        # 7. Part 7: Uncertainty Profile
        uncertainty = UncertaintyEngine.analyze(report)

        # 8. Part 8: Context Requirements
        context_reqs = ContextRequirementsEngine.get_requirements()

        # 9. Part 9: Advanced Explanations & Guardrails
        explanation = AdvancedExplanationEngine.generate(
            report, complexity, patterns, priorities, uncertainty
        )

        # Assemble full analytical report
        effective_context = patient_context or PatientContext()
        advanced_report = AdvancedPrescriptionIntelligenceReport(
            analysis_id=report.prescription_id,
            generated_at=datetime.now().isoformat(),
            complexity_profile=complexity,
            drug_participation_profiles=part_profiles,
            event_convergence_items=event_conv_items,
            evidence_patterns=patterns,
            review_priorities=priorities,
            uncertainty_profile=uncertainty,
            clinical_context_requirements=context_reqs,
            advanced_explanation=explanation,
            scientific_limitations=[
                "Evidence priority reflects structured knowledge graph density, not clinical severity.",
                "TWOSIDES combination adverse event counts are observational surveillance reports, not verified pharmacological causality.",
                "Absence of direct evidence in DrugBank/TWOSIDES does not establish safety.",
                "Patient-specific parameters (dose, age, renal/hepatic clearance) are required for clinical prescription validation."
            ],
            patient_context=effective_context,
            drug_risk_assessments=drug_risk_assessments
        )

        return report, advanced_report
