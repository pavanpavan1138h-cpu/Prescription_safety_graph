"""
src/runners/prescription/run_contextual_validation.py

Executes a live multi-drug evidence contextual stability validation run.
"""

import sys
import os
import json

# Ensure parent directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.prescription.reasoning import PrescriptionSafetyReasoner
from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
from src.prescription.contextual.contextual_aggregator import ContextualStabilityAggregator
from src.prescription.contextual.contextual_validation import ContextualStabilityValidator

def main():
    print("Initializing Prescription Safety Reasoner...")
    try:
        reasoner = PrescriptionSafetyReasoner()
    except Exception as e:
        print(f"Error loading reasoner: {e}")
        sys.exit(1)
        
    meds = ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
    print(f"Analyzing prescription: {meds}")
    
    report = reasoner.analyze_prescription(meds)
    print(f"Phase 6 Safety Analysis completed. Found {report.evidence_summary.pairs_with_evidence} positive pairs.")
    
    print("Running Phase 8 Network Structural Analysis...")
    structural_analysis = PrescriptionStructuralAnalyzer.analyze(report)
    
    print("Running Phase 10 Contextual Stability Analysis...")
    stability_profile = ContextualStabilityAggregator.analyze(report, structural_analysis, reasoner)
    
    print("Running Contextual Invariants Validation...")
    v_report = ContextualStabilityValidator.validate(stability_profile, report)
    
    print("\n--- VALIDATION SUMMARY ---")
    print(json.dumps(v_report, indent=2))
    
    print("\n--- CLINICAL EXECUTIVE NARRATIVE REPORT ---")
    print(stability_profile.summary_narrative)
    
    if v_report["validation_passed"]:
        print("\nSUCCESS: Phase 10 contextual stability analysis invariants successfully verified!")
        sys.exit(0)
    else:
        print("\nFAILURE: Phase 10 validation errors identified.")
        sys.exit(1)

if __name__ == "__main__":
    main()
