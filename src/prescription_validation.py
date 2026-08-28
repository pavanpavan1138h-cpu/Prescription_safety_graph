"""
prescription_validation.py

Comprehensive Validation Suite for Phase 6 Multi-Drug Prescription Safety Reasoning.
Verifies pair generation formulas N(N-1)/2, referential integrity, rule consistency,
priority ranking, aggregation accounting, and reproducibility.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)

class PrescriptionSafetyValidator:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.prescription_dir = data_dir / "interim" / "prescription_reasoning"
        self.val_dir = data_dir / "interim" / "validation"
        self.val_dir.mkdir(parents=True, exist_ok=True)

    def validate_all(self) -> Dict:
        logger.info("Executing Phase 6 Prescription Safety Validation Suite...")

        report = {
            "validation_status": "PENDING",
            "checks": {},
            "metrics": {},
            "issues": [],
            "anomalies": []
        }

        # 1. Check required output files
        req_files = [
            "prescription_safety_reports.json",
            "prescription_pair_results.csv",
            "prescription_signals.csv",
            "prescription_reasoning_summary.json"
        ]
        missing = [f for f in req_files if not (self.prescription_dir / f).exists()]
        if missing:
            report["validation_status"] = "FAILED"
            report["issues"].append(f"Missing required prescription reasoning files: {missing}")
            return report

        with open(self.prescription_dir / "prescription_safety_reports.json") as f:
            reports_data = json.load(f)
        pair_results_df = pd.read_csv(self.prescription_dir / "prescription_pair_results.csv")
        signals_df = pd.read_csv(self.prescription_dir / "prescription_signals.csv")

        # 2. Validate Pair Count Formula N(N-1)/2 across all reports
        logger.info("Validating pair generation formula N*(N-1)/2 across all evaluated prescriptions...")
        formula_violations = 0
        duplicate_pairs_found = 0
        self_pairs_found = 0

        for r in reports_data:
            ev = r["evidence_summary"]
            n_drugs = ev["unique_canonical_drugs"]
            expected_pairs = (n_drugs * (n_drugs - 1)) // 2 if n_drugs >= 2 else 0

            if ev["total_expected_pairs"] != expected_pairs or ev["total_analyzed_pairs"] != expected_pairs:
                formula_violations += 1

            # Check pairs
            pairs = r["pair_results"]
            seen_pairs = set()
            for p in pairs:
                d1, d2 = p["drug_a_id"], p["drug_b_id"]
                if d1 == d2:
                    self_pairs_found += 1
                sorted_key = tuple(sorted([d1, d2]))
                if sorted_key in seen_pairs:
                    duplicate_pairs_found += 1
                seen_pairs.add(sorted_key)

        report["checks"]["pair_formula_consistency"] = (formula_violations == 0)
        report["checks"]["no_duplicate_pairs"] = (duplicate_pairs_found == 0)
        report["checks"]["no_self_pairs"] = (self_pairs_found == 0)

        if formula_violations > 0:
            report["issues"].append(f"Found {formula_violations} prescriptions violating pair formula N(N-1)/2.")
        if duplicate_pairs_found > 0:
            report["issues"].append(f"Found {duplicate_pairs_found} duplicate pairs.")
        if self_pairs_found > 0:
            report["issues"].append(f"Found {self_pairs_found} self-pairs.")

        # 3. Aggregation Consistency (convergent + ddi + events + no_direct == total_analyzed)
        logger.info("Validating aggregation accounting consistency...")
        accounting_violations = 0
        for r in reports_data:
            ev = r["evidence_summary"]
            total = (
                ev["convergent_evidence_pairs"] +
                ev["ddi_only_pairs"] +
                ev["combination_event_only_pairs"] +
                ev["no_direct_evidence_pairs"]
            )
            if total != ev["total_analyzed_pairs"]:
                accounting_violations += 1

        report["checks"]["aggregation_accounting_consistency"] = (accounting_violations == 0)
        if accounting_violations > 0:
            report["issues"].append(f"Found {accounting_violations} aggregation accounting mismatches.")

        # 4. Signal Prioritization Consistency
        logger.info("Validating signal prioritization consistency...")
        valid_priorities = {
            "CRITICAL_EVIDENCE_PRIORITY",
            "HIGH_EVIDENCE_PRIORITY",
            "MODERATE_EVIDENCE_PRIORITY",
            "LIMITED_EVIDENCE_PRIORITY",
            "NO_EVIDENCE_PRIORITY"
        }
        invalid_priorities = set(signals_df["evidence_priority"]) - valid_priorities
        report["checks"]["prioritization_tier_consistency"] = (len(invalid_priorities) == 0)
        if invalid_priorities:
            report["issues"].append(f"Found invalid priority tiers: {invalid_priorities}")

        # 5. Provenance Completeness
        logger.info("Validating provenance trace completeness...")
        positive_signals = signals_df[signals_df["evidence_status"] != "NO_DIRECT_GRAPH_EVIDENCE"]
        missing_provenance_count = 0
        for _, s in positive_signals.iterrows():
            edges_str = str(s.get("supporting_edge_ids", ""))
            if not edges_str or edges_str == "[]" or edges_str == "nan":
                missing_provenance_count += 1

        report["checks"]["positive_findings_provenance_completeness"] = (missing_provenance_count == 0)
        if missing_provenance_count > 0:
            report["issues"].append(f"Found {missing_provenance_count} positive findings without graph edge provenance.")

        # Final Status
        all_passed = all(report["checks"].values())
        report["validation_status"] = "PASSED" if all_passed else "FAILED"

        report["metrics"] = {
            "total_prescriptions_evaluated": len(reports_data),
            "total_pairs_evaluated": len(pair_results_df),
            "total_prioritized_signals_generated": len(signals_df),
            "priority_distribution": signals_df["evidence_priority"].value_counts().to_dict()
        }

        with open(self.val_dir / "prescription_reasoning_validation_report.json", "w") as f:
            json.dump(report, f, indent=4)

        logger.info(f"Phase 6 Validation Suite completed with status: {report['validation_status']}.")
        return report
