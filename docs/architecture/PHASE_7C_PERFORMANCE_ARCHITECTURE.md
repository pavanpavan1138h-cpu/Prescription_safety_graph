# Phase 7.C — Data Flow, Service Lifecycle & Performance Architecture

## 1. Executive Summary & Core Performance Invariant
Phase 7.C defines the operational lifecycle, in-memory data structures, caching layers, and performance guarantees required to serve the **68,223 nodes** and **4,969,811 edges** knowledge graph with sub-100ms response times.

### Core Performance Invariant:
> **The massive knowledge graph indexes are constructed strictly ONCE during application startup into shared, thread-safe, read-only in-memory structures. Runtime HTTP requests NEVER re-scan CSV files, re-parse graph tables, or mutate underlying scientific data.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION STARTUP LIFECYCLE                         │
│                                                                                │
│  [Boot Stage]         Load Config -> Verify File Integrity                     │
│  [Index Stage]        Build In-Memory Lookup, DDI, & DrugPair Indexes          │
│  [Engine Stage]       Initialize Phase 5 & Phase 6 Service Singletons          │
│  [Warmup Stage]       Execute Internal Verification Query                      │
│  [Readiness]          State -> "SERVICE_READY"                                 │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                                       │ (Shared Read-Only Memory)
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                        RUNTIME REQUEST EXECUTION PIPELINE                      │
│                                                                                │
│  HTTP Request [/api/v1/prescriptions/analyze]                                  │
│        │                                                                       │
│        ▼                                                                       │
│  [Validation]         Enforce MAX_PRESCRIPTION_SIZE (<= 50 drugs)              │
│        │                                                                       │
│        ▼                                                                       │
│  [Result Cache]       Check Canonical Key (e.g. DRUG_000006|DRUG_000048)       │
│        │              ├── Hit  -> Return Cached Report Object (1ms)            │
│        │              └── Miss -> Proceed to Execution                         │
│        ▼                                                                       │
│  [Resolution]         Fast In-Memory Map Lookup (Names/RxCUIs/DB/CIDs)         │
│        │                                                                       │
│        ▼                                                                       │
│  [Pair Generator]     Deterministic N*(N-1)/2 Combination Generator            │
│        │                                                                       │
│        ▼                                                                       │
│  [Pairwise Engine]    O(1) DDI & DrugPair In-Memory Index Evaluation           │
│        │                                                                       │
│        ▼                                                                       │
│  [Aggregation]        Prescription Status & Priority Tier Sorting              │
│        │                                                                       │
│        ▼                                                                       │
│  [Report Synthesis]   Generate Structured JSON + Formatted Narrative Text      │
│        │                                                                       │
│        ▼                                                                       │
│  [Session Store]      Store in UI Retrieval Cache (PSR_xxxxxx)                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. In-Memory Indexed Data Structures (Zero CSV Scanning)

| Index | Key Type | Value Type | Lookup Complexity | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`drug_by_id`** | `str` (`DRUG_xxxxxx`) | `DrugIdentity` | $O(1)$ | Direct canonical entity retrieval. |
| **`drug_by_alias`** | `str` (lower-case name, RxCUI, DB ID, CID) | `str` (`DRUG_xxxxxx`) | $O(1)$ | Multi-format input resolution. |
| **`ddi_index`** | `Tuple[str, str]` (`(src_id, tgt_id)`) | `List[DDIEvidenceRecord]` | $O(1)$ | Forward/reverse directed DDI retrieval. |
| **`pair_id_index`** | `Tuple[str, str]` (`sorted(id1, id2)`) | `str` (`PAIR_xxx__yyy`) | $O(1)$ | Reified DrugPair node identification. |
| **`pair_side_effects`** | `str` (`PAIR_xxx__yyy`) | `(total_count, List[SampleSE])` | $O(1)$ | Combination adverse event retrieval. |

---

## 3. Three-Tier Caching Architecture

1. **Tier 1: Application Data Cache (Startup)**:
   - Holds the frozen knowledge graph in-memory indexes.
   - Initialized once at boot; destroyed only on process termination.
   - Read-only; completely thread-safe for concurrent requests.
2. **Tier 2: Prescription Analysis Cache (Runtime Execution)**:
   - Key: Canonical sorted drug ID string (e.g. `DRUG_000006|DRUG_000045|DRUG_000048`).
   - Value: `PrescriptionSafetyReport`.
   - Avoids redundant pairwise graph traversals when users re-submit the same combinations in different permutations.
3. **Tier 3: UI Retrieval Cache (Session-Level)**:
   - Key: `prescription_id` (e.g. `RX_REPORT_000042`).
   - Value: Full structured report object.
   - Allows instant tab switching, evidence drill-down, and provenance inspection without re-running analysis.

---

## 4. Service State Machine & Health Monitoring

```text
[STARTING] -> [LOADING_INDEXES] -> [WARMING_UP] -> [SERVICE_READY]
                                                          │
                                         ┌────────────────┴────────────────┐
                                         ▼                                 ▼
                                    [PROCESSING]                      [DEGRADED]
```

- **`STARTING`**: Process launched; reading environment configuration.
- **`LOADING_INDEXES`**: Streaming graph files into memory maps.
- **`WARMING_UP`**: Executing test query `cyclosporine + fluconazole`.
- **`SERVICE_READY`**: All indexes verified; `/health` returns `200 OK`.
- **`DEGRADED`**: Partial index availability (e.g. RxNorm cache offline, but core graph intact).

---

## 5. Performance Limits & Timing Diagnostics

### Operational Limits:
- **`MAX_PRESCRIPTION_SIZE`**: 50 medications ($1,225$ maximum theoretical pairs per prescription).
- **`MAX_REQUEST_TIMEOUT`**: 5.0 seconds.

### Diagnostic Timing Instrumentation:
Every response embeds fine-grained timing breakdowns:
```json
{
  "performance": {
    "resolution_time_ms": 1.2,
    "pair_generation_time_ms": 0.1,
    "reasoning_time_ms": 14.5,
    "report_generation_time_ms": 2.8,
    "total_time_ms": 18.6
  }
}
```

---

## 6. Failure Isolation & Partial Analysis Support

1. **Unresolved Medications $\ne$ System Failure**:
   - If a prescription contains `["fluconazole", "UnrecognizedChemical999"]`, the engine isolates the unresolved item, marks `unresolved_count = 1`, and generates a `PARTIAL_ANALYSIS` report for the remaining valid pairs.
2. **Crash Prevention**:
   - All router endpoints are wrapped with standardized error handlers.
   - Runtime exceptions log a unique `request_id` and return a structured `500 INTERNAL_ANALYSIS_ERROR` without leaking stack traces or crashing the uvicorn process.
