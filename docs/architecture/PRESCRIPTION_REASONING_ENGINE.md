# Phase 6 Documentation: Multi-Drug Prescription Safety Reasoning & Clinical Reporting Engine

## 1. Overview & Core Mission
Phase 6 elevates the Prescription Safety Graph project from pairwise reasoning to an auditable, deterministic, multi-drug **Prescription Safety Reasoning & Reporting Engine**.

Given a prescription containing an arbitrary list of medication strings, Phase 6:
1. **Resolves All Identifiers**: Resolves mixed formats (Names, RxCUIs, DrugBank IDs, PubChem CIDs, Internal IDs), collapses duplicates, and flags unresolved/ambiguous items.
2. **Generates All Unique Pairs**: Produces exactly $N(N-1)/2$ canonical, unordered pairs.
3. **Executes Phase 5 Pairwise Reasoning**: Reuses the validated multi-channel knowledge graph reasoning engine.
4. **Aggregates Evidence**: Computes prescription-level metrics, evidence distributions, and drug participation involvement.
5. **Prioritizes Findings**: Deterministically ranks findings into evidence priority tiers (`CRITICAL_EVIDENCE_PRIORITY`, `HIGH_EVIDENCE_PRIORITY`, `MODERATE_EVIDENCE_PRIORITY`, `LIMITED_EVIDENCE_PRIORITY`, `NO_EVIDENCE_PRIORITY`).
6. **Stratifies Overall Prescription Evidence**: Classifies overall status (`MULTI_SIGNAL_EVIDENCE`, `CONVERGENT_EVIDENCE_PRESENT`, `SINGLE_CHANNEL_EVIDENCE_PRESENT`, `LIMITED_GRAPH_EVIDENCE`, `NO_DIRECT_GRAPH_EVIDENCE`).
7. **Synthesizes Clinical Safety Reports**: Produces machine-readable JSON reports and human-readable clinical narratives with full provenance and explicit ethical guardrails.

---

## 2. Architecture & Pipeline Flow

```text
Medication List (Arbitrary length & mixed formats)
        │
        ▼
[1. Prescription Resolver]
        ├── Resolves to canonical DRUG_xxxxxx entities
        ├── Collapses duplicate representations (e.g. "fluconazole", "CID000003365", "DRUG_000048")
        └── Isolates unresolved / ambiguous entries
        │
        ▼
Canonical Unique Drug Set (N unique drugs)
        │
        ▼
[2. Pair Generator Engine]
        └── Deterministically produces N*(N-1)/2 unique pairs (0 self-pairs, 0 duplicates)
        │
        ▼
[3. Phase 5 Pairwise Safety Engine]
        ├── Direct DDI evidence retrieval
        ├── TWOSIDES combination adverse event retrieval
        ├── RxNorm clinical concept context
        └── Evidence classification & confidence scoring
        │
        ▼
[4. Evidence Aggregator & Participation Engine]
        ├── Prescription evidence distribution
        └── Drug participation & involvement metrics
        │
        ▼
[5. Signal Prioritization & Risk Stratification]
        ├── Evidence Priority Tiers (CRITICAL -> NO_EVIDENCE)
        └── Prescription Status (MULTI_SIGNAL -> NO_DIRECT_GRAPH_EVIDENCE)
        │
        ▼
[6. Clinical Safety Report Generator]
        └── Machine-readable JSON + Formatted narrative report + Multi-hop provenance
```

---

## 3. Prioritization Hierarchy & Prescription Statuses

### Evidence Priority Tiers
- **`CRITICAL_EVIDENCE_PRIORITY`**: `CONVERGENT_SAFETY_EVIDENCE` with High Confidence ($\ge 0.80$).
- **`HIGH_EVIDENCE_PRIORITY`**: `CONVERGENT_SAFETY_EVIDENCE` with Moderate Confidence OR High-Confidence DDI assertions.
- **`MODERATE_EVIDENCE_PRIORITY`**: `DDI_EVIDENCE_ONLY` OR `COMBINATION_EVENT_EVIDENCE_ONLY` with Score $\ge 0.50$.
- **`LIMITED_EVIDENCE_PRIORITY`**: `COMBINATION_EVENT_EVIDENCE_ONLY` with low observation counts / ambiguous mappings.
- **`NO_EVIDENCE_PRIORITY`**: `NO_DIRECT_GRAPH_EVIDENCE`.

### Overall Prescription Statuses
- **`MULTI_SIGNAL_EVIDENCE`**: $\ge 2$ independent evidence-supported pairs in the prescription.
- **`CONVERGENT_EVIDENCE_PRESENT`**: At least one pair demonstrates convergent evidence (DrugBank DDI + TWOSIDES events).
- **`SINGLE_CHANNEL_EVIDENCE_PRESENT`**: Exactly one pair with DDI or combination events.
- **`LIMITED_GRAPH_EVIDENCE`**: Most pairs have no direct evidence, or unresolved inputs are present.
- **`NO_DIRECT_GRAPH_EVIDENCE`**: No evaluated pair has direct graph evidence.

---

## 4. Scientific Guardrails & Ethical Boundaries
1. **Evidence Priority $\ne$ Clinical Severity/Probability**: Prioritization reflects graph evidence depth, not patient harm probability.
2. **Absence of Evidence $\ne$ Safety**: Prescriptions with no direct graph evidence are explicitly documented as *lacking direct evidence in current graph*, never marked "safe to take".
3. **Combination Association $\ne$ Single-Drug Causality**: Preserves TWOSIDES combination reporting context without inferring single-drug causality.
4. **No LLM Fabrication**: All assertions, descriptions, and counts are grounded in the Knowledge Graph.

---

## 5. Python API Reference (`src/prescription_queries.py`)

```python
from prescription_queries import PrescriptionQueryAPI

api = PrescriptionQueryAPI()

# Analyze an entire prescription list of arbitrary length and mixed format
medications = [
    "DRUG_000048",      # Fluconazole internal ID
    "cyclosporine",     # Drug name
    "phentermine",      # Drug name
    "CID000003365"      # Fluconazole duplicate CID
]

report = api.analyze_prescription(medications, prescription_id="RX_PATIENT_101")

# Access structured data
print(f"Unique Drugs: {report.evidence_summary.unique_canonical_drugs}")
print(f"Duplicates Collapsed: {report.evidence_summary.duplicates_collapsed_count}")
print(f"Prescription Status: {report.evidence_summary.prescription_status.value}")

# Print formatted clinical narrative report
print(report.clinical_narrative_report)
```

---

## 6. Output Files (`data/interim/prescription_reasoning/`)
- `prescription_safety_reports.json`: Full JSON dumps of evaluated prescription reports.
- `prescription_pair_results.csv`: Pairwise results across all evaluated prescriptions.
- `prescription_signals.csv`: Prioritized findings and signals.
- `prescription_reasoning_summary.json`: Summary distribution metrics.
- `prescription_failures.csv`: Unresolved or failed input logs.

---

## 7. Automated Validation Suite (`src/run_prescription_validation.py`)
- **Status**: **`PASSED`**
- **Pair Formula Consistency**: **PASS** ($N(N-1)/2$ verified across all prescriptions).
- **No Duplicate Pairs**: **PASS** (0 duplicate pairs generated).
- **No Self-Pairs**: **PASS** (0 self-pairs generated).
- **Aggregation Accounting Consistency**: **PASS** (Convergent + DDI + Events + NoDirect == Analyzed Pairs).
- **Prioritization Tier Consistency**: **PASS** (100% compliant with schema).
- **Provenance Completeness**: **PASS** (100% of positive findings backed by supporting graph edge IDs).

---

## 8. Reproducibility Instructions
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_prescription_analysis.py
/opt/anaconda3/envs/prescription_graph/bin/python src/run_prescription_validation.py
/opt/anaconda3/envs/prescription_graph/bin/python src/run_prescription_demo.py
```
