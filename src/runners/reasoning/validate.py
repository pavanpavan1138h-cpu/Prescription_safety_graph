"""
run_safety_validation.py

CLI Runner to execute the Phase 5 Safety Reasoning Validation Suite.
"""

import json
import logging
from pathlib import Path
from src.validation.safety_validation import SafetyReasonerValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    data_dir = project_root / "data"

    logger.info("Launching Phase 5 Safety Reasoning Validation Suite...")
    validator = SafetyReasonerValidator(data_dir)
    report = validator.validate_all()
    logger.info(f"Validation Finished with Status: {report['validation_status']}")

if __name__ == "__main__":
    main()
