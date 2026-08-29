"""
src/runners/prescription/run_intelligence_validation.py

Executes a live multi-drug evidence intelligence validation run.
"""

import sys
import os
import json

# Ensure parent directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.prescription.reasoning import PrescriptionSafetyReasoner
from src.prescription.structural.prescription_structural_analyzer import PrescriptionStructuralAnalyzer
from src.prescription.intelligence.intelligence_aggregator import PrescriptionEvidenceIntelligenceAnalyzer
from src.prescription.intelligence.intelligence_validation import EvidenceIntelligenceValidator

def main():
    print("Initializing Prescription Safety Reasoner...")
    try:
        reasoner = PrescriptionSafetyReasoner()
    except Exception as e:
        print(f"Error loading reasoner: {e}")
        sys.exit(1)
        
    # Multi-drug prescription to trigger clustering, centrality, themes, and alignments
    meds = ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
    print(f"Analyzing prescription: {meds}")
    
    report = reasoner.analyze_prescription(meds)
    print(f"Phase 6 Safety Analysis completed. Found {report.evidence_summary.pairs_with_evidence} positive pairs.")
    
    print("Running Phase 8 Network Structural Analysis...")
    structural_analysis = PrescriptionStructuralAnalyzer.analyze(report)
    
    print("Running Phase 9 Evidence Intelligence Analysis...")
    intelligence_profile = PrescriptionEvidenceIntelligenceAnalyzer.analyze(report, structural_analysis, reasoner)
    
    print("Running Evidence Intelligence Invariants Validation...")
    v_report = EvidenceIntelligenceValidator.validate(intelligence_profile, report)
    
    print("\n--- VALDATION SUMMARY ---")
    print(json.dumps(v_report, indent=2))
    
    print("\n--- CLINICAL NARRATIVE REPORT ---")
    print(intelligence_profile.narrative)
    
    if v_report["validation_passed"]:
        print("\nSUCCESS: Phase 9 evidence intelligence invariants successfully verified!")
        sys.exit(0)
    else:
        print("\nFAILURE: Phase 9 validation errors identified.")
        sys.exit(1)

if __name__ == "__main__":
    main()
