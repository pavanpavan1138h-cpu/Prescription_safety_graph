"""
src/api/graph_subgraph_builder.py

Query-driven subgraph extraction and layout metadata builder.
Converts Phase 4 graph nodes, edges, and Phase 5/6 reasoning traces into
Cytoscape.js ready JSON structures with controlled truncation and no hallucinations.
"""

import logging
from typing import List, Dict, Set, Optional, Tuple
from api.graph_schemas import GraphNode, GraphEdge, GraphMetadata, SubgraphResponse
from prescription_reasoning import PrescriptionSafetyReasoner
from reasoning_schema import EvidenceStatus

logger = logging.getLogger(__name__)

DEFAULT_SIDE_EFFECT_LIMIT = 15

class SubgraphBuilder:
    def __init__(self, reasoner: PrescriptionSafetyReasoner):
        self.reasoner = reasoner
        self.retriever = reasoner.safety_engine.retriever

    def build_prescription_overview_graph(
        self,
        analysis_id: str,
        medications: List[str],
        side_effect_limit: int = 5
    ) -> SubgraphResponse:
        """
        Builds the macro-level visualization network for an entire prescription:
        - Canonical Drug nodes
        - RxNorm concept nodes
        - Direct INTERACTS_WITH edges
        - Reified DrugPair nodes with converging MEMBER_OF_PAIR edges
        - Sample ASSOCIATED_WITH SideEffect nodes
        """
        report = self.reasoner.analyze_prescription(medications, analysis_id)
        canonical_drugs = report.resolution_summary.canonical_drug_ids

        nodes: Dict[str, GraphNode] = {}
        edges: Dict[str, GraphEdge] = {}
        total_hidden_se = 0

        # 1. Add Canonical Drug Nodes & RxNorm Nodes
        for drug_id in canonical_drugs:
            drug = self.retriever.resolve_drug(drug_id)
            if not drug:
                continue

            # Drug Node
            nodes[drug_id] = GraphNode(
                id=drug_id,
                label=drug.display_name or drug_id,
                node_type="Drug",
                display_category="Canonical Drug",
                properties={
                    "internal_drug_id": drug_id,
                    "entity_status": drug.entity_status,
                    "rxcui": drug.rxcui,
                    "drugbank_ids": drug.drugbank_ids,
                    "twosides_cids": drug.twosides_cids
                },
                evidence_summary=f"Involved in {len([pr for pr in report.pair_results if drug.display_name in [pr['drug_a_name'], pr['drug_b_name']]])} evaluated pairs",
                is_focal=True
            )

            # RxNorm Node if available
            if drug.rxcui:
                rx_id = f"RXCUI_{drug.rxcui}"
                if rx_id not in nodes:
                    nodes[rx_id] = GraphNode(
                        id=rx_id,
                        label=f"RxNorm: {drug.rxnorm_name or drug.display_name}",
                        node_type="RxNormConcept",
                        display_category="Clinical Concept",
                        properties={
                            "rxcui": drug.rxcui,
                            "match_status": drug.rxnorm_match_status
                        }
                    )
                # Edge: HAS_RXNORM_CONCEPT
                edge_id = f"E_RX_{drug_id}__{rx_id}"
                edges[edge_id] = GraphEdge(
                    id=edge_id,
                    source=drug_id,
                    target=rx_id,
                    relationship_type="HAS_RXNORM_CONCEPT",
                    label="HAS_RXNORM_CONCEPT",
                    directional=True,
                    source_dataset="RxNorm",
                    properties={"match_status": drug.rxnorm_match_status}
                )

        # 2. Add Pairwise Relationships
        for pair_res in report.pair_results:
            d1_id = pair_res["drug_a_id"]
            d2_id = pair_res["drug_b_id"]
            evidence_bundle = self.retriever.retrieve_pair_evidence(d1_id, d2_id)

            # DDI Direct Edges
            for ddi in (evidence_bundle.ddi_records_forward + evidence_bundle.ddi_records_reverse):
                if ddi.edge_id not in edges:
                    edges[ddi.edge_id] = GraphEdge(
                        id=ddi.edge_id,
                        source=ddi.source_drug_id,
                        target=ddi.target_drug_id,
                        relationship_type="INTERACTS_WITH",
                        label="INTERACTS_WITH",
                        directional=True,
                        source_dataset="DrugBank",
                        evidence_priority="CRITICAL_EVIDENCE_PRIORITY" if pair_res["evidence_status"] == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE.value else "HIGH_EVIDENCE_PRIORITY",
                        properties={
                            "interaction_description": ddi.interaction_description,
                            "source_record_id": f"DDI:{ddi.source_drugbank_id_1}:{ddi.source_drugbank_id_2}"
                        }
                    )

            # TWOSIDES Reified DrugPair Node
            if evidence_bundle.total_side_effects_count > 0:
                pair_node_id = evidence_bundle.drug_pair_node_id or f"PAIR_{min(d1_id, d2_id)}__{max(d1_id, d2_id)}"
                if pair_node_id not in nodes:
                    nodes[pair_node_id] = GraphNode(
                        id=pair_node_id,
                        label=f"Combination: {pair_res['drug_a_name']} + {pair_res['drug_b_name']}",
                        node_type="DrugPair",
                        display_category="Reified Combination",
                        properties={
                            "total_adverse_events": evidence_bundle.total_side_effects_count
                        },
                        evidence_summary=f"{evidence_bundle.total_side_effects_count} observed adverse events"
                    )

                    # Converging MEMBER_OF_PAIR edges
                    e1 = f"E_MEM_{d1_id}__{pair_node_id}"
                    edges[e1] = GraphEdge(
                        id=e1,
                        source=d1_id,
                        target=pair_node_id,
                        relationship_type="MEMBER_OF_PAIR",
                        label="MEMBER_OF_PAIR",
                        directional=True,
                        source_dataset="TWOSIDES"
                    )
                    e2 = f"E_MEM_{d2_id}__{pair_node_id}"
                    edges[e2] = GraphEdge(
                        id=e2,
                        source=d2_id,
                        target=pair_node_id,
                        relationship_type="MEMBER_OF_PAIR",
                        label="MEMBER_OF_PAIR",
                        directional=True,
                        source_dataset="TWOSIDES"
                    )

                # Sample Side Effect nodes
                sample_ses = evidence_bundle.side_effect_records[:side_effect_limit]
                total_hidden_se += max(0, evidence_bundle.total_side_effects_count - len(sample_ses))

                for se in sample_ses:
                    se_node_id = f"SE_{se.side_effect_id}"
                    if se_node_id not in nodes:
                        nodes[se_node_id] = GraphNode(
                            id=se_node_id,
                            label=se.side_effect_name,
                            node_type="SideEffect",
                            display_category="Adverse Event Concept",
                            properties={"concept_id": se.side_effect_id}
                        )
                    edges[se.edge_id] = GraphEdge(
                        id=se.edge_id,
                        source=pair_node_id,
                        target=se_node_id,
                        relationship_type="ASSOCIATED_WITH",
                        label="ASSOCIATED_WITH",
                        directional=True,
                        source_dataset="TWOSIDES",
                        properties={"side_effect_name": se.side_effect_name}
                    )

        return SubgraphResponse(
            nodes=list(nodes.values()),
            edges=list(edges.values()),
            metadata=GraphMetadata(
                graph_type="PRESCRIPTION_OVERVIEW",
                analysis_id=analysis_id,
                node_count=len(nodes),
                edge_count=len(edges),
                truncated=total_hidden_se > 0,
                hidden_node_count=total_hidden_se,
                generated_from="PrescriptionSafetyGraph_Phase4"
            )
        )

    def build_pair_evidence_graph(
        self,
        analysis_id: str,
        pair_id: str,
        side_effect_limit: int = 25
    ) -> SubgraphResponse:
        """
        Builds the focused evidence subgraph for a single evaluated pair:
        Drug A, Drug B, RxNorm concepts, directed DDI edges, DrugPair, and Top-N SideEffects.
        """
        clean_pair = pair_id.replace("PAIR_", "")
        parts = clean_pair.split("__")
        if len(parts) != 2:
            raise ValueError(f"Invalid pair_id format: {pair_id}")

        d1_id, d2_id = parts[0], parts[1]
        drug_a = self.retriever.resolve_drug(d1_id)
        drug_b = self.retriever.resolve_drug(d2_id)
        if not drug_a or not drug_b:
            raise ValueError(f"One or both drugs not found: {d1_id}, {d2_id}")

        inference = self.reasoner.safety_engine.evaluate_pair(d1_id, d2_id)
        bundle = self.retriever.retrieve_pair_evidence(d1_id, d2_id)

        nodes: Dict[str, GraphNode] = {}
        edges: Dict[str, GraphEdge] = {}

        # 1. Focal Drug Nodes
        nodes[d1_id] = GraphNode(
            id=d1_id,
            label=drug_a.display_name or d1_id,
            node_type="Drug",
            display_category="Canonical Drug",
            properties={"internal_drug_id": d1_id, "rxcui": drug_a.rxcui},
            is_focal=True
        )
        nodes[d2_id] = GraphNode(
            id=d2_id,
            label=drug_b.display_name or d2_id,
            node_type="Drug",
            display_category="Canonical Drug",
            properties={"internal_drug_id": d2_id, "rxcui": drug_b.rxcui},
            is_focal=True
        )

        # 2. RxNorm Nodes
        for drug_obj, did in [(drug_a, d1_id), (drug_b, d2_id)]:
            if drug_obj.rxcui:
                rx_id = f"RXCUI_{drug_obj.rxcui}"
                nodes[rx_id] = GraphNode(
                    id=rx_id,
                    label=f"RxNorm: {drug_obj.rxnorm_name or drug_obj.display_name}",
                    node_type="RxNormConcept",
                    display_category="Clinical Concept",
                    properties={"rxcui": drug_obj.rxcui}
                )
                e_id = f"E_RX_{did}__{rx_id}"
                edges[e_id] = GraphEdge(
                    id=e_id,
                    source=did,
                    target=rx_id,
                    relationship_type="HAS_RXNORM_CONCEPT",
                    label="HAS_RXNORM_CONCEPT",
                    directional=True,
                    source_dataset="RxNorm"
                )

        # 3. Direct DDI Edges
        for ddi in (bundle.ddi_records_forward + bundle.ddi_records_reverse):
            edges[ddi.edge_id] = GraphEdge(
                id=ddi.edge_id,
                source=ddi.source_drug_id,
                target=ddi.target_drug_id,
                relationship_type="INTERACTS_WITH",
                label="INTERACTS_WITH",
                directional=True,
                source_dataset="DrugBank",
                evidence_priority="CRITICAL_EVIDENCE_PRIORITY" if inference.evidence_status == EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE else "HIGH_EVIDENCE_PRIORITY",
                properties={"interaction_description": ddi.interaction_description}
            )

        # 4. DrugPair Node & Side Effects
        hidden_count = 0
        if bundle.total_side_effects_count > 0:
            pair_node_id = f"PAIR_{min(d1_id, d2_id)}__{max(d1_id, d2_id)}"
            nodes[pair_node_id] = GraphNode(
                id=pair_node_id,
                label=f"Pair: {drug_a.display_name} + {drug_b.display_name}",
                node_type="DrugPair",
                display_category="Reified Combination",
                properties={"total_events": bundle.total_side_effects_count},
                evidence_summary=f"{bundle.total_side_effects_count} combination adverse events"
            )
            # MEMBER_OF_PAIR converging edges
            e1 = f"E_MEM_{d1_id}__{pair_node_id}"
            edges[e1] = GraphEdge(id=e1, source=d1_id, target=pair_node_id, relationship_type="MEMBER_OF_PAIR", label="MEMBER_OF_PAIR", directional=True, source_dataset="TWOSIDES")
            e2 = f"E_MEM_{d2_id}__{pair_node_id}"
            edges[e2] = GraphEdge(id=e2, source=d2_id, target=pair_node_id, relationship_type="MEMBER_OF_PAIR", label="MEMBER_OF_PAIR", directional=True, source_dataset="TWOSIDES")

            sample_ses = bundle.side_effect_records[:side_effect_limit]
            hidden_count = max(0, bundle.total_side_effects_count - len(sample_ses))

            for se in sample_ses:
                se_id = f"SE_{se.side_effect_id}"
                nodes[se_id] = GraphNode(
                    id=se_id,
                    label=se.side_effect_name,
                    node_type="SideEffect",
                    display_category="Adverse Event Concept",
                    properties={"concept_id": se.side_effect_id}
                )
                edges[se.edge_id] = GraphEdge(
                    id=se.edge_id,
                    source=pair_node_id,
                    target=se_id,
                    relationship_type="ASSOCIATED_WITH",
                    label="ASSOCIATED_WITH",
                    directional=True,
                    source_dataset="TWOSIDES"
                )

        return SubgraphResponse(
            nodes=list(nodes.values()),
            edges=list(edges.values()),
            metadata=GraphMetadata(
                graph_type="PAIR_EVIDENCE",
                analysis_id=analysis_id,
                pair_id=pair_id,
                node_count=len(nodes),
                edge_count=len(edges),
                truncated=hidden_count > 0,
                hidden_node_count=hidden_count,
                generated_from="PrescriptionSafetyGraph_Phase4"
            )
        )

    def build_provenance_graph(
        self,
        analysis_id: str,
        pair_id: str
    ) -> SubgraphResponse:
        """
        Builds an auditable multi-hop provenance trace graph:
        Inference Decision -> Rule Node -> Supporting Knowledge Graph Edges -> Ingested Source Datasets (DrugBank, TWOSIDES, RxNorm).
        """
        clean_pair = pair_id.replace("PAIR_", "")
        parts = clean_pair.split("__")
        if len(parts) != 2:
            raise ValueError(f"Invalid pair_id: {pair_id}")

        d1_id, d2_id = parts[0], parts[1]
        inference = self.reasoner.safety_engine.evaluate_pair(d1_id, d2_id)
        if not inference:
            raise ValueError(f"No inference found for pair: {pair_id}")

        drug_a = self.retriever.resolve_drug(d1_id)
        drug_b = self.retriever.resolve_drug(d2_id)
        bundle = self.retriever.retrieve_pair_evidence(d1_id, d2_id)

        nodes: Dict[str, GraphNode] = {}
        edges: Dict[str, GraphEdge] = {}

        # 1. Central Inference Node
        inf_id = f"NODE_{inference.inference_id}"
        nodes[inf_id] = GraphNode(
            id=inf_id,
            label=f"Inference: {inference.evidence_status.value}",
            node_type="InferenceDecision",
            display_category="Reasoning Output",
            properties={
                "inference_id": inference.inference_id,
                "confidence_score": inference.confidence_score,
                "confidence_level": inference.confidence_level.value,
                "rule_fired": inference.inference_rule
            },
            is_focal=True
        )

        # 2. Rule Node
        rule_node_id = f"RULE_{inference.inference_rule}"
        nodes[rule_node_id] = GraphNode(
            id=rule_node_id,
            label=f"Rule: {inference.inference_rule}",
            node_type="ReasoningRule",
            display_category="Deterministic Rule",
            properties={"rule_name": inference.inference_rule}
        )
        edges[f"E_INF_{inf_id}__{rule_node_id}"] = GraphEdge(
            id=f"E_INF_{inf_id}__{rule_node_id}",
            source=inf_id,
            target=rule_node_id,
            relationship_type="DERIVED_FROM",
            label="FIRED_BY_RULE",
            source_dataset="Phase5_SafetyRules"
        )

        # 3. Source Provenance Nodes
        for ds_name in ["DrugBank", "TWOSIDES", "RxNorm"]:
            ds_id = f"SOURCE_{ds_name.upper()}"
            nodes[ds_id] = GraphNode(
                id=ds_id,
                label=f"Source: {ds_name}",
                node_type="ProvenanceSource",
                display_category="Ingested Dataset",
                properties={"dataset_name": ds_name}
            )

        # Connect Rule to Supporting Datasets
        if bundle.ddi_records_forward or bundle.ddi_records_reverse:
            edges["E_RULE_DRUGBANK"] = GraphEdge(
                id="E_RULE_DRUGBANK",
                source=rule_node_id,
                target="SOURCE_DRUGBANK",
                relationship_type="GROUNDED_IN",
                label="DDI_EVIDENCE",
                source_dataset="DrugBank",
                properties={"assertions": len(bundle.ddi_records_forward) + len(bundle.ddi_records_reverse)}
            )

        if bundle.total_side_effects_count > 0:
            edges["E_RULE_TWOSIDES"] = GraphEdge(
                id="E_RULE_TWOSIDES",
                source=rule_node_id,
                target="SOURCE_TWOSIDES",
                relationship_type="GROUNDED_IN",
                label="OBSERVED_EVENTS",
                source_dataset="TWOSIDES",
                properties={"total_events": bundle.total_side_effects_count}
            )

        if (drug_a and drug_a.rxcui) or (drug_b and drug_b.rxcui):
            edges["E_RULE_RXNORM"] = GraphEdge(
                id="E_RULE_RXNORM",
                source=rule_node_id,
                target="SOURCE_RXNORM",
                relationship_type="GROUNDED_IN",
                label="CLINICAL_IDENTITY",
                source_dataset="RxNorm"
            )

        return SubgraphResponse(
            nodes=list(nodes.values()),
            edges=list(edges.values()),
            metadata=GraphMetadata(
                graph_type="PROVENANCE_TRACE",
                analysis_id=analysis_id,
                pair_id=pair_id,
                node_count=len(nodes),
                edge_count=len(edges),
                truncated=False,
                hidden_node_count=0,
                generated_from="PrescriptionSafetyProvenanceEngine_Phase5"
            )
        )
