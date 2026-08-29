# 💊 Prescription Safety Knowledge Graph Platform & Clinical Intelligence Engine

A deterministic, provenance-preserving Biomedical Knowledge Graph and Advanced Clinical Intelligence Platform. Operates over an integrated multi-source graph containing **68,223 nodes** and **4,969,811 edges** (built from DrugBank, TWOSIDES, and RxNorm) to provide structured polypharmacy safety reasoning, cross-pair adverse event convergence, evidence pattern detection, interactive subgraph visualization, reverse explainability lineage tracing, computational robustness scoring, and longitudinal evolution tracking.

---

## 🌟 1. Project Identity
The **Prescription Safety Graph** is a flagship biomedical informatics platform designed to trace, evaluate, and visualize safety signals across polypharmacy prescriptions. Unlike stochastic black-box AI models, this platform employs a multi-layered deterministic reasoning engine grounded in a large-scale frozen knowledge graph compiled from curated pharmaceutical, chemical, and pharmacovigilance databases.

---

## ⚠️ 2. The Problem
Polypharmacy—the simultaneous administration of multiple medications—is a leading cause of Adverse Drug Events (ADEs) and preventable hospitalization. Detecting drug-drug interactions (DDIs) is exceptionally challenging because:
* **Heterogeneous Biomedical Identifiers**: Clinicians, pharmacies, and databases use disparate terminologies (e.g., brand names, generic names, RxCUIs, DrugBank IDs, PubChem/TWOSIDES CIDs), causing fragmented tracking.
* **Complex Polypharmacy Networks**: A prescription with $N$ medications contains $N(N-1)/2$ potential pairwise interactions. The safety profile is not just the sum of its parts; it is a complex structural network.
* **Evidence Dispersion**: High-fidelity clinical assertions (e.g., FDA labels from DrugBank) and observational surveillance signals (spontaneous reports in TWOSIDES) exist in silos.

---

## 🔍 3. Why Existing Approaches Are Limited
1. **Siloed Databases**: Most DDI lookup tools check a single source, missing the synergy between structured regulatory labels and real-world post-market surveillance.
2. **Lack of Explainability**: Modern deep learning models can predict DDIs but fail to provide a machine-readable, audit-ready computational trail explaining *why* a conclusion was reached.
3. **No Robustness Benchmarking**: Predictions are rarely evaluated for computational stability under minor input perturbations, duplicate identity claims, or contextual shifts.
4. **Static Analysis**: Existing systems analyze a prescription as a single static snapshot, failing to track how safety interpretations evolve over the longitudinal timeline of a patient's prescription history.

---

## 💡 4. Our Core Idea
We construct a unified **Biomedical Identity Crosswalk & Resolution Layer** to collapse duplicate representations into canonical Drug entities (`DRUG_xxxxxx`). On top of this clean graph foundation, we layer:
1. **Evidence Channel Convergence**: Checking regulatory assertions alongside real-world spontaneous reports.
2. **Context-Aware Structural Intelligence**: Evaluating network centrality and topological properties of the drug interaction graph.
3. **Reverse Proof Lineage & Explanations**: Tracking every conclusion back to explicit mathematical and structural operations.
4. **Computational Trustworthiness Metrics**: Benchmarking reproducibility and stability.
5. **Deterministic Longitudinal Progression**: Synthesizing timeline transitions across prescription changes without clinical inference.

---

## 📐 5. Complete System Architecture

```text
                                CANONICAL BIOMEDICAL SOURCES
                           (DrugBank + TWOSIDES + RxNorm Standard)
                                              │
                                              ▼
                                 IDENTITY RESOLUTION CROSSWALK
                                              │
                                              ▼
                                 PHASE 4 FROZEN KNOWLEDGE GRAPH
                        (68,223 Nodes | 4,969,811 Directed & Reified Edges)
                                              │
                                              ▼
                              PHASE 5-6 PAIRWISE EVIDENCE INFERENCE
                                              │
                                              ▼
                            PHASE 8 MULTI-DRUG PRESCRIPTION REASONER
                                              │
                             ┌────────────────┴────────────────┐
                             ▼                                 ▼
                     PHASE 9 EVIDENCE                  PHASE 10 CONTEXTUAL
                        SYNTHESIS                          STABILITY
                             │                                 │
                             └────────────────┬────────────────┘
                                              ▼
                                 PHASE 11 PROVENANCE EXPLAINER
                                              │
                                              ▼
                                 PHASE 12 COMPUTATIONAL TRUST
                                              │
                                              ▼
                                PHASE 13 LONGITUDINAL TIMELINE
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
             FastAPI REST SERVICE                           REACT + CYTOSCAPE.JS UI
          (/api/v1/prescriptions/*)                     (Evolution Lab Dashboard & Subgraph)
```

---

## 🧬 6. Intelligence Pipeline
The system operates as an immutable pipeline. Raw drug listings are resolved, mapped to the knowledge graph, and evaluated across consecutive layers:
1. **Resolution & Crosswalk**: collates duplicate inputs, resolving them to canonical DrugBank IDs.
2. **Retrieval**: Pulls reified relationship subgraphs from Zarr/Pandas indexes.
3. **Pairwise & Structural Inference**: Extracts interaction edges and computes topological centrality.
4. **Adverse Event Convergence**: Groups shared side effects to highlight systemic risks.
5. **Contextual Sensitivity Perturbation**: Simulates noise to measure interpretative resilience.
6. **Provenance Compilation**: Tracks the JSON execution tree.
7. **Trust Evaluation**: Scores cross-layer consistency and perturbation resistance.
8. **Longitudinal Alignment**: Compares consecutive prescription states, computing persistence ratios.

---

## 🗓️ 7. Phase-by-Phase Capabilities
* **Phases 1–3: Extraction & Crosswalk**: Extracted structured records; resolved synonym aliases to unique canonical drugs.
* **Phase 4: Unified Knowledge Graph**: Assembled 68,223 nodes and 4,969,811 edges into binary storage formats for high-speed sub-millisecond retrieval.
* **Phase 5: Pairwise Safety Inference**: Applied deterministic rules mapping pairs to four categories of graph evidence.
* **Phase 6: Multi-Drug Prescription Aggregator**: Evaluates network structures, computing drug participation levels and clinical narratives.
* **Phase 7: REST API & Cytoscape visualizer**: Served async endpoints and rendered query-driven interactive subgraphs.
* **Phase 8: Advanced Structural & Signal Intelligence**: Integrated Complexity category levels, convergence detection, and review priority tiers.
* **Phase 9: Signal Synthesis & Theme Detection**: Identifies toxicological themes reinforcing across multiple pairs.
* **Phase 10: Contextual Stability & Perturbation**: Simulates dose/comorbidity variations to flag context-sensitive edges.
* **Phase 11: Traceability & Explainability**: Exposes structured JSON lineage trees matching conclusions to input nodes.
* **Phase 12: Robustness & Computational Trustworthiness**: Computes reproducibility and consistency indexes (0.0 to 1.0).
* **Phase 13: Longitudinal Evolution & Change Intelligence**: Tracks persistence ratios, emergences, disappearances, and change points over multiple chronological snapshots.

---

## 💻 8. Technology Stack
* **Backend**: Python 3.12, FastAPI, Pydantic, Pytest, Uvicorn, Pandas, NetworkX.
* **Frontend**: React 18, TypeScript, Vite, Cytoscape.js, Lucide React.
* **Styling**: Vanilla CSS (TailwindCSS avoided for absolute control), CSS Variables, Glassmorphism design system.

---

## 📂 9. Repository Directory Structure
```text
Prescription_safety_graph/
│
├── src/                        # Core backend source code
│   ├── api/                    # FastAPI routes & Pydantic schemas
│   ├── core/                   # Global configuration & environment settings
│   ├── data/                   # Data loader, dictionary & database interfaces
│   ├── graph/                  # Graph builders & network construction
│   ├── prescription/           # Polypharmacy aggregators, resolvers, and intelligence modules
│   │   ├── advanced/           # Complexity, event convergence & priority engines (Phases 8-10)
│   │   ├── explainability/     # Traceability, explainability, & JSON lineages (Phase 11)
│   │   ├── trustworthiness/    # Robustness, perturbation, & scoring engines (Phase 12)
│   │   └── longitudinal/       # Persistence, change-points, & timelines (Phase 13)
│   ├── reasoning/              # Pairwise rule engines
│   └── runners/                # Command-line validation and validation runners
│
├── frontend/                   # React + TSX + Vite Frontend Application
│   ├── dist/                   # Bundled production static application files
│   └── src/
│       ├── api/                # API fetch clients
│       ├── components/         # Interactive Cytoscape graphs and analytical tab layouts
│       └── types/              # TypeScript API type schemas
│
├── tests/                      # Pytest automated test suites
├── data/                       # Required datasets (local interim database caches)
├── docs/                       # Organized architectural documents categorized in subdirectories
│   ├── api/
│   ├── architecture/
│   ├── evaluation/
│   ├── methodology/
│   ├── phases/
│   └── safety/
│
├── outputs/                    # Output logs, reports and screenshots
│   ├── validation/             # Validation runner outputs for phases 11-13
│   ├── examples/               # Output JSON report examples
│   └── screenshots/
│
├── references/                 # Source citations, methodology reference papers, and data dictionaries
├── examples/                   # Input files and expected outputs
│
├── README.md                   # Master flagship documentation
├── LICENSE
├── requirements.txt            # Python environment dependencies
└── .gitignore                  # Git tracking rules
```

---

## ⚙️ 10. Installation
### 1. Configure Python Environment
```bash
# Verify Python version (3.12 recommended)
python3 --version

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Node.js Environment
```bash
cd frontend
npm install
cd ..
```

---

## 🏃 11. Running the Backend
```bash
# Start backend FastAPI app on port 8000
PYTHONPATH=. python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger UI docs are automatically available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 12. Running the Frontend
```bash
# Start Dev server
cd frontend
npm run dev
```
Open your browser at: [http://localhost:5173](http://localhost:5173)

To build static production assets served directly by FastAPI:
```bash
cd frontend
npm run build
cd ..
PYTHONPATH=. python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

---

## 📡 13. API Overview
Key advanced intelligence endpoints:
* `POST /api/v1/prescriptions/analyze-advanced`: Triggers detailed multi-drug analysis including structural patterns, contextual requirements, and prior reviews.
* `GET /api/v1/analyses/{analysis_id}/explainability`: Fetches explanation lineage nodes and rules fired.
* `GET /api/v1/analyses/{analysis_id}/trustworthiness`: Returns consistency metrics, perturbation results, and weighted reliability scores.
* `POST /api/v1/analyses/longitudinal`: Compiles a historical tracking index over a sequence of analysis IDs.
* `GET /api/v1/longitudinal/{longitudinal_id}`: Retrieves complete longitudinal timeline evolutions, persistences, and change points.

---

## 📑 14. Example Workflow
To simulate the complete pipeline:
1. POST an analysis of baseline medication list (`cyclosporine`, `fluconazole`):
   ```json
   { "medications": ["cyclosporine", "fluconazole"] }
   ```
2. POST a modified medication list adding a drug (`cyclosporine`, `fluconazole`, `phentermine`).
3. POST a third list removing a drug (`cyclosporine`, `phentermine`).
4. Trigger longitudinal evaluation over the three generated IDs:
   ```json
   { "analysis_ids": ["RX_REPORT_1", "RX_REPORT_2", "RX_REPORT_3"] }
   ```
5. Inspect persistence runs, emerged signals (e.g. `phentermine` side effects emerging at Snapshot #2), and disappeared edges at Snapshot #3.

---

## 🧪 15. Validation & Testing
We enforce comprehensive test coverage (33 unit/integration tests).
```bash
# Run pytest test suite
PYTHONPATH=. pytest tests/ -v

# Run Phase 13 Longitudinal Validation runner
PYTHONPATH=. python src/runners/prescription/run_longitudinal_validation.py
```

---

## 🛡️ 16. Safety & Clinical Guardrails
1. **No Diagnostic Outcomes**: This platform does not predict patient diagnostic outcomes, medical deterioration, efficacy, or therapeutic superiority.
2. **Computational Scale**: review priority scores and trustworthiness markers indicate graph evidence density, not clinical severity.
3. **Context Sensitivity**: Unresolved items (missing Renal clearance, eGFR, dose concentration) are systematically flagged to prevent over-reliance on raw interaction links.
4. **Longitudinal Disclaimer**:
   > *"This longitudinal evaluation describes how the computational analytical profile changes across available prescription snapshots. It does not establish clinical progression, patient improvement or deterioration, medication efficacy, therapeutic superiority, patient safety, or medical correctness, and it does not recommend adding, removing, discontinuing, substituting, or modifying medication therapy."*

---

## 📚 17. Data / Knowledge Sources
* **DrugBank**: FDA-approved regulatory drug-drug interaction linkages.
* **TWOSIDES**: Spontaneous adverse event reports tracking synergistic combination signals.
* **RxNorm**: Standardized clinical drug names, concept mapping, and semantic relation graphs.

---

## 📈 18. Current Status
* **Core Engines (Phases 1-13)**: 100% complete and fully verified.
* **API Endpoints**: 100% integrated.
* **Web UI Panels**: Fully mounted and validated under static build compilation.
* **Test Coverage**: All 33 tests passing with 0 errors.

---

## ⚠️ 19. Limitations
* **Local In-Memory Cache**: Snapshot timeline resolutions depend on active FastAPI cache records. In production environments, this requires mounting a Redis persistent state layer.
* **Observational Density Bias**: Spontaneously reported side effects are prone to reporting bias, requiring cross-referencing with clinical trials.

---

## 🔮 20. Future Work
1. **Entity-Relation Resolution Expansion**: Adding mappings for ATC codes and SNOMED-CT clinical terms.
2. **Active Patient Records Integration**: Consuming HL7 FHIR electronic health record (EHR) prescription streams to automate timeline snapshot generation.
3. **Graph Neural Network (GNN) Embeddings**: Incorporating latent vector representations to predict potential unlogged linkages alongside our strict deterministic rules.

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for details.
