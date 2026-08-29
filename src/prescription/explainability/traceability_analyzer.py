"""
src/prescription/explainability/traceability_analyzer.py

Calculates explainability quality metrics, coverage scores, average provenance depth,
and surfaces orphaned/untraceable components.
"""

from typing import List, Dict, Any, Optional
from src.prescription.explainability.explainability_schema import (
    TraceabilityProfile,
    ExplanationGraph,
    SourceProvenanceRecord,
    CrossLayerTraceabilityLevel
)

class TraceabilityAnalyzer:
    """
    Evaluates how thoroughly the analytical conclusions can be traced backward
    to underlying computational rules and grounded source assertions.
    """

    def analyze_traceability(
        self,
        explanation_graph: ExplanationGraph,
        provenance_records: List[SourceProvenanceRecord]
    ) -> TraceabilityProfile:
        total_nodes = len(explanation_graph.nodes)
        if total_nodes == 0:
            return TraceabilityProfile(
                total_components_evaluated=0,
                traceable_components_count=0,
                traceability_coverage_score=1.0,
                average_provenance_depth=0.0,
                max_provenance_depth=0,
                orphaned_components_count=0,
                orphaned_component_ids=[],
                cross_layer_traceability=CrossLayerTraceabilityLevel.FULL_CROSS_LAYER_TRACEABILITY
            )

        # Build adjacency mapping (source -> target for outgoing edges)
        adj: Dict[str, List[str]] = {}
        for edge in explanation_graph.edges:
            adj.setdefault(edge.source_node_id, []).append(edge.target_node_id)

        # Calculate depth from each root node to leaves
        depths: List[int] = []
        orphaned_ids: List[str] = []

        available_source_ids = {rec.source_id for rec in provenance_records if rec.is_available}

        for root in explanation_graph.root_node_ids:
            visited = set()
            
            def get_depth(node: str, current_depth: int) -> int:
                if node in visited:
                    return current_depth
                visited.add(node)
                neighbors = adj.get(node, [])
                if not neighbors:
                    return current_depth
                return max(get_depth(nxt, current_depth + 1) for nxt in neighbors)

            d = get_depth(root, 1)
            depths.append(d)

        max_depth = max(depths) if depths else 1
        avg_depth = round(sum(depths) / max(len(depths), 1), 2) if depths else 1.0

        # Traceable components: nodes that have provenance or connect to valid leaf records
        traceable_count = 0
        for node in explanation_graph.nodes:
            if node.node_type.value in ["SOURCE_DATASET", "SOURCE_RECORD"]:
                if node.node_id in available_source_ids or node.source_reference:
                    traceable_count += 1
                else:
                    orphaned_ids.append(node.node_id)
            elif node.node_id in adj and len(adj[node.node_id]) > 0:
                traceable_count += 1
            else:
                if node.node_type.value == "FINAL_INTERPRETATION":
                    traceable_count += 1
                else:
                    orphaned_ids.append(node.node_id)

        coverage_score = round(traceable_count / max(total_nodes, 1), 3)
        coverage_score = max(0.0, min(1.0, coverage_score))

        if coverage_score >= 0.90 and max_depth >= 4:
            cross_level = CrossLayerTraceabilityLevel.FULL_CROSS_LAYER_TRACEABILITY
        elif coverage_score >= 0.65:
            cross_level = CrossLayerTraceabilityLevel.PARTIAL_CROSS_LAYER_TRACEABILITY
        else:
            cross_level = CrossLayerTraceabilityLevel.LIMITED_TRACEABILITY

        return TraceabilityProfile(
            total_components_evaluated=total_nodes,
            traceable_components_count=traceable_count,
            traceability_coverage_score=coverage_score,
            average_provenance_depth=avg_depth,
            max_provenance_depth=max_depth,
            orphaned_components_count=len(orphaned_ids),
            orphaned_component_ids=orphaned_ids,
            cross_layer_traceability=cross_level
        )
