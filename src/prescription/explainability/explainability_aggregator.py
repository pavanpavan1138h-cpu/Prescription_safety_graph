"""
src/prescription/explainability/explainability_aggregator.py

Master aggregator orchestrating Phase 11 Evidence Provenance, Traceability
and Explainability Intelligence Engine.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.explainability.explainability_schema import PrescriptionExplainabilityProfile
from src.prescription.explainability.provenance_resolver import ProvenanceResolver
from src.prescription.explainability.contribution_analyzer import ContributionAnalyzer
from src.prescription.explainability.dependency_mapper import DependencyMapper
from src.prescription.explainability.traceability_analyzer import TraceabilityAnalyzer
from src.prescription.explainability.explanation_graph_builder import ExplanationGraphBuilder
from src.prescription.explainability.explanation_interpreter import ExplanationInterpreter

class ExplainabilityAggregator:
    """
    Coordinates the full Phase 11 reverse traversal and explainability pipeline.
    """

    def __init__(self):
        self.provenance_resolver = ProvenanceResolver()
        self.contribution_analyzer = ContributionAnalyzer()
        self.dependency_mapper = DependencyMapper()
        self.traceability_analyzer = TraceabilityAnalyzer()
        self.graph_builder = ExplanationGraphBuilder()
        self.interpreter = ExplanationInterpreter()

    def generate_explainability_profile(
        self,
        analysis_result: PrescriptionSafetyReport,
        structural_analysis: Optional[Any] = None,
        evidence_intelligence: Optional[Any] = None,
        contextual_stability: Optional[Any] = None
    ) -> PrescriptionExplainabilityProfile:
        meta = getattr(analysis_result, "metadata", None)
        if meta:
            analysis_id = getattr(meta, "analysis_id", "UNKNOWN_ANALYSIS")
            prescription_id = getattr(meta, "prescription_id", None) or analysis_id
        else:
            prescription_id = getattr(analysis_result, "prescription_id", "UNKNOWN_PRESCRIPTION")
            analysis_id = prescription_id
        now_str = datetime.now(timezone.utc).isoformat()

        # 1. Resolve grounded source provenance
        provenance_records = self.provenance_resolver.resolve_provenance(
            analysis_result=analysis_result,
            evidence_intelligence=evidence_intelligence
        )

        # 2. Analyze multi-layer decision contributions
        contribution_profiles = self.contribution_analyzer.analyze_contributions(
            analysis_result=analysis_result,
            structural_analysis=structural_analysis,
            evidence_intelligence=evidence_intelligence,
            contextual_stability=contextual_stability
        )

        # 3. Map hierarchical decision dependencies DAG
        dependency_map = self.dependency_mapper.map_dependencies(
            analysis_result=analysis_result,
            structural_analysis=structural_analysis,
            evidence_intelligence=evidence_intelligence,
            contextual_stability=contextual_stability
        )

        # 4. Build complete explanation graph
        explanation_graph = self.graph_builder.build_graph(
            analysis_result=analysis_result,
            provenance_records=provenance_records,
            structural_analysis=structural_analysis,
            evidence_intelligence=evidence_intelligence,
            contextual_stability=contextual_stability
        )

        # 5. Calculate traceability coverage and provenance depth
        traceability_profile = self.traceability_analyzer.analyze_traceability(
            explanation_graph=explanation_graph,
            provenance_records=provenance_records
        )

        # 6. Generate narrative and structured claims
        narrative, claims = self.interpreter.generate_narrative_and_claims(
            prescription_id=prescription_id,
            contribution_profiles=contribution_profiles,
            traceability_profile=traceability_profile,
            dependency_map=dependency_map
        )

        return PrescriptionExplainabilityProfile(
            prescription_id=prescription_id,
            analysis_id=analysis_id,
            generated_at=now_str,
            explanation_graph=explanation_graph,
            contribution_profiles=contribution_profiles,
            dependency_map=dependency_map,
            traceability_profile=traceability_profile,
            provenance_records=provenance_records,
            structured_claims=claims,
            narrative=narrative,
            guardrails=[ExplanationInterpreter.MANDATORY_DISCLAIMER]
        )
