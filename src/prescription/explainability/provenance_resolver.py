"""
src/prescription/explainability/provenance_resolver.py

Module responsible for extracting and resolving concrete source provenance records
(DrugBank DDI assertions, TWOSIDES combination side effect reports, RxNorm resolution)
from baseline drug pairs and analytical artifacts.
"""

from typing import List, Dict, Any, Optional, Set
from src.prescription.schemas import PrescriptionSafetyReport
from src.prescription.explainability.explainability_schema import SourceProvenanceRecord

class ProvenanceResolver:
    """
    Recovers concrete evidentiary provenance ancestry for all evaluated drug entities
    and drug-pair combinations without fabricating missing records.
    """

    def resolve_provenance(
        self,
        analysis_result: PrescriptionSafetyReport,
        evidence_intelligence: Optional[Any] = None
    ) -> List[SourceProvenanceRecord]:
        records: List[SourceProvenanceRecord] = []
        seen_source_ids: Set[str] = set()

        # 1. Resolve RxNorm Drug Normalization Provenance
        if hasattr(analysis_result, "resolution_summary") and analysis_result.resolution_summary:
            for drug in analysis_result.resolution_summary.resolved_drugs:
                drug_id = getattr(drug, "resolved_internal_drug_id", None) or getattr(drug, "canonical_drug_id", "UNKNOWN")
                drug_name = getattr(drug, "display_name", None) or getattr(drug, "canonical_name", "UNKNOWN")
                rxcui = getattr(drug, "rxcui", None)
                orig_input = getattr(drug, "original_input", drug_name)
                
                source_id = f"RXNORM_{drug_id}"
                if source_id not in seen_source_ids:
                    seen_source_ids.add(source_id)
                    records.append(SourceProvenanceRecord(
                        source_id=source_id,
                        dataset_name="RxNorm",
                        record_type="CONCEPT_NORMALIZATION",
                        external_identifier=rxcui if rxcui else drug_id,
                        description=f"RxNorm normalized identity for '{drug_name}' (Input: {orig_input})",
                        is_available=True
                    ))

        # 2. Resolve Pair Evidence Provenance
        findings_map = {}
        if hasattr(analysis_result, "prioritized_findings") and analysis_result.prioritized_findings:
            for f in analysis_result.prioritized_findings:
                findings_map[f.finding_id] = f

        for pair in analysis_result.pair_results:
            pair_id = pair.get("pair_id") if isinstance(pair, dict) else getattr(pair, "pair_id", "")
            drug_a_id = pair.get("drug_a_id") if isinstance(pair, dict) else getattr(pair, "drug_a_id", "")
            drug_b_id = pair.get("drug_b_id") if isinstance(pair, dict) else getattr(pair, "drug_b_id", "")
            drug_a_name = pair.get("drug_a_name") if isinstance(pair, dict) else getattr(pair, "drug_a_name", "")
            drug_b_name = pair.get("drug_b_name") if isinstance(pair, dict) else getattr(pair, "drug_b_name", "")
            has_ddi = pair.get("ddi_evidence_present", False) if isinstance(pair, dict) else getattr(pair, "has_direct_ddi", False)
            has_events = pair.get("combination_event_evidence_present", False) if isinstance(pair, dict) else getattr(pair, "has_combination_side_effects", False)
            
            pair_label = f"{drug_a_name} + {drug_b_name}"
            
            # DrugBank DDI Assertion
            if has_ddi:
                db_id = f"DRUGBANK_DDI_{drug_a_id}_{drug_b_id}"
                if db_id not in seen_source_ids:
                    seen_source_ids.add(db_id)
                    records.append(SourceProvenanceRecord(
                        source_id=db_id,
                        dataset_name="DrugBank",
                        record_type="DDI_ASSERTION",
                        external_identifier=f"{drug_a_id}:{drug_b_id}",
                        description=f"DrugBank direct interaction assertion for {pair_label}",
                        is_available=True
                    ))

            # TWOSIDES Combination Side Effects
            if has_events:
                ts_id = f"TWOSIDES_COMB_{drug_a_id}_{drug_b_id}"
                if ts_id not in seen_source_ids:
                    seen_source_ids.add(ts_id)
                    records.append(SourceProvenanceRecord(
                        source_id=ts_id,
                        dataset_name="TWOSIDES",
                        record_type="COMBINATION_SIDE_EFFECTS",
                        external_identifier=f"{drug_a_id}:{drug_b_id}",
                        description=f"TWOSIDES pharmacovigilance combination signal for {pair_label}",
                        is_available=True
                    ))

            # If unsupported, record explicitly as unavailable provenance rather than fabricating
            if not has_ddi and not has_events:
                unav_id = f"PROVENANCE_UNAVAILABLE_{drug_a_id}_{drug_b_id}"
                if unav_id not in seen_source_ids:
                    seen_source_ids.add(unav_id)
                    records.append(SourceProvenanceRecord(
                        source_id=unav_id,
                        dataset_name="NONE",
                        record_type="NO_DIRECT_EVIDENCE_RECORD",
                        external_identifier=None,
                        description=f"No direct DrugBank DDI or TWOSIDES combination record found in graph for {pair_label}",
                        is_available=False
                    ))

        return records
