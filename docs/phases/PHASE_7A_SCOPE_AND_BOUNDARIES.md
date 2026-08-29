# Phase 7.A — True Objective, Scope & Boundaries Specification

## 1. Executive Summary & Objective
Phase 7 transforms the validated research pipeline (Phases 1–6) into a production-grade, interactive **Prescription Safety Application Platform**.

The core mission of Phase 7 is:
> **Safely, reproducibly, transparently, and interactively operationalize the existing Phase 1–6 intelligence without modifying earlier frozen layers or fabricating unsupported clinical claims.**

---

## 2. Frozen Scope & System Boundaries

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                           FROZEN INTELLIGENCE CORE                             │
│                                                                                │
│  Phase 1: Dataset Engineering & Entity Integration                             │
│  Phase 2: RxNorm Clinical Enrichment                                           │
│  Phase 3: Crosswalk & Chemical Standardization                                 │
│  Phase 4: Knowledge Graph (68,223 Nodes, 4,969,811 Edges)                      │
│  Phase 5: Pairwise Graph Reasoning & Provenance Engine                         │
│  Phase 6: Multi-Drug Prescription Reasoning & Clinical Reporting Engine        │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                                       │ (Read-Only Consumption)
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                     PHASE 7 APPLICATION INTEGRATION LAYER                      │
│                                                                                │
│  [Presentation Layer]     Interactive Web Dashboard & Local Graph Visualizer   │
│  [Application API]        FastAPI Routes, Schemas, & Error Handling            │
│  [Service Layer]          Prescription, Drug Lookup, Evidence & Report Services│
│  [Explainability Layer]   Multi-hop Provenance Traces & Guardrail Notices      │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Operating Principles

1. **No Duplicated or New Medical Reasoning**:
   - The application layer does **not** invent new safety classifications, hidden scoring algorithms, or LLM-generated medical assertions.
   - All pairwise and prescription evaluations are executed via the existing `PrescriptionSafetyReasoner` and `SafetyQueryEngine`.
2. **Thin Application & Service Layer**:
   - The API layer handles input validation, request routing, report serialization, and provenance translation.
3. **Full Traceability Survives the UI**:
   - Every finding, signal, and summary visible on the dashboard remains directly linkable to underlying Knowledge Graph edge IDs, source records, and datasets.
4. **Evidence First, Recommendation Never**:
   - The platform strictly surfaces **graph-supported evidence strength**.
   - It **never** converts evidence density into clinical severity, probability of harm, dosage recommendations, or "safe to take" declarations.
5. **Preservation of Earlier Phases**:
   - Phases 1 through 6 remain 100% frozen and read-only.

---

## 4. What Phase 7 IS vs. What Phase 7 IS NOT

| Feature / Dimension | Phase 7 IS | Phase 7 IS NOT |
| :--- | :--- | :--- |
| **Reasoning Engine** | Consumes frozen Phase 5 & 6 deterministic reasoning. | ❌ Does NOT introduce new scoring models or LLM inference. |
| **Clinical Decision Making** | Surfaces graph evidence density and known literature records. | ❌ Does NOT advise patients to stop/change medications. |
| **Patient-Specific Risk** | Evaluates generalized pharmacological and surveillance data. | ❌ Does NOT predict individual patient risk (no age, weight, labs). |
| **Medical Records (EHR)** | Session-based research & demonstration query platform. | ❌ Does NOT store patient medical charts or doctor accounts. |
| **Underlying Data** | Grounded in DrugBank, TWOSIDES, and RxNorm. | ❌ Does NOT fabricate synthetic interactions or unmapped links. |

---

## 5. The Phase 7 User Journey

```text
1. Enter Medications
   [Mixed Identifiers: Names, RxCUIs, DrugBank IDs, PubChem CIDs, Internal IDs]
        │
        ▼
2. Resolution Preview
   [Explicit status: RESOLVED, AMBIGUOUS, UNRESOLVED, DUPLICATE collapsed]
        │
        ▼
3. Analyze Prescription
   [Triggers Phase 6 multi-drug engine over N*(N-1)/2 unique pairs]
        │
        ▼
4. Prescription Safety Dashboard
   [Summary metrics, overall prescription status, drug participation]
        │
        ▼
5. Explore Prioritized Findings
   [Ranked findings: CRITICAL -> HIGH -> MODERATE -> LIMITED -> NO_EVIDENCE]
        │
        ▼
6. Inspect Evidence & Subgraph
   [Direct DDI text, TWOSIDES combination events, local evidence subgraph]
        │
        ▼
7. Full Multi-Hop Provenance Trace
   [Finding -> Inference ID -> Graph Edge ID -> Source Record ID -> Dataset]
```

---

## 6. Official Phase 7 Scope Statement (Frozen)

> **Phase 7 will implement a user-facing application layer consisting of a service-oriented backend API and interactive web interface that operationalizes the existing prescription safety reasoning engine. The phase will support multi-format medication input, deterministic identity resolution, multi-drug prescription analysis, evidence-backed finding exploration, pairwise reasoning inspection, provenance tracing, and controlled local graph visualization. Phase 7 will not introduce new clinical reasoning, modify frozen Phases 1–6, infer patient-specific risk, or provide medical recommendations.**
