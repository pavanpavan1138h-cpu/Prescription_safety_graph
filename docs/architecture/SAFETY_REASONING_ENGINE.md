# Phase 5 Documentation: Prescription Safety Graph Reasoning & Inference Engine

## 1. Overview & Core Mission
Phase 5 transforms the static Phase 4 Knowledge Graph into an explainable, auditable, deterministic **Prescription Safety Graph Reasoning & Inference Engine**.

The engine evaluates drug combinations across multiple independent graph channels:
1. **Direct Drug–Drug Interaction (DDI) Evidence** (DrugBank directed assertions).
2. **Combination-Specific Adverse Event Evidence** (TWOSIDES reified pair observations).
3. **Clinical Identity Context** (RxNorm concept mappings and term types).
4. **Transparent Evidence Confidence Scoring** (Identity quality + Cross-channel convergence).
5. **Full Multi-Hop Provenance Tracing** (Inference -> Rule -> Supporting Graph Edges -> Source Records).

---

## 2. Reasoning Architecture & Workflow

```text
User Drug Inputs (DrugBank ID / TWOSIDES CID / RxCUI / Name / Internal ID)
        │
        ▼
[1. Identity & Prescription Resolution]
        │
        ▼
Canonical Integrated Drug Entities (DRUG_xxxxxx)
        │
        ▼
[2. Graph Evidence Retrieval Layer]
        ├── Direct DDI Evidence (Forward & Reverse Assertions)
        ├── Combination Adverse Events (Associated Side Effect Concepts)
        └── Clinical Concept Context (RxCUI mappings)
        │
        ▼
[3. Deterministic Safety Rule Engine]
        ├── CONVERGENT_SAFETY_EVIDENCE (DDI + Combination Events)
        ├── DDI_EVIDENCE_ONLY (DrugBank assertion only)
        ├── COMBINATION_EVENT_EVIDENCE_ONLY (TWOSIDES combination only)
        └── NO_DIRECT_GRAPH_EVIDENCE (Absence of direct graph evidence)
        │
        ▼
[4. Evidence Confidence Engine]
        ├── Identity resolution reliability
        ├── Cross-channel convergence
        └── Ambiguity handling
        │
        ▼
[5. Structured Explanation & Provenance Synthesis]
        └── Graph paths, supporting edge IDs, source record IDs, and human-readable traces.
```

---

## 3. Safety Evidence Rules & Classifications

| Evidence Classification | Firing Condition | Scientific Interpretation |
| :--- | :--- | :--- |
| **`CONVERGENT_SAFETY_EVIDENCE`** | DDI present **AND** TWOSIDES combination events present. | Multiple independent graph channels corroborate the safety signal. |
| **`DDI_EVIDENCE_ONLY`** | DDI present **BUT NO** TWOSIDES combination observations. | Documented pharmacological interaction assertion present in DrugBank. |
| **`COMBINATION_EVENT_EVIDENCE_ONLY`** | TWOSIDES combination observations present **BUT NO** DrugBank DDI. | Observed combination adverse events reported in post-market surveillance (FAERS). |
| **`NO_DIRECT_GRAPH_EVIDENCE`** | Neither DDI nor TWOSIDES combination observations found. | **Explicit Guardrail**: Indicates absence of evidence in current graph, **NOT** clinical proof of safety. |

---

## 4. Evidence Confidence Methodology

Evidence confidence scores in $[0.0, 1.0]$ are computed from transparent rule contributions:
- **Identity Baseline (up to 0.40)**:
  - Both drugs confirmed integrated entities: `+0.25`
  - Ambiguous entity involved: `+0.10`
  - Both drugs resolve to RxNorm concepts: `+0.15` (one drug: `+0.08`)
- **Evidence Channel Support (up to 0.60)**:
  - Convergent evidence (DDI + TWOSIDES): `+0.60`
  - DDI evidence only: `+0.40`
  - Combination events evidence only: `+0.20` to `+0.40` (scaled by observation count)
  - No direct graph evidence: `+0.00`
- **Categorical Levels**:
  - `HIGH_EVIDENCE_CONFIDENCE`: Score $\ge 0.80$
  - `MODERATE_EVIDENCE_CONFIDENCE`: $0.50 \le \text{Score} < 0.80$
  - `LIMITED_EVIDENCE_CONFIDENCE`: Score $< 0.50$
  - `AMBIGUOUS_EVIDENCE`: Assigned if any participating entity is an ambiguous component.

---

## 5. Critical Scientific & Ethical Guardrails
1. **Evidence Strength vs. Clinical Probability**: The engine evaluates structured graph evidence strength. It does **not** predict clinical risk probabilities or harm likelihood.
2. **Association vs. Causality**: TWOSIDES adverse events are documented as combination associations in reporting systems, not proven single-drug or causal mechanisms.
3. **Absence of Evidence**: `NO_DIRECT_GRAPH_EVIDENCE` strictly denotes that no direct edge exists in the ingested databases; it must never be interpreted as clinical safety.

---

## 6. Python API Reference (`src/safety_queries.py`)

```python
from safety_queries import SafetyQueryEngine

engine = SafetyQueryEngine()

# 1. Lookup a drug by any identifier
drug = engine.lookup_drug("DB00191") # or "CID000003365", "DRUG_000045", "phentermine"

# 2. Evaluate pair safety evidence
result = engine.evaluate_pair("DRUG_000006", "DRUG_000048")
print(result.evidence_status)   # EvidenceStatus.CONVERGENT_SAFETY_EVIDENCE
print(result.confidence_level)  # ConfidenceLevel.HIGH_EVIDENCE_CONFIDENCE
print(result.confidence_score)  # 0.93

# 3. Retrieve formatted multi-hop explanation trace
explanation = engine.explain_inference(result.inference_id)
print(explanation)
```

---

## 7. Phase 5 Outputs & Validation Suite

### Outputs (`data/interim/reasoning/`)
- `safety_inference_results.csv`: Evaluated cohort pair summaries.
- `safety_inference_evidence.csv`: Granular supporting edge and record IDs.
- `safety_inference_explanations.json`: Complete structured explanation objects.
- `safety_reasoning_summary.json`: Aggregate distribution metrics.

### Validation Suite (`data/interim/validation/safety_reasoning_validation_report.json`)
- **Status**: **`PASSED`**
- Drug ID referential integrity: **PASS** (100% valid graph drug nodes).
- Rule classification consistency: **PASS** (0 rule violations).
- Confidence score bounds: **PASS** (100% in $[0.0, 1.0]$).
- Provenance completeness: **PASS** (0 positive inferences missing evidence).

---

## 8. Reproducibility Instructions
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_safety_inference.py
/opt/anaconda3/envs/prescription_graph/bin/python src/run_safety_validation.py
/opt/anaconda3/envs/prescription_graph/bin/python src/run_safety_demo.py
```
