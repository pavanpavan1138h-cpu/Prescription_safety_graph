"""
src/runners/prescription/run_structural_validation.py

Executes a live multi-drug structural analysis validation run.
"""

import sys
import os
import json

# Ensure parent directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.prescription.reasoning import PrescriptionSafetyReasoner
from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
from src.validation.structural_validation import StructuralValidator

def main():
    print("Initializing Prescription Safety Reasoner...")
    try:
        reasoner = PrescriptionSafetyReasoner()
    except Exception as e:
        print(f"Error loading reasoner: {e}")
        sys.exit(1)
        
    # Multi-drug prescription to trigger clustering, star/hub topology, and counterfactuals
    meds = ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
    print(f"Analyzing prescription: {meds}")
    
    report = reasoner.analyze_prescription(meds)
    print(f"Phase 6 Safety Analysis completed. Found {report.evidence_summary.pairs_with_evidence} positive pairs.")
    
    print("Running Phase 8 Network Structural Analysis...")
    analysis = PrescriptionStructuralAnalyzer.analyze(report)
    
    print("Running Structural Invariants Validation...")
    v_report = StructuralValidator.validate_analysis(analysis, report)
    
    print("\n--- VALIDATION RESULTS ---")
    print(json.dumps(v_report, indent=2))
    
    if v_report["validation_passed"]:
        print("\nSUCCESS: Phase 8 structural analysis invariants successfully verified!")
        sys.exit(0)
    else:
        print("\nFAILURE: Phase 8 validation errors identified.")
        sys.exit(1)

if __name__ == "__main__":
    main()
