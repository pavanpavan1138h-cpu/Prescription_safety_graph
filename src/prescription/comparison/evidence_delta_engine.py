from typing import List, Dict, Any, Set
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.comparison.comparison_schema import (
    EvidenceDelta,
    PairComparison,
    EvidenceChangeType
)

class EvidenceDeltaEngine:
    @staticmethod
    def compare(
        report_a: PrescriptionSafetyReport,
        report_b: PrescriptionSafetyReport,
        shared_drugs: Set[str]
    ) -> EvidenceDelta:
        pairs_a = {p["canonical_pair_key"]: p for p in report_a.pair_results}
        pairs_b = {p["canonical_pair_key"]: p for p in report_b.pair_results}

        all_keys = set(pairs_a.keys()).union(pairs_b.keys())
        pair_comparisons: List[PairComparison] = []

        added_count = 0
        removed_count = 0
        reclassified_count = 0
        preserved_count = 0

        for key in sorted(all_keys):
            in_a = key in pairs_a
            in_b = key in pairs_b

            if in_a and in_b:
                pa = pairs_a[key]
                pb = pairs_b[key]
                status_a = pa.get("evidence_status", "NO_DIRECT_GRAPH_EVIDENCE")
                status_b = pb.get("evidence_status", "NO_DIRECT_GRAPH_EVIDENCE")

                if status_a != status_b:
                    change = EvidenceChangeType.EVIDENCE_RECLASSIFIED
                    reclassified_count += 1
                else:
                    change = EvidenceChangeType.PRESERVED_EVIDENCE
                    preserved_count += 1

                pair_comparisons.append(PairComparison(
                    canonical_pair_key=key,
                    drug_a_id=pa["drug_a_id"],
                    drug_b_id=pa["drug_b_id"],
                    drug_a_name=pa["drug_a_name"],
                    drug_b_name=pa["drug_b_name"],
                    evidence_status_a=status_a,
                    evidence_status_b=status_b,
                    change_type=change
                ))

            elif in_a:
                pa = pairs_a[key]
                status_a = pa.get("evidence_status", "NO_DIRECT_GRAPH_EVIDENCE")
                removed_count += 1
                pair_comparisons.append(PairComparison(
                    canonical_pair_key=key,
                    drug_a_id=pa["drug_a_id"],
                    drug_b_id=pa["drug_b_id"],
                    drug_a_name=pa["drug_a_name"],
                    drug_b_name=pa["drug_b_name"],
                    evidence_status_a=status_a,
                    evidence_status_b="NO_DIRECT_GRAPH_EVIDENCE",
                    change_type=EvidenceChangeType.REMOVED_EVIDENCE
                ))

            else:
                pb = pairs_b[key]
                status_b = pb.get("evidence_status", "NO_DIRECT_GRAPH_EVIDENCE")
                added_count += 1
                pair_comparisons.append(PairComparison(
                    canonical_pair_key=key,
                    drug_a_id=pb["drug_a_id"],
                    drug_b_id=pb["drug_b_id"],
                    drug_a_name=pb["drug_a_name"],
                    drug_b_name=pb["drug_b_name"],
                    evidence_status_a="NO_DIRECT_GRAPH_EVIDENCE",
                    evidence_status_b=status_b,
                    change_type=EvidenceChangeType.NEW_EVIDENCE
                ))

        return EvidenceDelta(
            pair_comparisons=pair_comparisons,
            added_pairs_count=added_count,
            removed_pairs_count=removed_count,
            reclassified_pairs_count=reclassified_count,
            preserved_pairs_count=preserved_count
        )
