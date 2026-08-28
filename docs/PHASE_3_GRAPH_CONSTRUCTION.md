# Phase 3 Documentation: Prescription Safety Knowledge Graph Construction

## 1. Overview and Graph Design
Phase 3 builds the first unified, provenance-aware graph representation for the **Prescription Safety Graph**, bridging chemical structures, source database identifiers, standardized clinical identifiers (RxNorm RxCUIs), drug-drug interaction pairs, and drug-combination adverse safety observations.

The graph design enforces clean separation of concerns:
- **Entity Identity (`INTEGRATED_DRUG`)**: Internal project entities resulting from Phase 1 chemical crosswalk and structure integration.
- **Source Identity (`SOURCE_DRUG_IDENTIFIER`)**: Raw source database records (`DBxxxx`, `CIDxxxx`).
- **Clinical Identity (`RXNORM_CONCEPT`)**: Verified clinical concepts mapped during Phase 2.
- **Side Effect Concepts (`SIDE_EFFECT`)**: Standardized adverse reaction concepts from TWOSIDES.
- **Pair Safety Observations (`DRUG_PAIR_OBSERVATION`)**: N-ary combination observation nodes preserving drug-pair context.

---

## 2. Node Schema & Node Types

| Node Type | Count | Description | Primary ID / Source |
| :--- | :--- | :--- | :--- |
| **`INTEGRATED_DRUG`** | 1,836 | Internal integrated drug entity (Phase 1) | `internal_drug_id` (e.g. `DRUG_000001`) |
| **`SOURCE_DRUG_IDENTIFIER`** | 2,351 | Source-level identifier from DrugBank / TWOSIDES | `SRC:{DATASET}:{ID}` (e.g. `SRC:DRUGBANK:DB00001`) |
| **`RXNORM_CONCEPT`** | 1,597 | Clinical concept node (RxNorm / RxNav) | `RXNORM:{rxcui}` (e.g. `RXNORM:1272`) |
| **`SIDE_EFFECT`** | 1,317 | Side-effect / adverse event concept | `SE:{side_effect_id}` (e.g. `SE:1024`) |
| **`DRUG_PAIR_OBSERVATION`**| 63,473 | Unique drug pair combination safety observation | `OBS:TWOSIDES:{d1}:{d2}` |
| **Total Nodes** | **70,574** | | |

---

## 3. Edge Schema & Edge Types

| Edge Type | Count | Directed | Source Node Type | Target Node Type | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`HAS_SOURCE_IDENTIFIER`** | 2,351 | Yes | `INTEGRATED_DRUG` | `SOURCE_DRUG_IDENTIFIER` | Links internal entity to source records with mapping confidence. |
| **`CLINICALLY_MAPPED_TO`** | 1,616 | Yes | `INTEGRATED_DRUG` | `RXNORM_CONCEPT` | Links internal entity to resolved clinical concept with match confidence. |
| **`DRUG_INTERACTS_WITH`** | 191,808 | Yes | `INTEGRATED_DRUG` | `INTEGRATED_DRUG` | Directed DDI assertion from DrugBank with interaction text. |
| **`OBSERVED_IN_COMBINATION`**| 126,946 | Yes | `INTEGRATED_DRUG` | `DRUG_PAIR_OBSERVATION` | Connects individual drugs to the combination observation (2 edges/pair). |
| **`ASSOCIATED_WITH_SIDE_EFFECT`**| 4,649,441 | Yes | `DRUG_PAIR_OBSERVATION` | `SIDE_EFFECT` | Connects the combination observation to adverse events. |
| **Total Edges** | **4,972,162** | | | | |

---

## 4. TWOSIDES Drug-Pair Semantics & Evidence Preservation
TWOSIDES adverse event observations are fundamentally **pair-level interactions** rather than single-drug direct effects. To preserve scientific integrity and prevent invalid causal attribution to individual drugs, Phase 3 implements an explicit observation model:

```
[INTEGRATED_DRUG A] --(OBSERVED_IN_COMBINATION)--> [DRUG_PAIR_OBSERVATION] <--(OBSERVED_IN_COMBINATION)-- [INTEGRATED_DRUG B]
                                                                |
                                                (ASSOCIATED_WITH_SIDE_EFFECT)
                                                                v
                                                       [SIDE_EFFECT]
```

- **63,473** distinct drug combination observation nodes represent every unique drug-pair tested in TWOSIDES.
- **126,946** `OBSERVED_IN_COMBINATION` edges connect participating drugs to their observation node.
- **4,649,441** `ASSOCIATED_WITH_SIDE_EFFECT` edges connect the observation to specific side effects.

---

## 5. Ambiguous and Unresolved Entity Handling
- **Ambiguous Components (58 entities)**: Retained with status `AMBIGUOUS_MAPPING_COMPONENT`. Edges involving these nodes carry explicit ambiguity annotations.
- **Unresolved RxNorm Entities (220 entities)**: Retained with chemical structure and source identifiers, with `rxcui = None` and match status explicitly noted (`NO_MATCH` or `AMBIGUOUS_CLINICAL_MAPPING`).

---

## 6. Graph Files & Reproducibility
All files are saved under `data/interim/graph/`:
- `graph_nodes.csv`: Standardized node table (70,574 rows).
- `graph_edges.csv`: Standardized edge table (4,972,162 rows).
- `graph_schema.json`: Machine-readable graph schema definitions.
- `graph_build_summary.json`: Build statistics and distributions.
- `twosides_pair_observations.csv`: Intermediate pair observation index.
- `unresolved_graph_entities.csv`: 220 unresolved clinical mapping records.
- `ambiguous_graph_entities.csv`: 58 ambiguous component records.
- `graph_validation_report.json`: Validation suite report (`PASSED`).

To reproduce:
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_graph_build.py
/opt/anaconda3/envs/prescription_graph/bin/python src/run_graph_validation.py
```
