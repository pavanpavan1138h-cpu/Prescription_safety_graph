"""
src/api/main.py

FastAPI Application entry point for Phase 7 Prescription Safety Platform.
Defines REST API endpoints under /api/v1 and static/SPA mounting for the Web UI.
"""

import logging
from typing import Optional, List
from pathlib import Path

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.config import settings
from src.api.schemas import (
    HealthResponse,
    SystemInfoResponse,
    DrugResolveRequest,
    DrugResolveResponse,
    DrugEntityCardResponse,
    PairSafetyRequest,
    PairSafetyResponse,
    PrescriptionAnalyzeRequest,
    PrescriptionAnalysisResponse,
    PairDetailResponse,
    ErrorResponse
)
from src.api.advanced_schemas import (
    AdvancedPrescriptionAnalysisResponse,
    PrescriptionStructuralAnalysisSchema,
    DrugStructuralProfileSchema,
    ClusterMetricsSchema,
    CounterfactualResultSchema,
    # Phase 9
    PrescriptionEvidenceIntelligenceProfileSchema,
    EvidenceThemeSchema,
    CrossPairSignalGroupSchema,
    EvidenceConcentrationProfileSchema,
    StructuralEvidenceAlignmentSchema,
    # Phase 10
    ContextualStabilityProfileSchema,
    ScenarioProfileSchema,
    EvidenceStabilityScoreSchema,
    DrugDependencyImpactSchema,
    # Phase 11 Explainability
    PrescriptionExplainabilityProfileSchema,
    ExplanationGraphSchema,
    ContributionProfileSchema,
    DecisionDependencyMapSchema,
    TraceabilityProfileSchema,
    SourceProvenanceRecordSchema,
    # Comparison Schemas
    PrescriptionComparativeIntelligenceProfileSchema,
    EvidenceDeltaSchema,
    StructuralDeltaSchema,
    SignalDeltaSchema,
    StabilityDeltaSchema,
    # Phase 12 Trustworthiness
    PrescriptionTrustworthinessProfileSchema,
    ReproducibilityProfileSchema,
    InputPerturbationResultSchema,
    StructuralRobustnessProfileSchema,
    SignalRobustnessProfileSchema,
    CrossLayerConsistencyProfileSchema,
    ProvenanceCompletenessProfileSchema,
    ExplanationConsistencyProfileSchema,
    # Phase 13 Longitudinal Evolution
    PrescriptionLongitudinalProfileSchema,
    PrescriptionSnapshotReferenceSchema,
    PersistenceProfileSchema,
    EmergenceEventSchema,
    DisappearanceEventSchema,
    LongitudinalChangePointSchema,
    StructuralEvolutionProfileSchema,
    SignalEvolutionProfileSchema,
    StabilityEvolutionProfileSchema,
    TrustworthinessEvolutionProfileSchema,
    CrossLayerEvolutionProfileSchema,
    LongitudinalAnalysisRequest
)
from src.api.service import PrescriptionService, get_prescription_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Deterministic REST API and Reasoning Service for the Prescription Safety Knowledge Graph."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------------------------------
# 1. System Endpoints
# -------------------------------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(service: PrescriptionService = Depends(get_prescription_service)):
    """Service liveness and readiness probe."""
    return HealthResponse(
        status="healthy",
        service="prescription-safety-graph-api",
        graph_loaded=service.is_ready,
        reasoning_engine_available=service.is_ready
    )

@app.get("/api/v1/system/info", response_model=SystemInfoResponse, tags=["System"])
def get_system_info(service: PrescriptionService = Depends(get_prescription_service)):
    """Returns knowledge graph node/edge statistics and capabilities."""
    return service.get_system_info()

# -------------------------------------------------------------------------------------------------
# 2. Drug Identity & Resolution Endpoints
# -------------------------------------------------------------------------------------------------
@app.post("/api/v1/drugs/resolve", response_model=DrugResolveResponse, tags=["Drugs"])
def resolve_drugs(req: DrugResolveRequest, service: PrescriptionService = Depends(get_prescription_service)):
    """Resolves arbitrary mixed medication identifiers to canonical entities with duplicate detection."""
    clean_meds = [m.strip() for m in req.drugs if m.strip()]
    if not clean_meds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one valid medication string must be provided."
        )
    return service.resolve_drugs(clean_meds)

@app.get("/api/v1/drugs/{identifier}", response_model=DrugEntityCardResponse, tags=["Drugs"])
def get_drug_card(identifier: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves full entity details for a single drug identifier."""
    res = service.get_drug_card(identifier)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug identifier '{identifier}' could not be resolved in the knowledge graph."
        )
    return res

# -------------------------------------------------------------------------------------------------
# 3. Pairwise Safety Reasoning
# -------------------------------------------------------------------------------------------------
@app.post("/api/v1/safety/pair", response_model=PairSafetyResponse, tags=["Reasoning"])
def evaluate_pair(req: PairSafetyRequest, service: PrescriptionService = Depends(get_prescription_service)):
    """Evaluates direct interaction and combination adverse-event evidence for a single drug pair."""
    res = service.evaluate_pair(req.drug_a, req.drug_b)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not evaluate pair '{req.drug_a}' + '{req.drug_b}'. One or both medications not found."
        )
    return res

# -------------------------------------------------------------------------------------------------
# 4. Multi-Drug Prescription Analysis
# -------------------------------------------------------------------------------------------------
@app.post("/api/v1/prescriptions/analyze", response_model=PrescriptionAnalysisResponse, tags=["Prescriptions"])
def analyze_prescription(req: PrescriptionAnalyzeRequest, service: PrescriptionService = Depends(get_prescription_service)):
    """
    Main entry point: Analyzes an entire medication list, generates N*(N-1)/2 combinations,
    evaluates multi-channel evidence, aggregates participation, prioritizes findings, and returns report.
    """
    clean_meds = [m.strip() for m in req.medications if m.strip()]
    if not clean_meds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication list cannot be empty."
        )
    if len(clean_meds) > settings.max_medications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Medication list exceeds maximum allowed size of {settings.max_medications} items."
        )
    return service.analyze_prescription(clean_meds, req.prescription_id)

@app.post("/api/v1/prescriptions/analyze-advanced", response_model=AdvancedPrescriptionAnalysisResponse, tags=["Advanced Clinical Intelligence"])
def analyze_prescription_advanced(req: PrescriptionAnalyzeRequest, service: PrescriptionService = Depends(get_prescription_service)):
    """
    Phase 8 Advanced Clinical Intelligence:
    Performs multi-drug pairwise reasoning + complexity profiling, cross-pair adverse event convergence,
    evidence pattern detection, review prioritization, structured uncertainty, and context requirements.
    """
    clean_meds = [m.strip() for m in req.medications if m.strip()]
    if not clean_meds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication list cannot be empty."
        )
    if len(clean_meds) > settings.max_medications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Medication list exceeds maximum allowed size of {settings.max_medications} items."
        )
    return service.analyze_prescription_advanced(clean_meds, req.prescription_id)

@app.get("/api/v1/analyses/{analysis_id}/pairs/{pair_id}", response_model=PairDetailResponse, tags=["Prescriptions"])
def get_pair_detail(analysis_id: str, pair_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves granular on-demand evidence and multi-hop graph path traces for a specific evaluated pair."""
    res = service.get_pair_detail(analysis_id, pair_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pair '{pair_id}' not found for analysis '{analysis_id}'."
        )
    return res

# --- Phase 8 Structural Analysis Endpoints ---
@app.get("/api/v1/analyses/{analysis_id}/structure", response_model=PrescriptionStructuralAnalysisSchema, tags=["Advanced Clinical Intelligence"])
def get_structural_analysis(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves full network topology and structural safety analysis for a completed prescription."""
    res = service.get_structural_analysis(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/structure/drugs", response_model=List[DrugStructuralProfileSchema], tags=["Advanced Clinical Intelligence"])
def get_structural_drugs(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves ranked structural profiles for all drugs in the prescription network."""
    res = service.get_structural_drugs(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/structure/clusters", response_model=List[ClusterMetricsSchema], tags=["Advanced Clinical Intelligence"])
def get_structural_clusters(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves cluster segmentation and component metrics for the prescription network."""
    res = service.get_structural_clusters(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/structure/counterfactuals", response_model=List[CounterfactualResultSchema], tags=["Advanced Clinical Intelligence"])
def get_structural_counterfactuals(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves simulated drug removal counterfactual exclusion details."""
    res = service.get_structural_counterfactuals(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

# --- Phase 9 Evidence Intelligence Endpoints ---
@app.get("/api/v1/analyses/{analysis_id}/intelligence", response_model=PrescriptionEvidenceIntelligenceProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_evidence_intelligence(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves synthesized evidence themes, signals convergence, and alignment for a completed prescription."""
    res = service.get_evidence_intelligence(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/intelligence/themes", response_model=List[EvidenceThemeSchema], tags=["Advanced Clinical Intelligence"])
def get_intelligence_themes(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves all clinical safety themes identified across combinations."""
    res = service.get_intelligence_themes(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/intelligence/signals", response_model=List[CrossPairSignalGroupSchema], tags=["Advanced Clinical Intelligence"])
def get_intelligence_signals(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves recurring cross-pair signal groups with reinforcement scores."""
    res = service.get_intelligence_signals(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/intelligence/concentration", response_model=EvidenceConcentrationProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_intelligence_concentration(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves evidence concentration patterns (Centralized vs Distributed)."""
    res = service.get_intelligence_concentration(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/intelligence/alignment", response_model=StructuralEvidenceAlignmentSchema, tags=["Advanced Clinical Intelligence"])
def get_intelligence_alignment(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves structural hub and evidence pathway ranking correlations."""
    res = service.get_intelligence_alignment(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

# --- Phase 10 Contextual Stability Endpoints ---
@app.get("/api/v1/analyses/{analysis_id}/contextual", response_model=ContextualStabilityProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_contextual_stability(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves full contextual stability profile evaluating analytical perturbations."""
    res = service.get_contextual_stability(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/contextual/scenarios", response_model=List[ScenarioProfileSchema], tags=["Advanced Clinical Intelligence"])
def get_contextual_scenarios(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves list of evaluated contextual scenarios and outcomes."""
    res = service.get_contextual_scenarios(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/contextual/metrics", response_model=EvidenceStabilityScoreSchema, tags=["Advanced Clinical Intelligence"])
def get_contextual_metrics(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves high-level evidence stability scoring metrics."""
    res = service.get_contextual_metrics(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/contextual/dependency", response_model=List[DrugDependencyImpactSchema], tags=["Advanced Clinical Intelligence"])
def get_contextual_dependency(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves drug-level evidence dependency loss scores."""
    res = service.get_contextual_dependency(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

class PrescriptionComparisonRequest(BaseModel):
    analysis_id_a: str
    analysis_id_b: str

# --- Phase 11 Prescription Comparative Intelligence Endpoints ---
@app.post("/api/v1/prescriptions/compare", response_model=PrescriptionComparativeIntelligenceProfileSchema, tags=["Advanced Clinical Intelligence"])
def compare_prescriptions(req: PrescriptionComparisonRequest, service: PrescriptionService = Depends(get_prescription_service)):
    """Computes comparison delta report between two previous prescription snapshots."""
    try:
        return service.compare_prescriptions(req.analysis_id_a, req.analysis_id_b)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/api/v1/comparisons/{comparison_id}", response_model=PrescriptionComparativeIntelligenceProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_comparison_profile(comparison_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves cached comparative profile by ID."""
    res = service.get_comparison_profile(comparison_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison report '{comparison_id}' not found."
        )
    return res

@app.get("/api/v1/comparisons/{comparison_id}/evidence", response_model=EvidenceDeltaSchema, tags=["Advanced Clinical Intelligence"])
def get_comparison_evidence(comparison_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves evidence status reclassifications delta."""
    res = service.get_comparison_evidence(comparison_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison report '{comparison_id}' not found."
        )
    return res

@app.get("/api/v1/comparisons/{comparison_id}/structure", response_model=StructuralDeltaSchema, tags=["Advanced Clinical Intelligence"])
def get_comparison_structure(comparison_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves structural network metric delta and drug rank movements."""
    res = service.get_comparison_structure(comparison_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison report '{comparison_id}' not found."
        )
    return res

@app.get("/api/v1/comparisons/{comparison_id}/signals", response_model=SignalDeltaSchema, tags=["Advanced Clinical Intelligence"])
def get_comparison_signals(comparison_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves theme emergence and reinforcement delta."""
    res = service.get_comparison_signals(comparison_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison report '{comparison_id}' not found."
        )
    return res

@app.get("/api/v1/comparisons/{comparison_id}/stability", response_model=StabilityDeltaSchema, tags=["Advanced Clinical Intelligence"])
def get_comparison_stability(comparison_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves contextual sensitivity and interpretation stability delta."""
    res = service.get_comparison_stability(comparison_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison report '{comparison_id}' not found."
        )
    return res

# --- Phase 11 Prescription Explainability & Provenance Endpoints ---
@app.get("/api/v1/analyses/{analysis_id}/explainability", response_model=PrescriptionExplainabilityProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_explainability(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves full explainability and reverse derivation profile."""
    res = service.get_explainability_profile(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/explainability/graph", response_model=ExplanationGraphSchema, tags=["Advanced Clinical Intelligence"])
def get_explainability_graph(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves machine-readable explanation lineage graph."""
    res = service.get_explainability_graph(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/explainability/provenance", response_model=List[SourceProvenanceRecordSchema], tags=["Advanced Clinical Intelligence"])
def get_explainability_provenance(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves grounded source provenance records."""
    res = service.get_explainability_provenance(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/explainability/contributors", response_model=List[ContributionProfileSchema], tags=["Advanced Clinical Intelligence"])
def get_explainability_contributors(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves multi-layer decision contribution rankings."""
    res = service.get_explainability_contributors(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/explainability/dependencies", response_model=DecisionDependencyMapSchema, tags=["Advanced Clinical Intelligence"])
def get_explainability_dependencies(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves hierarchical decision dependency DAG."""
    res = service.get_explainability_dependencies(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/explainability/traceability", response_model=TraceabilityProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_explainability_traceability(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves traceability coverage score and provenance depth metrics."""
    res = service.get_explainability_traceability(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

# --- Phase 12 Trustworthiness Endpoints ---
@app.get("/api/v1/analyses/{analysis_id}/trustworthiness", response_model=PrescriptionTrustworthinessProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_trustworthiness(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves full trustworthiness profile."""
    res = service.get_trustworthiness_profile(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/trustworthiness/reproducibility", response_model=ReproducibilityProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_reproducibility(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves reproducibility evaluations."""
    res = service.get_trustworthiness_reproducibility(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/trustworthiness/perturbations", response_model=List[InputPerturbationResultSchema], tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_perturbations(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves medication input perturbation invariance matrices."""
    res = service.get_trustworthiness_perturbations(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/trustworthiness/structure", response_model=StructuralRobustnessProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_structure(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves structural network topology persistence values."""
    res = service.get_trustworthiness_structure(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/trustworthiness/signals", response_model=List[SignalRobustnessProfileSchema], tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_signals(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves evidence theme persistence rates."""
    res = service.get_trustworthiness_signals(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/trustworthiness/cross-layer", response_model=CrossLayerConsistencyProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_cross_layer(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves cross-layer alignment convergence metrics."""
    res = service.get_trustworthiness_cross_layer(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/trustworthiness/provenance", response_model=ProvenanceCompletenessProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_provenance(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves provenance completeness and depth rankings."""
    res = service.get_trustworthiness_provenance(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

@app.get("/api/v1/analyses/{analysis_id}/trustworthiness/explanation-consistency", response_model=ExplanationConsistencyProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_explanation_consistency(analysis_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves explanation validation claim checks."""
    res = service.get_trustworthiness_explanation_consistency(analysis_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found."
        )
    return res

# -------------------------------------------------------------------------------------------------
# 5. Interactive Graph Visualization Endpoints
# -------------------------------------------------------------------------------------------------
from src.graph.schemas import SubgraphResponse
from src.api.graph_service import GraphService, get_graph_service

@app.get("/api/v1/analyses/{analysis_id}/graph", response_model=SubgraphResponse, tags=["Visualization"])
def get_prescription_graph(analysis_id: str, side_effect_limit: int = 5, graph_service: GraphService = Depends(get_graph_service)):
    """Retrieves Cytoscape-ready subgraph for an entire analyzed prescription."""
    try:
        return graph_service.get_prescription_overview_graph(analysis_id, side_effect_limit=side_effect_limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/api/v1/analyses/{analysis_id}/pairs/{pair_id}/graph", response_model=SubgraphResponse, tags=["Visualization"])
def get_pair_evidence_graph(analysis_id: str, pair_id: str, side_effect_limit: int = 25, graph_service: GraphService = Depends(get_graph_service)):
    """Retrieves focused evidence subgraph for a single evaluated pair."""
    try:
        return graph_service.get_pair_evidence_graph(analysis_id, pair_id, side_effect_limit=side_effect_limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/api/v1/analyses/{analysis_id}/pairs/{pair_id}/provenance-graph", response_model=SubgraphResponse, tags=["Visualization"])
def get_provenance_graph(analysis_id: str, pair_id: str, graph_service: GraphService = Depends(get_graph_service)):
    """Retrieves multi-hop provenance graph tracing inference decisions to source datasets."""
    try:
        return graph_service.get_provenance_graph(analysis_id, pair_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# -------------------------------------------------------------------------------------------------
# 5.5. Longitudinal Evolution Endpoints (Phase 13)
# -------------------------------------------------------------------------------------------------
@app.post("/api/v1/analyses/longitudinal", tags=["Advanced Clinical Intelligence"])
def post_longitudinal(req: LongitudinalAnalysisRequest, service: PrescriptionService = Depends(get_prescription_service)):
    """Triggers longitudinal timeline resolution over analysis snapshots list."""
    long_id = service.create_longitudinal_profile(req.analysis_ids)
    if not long_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="None of the specified analysis IDs were found in cache."
        )
    return {"longitudinal_id": long_id}

@app.get("/api/v1/longitudinal/{longitudinal_id}", response_model=PrescriptionLongitudinalProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_longitudinal_profile(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves complete longitudinal profile."""
    res = service.get_longitudinal_profile(longitudinal_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/timeline", response_model=List[PrescriptionSnapshotReferenceSchema], tags=["Advanced Clinical Intelligence"])
def get_longitudinal_timeline(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves resolved timeline snapshots."""
    res = service.get_longitudinal_timeline(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/persistence", response_model=List[PersistenceProfileSchema], tags=["Advanced Clinical Intelligence"])
def get_longitudinal_persistence(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves computed entity presence metrics."""
    res = service.get_longitudinal_persistence(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/emergence", response_model=List[EmergenceEventSchema], tags=["Advanced Clinical Intelligence"])
def get_longitudinal_emergence(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves theme emergence events."""
    res = service.get_longitudinal_emergence(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/disappearance", response_model=List[DisappearanceEventSchema], tags=["Advanced Clinical Intelligence"])
def get_longitudinal_disappearance(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves theme disappearance events."""
    res = service.get_longitudinal_disappearance(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/change-points", response_model=List[LongitudinalChangePointSchema], tags=["Advanced Clinical Intelligence"])
def get_longitudinal_change_points(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves transitional change-points."""
    res = service.get_longitudinal_change_points(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/structure", response_model=StructuralEvolutionProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_structural_evolution(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves structural network evolution sequences."""
    res = service.get_structural_evolution(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/signals", response_model=List[SignalEvolutionProfileSchema], tags=["Advanced Clinical Intelligence"])
def get_signal_evolution(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves signal theme evolution records."""
    res = service.get_signal_evolution(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/stability", response_model=StabilityEvolutionProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_stability_evolution(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves contextual stability trends."""
    res = service.get_stability_evolution(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/trustworthiness", response_model=TrustworthinessEvolutionProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_trustworthiness_evolution(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves Phase 12 score trends."""
    res = service.get_trustworthiness_evolution(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

@app.get("/api/v1/longitudinal/{longitudinal_id}/cross-layer", response_model=CrossLayerEvolutionProfileSchema, tags=["Advanced Clinical Intelligence"])
def get_cross_layer_evolution(longitudinal_id: str, service: PrescriptionService = Depends(get_prescription_service)):
    """Retrieves multi-layer change alignment data."""
    res = service.get_cross_layer_evolution(longitudinal_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Longitudinal analysis '{longitudinal_id}' not found."
        )
    return res

# -------------------------------------------------------------------------------------------------
# 6. Frontend Static Files Mount & SPA Catch-All
# -------------------------------------------------------------------------------------------------
frontend_dist_dir = settings.project_root / "frontend" / "dist"
if frontend_dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist_dir / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        file_path = frontend_dist_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist_dir / "index.html")

# -------------------------------------------------------------------------------------------------
# 6. Global Exception Handler
# -------------------------------------------------------------------------------------------------
@app.exception_handler(HTTPException)
def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": exc.detail}}
    )

@app.exception_handler(Exception)
def generic_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ANALYSIS_ERROR", "message": "An internal server error occurred while processing the prescription."}}
    )
