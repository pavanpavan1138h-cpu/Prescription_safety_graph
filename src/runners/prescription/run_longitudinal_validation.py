import logging
import json
from src.api.service import PrescriptionService
from src.prescription.longitudinal.longitudinal_validation import LongitudinalValidation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_validation():
    logger.info("Initializing service...")
    service = PrescriptionService()

    # Create 3 sequential prescription snapshots representing history
    snapshots_sets = [
        ["cyclosporine", "fluconazole"],
        ["cyclosporine", "fluconazole", "phentermine"],
        ["cyclosporine", "phentermine"]
    ]

    analysis_ids = []
    for idx, meds in enumerate(snapshots_sets):
        logger.info(f"Generating Snapshot #{idx + 1} for: {meds}")
        res = service.analyze_prescription_advanced(meds)
        aid = res.prescription_report.metadata.analysis_id
        analysis_ids.append(aid)

    logger.info(f"Assembling Longitudinal Timeline for: {analysis_ids}")
    long_id = service.create_longitudinal_profile(analysis_ids)
    assert long_id is not None
    logger.info(f"Longitudinal analysis created with ID: {long_id}")

    # Fetch longitudinal profile
    profile = service._longitudinal_profiles.get(long_id)
    assert profile is not None

    # Run validation invariants
    logger.info("Running Phase 13 invariant checks...")
    val_res = LongitudinalValidation.validate_invariants(profile)
    print(json.dumps(val_res, indent=2))

    assert val_res["validation_passed"] is True
    print("\nSUCCESS: Phase 13 Longitudinal evolution engine validated successfully!")

if __name__ == "__main__":
    run_validation()
