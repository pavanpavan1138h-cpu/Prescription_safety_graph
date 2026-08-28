"""
safety_validation.py

Comprehensive Validation Suite for Phase 5 Prescription Safety Graph Reasoning.
Verifies referential integrity, rule classification consistency, confidence bounds,
and provenance completeness across batch inferences.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set
import pandas as pd

from reasoning_schema import EvidenceStatus, ConfidenceLevel

logger = logging.getLogger(__name__)

class SafetyReasonerValidator:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.reasoning_dir = data_dir / "interim" / "reasoning"
        self.graph_dir = data_dir / "interim" / "graph"
        self.val_dir = data_dir / "interim" / "validation"
        self.val_dir.mkdir(parents=True, exist_ok=True)

    def validate_all(self) -> Dict:
        logger.info("Executing comprehensive Phase 5 Reasoning Validation Suite...")

        report = {
            "validation_status": "PENDING",
            "checks": {},
            "metrics": {},
            "issues": [],
            "anomalies": []
        }

        # 1. File existence
        req_files = [
            "safety_inference_results.csv",
            "safety_inference_evidence.csv",
            "safety_inference_explanations.json",
            "safety_reasoning_summary.json"
        ]
        missing = [f for f in req_files if not (self.reasoning_dir / f).exists()]
        if missing:
            report["validation_status"] = "FAILED"
            report["issues"].append(f"Missing required reasoning output files: {missing}")
            return report

        results_df = pd.read_csv(self.reasoning_dir / "safety_inference_results.csv")
        evidence_df = pd.read_csv(self.reasoning_dir / "safety_inference_evidence.csv")
        with open(self.reasoning_dir / "safety_inference_explanations.json") as f:
            explanations = json.load(f)

        # 2. Referential Integrity Check
        logger.info("Validating referential integrity against Phase 4 graph...")
        nodes_df = pd.read_csv(self.graph_dir / "graph_nodes.csv")
        valid_drug_ids = set(nodes_df[nodes_df["node_type"] == "Drug"]["node_id"])

        invalid_drugs = []
        for _, row in results_df.iterrows():
            if row["drug_a_id"] not in valid_drug_ids or row["drug_b_id"] not in valid_drug_ids:
                invalid_drugs.append(row["inference_id"])

        report["checks"]["drug_id_referential_integrity"] = (len(invalid_drugs) == 0)
        if invalid_drugs:
            report["issues"].append(f"Found {len(invalid_drugs)} inferences referencing invalid drug IDs.")

        # 3. Rule Classification Consistency
        logger.info("Validating rule classification consistency...")
        rule_violations = 0
        for _, row in results_df.iterrows():
            st = row["evidence_status"]
            has_ddi = bool(row["ddi_evidence_present"])
            has_events = bool(row["combination_event_present"])

            if st == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE.value and not (has_ddi and has_events):
                rule_violations += 1
            elif st == EvidenceStatus.DDI_EVIDENCE_ONLY.value and not (has_ddi and not has_events):
                rule_violations += 1
            elif st == EvidenceStatus.COMBINATION_EVENT_EVIDENCE_ONLY.value and not (not has_ddi and has_events):
                rule_violations += 1
            elif st == EvidenceStatus.NO_DIRECT_GRAPH_EVIDENCE.value and (has_ddi or has_events):
                rule_violations += 1

        report["checks"]["rule_classification_consistency"] = (rule_violations == 0)
        if rule_violations > 0:
            report["issues"].append(f"Found {rule_violations} rule classification inconsistencies.")

        # 4. Confidence Score Bounds & Categorization
        logger.info("Validating confidence score bounds...")
        invalid_scores = results_df[(results_df["confidence_score"] < 0.0) | (results_df["confidence_score"] > 1.0)]
        report["checks"]["confidence_score_bounds"] = (len(invalid_scores) == 0)
        if len(invalid_scores) > 0:
            report["issues"].append(f"Found {len(invalid_scores)} confidence scores outside [0.0, 1.0].")

        # 5. Provenance Completeness
        logger.info("Validating provenance completeness...")
        positive_inferences = set(results_df[results_df["evidence_status"] != EvidenceStatus.NO_DIRECT_GRAPH_EVIDENCE.value]["inference_id"])
        evidence_inferences = set(evidence_df["inference_id"])
        missing_provenance = positive_inferences - evidence_inferences

        report["checks"]["provenance_completeness"] = (len(missing_provenance) == 0)
        if missing_provenance:
            report["issues"].append(f"Found {len(missing_provenance)} positive inferences with zero supporting evidence records.")

        # Anomalies output
        pd.DataFrame(report["anomalies"]).to_csv(self.val_dir / "safety_reasoning_anomalies.csv", index=False)

        # Status
        all_passed = all(report["checks"].values())
        report["validation_status"] = "PASSED" if all_passed else "FAILED"

        # Metrics
        report["metrics"] = {
            "total_inferences_evaluated": len(results_df),
            "evidence_status_distribution": results_df["evidence_status"].value_counts().to_dict(),
            "confidence_level_distribution": results_df["confidence_level"].value_counts().to_dict(),
            "total_evidence_records": len(evidence_df),
            "total_explanations_generated": len(explanations)
        }

        with open(self.val_dir / "safety_reasoning_validation_report.json", "w") as f:
            json.dump(report, f, indent=4)

        logger.info(f"Phase 5 Reasoning Validation completed with status: {report['validation_status']}.")
        return report
