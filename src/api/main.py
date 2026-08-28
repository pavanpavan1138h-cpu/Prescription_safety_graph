"""
src/api/main.py

FastAPI Application entry point for Phase 7 Prescription Safety Platform.
Defines REST API endpoints under /api/v1 and static/SPA mounting for the Web UI.
"""

import logging
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.schemas import (
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
from api.advanced_schemas import AdvancedPrescriptionAnalysisResponse
from api.service import PrescriptionService, get_prescription_service

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

# -------------------------------------------------------------------------------------------------
# 5. Interactive Graph Visualization Endpoints
# -------------------------------------------------------------------------------------------------
from api.graph_schemas import SubgraphResponse
from api.graph_service import GraphService, get_graph_service

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
