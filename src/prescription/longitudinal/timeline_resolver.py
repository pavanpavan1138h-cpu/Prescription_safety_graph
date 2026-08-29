from typing import List, Any
from datetime import datetime
from src.prescription.longitudinal.longitudinal_schema import (
    PrescriptionSnapshotReference,
    SnapshotPositionType
)

class TimelineResolver:
    @staticmethod
    def resolve_timeline(
        snapshots: List[Any]
    ) -> List[PrescriptionSnapshotReference]:
        """
        Orders snapshots deterministically using timestamps (ISO-8601 strings) if available,
        falling back to index-based sequence ordering otherwise.
        """
        # Step 1: Parse and sort snapshots
        decorated = []
        for idx, snap in enumerate(snapshots):
            meta = getattr(snap, "metadata", None)
            analysis_id = getattr(meta, "analysis_id", None) or getattr(snap, "analysis_id", f"MOCK_{idx}")
            prescription_id = getattr(meta, "prescription_id", None) or getattr(snap, "prescription_id", f"PRES_{idx}")
            
            ts_str = ""
            if meta and hasattr(meta, "generated_at"):
                ts_str = getattr(meta, "generated_at", "")
            elif hasattr(snap, "generated_at"):
                ts_str = getattr(snap, "generated_at", "")
                
            # Parse list of resolved drugs as medications list
            resolved_drugs = []
            if hasattr(snap, "resolution_summary") and snap.resolution_summary:
                for rd in snap.resolution_summary.resolved_drugs:
                    resolved_drugs.append(getattr(rd, "original_input", ""))
            
            decorated.append({
                "snapshot": snap,
                "analysis_id": analysis_id,
                "prescription_id": prescription_id,
                "timestamp": ts_str,
                "original_index": idx,
                "medications": resolved_drugs
            })

        # Deterministic sorting function
        def get_sort_key(item):
            ts = item["timestamp"]
            if ts:
                try:
                    return (datetime.fromisoformat(ts.replace("Z", "+00:00")), item["original_index"])
                except Exception:
                    pass
            return (datetime.min, item["original_index"])

        sorted_items = sorted(decorated, key=get_sort_key)
        total = len(sorted_items)

        references = []
        for seq_idx, item in enumerate(sorted_items):
            if seq_idx == 0:
                pos = SnapshotPositionType.BASELINE
            elif seq_idx == total - 1:
                pos = SnapshotPositionType.LATEST
            else:
                pos = SnapshotPositionType.INTERMEDIATE

            ref = PrescriptionSnapshotReference(
                analysis_id=item["analysis_id"],
                prescription_id=item["prescription_id"],
                snapshot_timestamp=item["timestamp"],
                sequence_index=seq_idx,
                position_type=pos,
                medications=item["medications"]
            )
            # Store the sorted snapshot reference directly in object for subsequent stages
            ref._snapshot = item["snapshot"]
            references.append(ref)

        return references
