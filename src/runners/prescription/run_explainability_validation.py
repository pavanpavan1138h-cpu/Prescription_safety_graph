"""
src/runners/prescription/run_explainability_validation.py

Standalone runner executing and verifying the Phase 11 Explainability & Reverse Traversal Engine.
"""

import sys
import json
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from src.api.service import PrescriptionService
from src.prescription.explainability.explainability_aggregator import ExplainabilityAggregator
from src.prescription.explainability.explainability_validation import ExplainabilityValidator

def run_validation():
    print("Initializing PrescriptionService for Phase 11 Validation...")
    service = PrescriptionService()

    medications = ["cyclosporine", "fluconazole", "phentermine"]
    print(f"Running Baseline Advanced Prescription Analysis for: {medications}")
    adv_res = service.analyze_prescription_advanced(medications=medications)

    baseline_rx = adv_res.prescription_report
    struct_analysis = adv_res.structural_analysis
    ev_intel = adv_res.evidence_intelligence
    ctx_stab = adv_res.contextual_stability

    print("Executing Phase 11 ExplainabilityAggregator...")
    aggregator = ExplainabilityAggregator()
    profile = aggregator.generate_explainability_profile(
        analysis_result=baseline_rx,
        structural_analysis=struct_analysis,
        evidence_intelligence=ev_intel,
        contextual_stability=ctx_stab
    )

    print(f"Explainability Profile Generated (Prescription ID: {profile.prescription_id})")
    print(f"  - Nodes Count: {len(profile.explanation_graph.nodes)}")
    print(f"  - Edges Count: {len(profile.explanation_graph.edges)}")
    print(f"  - Provenance Records: {len(profile.provenance_records)}")
    print(f"  - Traceability Coverage: {profile.traceability_profile.traceability_coverage_score * 100:.1f}%")
    print(f"  - Top Contributor: {profile.contribution_profiles[0].entity_label} ({profile.contribution_profiles[0].contribution_level.value})")

    print("\nValidating Phase 11 Invariants...")
    validator = ExplainabilityValidator()
    is_valid, errors, warnings = validator.validate_profile(profile)

    summary = {
        "validation_passed": is_valid,
        "error_count": len(errors),
        "errors": errors,
        "warning_count": len(warnings),
        "warnings": warnings,
        "traceability_coverage": profile.traceability_profile.traceability_coverage_score,
        "cross_layer_traceability": profile.traceability_profile.cross_layer_traceability.value
    }
    print(json.dumps(summary, indent=2))

    if not is_valid:
        print("FAIL: Phase 11 explainability validation failed!")
        sys.exit(1)

    print("\nSUCCESS: Phase 11 explainability engine validated successfully!")

if __name__ == "__main__":
    run_validation()
