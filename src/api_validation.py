"""
src/api_validation.py

Phase 7 API Contract and Scientific Regression Validation Suite.
Verifies OpenAPI schema compliance, engine/API reasoning consistency,
performance latency, error contracts, and guardrails.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from api.service import get_prescription_service
from prescription_reasoning import PrescriptionSafetyReasoner

logger = logging.getLogger(__name__)

class APIValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.val_dir = project_root / "data" / "interim" / "validation"
        self.val_dir.mkdir(parents=True, exist_ok=True)
        self.client = TestClient(app)
        self.direct_reasoner = PrescriptionSafetyReasoner(project_root / "data" / "interim" / "graph")

    def validate_all(self) -> Dict:
        logger.info("Executing Phase 7 API and Reasoning Preservation Validation Suite...")
        
        report = {
            "validation_status": "PENDING",
            "checks": {},
            "metrics": {},
            "issues": []
        }

        # 1. Health Endpoint Test
        logger.info("1. Testing /health endpoint...")
        r = self.client.get("/health")
        report["checks"]["health_endpoint_200"] = (r.status_code == 200 and r.json().get("status") == "healthy")

        # 2. System Info Endpoint Test
        logger.info("2. Testing /api/v1/system/info endpoint...")
        r_sys = self.client.get("/api/v1/system/info")
        sys_data = r_sys.json()
        report["checks"]["system_info_node_count"] = (sys_data.get("graph_nodes") == 68223)
        report["checks"]["system_info_edge_count"] = (sys_data.get("graph_edges") == 4969811)

        # 3. Drug Resolve Test (with duplicate collapsing)
        logger.info("3. Testing /api/v1/drugs/resolve duplicate collapsing...")
        r_res = self.client.post("/api/v1/drugs/resolve", json={
            "drugs": ["fluconazole", "CID000003365", "DRUG_000048", "cyclosporine", "NonExistentDrug999"]
        })
        res_data = r_res.json()
        report["checks"]["duplicate_collapsing_preservation"] = (
            res_data.get("unique_resolved_drugs") == 2 and
            res_data.get("duplicates_collapsed") == 2 and
            res_data.get("unresolved_count") == 1
        )

        # 4. Pairwise Safety Reasoning Test
        logger.info("4. Testing /api/v1/safety/pair endpoint...")
        r_pair = self.client.post("/api/v1/safety/pair", json={
            "drug_a": "cyclosporine",
            "drug_b": "fluconazole"
        })
        pair_data = r_pair.json()
        report["checks"]["pairwise_convergent_inference"] = (
            pair_data.get("evidence_status") == "CONVERGENT_SAFETY_EVIDENCE" and
            pair_data.get("confidence", {}).get("score") == 0.93
        )

        # 5. Master Prescription Analysis Reasoning Preservation (API == Phase 6 Direct Engine)
        logger.info("5. Testing Prescription Analysis reasoning preservation vs direct Phase 6 engine...")
        test_meds = ["cyclosporine", "fluconazole", "phentermine", "trioxsalen"]
        
        # Direct Phase 6 Call
        direct_rep = self.direct_reasoner.analyze_prescription(test_meds, prescription_id="TEST_DIRECT_RX")
        
        # API Call
        r_analyze = self.client.post("/api/v1/prescriptions/analyze", json={
            "medications": test_meds,
            "prescription_id": "TEST_API_RX"
        })
        api_data = r_analyze.json()

        # Invariant Assertions
        status_match = (api_data["prescription_summary"]["evidence_status"] == direct_rep.evidence_summary.prescription_status.value)
        pairs_match = (api_data["prescription_summary"]["total_pairs_analyzed"] == direct_rep.evidence_summary.total_analyzed_pairs)
        drugs_match = (api_data["prescription_summary"]["total_unique_drugs"] == direct_rep.evidence_summary.unique_canonical_drugs)
        findings_count_match = (len(api_data["prioritized_findings"]) == len(direct_rep.prioritized_findings))
        
        report["checks"]["reasoning_status_preservation"] = status_match
        report["checks"]["pair_count_preservation"] = pairs_match
        report["checks"]["drug_count_preservation"] = drugs_match
        report["checks"]["findings_count_preservation"] = findings_count_match

        # 6. Granular Pair Detail Drilldown Test
        logger.info("6. Testing /api/v1/analyses/{id}/pairs/{id} drilldown endpoint...")
        sample_pair_id = api_data["prioritized_findings"][0]["pair_id"]
        r_drill = self.client.get(f"/api/v1/analyses/{api_data['metadata']['analysis_id']}/pairs/{sample_pair_id}")
        drill_data = r_drill.json()
        report["checks"]["pair_drilldown_evidence_retrieval"] = (
            r_drill.status_code == 200 and
            len(drill_data.get("direct_ddi_evidence", [])) > 0 or
            drill_data.get("combination_adverse_events", {}).get("total_event_count", 0) > 0
        )

        # 7. Error Contract Testing
        logger.info("7. Testing error handling contracts...")
        r_err_empty = self.client.post("/api/v1/prescriptions/analyze", json={"medications": []})
        report["checks"]["empty_medication_rejection_400"] = (r_err_empty.status_code == 400)

        r_err_notfound = self.client.get("/api/v1/drugs/NonExistentDrugXYZ_404")
        report["checks"]["drug_not_found_404"] = (r_err_notfound.status_code == 404)

        # 8. Guardrails & Limitation Notices Preservation
        logger.info("8. Testing server-enforced scientific limitations in API responses...")
        limitations = api_data.get("limitations", [])
        has_guardrails = any("clinical risk" in l.lower() for l in limitations) and any("not evidence of medical safety" in l.lower() for l in limitations)
        report["checks"]["server_enforced_guardrails"] = has_guardrails

        # Final Status
        all_passed = all(report["checks"].values())
        report["validation_status"] = "PASSED" if all_passed else "FAILED"

        report["metrics"] = {
            "total_endpoints_tested": 6,
            "total_assertions_verified": len(report["checks"]),
            "graph_nodes_verified": 68223,
            "graph_edges_verified": 4969811
        }

        # Write validation report
        with open(self.val_dir / "api_contract_validation_report.json", "w") as f:
            json.dump(report, f, indent=4)

        logger.info(f"Phase 7 API Validation completed with status: {report['validation_status']}")
        return report
