"""
src/run_advanced_intelligence_demo.py

End-to-End demonstration runner for Phase 8 Advanced Clinical Intelligence.
Demonstrates:
1. Single-drug boundary behavior
2. Convergent evidence pair
3. Multi-drug prescription with central signal participant & event convergence
4. Unresolved medication and structured uncertainty reporting
5. Scientific guardrails and missing context requirements
"""

import json
import logging
from pathlib import Path
from fastapi.testclient import TestClient
from api.main import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run():
    client = TestClient(app)
    logger.info("================================================================================")
    logger.info("PRESCRIPTION SAFETY PLATFORM — PHASE 8 ADVANCED CLINICAL INTELLIGENCE DEMO")
    logger.info("================================================================================")

    # 1. Single-Drug Boundary Case
    logger.info("\n--- DEMO 1: Single-Drug Boundary Evaluation (fluconazole) ---")
    r1 = client.post("/api/v1/prescriptions/analyze-advanced", json={"medications": ["fluconazole"]}).json()
    logger.info(f"Complexity: {r1['complexity_profile']['complexity_category']} (Score: {r1['complexity_profile']['complexity_score']})")
    logger.info(f"Summary: {r1['complexity_profile']['explanation']}")

    # 2. Two-Drug Convergent Pair
    logger.info("\n--- DEMO 2: Convergent Evidence Pair (cyclosporine + fluconazole) ---")
    r2 = client.post("/api/v1/prescriptions/analyze-advanced", json={"medications": ["cyclosporine", "fluconazole"]}).json()
    logger.info(f"Review Priority: {r2['review_priorities'][0]['review_priority']} (Score: {r2['review_priorities'][0]['review_score']})")
    logger.info(f"Deterministic Reasons: {r2['review_priorities'][0]['deterministic_reasons']}")
    logger.info(f"Detected Patterns: {[p['title'] for p in r2['evidence_patterns']]}")

    # 3. Multi-Drug Polypharmacy & Cross-Pair Event Convergence
    logger.info("\n--- DEMO 3: Polypharmacy with Central Signal Participant (cyclosporine + fluconazole + phentermine) ---")
    r3 = client.post("/api/v1/prescriptions/analyze-advanced", json={"medications": ["cyclosporine", "fluconazole", "phentermine"]}).json()
    logger.info(f"Complexity: {r3['complexity_profile']['complexity_category']}")
    logger.info("Drug Participation Profiles:")
    for dp in r3['drug_participation_profiles']:
        logger.info(f"  • {dp['display_name']}: {dp['participation_category']} ({dp['positive_evidence_pairs']} positive pairs, concentration {dp['relative_evidence_concentration']})")
    
    logger.info(f"Cross-Pair Event Convergence Items: {len(r3['event_convergence_items'])} side effects analyzed.")
    for ec in r3['event_convergence_items'][:4]:
        logger.info(f"  • {ec['side_effect_name']}: {ec['convergence_category']} ({ec['participating_pairs_count']} pairs across {len(ec['participating_drug_names'])} drugs)")

    # 4. Unresolved Input Uncertainty
    logger.info("\n--- DEMO 4: Unresolved Inputs & Uncertainty Profile ---")
    r4 = client.post("/api/v1/prescriptions/analyze-advanced", json={"medications": ["fluconazole", "InvestigationalDrugX"]}).json()
    logger.info(f"Uncertainty Level: {r4['uncertainty_profile']['uncertainty_level']}")
    logger.info(f"Uncertainty Categories: {r4['uncertainty_profile']['uncertainty_categories']}")
    logger.info(f"Unresolved Inputs: {r4['uncertainty_profile']['unresolved_input_names']}")

    # 5. Context Requirements & Scientific Limitations
    logger.info("\n--- DEMO 5: Context Requirements & Scientific Guardrails ---")
    logger.info("Required Clinical Context (Not in Knowledge Graph):")
    for req in r3['clinical_context_requirements']:
        logger.info(f"  • {req['context_category']}: {req['why_it_matters']}")

    logger.info("\nScientific Limitations & Guardrails:")
    for g in r3['advanced_explanation']['scientific_guardrails']:
        logger.info(f"  [GUARDRAIL] {g}")

    # Export demo results to data/interim/advanced_intelligence/
    out_dir = Path(__file__).resolve().parent.parent / "data" / "interim" / "advanced_intelligence"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "advanced_prescription_reports.json", "w") as f:
        json.dump({"demo_polypharmacy_report": r3}, f, indent=2)

    logger.info("\n================================================================================")
    logger.info(f"PHASE 8 ADVANCED CLINICAL INTELLIGENCE DEMO COMPLETED SUCCESSFULLY!")
    logger.info(f"Output saved to: {out_dir / 'advanced_prescription_reports.json'}")
    logger.info("================================================================================")

if __name__ == "__main__":
    run()
