import sys
from pathlib import Path

# Add project root to system path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.audit import execute_audit

if __name__ == "__main__":
    try:
        execute_audit(project_root)
        print("\nPipeline audit and validation suite completed successfully!")
    except Exception as e:
        print(f"\nAudit execution failed with error: {e}", file=sys.stderr)
        sys.exit(1)
