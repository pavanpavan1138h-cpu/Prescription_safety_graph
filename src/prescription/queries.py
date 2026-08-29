"""
prescription_queries.py

High-level Query API for Phase 6 Multi-Drug Prescription Safety Analysis.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.reasoning import PrescriptionSafetyReasoner

class PrescriptionQueryAPI:
    def __init__(self, graph_dir: Optional[Path] = None):
        self.reasoner = PrescriptionSafetyReasoner(graph_dir)
        self._reports_cache: Dict[str, PrescriptionSafetyReport] = {}

    def analyze_prescription(self, medications: List[str], prescription_id: Optional[str] = None) -> PrescriptionSafetyReport:
        report = self.reasoner.analyze_prescription(medications, prescription_id)
        self._reports_cache[report.prescription_id] = report
        return report

    def get_report(self, prescription_id: str) -> Optional[PrescriptionSafetyReport]:
        return self._reports_cache.get(prescription_id)
