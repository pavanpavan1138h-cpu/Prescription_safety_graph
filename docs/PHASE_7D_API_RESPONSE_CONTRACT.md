# Phase 7.D — Safety Report API & Response Contract Design

## 1. Executive Summary & Response Philosophy
Phase 7.D establishes the authoritative **Public API Response Contract** decoupling internal reasoning structures (`PrescriptionSafetyReport`) from the client-facing presentation layer.

### The API Presentation Rule:
> **The UI never parses raw graph structures or interprets inference rules. The API Response Adapter translates internal reasoning objects into a clean, predictable, frontend-friendly JSON schema with version metadata, summary cards, drill-down endpoints, and server-enforced scientific limitations.**

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   INTERNAL PHASE 6 REASONING LAYER                     │
│                                                                        │
│   PrescriptionSafetyReport                                             │
│   - Raw graph node IDs, edge IDs, internal inference objects           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       API RESPONSE ADAPTER                             │
│                                                                        │
│   - Enforces Pydantic Response Models                                  │
│   - Strips internal-only memory references                             │
│   - Structures summary & card-ready finding lists                      │
│   - Embeds system version metadata & scientific boundaries             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   STANDARDIZED CLIENT JSON CONTRACT                    │
│                                                                        │
│   PrescriptionAnalysisResponse                                         │
│   ├── metadata                                                         │
│   ├── input_summary                                                    │
│   ├── resolution_summary                                               │
│   ├── prescription_summary                                             │
│   ├── prioritized_findings                                             │
│   ├── pair_results                                                     │
│   ├── drug_participation                                               │
│   ├── unresolved_items                                                 │
│   ├── limitations                                                      │
│   └── provenance                                                       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master Analysis Response Schema (`POST /api/v1/prescriptions/analyze`)

### Full JSON Contract Definition

```json
{
  "metadata": {
    "analysis_id": "ANL_20260829_000042",
    "api_version": "v1.0.0",
    "generated_at": "2026-08-29T00:05:00.123456",
    "graph_version": "phase4_frozen_68k_nodes",
    "reasoning_engine_version": "phase6_multi_drug_v1"
  },
  "input_summary": {
    "submitted_medication_count": 5,
    "submitted_medications": [
      "fluconazole",
      "CID000003365",
      "DRUG_000048",
      "cyclosporine",
      "NonExistentDrugXYZ_99"
    ]
  },
  "resolution_summary": {
    "resolved_count": 4,
    "unique_canonical_drug_count": 2,
    "duplicate_count": 2,
    "unresolved_count": 1,
    "resolved_drugs": [
      {
        "canonical_drug_id": "DRUG_000048",
        "canonical_name": "Fluconazole",
        "rxcui": null,
        "input_values": ["fluconazole", "CID000003365", "DRUG_000048"]
      },
      {
        "canonical_drug_id": "DRUG_000006",
        "canonical_name": "cyclosporine",
        "rxcui": "3008",
        "input_values": ["cyclosporine"]
      }
    ]
  },
  "prescription_summary": {
    "evidence_status": "CONVERGENT_EVIDENCE_PRESENT",
    "highest_evidence_priority": "CRITICAL_EVIDENCE_PRIORITY",
    "total_unique_drugs": 2,
    "total_pairs_analyzed": 1,
    "positive_evidence_pairs": 1,
    "convergent_evidence_pairs": 1,
    "ddi_only_pairs": 0,
    "combination_event_only_pairs": 0,
    "no_direct_evidence_pairs": 0
  },
  "prioritized_findings": [
    {
      "finding_id": "FND_0001",
      "pair_id": "PAIR_DRUG_000006__DRUG_000048",
      "priority": "CRITICAL_EVIDENCE_PRIORITY",
      "drug_a": {
        "drug_id": "DRUG_000006",
        "name": "cyclosporine"
      },
      "drug_b": {
        "drug_id": "DRUG_000048",
        "name": "Fluconazole"
      },
      "evidence_status": "CONVERGENT_SAFETY_EVIDENCE",
      "confidence": {
        "level": "HIGH_EVIDENCE_CONFIDENCE",
        "score": 0.93
      },
      "summary_narrative": "cyclosporine + Fluconazole: Direct DrugBank DDI assertion present and 202 observed TWOSIDES adverse events.",
      "evidence_channels": {
        "drugbank_ddi": true,
        "twosides_combination_events": true
      },
      "ddi_record_count": 1,
      "adverse_event_count": 202,
      "inference_id": "INF_0000001",
      "detail_endpoint": "/api/v1/analyses/ANL_20260829_000042/pairs/PAIR_DRUG_000006__DRUG_000048"
    }
  ],
  "pair_results": [
    {
      "pair_id": "PAIR_DRUG_000006__DRUG_000048",
      "drug_a_name": "cyclosporine",
      "drug_b_name": "Fluconazole",
      "evidence_status": "CONVERGENT_SAFETY_EVIDENCE",
      "evidence_priority": "CRITICAL_EVIDENCE_PRIORITY",
      "confidence_level": "HIGH_EVIDENCE_CONFIDENCE",
      "confidence_score": 0.93,
      "ddi_evidence_present": true,
      "combination_event_evidence_present": true
    }
  ],
  "drug_participation": [
    {
      "drug_id": "DRUG_000048",
      "drug_name": "Fluconazole",
      "total_pairs": 1,
      "pairs_with_evidence": 1,
      "convergent_evidence_pairs": 1,
      "highest_priority": "CRITICAL_EVIDENCE_PRIORITY"
    },
    {
      "drug_id": "DRUG_000006",
      "drug_name": "cyclosporine",
      "total_pairs": 1,
      "pairs_with_evidence": 1,
      "convergent_evidence_pairs": 1,
      "highest_priority": "CRITICAL_EVIDENCE_PRIORITY"
    }
  ],
  "unresolved_items": [
    {
      "input_value": "NonExistentDrugXYZ_99",
      "resolution_status": "UNRESOLVED",
      "reason": "NO_MATCHING_CANONICAL_ENTITY"
    }
  ],
  "limitations": [
    "Evidence priority reflects the depth and convergence of evidence available in the current knowledge graph and is not a clinical probability of harm.",
    "Combination adverse event evidence represents observational associations from post-marketing surveillance and does not establish causality.",
    "Absence of direct graph evidence does not establish that a drug combination is clinically safe.",
    "This system does not incorporate patient-specific clinical variables such as dose, age, kidney/liver function, or lab values."
  ],
  "provenance": {
    "evidence_sources": ["DrugBank", "TWOSIDES", "RxNorm"],
    "supporting_edge_count": 203,
    "top_supporting_edge_ids": ["E_DDI_166133", "E_SE_02061836", "E_SE_02061837"]
  }
}
```

---

## 3. Pair-Level Detail Endpoint (`GET /api/v1/analyses/{analysis_id}/pairs/{pair_id}`)

To keep the initial analysis response lightweight, full granular evidence (all 200+ side effect rows and directed path descriptions) is delivered on-demand via the pair drill-down endpoint.

### Response Schema:
```json
{
  "pair_id": "PAIR_DRUG_000006__DRUG_000048",
  "drug_a": {
    "internal_drug_id": "DRUG_000006",
    "display_name": "cyclosporine",
    "rxcui": "3008",
    "rxnorm_name": "cyclosporine"
  },
  "drug_b": {
    "internal_drug_id": "DRUG_000048",
    "display_name": "Fluconazole",
    "rxcui": null,
    "rxnorm_name": null
  },
  "inference": {
    "inference_id": "INF_0000001",
    "evidence_status": "CONVERGENT_SAFETY_EVIDENCE",
    "evidence_priority": "CRITICAL_EVIDENCE_PRIORITY",
    "confidence_level": "HIGH_EVIDENCE_CONFIDENCE",
    "confidence_score": 0.93,
    "rule_fired": "RULE_CONVERGENT_SAFETY_EVIDENCE"
  },
  "direct_ddi_evidence": [
    {
      "edge_id": "E_DDI_166133",
      "direction": "DRUG_000006 -> DRUG_000048",
      "source_dataset": "drugbank",
      "source_record_id": "DDI:DB00091:DB00196",
      "interaction_description": "The serum concentration of #Drug2 can be increased when it is combined with #Drug1."
    }
  ],
  "combination_adverse_events": {
    "total_event_count": 202,
    "observed_events": [
      {
        "edge_id": "E_SE_02061836",
        "side_effect_id": "SE_342",
        "side_effect_name": "gastric inflammation",
        "source_dataset": "twosides"
      },
      {
        "edge_id": "E_SE_02061837",
        "side_effect_id": "SE_584",
        "side_effect_name": "myelodysplasia",
        "source_dataset": "twosides"
      }
    ]
  },
  "provenance_trace": {
    "graph_paths": [
      "(DRUG_000006) -[:INTERACTS_WITH]-> (DRUG_000048)",
      "(DRUG_000006) -> [PAIR_DRUG_000006__DRUG_000048] <- (DRUG_000048)"
    ],
    "confidence_reasons": [
      "Both drug identities are confirmed integrated entities (+0.25).",
      "One drug resolves to an RxNorm concept (+0.08).",
      "Convergent evidence across DrugBank DDI and TWOSIDES combination events (+0.60)."
    ]
  }
}
```

---

## 4. Standardized Error Contracts

All non-200 responses return a uniform envelope:
```json
{
  "error": {
    "code": "INVALID_PRESCRIPTION_INPUT",
    "message": "At least one medication identifier is required.",
    "details": {
      "field": "medications",
      "provided_count": 0
    }
  }
}
```
