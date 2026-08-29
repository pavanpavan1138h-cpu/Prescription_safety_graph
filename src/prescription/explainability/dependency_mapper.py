"""
src/prescription/explainability/dependency_mapper.py

Constructs the decision dependency DAG tracing final conclusions through
intermediate themes, structural clusters, and underlying pair evidence.
"""

from typing import List, Dict, Any, Optional, Set
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.explainability.explainability_schema import DecisionDependencyMap, DependencyNode

class DependencyMapper:
    """
    Creates an acyclic dependency structure linking aggregate interpretations
    down through analytical layers.
    """

    def map_dependencies(
        self,
        analysis_result: PrescriptionSafetyReport,
        structural_analysis: Optional[Any] = None,
        evidence_intelligence: Optional[Any] = None,
        contextual_stability: Optional[Any] = None
    ) -> DecisionDependencyMap:
        dependencies: List[DependencyNode] = []
        critical_entities: List[str] = []

        root_id = "FINAL_INTERPRETATION"
        root_depends: List[str] = []

        # 1. Themes / Signals layer
        if evidence_intelligence and hasattr(evidence_intelligence, "evidence_themes"):
            for theme in evidence_intelligence.evidence_themes:
                t_id = f"THEME_{theme.theme_name}"
                root_depends.append(t_id)
                pair_deps = [f"PAIR_{p}" for p in theme.supporting_pairs]
                dependencies.append(DependencyNode(
                    entity_id=t_id,
                    entity_label=f"Evidence Theme: {theme.theme_name}",
                    entity_type="SIGNAL_THEME",
                    depends_on_ids=pair_deps,
                    dependency_weight=round(min(1.0, theme.reinforcement_score / 5.0), 2),
                    critical_dependency=(theme.reinforcement_level == "HIGH_REINFORCEMENT")
                ))
                if theme.reinforcement_level == "HIGH_REINFORCEMENT":
                    critical_entities.append(t_id)

        # 2. Structural Layer
        if structural_analysis:
            s_id = "STRUCTURAL_TOPOLOGY"
            root_depends.append(s_id)
            highest_drug = None
            if hasattr(structural_analysis, "structural_interpretation") and structural_analysis.structural_interpretation:
                highest_drug = getattr(structural_analysis.structural_interpretation, "highest_participation_drug", None)
            
            top_type = "EVALUATED_NETWORK"
            if hasattr(structural_analysis, "topology") and structural_analysis.topology:
                top_type = getattr(structural_analysis.topology, "primary_topology", None) or getattr(structural_analysis.topology, "topology_classification", "EVALUATED_NETWORK")
            elif hasattr(structural_analysis, "structural_interpretation") and structural_analysis.structural_interpretation:
                top_type = getattr(structural_analysis.structural_interpretation, "topology_classification", "EVALUATED_NETWORK")

            struct_deps = [f"DRUG_{highest_drug}"] if highest_drug else []
            dependencies.append(DependencyNode(
                entity_id=s_id,
                entity_label=f"Topology: {top_type}",
                entity_type="STRUCTURAL_RESULT",
                depends_on_ids=struct_deps,
                dependency_weight=0.8,
                critical_dependency=True
            ))

        # 3. Pair results layer
        for pair in analysis_result.pair_results:
            p_id = pair.get("pair_id") if isinstance(pair, dict) else getattr(pair, "pair_id", "")
            drug_a_id = pair.get("drug_a_id") if isinstance(pair, dict) else getattr(pair, "drug_a_id", "")
            drug_b_id = pair.get("drug_b_id") if isinstance(pair, dict) else getattr(pair, "drug_b_id", "")
            drug_a_name = pair.get("drug_a_name") if isinstance(pair, dict) else getattr(pair, "drug_a_name", "")
            drug_b_name = pair.get("drug_b_name") if isinstance(pair, dict) else getattr(pair, "drug_b_name", "")
            st = pair.get("evidence_status") if isinstance(pair, dict) else getattr(pair, "evidence_status", "")

            node_p_id = f"PAIR_{p_id}"
            drug_deps = [f"DRUG_{drug_a_id}", f"DRUG_{drug_b_id}"]
            is_critical = st == "CONVERGENT_SAFETY_EVIDENCE"
            dependencies.append(DependencyNode(
                entity_id=node_p_id,
                entity_label=f"{drug_a_name} + {drug_b_name}",
                entity_type="DRUG_PAIR",
                depends_on_ids=drug_deps,
                dependency_weight=0.9 if is_critical else 0.5,
                critical_dependency=is_critical
            ))
            if is_critical:
                critical_entities.append(node_p_id)

        # 4. Drug Entities Layer
        if analysis_result.resolution_summary:
            for drug in analysis_result.resolution_summary.resolved_drugs:
                d_id = getattr(drug, "resolved_internal_drug_id", None) or getattr(drug, "canonical_drug_id", "UNKNOWN")
                d_name = getattr(drug, "display_name", None) or getattr(drug, "canonical_name", "UNKNOWN")
                dependencies.append(DependencyNode(
                    entity_id=f"DRUG_{d_id}",
                    entity_label=d_name,
                    entity_type="DRUG_ENTITY",
                    depends_on_ids=[f"RXNORM_{d_id}"],
                    dependency_weight=0.5,
                    critical_dependency=False
                ))

        # Root Node
        pair_ids = [p.get("pair_id") if isinstance(p, dict) else getattr(p, "pair_id", "") for p in analysis_result.pair_results]
        dependencies.append(DependencyNode(
            entity_id=root_id,
            entity_label="Aggregate Prescription Evidence Interpretation",
            entity_type="FINAL_INTERPRETATION",
            depends_on_ids=root_depends if root_depends else [f"PAIR_{pid}" for pid in pair_ids],
            dependency_weight=1.0,
            critical_dependency=True
        ))

        # Verify Acyclic DAG (Topological check)
        is_acyclic = self._check_acyclic(dependencies)

        return DecisionDependencyMap(
            target_interpretation_id=root_id,
            dependencies=dependencies,
            critical_path_entities=list(set(critical_entities)),
            acyclic_verified=is_acyclic
        )

    def _check_acyclic(self, dependencies: List[DependencyNode]) -> bool:
        adj: Dict[str, List[str]] = {d.entity_id: d.depends_on_ids for d in dependencies}
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if not dfs(neighbor):
                        return False
                elif neighbor in rec_stack:
                    return False
            rec_stack.remove(node)
            return True

        for node in adj:
            if node not in visited:
                if not dfs(node):
                    return False
        return True
