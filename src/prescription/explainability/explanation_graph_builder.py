"""
src/prescription/explainability/explanation_graph_builder.py

Builds the machine-readable, Cytoscape-compatible explanation graph modeling
the reverse derivation chain from final conclusions down to source datasets.
"""

from typing import List, Dict, Any, Optional
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.explainability.explainability_schema import (
    ExplanationGraph,
    ExplanationNode,
    ExplanationEdge,
    ExplanationNodeType,
    ExplanationRelationType,
    SourceProvenanceRecord
)

class ExplanationGraphBuilder:
    """
    Constructs the complete hierarchical explanation graph linking all analytical
    levels from Final Interpretation to underlying Evidence Assertions & Source Datasets.
    """

    def build_graph(
        self,
        analysis_result: PrescriptionSafetyReport,
        provenance_records: List[SourceProvenanceRecord],
        structural_analysis: Optional[Any] = None,
        evidence_intelligence: Optional[Any] = None,
        contextual_stability: Optional[Any] = None
    ) -> ExplanationGraph:
        nodes: List[ExplanationNode] = []
        edges: List[ExplanationEdge] = []
        seen_node_ids = set()

        def add_node(n: ExplanationNode):
            if n.node_id not in seen_node_ids:
                seen_node_ids.add(n.node_id)
                nodes.append(n)

        # 1. Root Node: Final Interpretation
        root_id = "NODE_FINAL_INTERPRETATION"
        root_status = "EVALUATED"
        if hasattr(analysis_result, "evidence_summary") and analysis_result.evidence_summary:
            ev_stat = getattr(analysis_result.evidence_summary, "prescription_status", None)
            root_status = ev_stat.value if hasattr(ev_stat, "value") else str(ev_stat or "EVALUATED")
        elif hasattr(analysis_result, "prescription_summary") and analysis_result.prescription_summary:
            root_status = getattr(analysis_result.prescription_summary, "evidence_status", "EVALUATED")
        add_node(ExplanationNode(
            node_id=root_id,
            node_type=ExplanationNodeType.FINAL_INTERPRETATION,
            label=f"Prescription Assessment: {root_status}",
            description=f"Aggregate multi-drug safety interpretation ({root_status})",
            phase_origin="Phase 6 / Master Engine",
            metadata={"status": root_status}
        ))

        # 2. Layer 4: Contextual Stability Node (Phase 10)
        if contextual_stability:
            cs_id = "NODE_CONTEXTUAL_STABILITY"
            stab_level = getattr(contextual_stability, "interpretation_stability", "STABLE")
            add_node(ExplanationNode(
                node_id=cs_id,
                node_type=ExplanationNodeType.CONTEXTUAL_STABILITY_RESULT,
                label=f"Context Stability: {stab_level}",
                description="Evaluation of interpretation resilience across contextual scenarios",
                phase_origin="Phase 10",
                metadata={"stability_level": stab_level}
            ))
            edges.append(ExplanationEdge(
                edge_id=f"EDGE_{root_id}_{cs_id}",
                source_node_id=root_id,
                target_node_id=cs_id,
                relationship_type=ExplanationRelationType.VALIDATED_BY,
                contribution_weight=0.85,
                description="Final interpretation validity tested via perturbation stability"
            ))

        # 3. Layer 3: Evidence Intelligence Themes (Phase 9)
        if evidence_intelligence and hasattr(evidence_intelligence, "evidence_themes"):
            for theme in evidence_intelligence.evidence_themes:
                t_id = f"NODE_THEME_{theme.theme_name}"
                add_node(ExplanationNode(
                    node_id=t_id,
                    node_type=ExplanationNodeType.SIGNAL_THEME,
                    label=f"Theme: {theme.theme_name}",
                    description=f"Cross-pair reinforced safety theme ({theme.reinforcement_level})",
                    phase_origin="Phase 9",
                    metadata={"reinforcement_score": theme.reinforcement_score}
                ))
                edges.append(ExplanationEdge(
                    edge_id=f"EDGE_{root_id}_{t_id}",
                    source_node_id=root_id,
                    target_node_id=t_id,
                    relationship_type=ExplanationRelationType.SUPPORTED_BY,
                    contribution_weight=min(1.0, theme.reinforcement_score / 4.0),
                    description="Aggregate evidence synthesized into cross-pair signal theme"
                ))

        # 4. Layer 2: Structural Network Result (Phase 8)
        if structural_analysis:
            struct_id = "NODE_STRUCTURAL_TOPOLOGY"
            top_type = "EVALUATED_NETWORK"
            if hasattr(structural_analysis, "topology") and structural_analysis.topology:
                top_type = getattr(structural_analysis.topology, "primary_topology", None) or getattr(structural_analysis.topology, "topology_classification", "EVALUATED_NETWORK")
            elif hasattr(structural_analysis, "structural_interpretation") and structural_analysis.structural_interpretation:
                top_type = getattr(structural_analysis.structural_interpretation, "topology_classification", "EVALUATED_NETWORK")

            add_node(ExplanationNode(
                node_id=struct_id,
                node_type=ExplanationNodeType.STRUCTURAL_RESULT,
                label=f"Topology: {top_type}",
                description=f"Evidence network topology classification ({top_type})",
                phase_origin="Phase 8",
                metadata={"topology": top_type}
            ))
            edges.append(ExplanationEdge(
                edge_id=f"EDGE_{root_id}_{struct_id}",
                source_node_id=root_id,
                target_node_id=struct_id,
                relationship_type=ExplanationRelationType.COMPUTED_FROM,
                contribution_weight=0.75,
                description="Prescription graph structured into topological clusters"
            ))

        # 5. Layer 1: Pair Results & Drug Entities (Phase 5/6)
        for pair in analysis_result.pair_results:
            pair_id = pair.get("pair_id") if isinstance(pair, dict) else getattr(pair, "pair_id", "")
            drug_a_id = pair.get("drug_a_id") if isinstance(pair, dict) else getattr(pair, "drug_a_id", "")
            drug_b_id = pair.get("drug_b_id") if isinstance(pair, dict) else getattr(pair, "drug_b_id", "")
            drug_a_name = pair.get("drug_a_name") if isinstance(pair, dict) else getattr(pair, "drug_a_name", "")
            drug_b_name = pair.get("drug_b_name") if isinstance(pair, dict) else getattr(pair, "drug_b_name", "")
            st = pair.get("evidence_status") if isinstance(pair, dict) else getattr(pair, "evidence_status", "")
            conf = pair.get("confidence_score", 0.0) if isinstance(pair, dict) else getattr(pair, "confidence_score", 0.0)

            p_node_id = f"NODE_PAIR_{pair_id}"
            add_node(ExplanationNode(
                node_id=p_node_id,
                node_type=ExplanationNodeType.PAIR_REASONING_RESULT,
                label=f"{drug_a_name} + {drug_b_name}",
                description=f"Pairwise reasoning result: {st}",
                phase_origin="Phase 5 / Phase 6",
                metadata={"status": st, "confidence": conf}
            ))

            # Connect theme to pair if theme exists
            if evidence_intelligence and hasattr(evidence_intelligence, "evidence_themes"):
                for theme in evidence_intelligence.evidence_themes:
                    if pair_id in theme.supporting_pairs or f"{drug_a_id}:{drug_b_id}" in theme.supporting_pairs:
                        t_id = f"NODE_THEME_{theme.theme_name}"
                        edges.append(ExplanationEdge(
                            edge_id=f"EDGE_{t_id}_{p_node_id}",
                            source_node_id=t_id,
                            target_node_id=p_node_id,
                            relationship_type=ExplanationRelationType.DERIVED_FROM,
                            contribution_weight=0.9,
                            description=f"Theme {theme.theme_name} aggregated from pairwise interaction evidence"
                        ))
            else:
                # Direct link from root if no themes
                edges.append(ExplanationEdge(
                    edge_id=f"EDGE_{root_id}_{p_node_id}",
                    source_node_id=root_id,
                    target_node_id=p_node_id,
                    relationship_type=ExplanationRelationType.DERIVED_FROM,
                    contribution_weight=0.8,
                    description="Aggregate interpretation directly derived from pair evaluation"
                ))

            # Link pair to Source Provenance Records
            for rec in provenance_records:
                if f"{drug_a_id}_{drug_b_id}" in rec.source_id or f"{drug_a_id}:{drug_b_id}" == rec.external_identifier:
                    s_node_id = f"NODE_SOURCE_{rec.source_id}"
                    add_node(ExplanationNode(
                        node_id=s_node_id,
                        node_type=ExplanationNodeType.SOURCE_RECORD,
                        label=f"{rec.dataset_name}: {rec.record_type}",
                        description=rec.description,
                        phase_origin="Knowledge Graph Grounding",
                        source_reference=rec.external_identifier,
                        metadata={"dataset": rec.dataset_name, "available": rec.is_available}
                    ))
                    edges.append(ExplanationEdge(
                        edge_id=f"EDGE_{p_node_id}_{s_node_id}",
                        source_node_id=p_node_id,
                        target_node_id=s_node_id,
                        relationship_type=ExplanationRelationType.TRACES_TO,
                        contribution_weight=1.0 if rec.is_available else 0.0,
                        description=f"Pair grounded in {rec.dataset_name} evidentiary assertion"
                    ))

        # Identify Leaf and Root nodes
        sources = {e.source_node_id for e in edges}
        targets = {e.target_node_id for e in edges}
        roots = [n.node_id for n in nodes if n.node_id not in targets]
        leaves = [n.node_id for n in nodes if n.node_id not in sources]

        return ExplanationGraph(
            nodes=nodes,
            edges=edges,
            root_node_ids=roots if roots else [root_id],
            leaf_node_ids=leaves
        )
