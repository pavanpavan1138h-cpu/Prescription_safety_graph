from typing import Tuple, Any
from src.prescription.schemas import PrescriptionSafetyReport

class ComparisonInputResolver:
    @staticmethod
    def resolve(
        analysis_id_a: str,
        analysis_id_b: str,
        service: Any
    ) -> Tuple[PrescriptionSafetyReport, PrescriptionSafetyReport]:
        if not service:
            raise ValueError("PrescriptionService reference must be provided to retrieve analyses.")

        report_a = service._report_objects.get(analysis_id_a)
        report_b = service._report_objects.get(analysis_id_b)

        if not report_a:
            raise ValueError(f"Analysis snapshot A '{analysis_id_a}' not found in the service cache.")
        if not report_b:
            raise ValueError(f"Analysis snapshot B '{analysis_id_b}' not found in the service cache.")

        return report_a, report_b
