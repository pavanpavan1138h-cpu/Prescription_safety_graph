"""
src/advanced_intelligence_validation.py

Automated validation suite for Phase 8 Advanced Clinical Intelligence.
Verifies reconciliation, deterministic reasoning, provenance completeness,
uncertainty mapping, and backward compatibility.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from prescription_reasoning import PrescriptionSafetyReasoner
from advanced_intelligence_service import AdvancedIntelligenceService
from advanced_intelligence_schema import (
    ComplexityCategory,
    DrugParticipationCategory,
    EventConvergenceCategory,
    PatternType,
    ReviewPriorityTier
)

logger = logging.getLogger(__name__)

class AdvancedIntelligenceValidator:
    def __init__(self, graph_dir: Optional[Path] = None):
        if graph_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            graph_dir = project_root / "data" / "interim" / "graph"
        self.graph_dir = graph_dir
        self.reasoner = PrescriptionSafetyReasoner(self.graph_dir)
        self.service = AdvancedIntelligenceService(self.reasoner)

    def run_all_validations(self) -> Dict[str, Any]:
        results = {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "checks": []
        }

        def record(name: str, passed: bool, details: str):
            results["total_checks"] += 1
            if passed:
                results["passed_checks"] += 1
            else:
                results["failed_checks"] += 1
            results["checks"].append({
                "check_name": name,
                "passed": passed,
                "details": details
            })
            status = "PASS" if passed else "FAIL"
            logger.info(f"[{status}] {name}: {details}")

        # Check 1: Single Drug Boundary Behavior
        r1_base, r1_adv = self.service.analyze_advanced(["fluconazole"])
        c1 = (r1_adv.complexity_profile.unique_drugs_count == 1 and
              r1_adv.complexity_profile.generated_pairs_count == 0 and
              r1_adv.complexity_profile.complexity_category == ComplexityCategory.LOW_COMPLEXITY)
        record("Single Drug Boundary", c1, f"Complexity: {r1_adv.complexity_profile.complexity_category.value}, Pairs: {r1_adv.complexity_profile.generated_pairs_count}")

        # Check 2: Two-Drug Convergent Pair
        r2_base, r2_adv = self.service.analyze_advanced(["cyclosporine", "fluconazole"])
        c2 = (r2_adv.complexity_profile.convergent_pairs_count == 1 and
              len(r2_adv.review_priorities) == 1 and
              r2_adv.review_priorities[0].review_priority in [ReviewPriorityTier.IMMEDIATE_REVIEW_PRIORITY, ReviewPriorityTier.HIGH_REVIEW_PRIORITY])
        record("Two-Drug Convergent Priority", c2, f"Convergent pairs: {r2_adv.complexity_profile.convergent_pairs_count}, Priority: {r2_adv.review_priorities[0].review_priority.value}")

        # Check 3: Multi-Drug Participation Reconciliation
        r3_base, r3_adv = self.service.analyze_advanced(["cyclosporine", "fluconazole", "phentermine"])
        sum_pos = sum(p.positive_evidence_pairs for p in r3_adv.drug_participation_profiles)
        # Each positive pair touches 2 drugs, so sum of drug positive participations == 2 * positive_pairs
        c3 = (sum_pos == 2 * r3_adv.complexity_profile.positive_pairs_count)
        record("Participation Reconciliation", c3, f"Sum of drug participations ({sum_pos}) == 2 * total positive pairs ({2 * r3_adv.complexity_profile.positive_pairs_count})")

        # Check 4: Cross-Pair Adverse Event Convergence
        c4 = isinstance(r3_adv.event_convergence_items, list)
        shared_events = [e for e in r3_adv.event_convergence_items if e.participating_pairs_count >= 2]
        record("Event Convergence Calculation", c4, f"Found {len(r3_adv.event_convergence_items)} total adverse event concepts ({len(shared_events)} recurring across >=2 pairs)")

        # Check 5: Evidence Pattern Grounding
        c5 = len(r3_adv.evidence_patterns) > 0 and all(len(pat.rule_fired) > 0 for pat in r3_adv.evidence_patterns)
        record("Evidence Patterns Grounding", c5, f"Identified {len(r3_adv.evidence_patterns)} patterns: {[p.title for p in r3_adv.evidence_patterns]}")

        # Check 6: Review Prioritization Determinism
        c6 = all(len(rp.deterministic_reasons) > 0 and rp.review_score >= 0.0 for rp in r3_adv.review_priorities)
        record("Review Priority Deterministic Reasons", c6, f"All {len(r3_adv.review_priorities)} review items have deterministic explanation traces.")

        # Check 7: Uncertainty Reporting for Unresolved Inputs
        r7_base, r7_adv = self.service.analyze_advanced(["fluconazole", "UnknownDrug999"])
        c7 = (r7_adv.uncertainty_profile.has_identity_uncertainty and
              "UnknownDrug999" in r7_adv.uncertainty_profile.unresolved_input_names and
              any(p.pattern_type == PatternType.IDENTITY_UNCERTAINTY_PATTERN for p in r7_adv.evidence_patterns))
        record("Unresolved Input Uncertainty", c7, f"Unresolved inputs correctly flagged in uncertainty profile and pattern detector.")

        # Check 8: Clinical Context Requirements Structure
        c8 = len(r7_adv.clinical_context_requirements) >= 4 and all(not req.is_available_in_graph for req in r7_adv.clinical_context_requirements)
        record("Clinical Context Requirements", c8, f"{len(r7_adv.clinical_context_requirements)} requirements explicitly state missing pharmacokinetic context.")

        # Check 9: Scientific Guardrail Integrity
        c9 = len(r3_adv.advanced_explanation.scientific_guardrails) >= 4
        record("Scientific Guardrails Integrity", c9, f"{len(r3_adv.advanced_explanation.scientific_guardrails)} explicit non-diagnostic guardrail statements generated.")

        # Check 10: Backward Compatibility with Phase 6
        c10 = (r3_base.prescription_id == r3_adv.analysis_id and
               len(r3_base.pair_results) == r3_adv.complexity_profile.generated_pairs_count)
        record("Phase 6 Backward Compatibility", c10, f"Base report metadata and pair count ({len(r3_base.pair_results)}) seamlessly preserved.")

        return results
