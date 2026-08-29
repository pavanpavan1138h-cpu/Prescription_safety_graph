# Phase 7 — Prescription Safety Application Platform Documentation

## 1. System Overview & Architecture
Phase 7 operationalizes the **Prescription Safety Knowledge Graph** and multi-drug reasoning core into an interactive, reproducible, and verifiable web application platform.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   INTERACTIVE WEB DASHBOARD (React + Vite)             │
│                                                                        │
│   - Multi-format medication input (Names, RxCUIs, DB IDs, CIDs)        │
│   - Live duplicate collapsing & unresolved entity isolation            │
│   - Prioritized finding cards & interactive pair explorer table        │
│   - Granular pair drilldown modal & multi-hop provenance visualizer    │
│   - Formatted clinical safety narrative text inspector                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   FASTAPI REST SERVICE LAYER (/api/v1)                 │
│                                                                        │
│   GET  /health                                                         │
│   GET  /api/v1/system/info                                             │
│   POST /api/v1/drugs/resolve                                           │
│   GET  /api/v1/drugs/{identifier}                                      │
│   POST /api/v1/safety/pair                                             │
│   POST /api/v1/prescriptions/analyze                                  │
│   GET  /api/v1/analyses/{analysis_id}/pairs/{pair_id}                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Service Adapter)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               FROZEN SCIENTIFIC REASONING CORE (Phases 1–6)            │
│                                                                        │
│   PrescriptionSafetyReasoner  ->  SafetyQueryEngine                    │
│   - 68,223 Nodes (Drug, RxNormConcept, DrugPair, SideEffect)           │
│   - 4,969,811 Edges (HAS_RXNORM, INTERACTS_WITH, ASSOCIATED_WITH)      │
│   - In-memory index loaded once at startup for sub-50ms query latency  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Running the Application Locally

### A. Start the Backend API Server
```bash
cd /Users/apple/Documents/SIH2026/Prescription_safety_graph
PYTHONPATH=src /opt/anaconda3/envs/prescription_graph/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/health`
- System Info: `http://localhost:8000/api/v1/system/info`

### B. Start the Frontend Development Server
```bash
cd /Users/apple/Documents/SIH2026/Prescription_safety_graph/frontend
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

## 3. Running Automated Tests & Validation

### Run Full Pytest Suite (9 Tests Passed)
```bash
cd /Users/apple/Documents/SIH2026/Prescription_safety_graph
PYTHONPATH=src /opt/anaconda3/envs/prescription_graph/bin/pytest tests/test_api_endpoints.py -v
```

### Run API Validation Suite
```bash
cd /Users/apple/Documents/SIH2026/Prescription_safety_graph
/opt/anaconda3/envs/prescription_graph/bin/python src/run_api_validation.py
```
Validation report written to `data/interim/validation/api_contract_validation_report.json`.

### Run End-to-End Platform Demonstration (7 Scenarios)
```bash
cd /Users/apple/Documents/SIH2026/Prescription_safety_graph
/opt/anaconda3/envs/prescription_graph/bin/python src/run_platform_demo.py
```

---

## 4. Key Scientific Guardrails Preserved
1. **Evidence Priority $\ne$ Clinical Severity**: `CRITICAL_EVIDENCE_PRIORITY` denotes multi-channel convergent graph evidence (DrugBank DDI + TWOSIDES events), not a medical severity rating.
2. **Absence of Evidence $\ne$ Safety**: `NO_DIRECT_GRAPH_EVIDENCE` strictly indicates that the current knowledge graph does not contain direct edges for the pair.
3. **Observational Associations $\ne$ Causality**: TWOSIDES combination events are described strictly as *observed associations* from post-marketing surveillance.
4. **Transparent Resolution**: Duplicate medication inputs collapse transparently into canonical entities, and unmapped items are isolated into `unresolved_items` without crashing the analysis.
