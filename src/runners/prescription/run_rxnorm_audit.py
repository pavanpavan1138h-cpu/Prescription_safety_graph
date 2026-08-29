import logging
from src.data.rxnorm_audit import run_audit_suite

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    run_audit_suite()
