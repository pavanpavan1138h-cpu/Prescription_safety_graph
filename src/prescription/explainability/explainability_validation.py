"""
src/prescription/explainability/explainability_validation.py

Enforces invariants and validation checks for Phase 11 Explainability Profile.
"""

from typing import List, Dict, Any, Tuple
from src.prescription.explainability.explainability_schema import PrescriptionExplainabilityProfile
from src.prescription.explainability.explanation_interpreter import ExplanationInterpreter

class ExplainabilityValidator:
    """
    Validates structural, mathematical, acyclicity, and guardrail invariants on
    PrescriptionExplainabilityProfile instances.
    """

    DISALLOWED_PHRASES = [
        "is clinically safe",
        "is medically safe",
        "recommend discontinuing",
        "should stop taking",
        "should remove medication",
        "prescribe this instead"
    ]

    def validate_profile(self, profile: PrescriptionExplainabilityProfile) -> Tuple[bool, List[str], List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        # Invariant 1: Contribution scores in [0.0, 1.0]
        for cp in profile.contribution_profiles:
            if not (0.0 <= cp.overall_contribution_score <= 1.0):
                errors.append(f"Contribution score out of bounds for '{cp.entity_id}': {cp.overall_contribution_score}")
            if not (0.0 <= cp.direct_decision_contribution <= 1.0):
                errors.append(f"Direct decision contribution out of bounds for '{cp.entity_id}'")
            if not (0.0 <= cp.evidence_coverage <= 1.0):
                errors.append(f"Evidence coverage out of bounds for '{cp.entity_id}'")

        # Invariant 2: Traceability coverage score in [0.0, 1.0]
        tp = profile.traceability_profile
        if not (0.0 <= tp.traceability_coverage_score <= 1.0):
            errors.append(f"Traceability coverage score out of bounds: {tp.traceability_coverage_score}")

        # Invariant 3: Valid Explanation Graph Edges
        node_ids = {n.node_id for n in profile.explanation_graph.nodes}
        for edge in profile.explanation_graph.edges:
            if edge.source_node_id not in node_ids:
                errors.append(f"Edge {edge.edge_id} references missing source node: {edge.source_node_id}")
            if edge.target_node_id not in node_ids:
                errors.append(f"Edge {edge.edge_id} references missing target node: {edge.target_node_id}")

        # Invariant 4: Dependency DAG must be acyclic
        if not profile.dependency_map.acyclic_verified:
            errors.append("Decision dependency map contains cyclical dependencies.")

        # Invariant 5: Mandatory Guardrail presence
        if not profile.guardrails:
            errors.append("No guardrail statements provided in explainability profile.")
        else:
            if ExplanationInterpreter.MANDATORY_DISCLAIMER not in profile.guardrails[0]:
                errors.append("Mandatory clinical disclaimer missing or altered in guardrail.")

        # Invariant 6: Narrative safety language scan
        narrative_lower = profile.narrative.lower()
        for phrase in self.DISALLOWED_PHRASES:
            if phrase in narrative_lower:
                errors.append(f"Disallowed clinical prescription recommendation phrase found in narrative: '{phrase}'")

        # Invariant 7: Claims validation
        for claim in profile.structured_claims:
            if not claim.claim_id:
                errors.append("Structured claim missing claim_id")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings
