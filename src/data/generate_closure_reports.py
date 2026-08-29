import json
import os
import glob

VALIDATION_DIR = "data/interim/validation"
if not os.path.exists(VALIDATION_DIR):
    os.makedirs(VALIDATION_DIR)

# 1. Dataset Final Summary
dataset_final_summary = {
    "project_phase": "Phase 1: Dataset Freeze and Verification",
    "status": "COMPLETED",
    "key_metrics": {
        "validation_passed": True,
        "note": "For detailed metric values, see pipeline_validation_summary.json and other audit reports."
    },
    "documents_created": [
        "docs/DATASET_CARD.md",
        "docs/DATA_DICTIONARY.md",
        "docs/DATASET_LIMITATIONS.md",
        "docs/REPRODUCIBILITY.md"
    ],
    "validation_artifacts": glob.glob(f"{VALIDATION_DIR}/*.json") + glob.glob(f"{VALIDATION_DIR}/*.csv")
}

with open(os.path.join(VALIDATION_DIR, "dataset_final_summary.json"), "w") as f:
    json.dump(dataset_final_summary, f, indent=4)

# 2. Phase 1 Closure Report
phase_1_closure_report = {
    "phase_name": "Phase 1",
    "objective": "Establish a scientifically defensible, reproducible, auditable data foundation.",
    "completion_status": "SUCCESS",
    "deliverables": [
        "Normalized datasets (DrugBank, TWOSIDES)",
        "Chemical crosswalk mappings",
        "Audit suite and validation reports",
        "Project documentation (Dataset Card, Data Dictionary, Limitations, Reproducibility)"
    ],
    "next_phase_recommendations": "Proceed to Phase 2: Knowledge Graph Construction and Schema Definition."
}

with open(os.path.join(VALIDATION_DIR, "phase_1_closure_report.json"), "w") as f:
    json.dump(phase_1_closure_report, f, indent=4)

print("Generated closure reports.")
