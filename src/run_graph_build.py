"""
run_graph_build.py

Command-line entry point to build the Phase 3 Prescription Safety Knowledge Graph.
"""

import logging
from pathlib import Path
from graph_builder import GraphBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    
    logger.info("Launching Phase 3 Graph Builder...")
    builder = GraphBuilder(data_dir)
    builder.build_all()
    logger.info("Graph Builder finished execution.")

if __name__ == "__main__":
    main()
