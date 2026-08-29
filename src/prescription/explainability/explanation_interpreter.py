"""
src/prescription/explainability/explanation_interpreter.py

Generates template-assembled human-readable explanation narratives and
audits deterministic structured explanation claims.
"""

from typing import List, Dict, Any, Optional
from src.prescription.explainability.explainability_schema import (
    ContributionProfile,
    TraceabilityProfile,
    DecisionDependencyMap,
    StructuredExplanationClaim
)

class ExplanationInterpreter:
    """
    Assembles auditable deterministic explanation narratives explaining why conclusions
    were reached across analytical layers, coupled with strict safety disclaimers.
    """

    MANDATORY_DISCLAIMER = (
        "This explanation describes how the computational system derived its analytical "
        "outputs from available graph evidence. It is not a clinical recommendation and does "
        "not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."
    )

    def generate_narrative_and_claims(
        self,
        prescription_id: str,
        contribution_profiles: List[ContributionProfile],
        traceability_profile: TraceabilityProfile,
        dependency_map: DecisionDependencyMap
    ) -> tuple[str, List[StructuredExplanationClaim]]:
        claims: List[StructuredExplanationClaim] = []
        lines: List[str] = []

        lines.append(f"=== PRESCRIPTION EXPLANABILITY & REASONING LINEAGE REPORT ({prescription_id}) ===")
        lines.append("")

        # Section 1: Executive Traceability Summary
        lines.append("1. TRACEABILITY & REVERSE TRAVERSAL OVERVIEW:")
        lines.append(f"  - Traceability Coverage: {round(traceability_profile.traceability_coverage_score * 100, 1)}%")
        lines.append(f"  - Average Lineage Provenance Depth: {traceability_profile.average_provenance_depth} layers (Max: {traceability_profile.max_provenance_depth})")
        lines.append(f"  - Cross-Layer Traceability Classification: {traceability_profile.cross_layer_traceability.value}")
        lines.append(f"  - Orphaned / Unavailable Provenance Components: {traceability_profile.orphaned_components_count}")
        lines.append("")

        # Claim 1: Traceability
        claims.append(StructuredExplanationClaim(
            claim_id="CLAIM_TRACEABILITY_COVERAGE",
            claim_type="TRACEABILITY_EVALUATION",
            claim_text=f"The prescription analysis achieved {round(traceability_profile.traceability_coverage_score * 100, 1)}% traceability coverage across {traceability_profile.total_components_evaluated} evaluated components.",
            referenced_entity_ids=[d.entity_id for d in dependency_map.dependencies[:3]],
            is_supported=(traceability_profile.traceability_coverage_score >= 0.5),
            supporting_evidence_ids=["TRACEABILITY_PROFILE"]
        ))

        # Section 2: Key Decision Contributors
        primary_contribs = [p for p in contribution_profiles if p.contribution_level.value in ["PRIMARY_CONTRIBUTOR", "MAJOR_CONTRIBUTOR"]]
        lines.append("2. PRIMARY ANALYTICAL CONTRIBUTORS:")
        if primary_contribs:
            for idx, c in enumerate(primary_contribs[:5], start=1):
                lines.append(f"  {idx}. {c.entity_label} [{c.entity_type}] (Score: {c.overall_contribution_score}, Level: {c.contribution_level.value})")
                lines.append(f"     Why: {c.explanation}")
        else:
            lines.append("  - No dominant primary contributors identified; decision components are uniformly distributed.")
        lines.append("")

        # Claim 2: Contributors
        if primary_contribs:
            top_c = primary_contribs[0]
            claims.append(StructuredExplanationClaim(
                claim_id="CLAIM_PRIMARY_CONTRIBUTOR",
                claim_type="CONTRIBUTION_RANKING",
                claim_text=f"Entity '{top_c.entity_label}' is identified as the primary analytical contributor with a contribution score of {top_c.overall_contribution_score}.",
                referenced_entity_ids=[top_c.entity_id],
                is_supported=(top_c.overall_contribution_score >= 0.5),
                supporting_evidence_ids=[top_c.entity_id]
            ))

        # Section 3: Decision Dependency Structure
        lines.append("3. DECISION DEPENDENCY HIERARCHY:")
        lines.append(f"  - Acyclic Derivation DAG Verified: {dependency_map.acyclic_verified}")
        lines.append(f"  - Critical Path Entities Count: {len(dependency_map.critical_path_entities)}")
        if dependency_map.critical_path_entities:
            lines.append(f"  - Critical Nodes: {', '.join(dependency_map.critical_path_entities[:4])}")
        lines.append("")

        # Section 4: Mandatory Guardrail
        lines.append("4. SCIENTIFIC & CLINICAL GUARDRAIL:")
        lines.append(f"  {self.MANDATORY_DISCLAIMER}")

        narrative = "\n".join(lines)
        return narrative, claims
