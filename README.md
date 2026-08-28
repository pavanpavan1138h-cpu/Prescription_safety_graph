# Prescription Safety Knowledge Graph Platform & Clinical Intelligence Engine

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Cytoscape.js](https://img.shields.io/badge/Cytoscape.js-3.28-F58220.svg)](https://js.cytoscape.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A deterministic, provenance-preserving Biomedical Knowledge Graph and Advanced Clinical Intelligence Platform. Operates over an integrated multi-source graph containing **68,223 nodes** and **4,969,811 edges** (built from DrugBank, TWOSIDES, and RxNorm) to provide structured polypharmacy safety reasoning, cross-pair adverse event convergence, evidence pattern detection, and interactive subgraph visualization.

---

## 🌟 Key Features

- **Biomedical Identity Crosswalk & Resolution Layer**: Maps heterogeneous inputs (Drug Names, DrugBank IDs, RxCUIs, PubChem/TWOSIDES CIDs) into normalized canonical Drug entities (`DRUG_xxxxxx`), collapsing duplicate representations.
- **Phase 4 Frozen Knowledge Graph**: Integrated graph containing 1,836 canonical Drugs, 1,597 RxNorm Concepts, 63,473 reified DrugPair combinations, and 1,317 SideEffect concepts across nearly 5 million DDI and observational edges.
- **Multi-Channel Pairwise Safety Inference Engine**: Classifies pair interactions into explicit evidence states:
  - `CONVERGENT_SAFETY_EVIDENCE` (DrugBank DDI assertion + TWOSIDES observational adverse events)
  - `DDI_EVIDENCE_ONLY`
  - `COMBINATION_EVENT_EVIDENCE_ONLY`
  - `NO_DIRECT_GRAPH_EVIDENCE`
- **Polypharmacy Prescription Aggregator & Risk Engine**: Evaluates $N \times (N-1) / 2$ pair combinations for multi-drug lists, calculating drug participation centrality, highest priority tiers, and clinical narrative reports.
- **Phase 7 REST API Service**: FastAPI service providing asynchronous health, entity resolution, pairwise evaluation, prescription analysis, and pair detail endpoints.
- **Phase 7.5 Query-Driven Subgraph Visualizer**: Cytoscape.js visualizer with force-directed, circular, hierarchical, and concentric layouts, controlled side-effect truncation, and complete node/edge metadata inspection.
- **Phase 8 Advanced Clinical Intelligence & Decision Support**:
  - **Prescription Complexity Profiler** (`LOW`, `MODERATE`, `HIGH`, `VERY_HIGH` complexity scores).
  - **Cross-Pair Adverse Event Convergence** (detects recurring toxicological concepts across independent drug pairs).
  - **Deterministic Pattern Detector** (`CONVERGENT_EVIDENCE_CLUSTER`, `CENTRAL_DRUG_SIGNAL_PATTERN`, `EVENT_CONVERGENCE_PATTERN`, `IDENTITY_UNCERTAINTY_PATTERN`, `LIMITED_EVIDENCE_COVERAGE`).
  - **Deterministic Review Prioritization Engine**.
  - **Structured Uncertainty & Context Requirements Model** (explicitly flags missing pharmacokinetic context like dose, eGFR, liver function, and administration timing).

---

## 📐 Architecture Overview

```text
                                CANONICAL BIOMEDICAL SOURCES
                          (DrugBank + TWOSIDES + RxNorm Standard)
                                             │
                                             ▼
                                PHASE 1-3 NORMALIZATION & ID CROSSWALK
                                             │
                                             ▼
                                PHASE 4 FROZEN KNOWLEDGE GRAPH
                       (68,223 Nodes | 4,969,811 Directed & Reified Edges)
                                             │
                                             ▼
                             PHASE 5 PAIRWISE EVIDENCE INFERENCE
                                             │
                                             ▼
                          PHASE 6 MULTI-DRUG PRESCRIPTION REASONER
                                             │
                                             ▼
                       PHASE 8 ADVANCED CLINICAL INTELLIGENCE ENGINES
          (Complexity + Participation + Event Convergence + Patterns + Priorities)
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             FastAPI REST SERVICE                         REACT + CYTOSCAPE.JS UI
          (/api/v1/prescriptions/analyze-advanced)     (Interactive Visualizer & Dashboard)
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python**: 3.10+ (Python 3.12 recommended)
- **Node.js**: 18+ and `npm`

### 1. Clone Repository & Setup Environment

```bash
git clone https://github.com/your-org/Prescription_safety_graph.git
cd Prescription_safety_graph

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Frontend Dependencies Setup

```bash
cd frontend
npm install
cd ..
```

---

## 🏃 Running the Application

### Option A: Running Backend & Frontend Dev Servers (Recommended for Development)

```bash
# Terminal 1: Launch FastAPI REST Server
PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch Vite React Frontend
cd frontend
npm run dev
```

- **Interactive Dashboard**: Navigate to `http://localhost:5173`
- **Swagger API Documentation**: Navigate to `http://localhost:8000/docs`

### Option B: Production Single-Service Build

```bash
# Build production React frontend bundle
cd frontend
npm run build
cd ..

# Run FastAPI serving both REST endpoints and bundled static Web UI
PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000` in your web browser.

---

## 🧪 Testing & Validation

Run the complete test suite (17/17 tests passing):

```bash
# Execute Pytest suite
PYTHONPATH=src pytest tests/ -v

# Run Phase 8 Advanced Intelligence Validation Suite
PYTHONPATH=src python src/run_advanced_intelligence_validation.py

# Run API Validation Suite
PYTHONPATH=src python src/run_api_validation.py

# Run End-to-End Advanced Intelligence Demo
PYTHONPATH=src python src/run_advanced_intelligence_demo.py
```

---

## 📂 Repository Directory Structure

```text
Prescription_safety_graph/
├── api/                           # FastAPI API route modules
├── data/
│   ├── interim/                   # Processed crosswalks, graph indexes, & validation reports
│   └── raw/                       # Raw dataset files (DrugBank, TWOSIDES, RxNorm)
├── docs/                          # Comprehensive phase documentation (Phases 1-8)
├── frontend/                      # React + TypeScript + Vite + Cytoscape Web Dashboard
│   ├── src/
│   │   ├── api/                   # API fetch clients
│   │   ├── components/            # InteractiveGraph visualizer component
│   │   ├── App.tsx                # Clinical Intelligence Dashboard UI
│   │   └── index.css              # Glassmorphic Design System
│   ├── package.json
│   └── vite.config.ts
├── src/                           # Core Python Reasoning & Intelligence Source Code
│   ├── advanced_intelligence_engines.py # Phase 8 Analytical Engines
│   ├── advanced_intelligence_schema.py  # Phase 8 Data Schemas & Enums
│   ├── advanced_intelligence_service.py # Phase 8 Orchestrator
│   ├── advanced_intelligence_validation.py # Phase 8 Validation
│   ├── clinical_report_generator.py # Clinical narrative generator
│   ├── confidence_engine.py       # Deterministic scoring logic
│   ├── crosswalk.py               # Biomedical ID mapper
│   ├── evidence_retrieval.py       # High-speed Phase 4 graph retriever
│   ├── graph_builder.py           # Knowledge Graph constructor
│   ├── prescription_reasoning.py   # Multi-drug polypharmacy reasoner
│   ├── prescription_resolver.py    # Identity resolver & duplicate collapser
│   ├── safety_queries.py          # Safety query engine
│   └── safety_rules.py            # Phase 5 inference rules
├── tests/                         # Pytest automated test suites
├── requirements.txt               # Python package dependencies
├── README.md                      # Project documentation
└── .gitignore                     # Git exclusion rules
```

---

## 🛡️ Scientific Safety Guardrails & Disclaimers

1. **Non-Diagnostic & Non-Prescriptive**: This platform is an evidence-grounded decision support tool designed for research and clinical evidence exploration. It does NOT diagnose patients, prescribe medication, or replace licensed clinical judgment.
2. **Graph Density $\ne$ Clinical Severity**: Review priorities and confidence scores reflect the density and channel convergence of evidence in the underlying knowledge graph, NOT patient-specific clinical severity or probability of harm.
3. **Observational Surveillance $\ne$ Causality**: Adverse event co-occurrence data from TWOSIDES reflect spontaneous pharmacovigilance reports and do not independently establish biological mechanism or causality.
4. **Absence of Evidence $\ne$ Safety**: The absence of an interaction edge or adverse event record in the frozen knowledge graph does NOT prove clinical safety.
5. **Out-of-Graph Parameters**: Patient-specific pharmacokinetic evaluation requires parameters outside the scope of this graph (e.g., dosage, administration timing, renal eGFR, hepatic clearance, and patient comorbidities).

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
