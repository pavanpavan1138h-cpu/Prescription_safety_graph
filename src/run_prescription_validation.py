"""
run_prescription_validation.py

CLI Runner to execute the Phase 6 Prescription Safety Validation Suite.
"""

import logging
from pathlib import Path
from prescription_validation import PrescriptionSafetyValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"

    logger.info("Launching Phase 6 Prescription Safety Validation Suite...")
    validator = PrescriptionSafetyValidator(data_dir)
    report = validator.validate_all()
    logger.info(f"Phase 6 Validation Finished with Status: {report['validation_status']}")

if __name__ == "__main__":
    main()
