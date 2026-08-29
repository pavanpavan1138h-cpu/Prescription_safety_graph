import hashlib
import json
from typing import Any, Dict, List
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.trustworthiness.trustworthiness_schema import ReproducibilityProfile, ReproducibilityLevel

class ReproducibilityEngine:
    @staticmethod
    def generate_canonical_hash(report: Any) -> str:
        """
        Creates a deterministic hash signature of the analytical safety report,
        excluding volatile execution metadata (timestamps, analysis_ids, etc.).
        """
        # Build canonical payload dict
        payload: Dict[str, Any] = {}

        # 1. Normalized resolved drugs (sorted by original input)
        resolved_list = []
        res_summary = getattr(report, "resolution_summary", None)
        if res_summary:
            drugs = getattr(res_summary, "resolved_drugs", []) or []
            for d in drugs:
                orig = getattr(d, "original_input", "")
                internal_id = getattr(d, "resolved_internal_drug_id", None) or getattr(d, "canonical_drug_id", "")
                disp = getattr(d, "display_name", None) or getattr(d, "canonical_name", "")
                status = getattr(d, "resolution_status", "")
                resolved_list.append({
                    "original_input": orig,
                    "resolved_internal_drug_id": internal_id,
                    "display_name": disp,
                    "resolution_status": str(status)
                })
        resolved_list.sort(key=lambda x: x["original_input"])
        payload["resolved_drugs"] = resolved_list

        # 2. Pair results (sorted by pair_id)
        pair_list = []
        pair_results = getattr(report, "pair_results", []) or []
        for pair in pair_results:
            if isinstance(pair, dict):
                pid = pair.get("pair_id") or f"{pair.get('drug_a_id')}:{pair.get('drug_b_id')}"
                st = pair.get("evidence_status", "")
                conf = pair.get("confidence_score", 0.0)
            else:
                pid = getattr(pair, "pair_id", "") or f"{getattr(pair, 'drug_a_id', '')}:{getattr(pair, 'drug_b_id', '')}"
                st = getattr(pair, "evidence_status", "")
                conf = getattr(pair, "confidence_score", 0.0)
            
            pair_list.append({
                "pair_id": pid,
                "evidence_status": st,
                "confidence_score": conf
            })
        pair_list.sort(key=lambda x: x["pair_id"])
        payload["pair_results"] = pair_list

        # 3. Evidence summary counts
        ev_summary = getattr(report, "evidence_summary", None)
        if ev_summary:
            payload["evidence_summary"] = {
                "unique_canonical_drugs": getattr(ev_summary, "unique_canonical_drugs", 0),
                "total_analyzed_pairs": getattr(ev_summary, "total_analyzed_pairs", 0),
                "pairs_with_evidence": getattr(ev_summary, "pairs_with_evidence", 0),
                "prescription_status": str(getattr(ev_summary, "prescription_status", ""))
            }

        # Deterministic serialization to JSON
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def evaluate_reproducibility(cls, baseline_report: Any, repeat_reports: List[Any]) -> ReproducibilityProfile:
        """
        Validates reproducibility across multiple repeat evaluations using canonical signatures.
        """
        baseline_sig = cls.generate_canonical_hash(baseline_report)
        repeat_sigs = [cls.generate_canonical_hash(r) for r in repeat_reports]

        match_count = sum(1 for s in repeat_sigs if s == baseline_sig)
        total_runs = len(repeat_sigs)
        ratio = match_count / max(total_runs, 1)

        mismatched_components = []
        if ratio < 1.0:
            mismatched_components.append("CANONICAL_SIGNATURE_MISMATCH")

        if ratio == 1.0:
            level = ReproducibilityLevel.EXACTLY_REPRODUCIBLE
        elif ratio >= 0.90:
            level = ReproducibilityLevel.HIGHLY_REPRODUCIBLE
        elif ratio >= 0.50:
            level = ReproducibilityLevel.PARTIALLY_REPRODUCIBLE
        else:
            level = ReproducibilityLevel.NON_REPRODUCIBLE

        return ReproducibilityProfile(
            baseline_signature=baseline_sig,
            repeat_run_signatures=repeat_sigs,
            deterministic_match_ratio=ratio,
            classification=level,
            mismatched_components=mismatched_components
        )
