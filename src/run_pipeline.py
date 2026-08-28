import sys
from pathlib import Path

# Add project root to path to ensure package structure works
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.pipeline import run_data_pipeline

if __name__ == "__main__":
    try:
        summary, report = run_data_pipeline(project_root)
        print("\nPipeline execution summary successfully generated!")
    except Exception as e:
        print(f"\nPipeline run failed with error: {e}", file=sys.stderr)
        sys.exit(1)
