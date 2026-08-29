"""
run_graph_validation.py

Command-line entry point to validate the Phase 3 Prescription Safety Knowledge Graph.
"""

import logging
from pathlib import Path
from src.validation.graph_validation import GraphValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    data_dir = project_root / "data"
    
    logger.info("Launching Phase 3 Graph Validation Suite...")
    validator = GraphValidator(data_dir)
    report = validator.validate_all()
    logger.info(f"Validation Result: {report['validation_status']}")

if __name__ == "__main__":
    main()
