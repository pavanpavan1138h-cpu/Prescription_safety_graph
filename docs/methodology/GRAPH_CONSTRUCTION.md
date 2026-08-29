# Phase 4 Documentation: Prescription Safety Knowledge Graph Construction & Validation

## 1. Executive Summary & Objective
Phase 4 formally constructs the **Prescription Safety Knowledge Graph**, transitioning all validated Phase 1 dataset entities, Phase 2 RxNorm clinical enrichments, and interaction/safety evidence into a canonical, provenance-aware graph representation.

- **Total Canonical Graph Nodes**: **68,223**
- **Total Canonical Graph Edges**: **4,969,811**
- **Graph Validation Status**: **`PASSED`** (100% referential integrity, 0 dangling endpoints, 0 duplicate keys)
- **Source Accounting Reconciliation**: **100% complete** across DrugBank (191,808 interactions), TWOSIDES (4,649,441 side effect associations across 63,473 drug pairs), and RxNorm (1,616 clinical mappings).

---

## 2. Frozen Graph Ontology & Node Types

| Node Type | Count | Identifier Syntax | Description |
| :--- | :--- | :--- | :--- |
| **`Drug`** | 1,836 | `DRUG_xxxxxx` | Canonical integrated drug entity (100% Phase 1 entity preservation). |
| **`RxNormConcept`** | 1,597 | `RXCUI_{rxcui}` | Standardized clinical concept node from RxNorm. |
| **`DrugPair`** | 63,473 | `PAIR_{d1}__{d2}` | Reified drug combination safety observation node (deterministic sorted ordering). |
| **`SideEffect`** | 1,317 | `SE_{side_effect_id}` | Standardized adverse event concept from TWOSIDES. |
| **Total Nodes** | **68,223** | | |

---

## 3. Relationship Types & Provenance Model

| Relationship Type | Count | Directed | Source Node | Target Node | Provenance & Evidence Model |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`HAS_RXNORM_CONCEPT`** | 1,616 | Yes | `Drug` | `RxNormConcept` | Captures mapping method, match score, and clinical confidence. |
| **`INTERACTS_WITH`** | 191,808 | Yes | `Drug` | `Drug` | Directed DDI assertion from DrugBank with textual interaction descriptions. |
| **`MEMBER_OF_PAIR`** | 126,946 | Yes | `Drug` | `DrugPair` | Exactly 2 membership edges per `DrugPair` preserving combination context. |
| **`ASSOCIATED_WITH`** | 4,649,441 | Yes | `DrugPair` | `SideEffect` | Links combination observations to adverse events. |
| **Total Edges** | **4,969,811** | | | | |

---

## 4. TWOSIDES DrugPair Reification & Safety Semantics
TWOSIDES adverse drug reactions represent **combination safety observations** rather than isolated single-drug causality. To maintain scientific fidelity, Phase 4 models combinations as first-class `DrugPair` nodes:

```
[Drug A] --(MEMBER_OF_PAIR)--> [DrugPair] <--(MEMBER_OF_PAIR)-- [Drug B]
                                    │
                              (ASSOCIATED_WITH)
                                    ▼
                              [SideEffect]
```

- **63,473** unique drug combinations tested in TWOSIDES are represented.
- Every `DrugPair` node connects to exactly two `Drug` nodes via `MEMBER_OF_PAIR`.
- Individual single drugs are not falsely asserted to cause side effects observed exclusively in combination therapy.

---

## 5. Source Reconciliation & Validation Accounting
Automated validation generated under `data/interim/validation/graph_source_accounting.json`:
1. **DrugBank**:
   - Raw normalized interactions: 191,808
   - Mapped `INTERACTS_WITH` edges: 191,808
   - Unmapped/excluded records: 0
2. **TWOSIDES**:
   - Raw normalized relationships: 4,649,441
   - Unique drug pairs: 63,473
   - Mapped `MEMBER_OF_PAIR` edges: 126,946 (63,473 × 2)
   - Mapped `ASSOCIATED_WITH` edges: 4,649,441
   - Unmapped/excluded records: 0
3. **RxNorm**:
   - Resolved clinical mappings: 1,616
   - Unique `RxNormConcept` nodes: 1,597
   - Mapped `HAS_RXNORM_CONCEPT` edges: 1,616
   - Unmapped/excluded records: 0

---

## 6. Graph Artifacts & File Structure

### Canonical Graph Layer (`data/interim/graph/`)
- `graph_nodes.csv`: Canonical node table (68,223 rows).
- `graph_edges.csv`: Canonical edge table (4,969,811 rows).
- `graph_schema.json`: Machine-readable schema definitions.
- `graph_build_summary.json`: Build statistics and distributions.

### Relationship-Specific CSV Exports
- `drug_rxnorm_edges.csv`: All 1,616 clinical mapping edges.
- `drug_interaction_edges.csv`: All 191,808 directed DDI edges.
- `drug_pair_nodes.csv`: All 63,473 reified drug pair nodes.
- `drug_pair_membership_edges.csv`: All 126,946 pair membership edges.
- `drug_pair_side_effect_edges.csv`: All 4,649,441 adverse event edges.

### Validation Reports (`data/interim/validation/`)
- `graph_validation_report.json`: Full validation suite report (`status: PASSED`).
- `graph_source_accounting.json`: Source reconciliation report.
- `graph_anomalies.csv`: Graph anomaly register (0 records).
- `graph_unmapped_relationships.csv`: Unmapped relationships register (0 records).

---

## 7. Query Engine & Retrieval Demonstration
The retrieval layer in `src/graph_queries.py` and demonstration in `src/run_graph_demo.py` verify that the graph supports multi-hop clinical and safety retrieval:
1. **Source identifier lookup** (`DB00191` -> `DRUG_000045`).
2. **Clinical concept retrieval** (`DRUG_000001` -> `RXCUI_60819`).
3. **Direct DDI evidence retrieval** (`DRUG_001202` + `DRUG_000302` -> directed interaction text).
4. **Drug-pair side effect retrieval** (`DRUG_000045` + `DRUG_000048` -> 75 adverse event associations).
5. **Full provenance tracing** (Edge ID -> Source Dataset -> Original Record ID -> Confidence).

---

## 8. Reproducibility Instructions
To build and validate the entire graph from scratch:
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_graph_build.py
/opt/anaconda3/envs/prescription_graph/bin/python src/run_graph_validation.py
/opt/anaconda3/envs/prescription_graph/bin/python src/run_graph_demo.py
```
