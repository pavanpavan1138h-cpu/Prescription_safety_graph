# Phase 7.F — Validation, Testing, Security & Deployment Architecture

## 1. Executive Summary & Validation Invariant
Phase 7.F defines the complete testing, security, regression, performance benchmarking, and deployment architecture for the **Prescription Safety Application Platform**.

### Core Validation Invariant:
> **The API and UI layers must strictly preserve the scientific reasoning, evidence classification, priority ranking, and confidence scores established by the frozen Phase 5 & 6 core. Zero drift, reinterpretation, or hallucinated clinical claims are permitted.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 7 VALIDATION SUITE                             │
│                                                                                │
│  [1. API Contract Tests]        Pydantic Schemas, HTTP Codes, Type Integrity   │
│  [2. Reasoning Regression]     Direct Phase 6 Output == API Response JSON      │
│  [3. Safety Regression]        No-Evidence != Safe, Associations != Causality   │
│  [4. Frontend Integration]     E2E User Journeys, Resolution, Drill-downs      │
│  [5. Performance Benchmarks]   Sub-100ms warm responses, Timing instrumentation│
│  [6. Deployment Health]        /health (liveness) and /ready (engine readiness)│
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Four-Layer Testing Architecture

### Layer 1: API Contract & Schema Testing
- Validates all request/response models against OpenAPI / Pydantic schemas.
- Ensures all mandatory sections (`metadata`, `input_summary`, `resolution_summary`, `prescription_summary`, `prioritized_findings`, `pair_results`, `drug_participation`, `unresolved_items`, `limitations`, `provenance`) are present.
- Enforces strict enum integrity (`CONVERGENT_SAFETY_EVIDENCE`, `CRITICAL_EVIDENCE_PRIORITY`, etc.).

### Layer 2: Scientific Reasoning Preservation (Regression Invariant)
- Executes identical test prescriptions through both direct `PrescriptionSafetyReasoner` calls and HTTP API calls.
- **Assertion**:
  $$\text{API Response}(\text{Rx}) \equiv \text{Phase 6 Engine Output}(\text{Rx})$$
  (Drug IDs, Pair counts, Evidence Status, Priority Tiers, Confidence Scores, and Supporting Edge IDs must match 100%).

### Layer 3: Safety Regression & Guardrail Tests
- **Rule 1 (No Evidence $\ne$ Safe)**: Verifies that `NO_DIRECT_GRAPH_EVIDENCE` responses always carry the explicit disclaimer: *"absence of evidence in current graph is not confirmation of clinical safety"*.
- **Rule 2 (Priority $\ne$ Severity)**: Verifies that `CRITICAL_EVIDENCE_PRIORITY` is never converted to a patient risk probability or clinical severity score.
- **Rule 3 (Associations $\ne$ Causality)**: Verifies that TWOSIDES combination events are described as *observed associations*, never *causal side effects*.
- **Rule 4 (Unresolved Item Visibility)**: Verifies that unmapped drugs (`NonExistentXYZ`) remain explicitly visible in `unresolved_items` and are never silently discarded.

### Layer 4: Performance & Concurrency Benchmarks
- Validates that startup indexing happens strictly once.
- Benchmarks warm request execution for 2, 5, 10, and 20 medications.
- Output generated to `data/interim/api_validation/api_performance_report.json`.

---

## 3. Security, Input Limits & Configuration Architecture

### Operational Constraints:
- **`MAX_MEDICATIONS`**: 20 submitted medications ($190$ maximum unique pairs). Submissions $> 20$ return `400 MEDICATION_LIMIT_EXCEEDED`.
- **`MAX_INPUT_STRING_LENGTH`**: 250 characters per medication string.
- **Error Sanitization**: Server exceptions return standardized envelopes (`INTERNAL_ANALYSIS_ERROR`) with traceable `request_id`. Zero stack traces or internal filesystem paths are leaked.

### CORS & Environment Configuration (`.env.example`):
```ini
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

CORS_ORIGINS=http://localhost:5173,http://localhost:3000

MAX_MEDICATIONS=20
GRAPH_DATA_DIR=data/interim/graph
REASONING_DATA_DIR=data/interim/prescription_reasoning

API_TITLE=Prescription Safety Graph Reasoning API
API_VERSION=v1.0.0
```

---

## 4. Containerization & Deployment Layout

### Dockerfile Layout:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/interim/graph/ ./data/interim/graph/
COPY data/interim/reasoning/ ./data/interim/reasoning/
COPY data/interim/prescription_reasoning/ ./data/interim/prescription_reasoning/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 5. Required Phase 7 Artifacts & Validation Reports

### Validation Directory (`data/interim/api_validation/`):
- `api_contract_validation_report.json`: OpenAPI schema compliance results.
- `reasoning_regression_report.json`: Direct engine vs API comparison results.
- `api_performance_report.json`: Latency metrics across prescription sizes.
- `safety_regression_report.json`: Guardrail and ethical notice enforcement.
- `phase7_validation_summary.json`: Overall phase closure report.

### Documentation Files (`docs/`):
- `docs/PHASE_7A_SCOPE_AND_BOUNDARIES.md` (Scope & User Journey)
- `docs/PHASE_7B_API_CONTRACT.md` (REST Endpoint Hierarchy)
- `docs/PHASE_7C_PERFORMANCE_ARCHITECTURE.md` (Startup Lifecycle & In-Memory Indexes)
- `docs/PHASE_7D_API_RESPONSE_CONTRACT.md` (Pydantic Schemas & Error Envelopes)
- `docs/PHASE_7E_UI_DASHBOARD_ARCHITECTURE.md` (Frontend Components & User Experience)
- `docs/PHASE_7F_VALIDATION_AND_DEPLOYMENT.md` (Testing, Security & Docker Layout)
