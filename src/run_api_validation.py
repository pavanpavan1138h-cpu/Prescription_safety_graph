"""
src/run_api_validation.py

CLI Runner to execute Phase 7 API Validation Suite.
"""

import json
import logging
from pathlib import Path
from api_validation import APIValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent
    logger.info("Launching Phase 7 API and Reasoning Preservation Validation Suite...")
    validator = APIValidator(project_root)
    report = validator.validate_all()
    logger.info(f"Phase 7 Validation Finished with Status: {report['validation_status']}")

if __name__ == "__main__":
    main()
