"""
src/runners/prescription/run_comparison_validation.py

Executes a live comparative intelligence analysis validation run.
"""

import sys
import os
import json

# Ensure parent directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.api.service import PrescriptionService
from src.prescription.comparison.comparison_aggregator import PrescriptionComparativeIntelligenceEngine
from src.prescription.comparison.comparison_validation import ComparisonValidator

def main():
    print("Initializing Prescription Service (API level)...")
    try:
        service = PrescriptionService()
    except Exception as e:
        print(f"Error loading service: {e}")
        sys.exit(1)
        
    meds_a = ["cyclosporine", "fluconazole", "phentermine"]
    meds_b = ["cyclosporine", "fluconazole", "trioxsalen"]
    
    print(f"\nAnalyzing Baseline Prescription A: {meds_a}")
    res_a = service.analyze_prescription_advanced(meds_a)
    id_a = res_a.prescription_report.metadata.analysis_id
    
    print(f"Analyzing Variant Prescription B: {meds_b}")
    res_b = service.analyze_prescription_advanced(meds_b)
    id_b = res_b.prescription_report.metadata.analysis_id
    
    print("\nTriggering Prescription Comparative Engine (A -> B)...")
    profile_ab = PrescriptionComparativeIntelligenceEngine.compare(id_a, id_b, service)
    
    print("Triggering Prescription Comparative Engine (B -> A)...")
    profile_ba = PrescriptionComparativeIntelligenceEngine.compare(id_b, id_a, service)
    
    print("\nRunning Comparative Invariants Validation A -> B...")
    report_ab = ComparisonValidator.validate(
        profile_ab,
        service._report_objects[id_a],
        service._report_objects[id_b]
    )
    print(json.dumps(report_ab, indent=2))
    
    print("\nRunning Symmetry Verification Check...")
    symmetry_errors = []
    
    # 1. Added vs Removed check
    added_ab = profile_ab.evidence_delta.added_pairs_count
    removed_ab = profile_ab.evidence_delta.removed_pairs_count
    added_ba = profile_ba.evidence_delta.added_pairs_count
    removed_ba = profile_ba.evidence_delta.removed_pairs_count
    
    if added_ab != removed_ba:
        symmetry_errors.append(f"Symmetry Mismatch: A->B added ({added_ab}) != B->A removed ({removed_ba}).")
    if removed_ab != added_ba:
        symmetry_errors.append(f"Symmetry Mismatch: A->B removed ({removed_ab}) != B->A added ({added_ba}).")
        
    # 2. Node/edge counts checks
    node_ab = profile_ab.structural_delta.node_count_delta
    node_ba = profile_ba.structural_delta.node_count_delta
    if node_ab != -node_ba:
        symmetry_errors.append(f"Symmetry Mismatch: A->B node delta ({node_ab}) != -B->A node delta ({node_ba}).")
        
    edge_ab = profile_ab.structural_delta.edge_count_delta
    edge_ba = profile_ba.structural_delta.edge_count_delta
    if edge_ab != -edge_ba:
        symmetry_errors.append(f"Symmetry Mismatch: A->B edge delta ({edge_ab}) != -B->A edge delta ({edge_ba}).")

    if not symmetry_errors:
        print("SUCCESS: Comparison Symmetry Awareness Check Verified! All directional deltas correctly inverted.")
    else:
        print("FAILURE: Symmetry check failed:")
        for err in symmetry_errors:
            print(f"  * {err}")
        sys.exit(1)
        
    print("\n--- CLINICAL COMPARATIVE INTELLIGENCE REPORT ---")
    print(profile_ab.narrative)
    
    if report_ab["validation_passed"] and not symmetry_errors:
        print("\nSUCCESS: Phase 11 comparative intelligence engine validated successfully!")
        sys.exit(0)
    else:
        print("\nFAILURE: Phase 11 validation errors identified.")
        sys.exit(1)

if __name__ == "__main__":
    main()
