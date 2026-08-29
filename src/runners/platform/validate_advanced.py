"""
src/run_advanced_intelligence_validation.py

Runner script for Phase 8 Advanced Clinical Intelligence validation suite.
Generates data/interim/validation/advanced_intelligence_validation_report.json.
"""

import json
import logging
from pathlib import Path
from src.validation.advanced_intelligence_validation import AdvancedIntelligenceValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run():
    logger.info("================================================================================")
    logger.info("STARTING PHASE 8 ADVANCED CLINICAL INTELLIGENCE VALIDATION SUITE")
    logger.info("================================================================================")

    validator = AdvancedIntelligenceValidator()
    results = validator.run_all_validations()

    # Save validation report
    output_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "interim" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_file = output_dir / "advanced_intelligence_validation_report.json"
    
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info("================================================================================")
    logger.info(f"VALIDATION FINISHED: {results['passed_checks']}/{results['total_checks']} checks passed.")
    logger.info(f"Report saved to: {report_file}")
    logger.info("================================================================================")

    if results["failed_checks"] > 0:
        raise RuntimeError(f"{results['failed_checks']} validation checks failed.")

if __name__ == "__main__":
    run()
