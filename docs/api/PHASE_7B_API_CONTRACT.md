# Phase 7.B — API Contract & Request/Response Architecture

## 1. System Context & Architectural Invariant
Phase 7.B defines the formal HTTP / REST API contract wrapping the frozen **Phase 1–6 intelligence core**.

### The Core Architectural Invariant:
> **The API layer is a strict, thin service boundary. It never directly accesses raw Knowledge Graph files, nor does it reimplement pairwise classification, pair generation, or prioritization logic. All analysis requests route directly through `PrescriptionSafetyReasoner` and `SafetyQueryEngine`.**

```text
┌────────────────────────────────────────────────────────┐
│                        WEB UI                          │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP JSON Request
                            ▼
┌────────────────────────────────────────────────────────┐
│               FASTAPI REST API LAYER                   │
│                                                        │
│   /api/v1/health                                       │
│   /api/v1/system/info                                  │
│   /api/v1/drugs/resolve                                │
│   /api/v1/drugs/{identifier}                           │
│   /api/v1/safety/pair                                  │
│   /api/v1/prescriptions/analyze                       │
│   /api/v1/prescriptions/{prescription_id}              │
│   /api/v1/evidence/{inference_id}                      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 SERVICE ADAPTER LAYER                  │
│                                                        │
│   PrescriptionService  │  DrugLookupService            │
│   EvidenceService      │  ReportService                │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│         FROZEN PHASE 5 & 6 REASONING CORE              │
│                                                        │
│   PrescriptionSafetyReasoner.analyze_prescription()    │
│   SafetyQueryEngine.evaluate_pair()                    │
│   SafetyQueryEngine.lookup_drug()                      │
└────────────────────────────────────────────────────────┘
```

---

## 2. API Endpoint Specification (`/api/v1`)

### A. Health & System Information

#### 1. `GET /health`
- **Purpose**: Liveness and readiness check.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "prescription-safety-graph-api",
  "graph_loaded": true,
  "reasoning_engine_available": true
}
```

#### 2. `GET /api/v1/system/info`
- **Purpose**: Exposes graph scale and system capabilities.
- **Response `200 OK`**:
```json
{
  "api_version": "1.0.0",
  "graph_nodes": 68223,
  "graph_edges": 4969811,
  "node_breakdown": {
    "Drug": 1836,
    "RxNormConcept": 1597,
    "DrugPair": 63473,
    "SideEffect": 1317
  },
  "edge_breakdown": {
    "HAS_RXNORM_CONCEPT": 1616,
    "INTERACTS_WITH": 191808,
    "MEMBER_OF_PAIR": 126946,
    "ASSOCIATED_WITH": 4649441
  },
  "supported_identifier_types": [
    "drug_name",
    "internal_drug_id",
    "drugbank_id",
    "pubchem_cid",
    "rxcui"
  ]
}
```

---

### B. Drug Identity & Resolution Endpoints

#### 3. `POST /api/v1/drugs/resolve`
- **Purpose**: Batch resolution of mixed medication identifiers into canonical entities with duplicate detection.
- **Request Body**:
```json
{
  "drugs": [
    "fluconazole",
    "CID000003365",
    "DB00091",
    "UnknownDrugXYZ_99"
  ]
}
```
- **Response `200 OK`**:
```json
{
  "input_count": 4,
  "unique_resolved_drugs": 2,
  "duplicates_collapsed": 1,
  "unresolved_count": 1,
  "results": [
    {
      "input": "fluconazole",
      "status": "RESOLVED",
      "internal_drug_id": "DRUG_000048",
      "canonical_name": "Fluconazole",
      "identifier_type_matched": "CANONICAL_NAME",
      "rxcui": null
    },
    {
      "input": "CID000003365",
      "status": "DUPLICATE",
      "internal_drug_id": "DRUG_000048",
      "canonical_name": "Fluconazole",
      "identifier_type_matched": "TWOSIDES_CID",
      "rxcui": null
    },
    {
      "input": "DB00091",
      "status": "RESOLVED",
      "internal_drug_id": "DRUG_000006",
      "canonical_name": "cyclosporine",
      "identifier_type_matched": "DRUGBANK_ID",
      "rxcui": "3008"
    },
    {
      "input": "UnknownDrugXYZ_99",
      "status": "UNRESOLVED",
      "internal_drug_id": null,
      "canonical_name": null,
      "identifier_type_matched": null,
      "rxcui": null
    }
  ]
}
```

#### 4. `GET /api/v1/drugs/{identifier}`
- **Purpose**: Retrieves full entity card for a single drug identifier.
- **Response `200 OK`**:
```json
{
  "internal_drug_id": "DRUG_000006",
  "display_name": "cyclosporine",
  "entity_status": "CONFIRMED_INTEGRATED_ENTITY",
  "source_membership": "both",
  "rxcui": "3008",
  "rxnorm_name": "cyclosporine",
  "rxnorm_match_status": "HIGH_EXACT",
  "drugbank_ids": ["DB00091"],
  "twosides_cids": ["CID000002909"]
}
```

---

### C. Pairwise Safety Reasoning Endpoint

#### 5. `POST /api/v1/safety/pair`
- **Purpose**: Direct evaluation of two drugs via Phase 5 reasoning.
- **Request Body**:
```json
{
  "drug_a": "cyclosporine",
  "drug_b": "fluconazole"
}
```
- **Response `200 OK`**:
```json
{
  "inference_id": "INF_0000001",
  "drug_a": {
    "internal_drug_id": "DRUG_000006",
    "display_name": "cyclosporine"
  },
  "drug_b": {
    "internal_drug_id": "DRUG_000048",
    "display_name": "Fluconazole"
  },
  "evidence_status": "CONVERGENT_SAFETY_EVIDENCE",
  "confidence": {
    "level": "HIGH_EVIDENCE_CONFIDENCE",
    "score": 0.93
  },
  "evidence_summary": {
    "ddi_present": true,
    "ddi_forward_count": 1,
    "ddi_reverse_count": 0,
    "events_present": true,
    "event_count": 202
  },
  "clinical_interpretation": "This evaluation reflects structured graph evidence strength. It is not a clinical risk probability or medical diagnosis."
}
```

---

### D. Multi-Drug Prescription Analysis Endpoint

#### 6. `POST /api/v1/prescriptions/analyze`
- **Purpose**: Master analysis endpoint evaluating an entire multi-drug medication list.
- **Request Body**:
```json
{
  "medications": [
    "cyclosporine",
    "fluconazole",
    "phentermine"
  ]
}
```
- **Response `200 OK`**:
```json
{
  "prescription_id": "RX_REPORT_000001",
  "generated_at": "2026-08-29T00:03:00.123456",
  "input_summary": {
    "total_input_items": 3,
    "unique_canonical_drugs": 3,
    "duplicates_collapsed_count": 0,
    "ambiguous_items_count": 0,
    "unresolved_items_count": 0
  },
  "overall_assessment": {
    "prescription_status": "MULTI_SIGNAL_EVIDENCE",
    "total_expected_pairs": 3,
    "total_analyzed_pairs": 3,
    "pairs_with_evidence": 2,
    "convergent_evidence_pairs": 1,
    "ddi_only_pairs": 0,
    "combination_event_only_pairs": 1,
    "no_direct_evidence_pairs": 1
  },
  "prioritized_findings": [
    {
      "finding_id": "FIND_0001",
      "pair_index": 1,
      "drug_a_name": "cyclosporine",
      "drug_b_name": "Fluconazole",
      "evidence_priority": "CRITICAL_EVIDENCE_PRIORITY",
      "evidence_status": "CONVERGENT_SAFETY_EVIDENCE",
      "confidence_level": "HIGH_EVIDENCE_CONFIDENCE",
      "confidence_score": 0.93,
      "ddi_count": 1,
      "event_count": 202,
      "inference_id": "INF_0000001",
      "supporting_edge_ids": ["E_DDI_166133", "E_SE_02061836", "E_SE_02061837"]
    },
    {
      "finding_id": "FIND_0002",
      "pair_index": 3,
      "drug_a_name": "Fluconazole",
      "drug_b_name": "Phentermine",
      "evidence_priority": "MODERATE_EVIDENCE_PRIORITY",
      "evidence_status": "COMBINATION_EVENT_EVIDENCE_ONLY",
      "confidence_level": "MODERATE_EVIDENCE_CONFIDENCE",
      "confidence_score": 0.65,
      "ddi_count": 0,
      "event_count": 75,
      "inference_id": "INF_0000003",
      "supporting_edge_ids": ["E_SE_01192345", "E_SE_01192346", "E_SE_01192347"]
    }
  ],
  "drug_participation": [
    {
      "internal_drug_id": "DRUG_000048",
      "display_name": "Fluconazole",
      "total_pairs_involved": 2,
      "evidence_supported_pairs": 2
    },
    {
      "internal_drug_id": "DRUG_000006",
      "display_name": "cyclosporine",
      "total_pairs_involved": 2,
      "evidence_supported_pairs": 1
    },
    {
      "internal_drug_id": "DRUG_000045",
      "display_name": "Phentermine",
      "total_pairs_involved": 2,
      "evidence_supported_pairs": 1
    }
  ],
  "limitations": [
    "Graph evidence priority is not equivalent to patient-specific clinical risk.",
    "Absence of evidence in the current graph is not evidence of medical safety.",
    "Drug interaction assertions and observational adverse event associations do not independently establish causality.",
    "This report is generated strictly from the ingested knowledge graph datasets and does not replace professional clinical judgment."
  ]
}
```

---

### E. Provenance & Full Report Retrieval

#### 7. `GET /api/v1/prescriptions/{prescription_id}`
- **Purpose**: Retrieves full structured report with complete clinical narrative text.

#### 8. `GET /api/v1/evidence/{inference_id}`
- **Purpose**: Full multi-hop graph path and source record inspection for a specific inference.
- **Response `200 OK`**:
```json
{
  "inference_id": "INF_0000001",
  "evidence_status": "CONVERGENT_SAFETY_EVIDENCE",
  "rule_fired": "RULE_CONVERGENT_SAFETY_EVIDENCE",
  "graph_paths": [
    "(DRUG_000006) -[:INTERACTS_WITH]-> (DRUG_000048)",
    "(DRUG_000006) -> [PAIR_DRUG_000006__DRUG_000048] <- (DRUG_000048)"
  ],
  "supporting_edges": [
    {
      "edge_id": "E_DDI_166133",
      "relationship_type": "INTERACTS_WITH",
      "source_dataset": "drugbank",
      "source_record_id": "DDI:DB00091:DB00196",
      "description": "The serum concentration of #Drug2 can be increased when it is combined with #Drug1."
    },
    {
      "edge_id": "E_SE_02061836",
      "relationship_type": "ASSOCIATED_WITH",
      "source_dataset": "twosides",
      "source_record_id": "TWOSIDES_EVENT:CID000002909:CID000003365:SE_342",
      "side_effect_name": "gastric inflammation"
    }
  ],
  "confidence_reasons": [
    "Both drug identities are confirmed integrated entities (+0.25).",
    "One drug resolves to an RxNorm concept (+0.08).",
    "Convergent evidence across DrugBank DDI and TWOSIDES combination events (+0.60)."
  ]
}
```

---

## 3. Standardized Error Architecture

| Error Code | HTTP Status | Trigger Condition | Example Error Response |
| :--- | :--- | :--- | :--- |
| **`EMPTY_MEDICATION_LIST`** | `400 Bad Request` | `medications` array is empty or contains only whitespace. | `{"error": {"code": "EMPTY_MEDICATION_LIST", "message": "At least one medication identifier must be provided."}}` |
| **`DRUG_NOT_FOUND`** | `404 Not Found` | Single drug lookup failed to find any entity. | `{"error": {"code": "DRUG_NOT_FOUND", "message": "Identifier 'UnknownXYZ' could not be resolved in knowledge graph."}}` |
| **`REPORT_NOT_FOUND`** | `404 Not Found` | `prescription_id` does not exist in session cache. | `{"error": {"code": "REPORT_NOT_FOUND", "message": "Prescription report 'RX_999' not found."}}` |
| **`INTERNAL_ANALYSIS_ERROR`** | `500 Server Error` | Unexpected runtime exception during analysis. | `{"error": {"code": "INTERNAL_ANALYSIS_ERROR", "message": "Reasoning engine encountered an internal failure."}}` |
