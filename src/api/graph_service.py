"""
src/api/graph_service.py

Graph service layer exposing visualization endpoints.
Coordinates SubgraphBuilder and PrescriptionService.
"""

import logging
from typing import List, Optional
from api.graph_schemas import SubgraphResponse
from api.graph_subgraph_builder import SubgraphBuilder
from api.service import PrescriptionService

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self, prescription_service: PrescriptionService):
        self.prescription_service = prescription_service
        self.builder = SubgraphBuilder(prescription_service.reasoner)

    def get_prescription_overview_graph(
        self,
        analysis_id: str,
        medications: Optional[List[str]] = None,
        side_effect_limit: int = 5
    ) -> SubgraphResponse:
        report = self.prescription_service._report_objects.get(analysis_id)
        if not report and not medications:
            raise ValueError(f"Analysis ID '{analysis_id}' not found.")
        
        meds = medications or report.resolution_summary.original_inputs
        return self.builder.build_prescription_overview_graph(
            analysis_id=analysis_id,
            medications=meds,
            side_effect_limit=side_effect_limit
        )

    def get_pair_evidence_graph(
        self,
        analysis_id: str,
        pair_id: str,
        side_effect_limit: int = 25
    ) -> SubgraphResponse:
        return self.builder.build_pair_evidence_graph(
            analysis_id=analysis_id,
            pair_id=pair_id,
            side_effect_limit=side_effect_limit
        )

    def get_provenance_graph(
        self,
        analysis_id: str,
        pair_id: str
    ) -> SubgraphResponse:
        return self.builder.build_provenance_graph(
            analysis_id=analysis_id,
            pair_id=pair_id
        )

# Singleton GraphService instance
graph_service_instance: Optional[GraphService] = None

def get_graph_service() -> GraphService:
    global graph_service_instance
    if graph_service_instance is None:
        from api.service import get_prescription_service
        p_service = get_prescription_service()
        graph_service_instance = GraphService(p_service)
    return graph_service_instance
