"""
prescription_resolver.py

Multi-identifier Prescription Resolution Engine for Phase 6.
Resolves arbitrary input medications (Names, DrugBank IDs, PubChem CIDs, RxCUIs, Internal IDs)
into canonical integrated Drug entities (DRUG_xxxxxx) with duplicate collapsing and unresolved item isolation.
"""

import logging
from typing import List, Dict, Optional, Set
from prescription_schema import (
    ResolutionStatus,
    ResolvedPrescriptionDrug,
    PrescriptionResolutionResult
)
from evidence_retrieval import EvidenceRetriever

logger = logging.getLogger(__name__)

class PrescriptionResolver:
    def __init__(self, retriever: EvidenceRetriever):
        self.retriever = retriever

    def resolve_prescription(self, medication_inputs: List[str]) -> PrescriptionResolutionResult:
        """
        Resolves a list of arbitrary medication string inputs into unique canonical drug entities.
        Detects duplicates, ambiguous components, and unresolvable inputs without guessing.
        """
        self.retriever.load()

        resolved_drugs: List[ResolvedPrescriptionDrug] = []
        canonical_drug_ids_ordered: List[str] = []
        seen_canonical_ids: Set[str] = set()

        unresolved_inputs: List[str] = []
        ambiguous_inputs: List[str] = []
        duplicate_inputs: List[str] = []

        for orig_input in medication_inputs:
            q = str(orig_input).strip()
            if not q:
                continue

            drug_obj = self.retriever.resolve_drug(q)

            if not drug_obj:
                unresolved_inputs.append(q)
                resolved_drugs.append(ResolvedPrescriptionDrug(
                    original_input=q,
                    resolved_internal_drug_id=None,
                    display_name=None,
                    resolution_status=ResolutionStatus.UNRESOLVED,
                    identifier_type_matched=None
                ))
                continue

            cid = drug_obj.internal_drug_id
            matched_type = self._detect_identifier_type(q, drug_obj)

            # Check if this canonical ID was already added by a previous item in the same prescription
            if cid in seen_canonical_ids:
                duplicate_inputs.append(q)
                resolved_drugs.append(ResolvedPrescriptionDrug(
                    original_input=q,
                    resolved_internal_drug_id=cid,
                    display_name=drug_obj.display_name,
                    resolution_status=ResolutionStatus.DUPLICATE,
                    identifier_type_matched=matched_type,
                    entity_status=drug_obj.entity_status,
                    rxcui=drug_obj.rxcui,
                    rxnorm_name=drug_obj.rxnorm_name
                ))
            else:
                seen_canonical_ids.add(cid)
                canonical_drug_ids_ordered.append(cid)

                res_status = ResolutionStatus.RESOLVED
                if drug_obj.entity_status == "AMBIGUOUS_MAPPING_COMPONENT":
                    res_status = ResolutionStatus.AMBIGUOUS
                    ambiguous_inputs.append(q)

                resolved_drugs.append(ResolvedPrescriptionDrug(
                    original_input=q,
                    resolved_internal_drug_id=cid,
                    display_name=drug_obj.display_name,
                    resolution_status=res_status,
                    identifier_type_matched=matched_type,
                    entity_status=drug_obj.entity_status,
                    rxcui=drug_obj.rxcui,
                    rxnorm_name=drug_obj.rxnorm_name
                ))

        return PrescriptionResolutionResult(
            original_inputs=medication_inputs,
            resolved_drugs=resolved_drugs,
            canonical_drug_ids=canonical_drug_ids_ordered,
            unresolved_inputs=unresolved_inputs,
            ambiguous_inputs=ambiguous_inputs,
            duplicate_inputs=duplicate_inputs
        )

    def _detect_identifier_type(self, q: str, drug_obj) -> str:
        q_clean = q.strip()
        if q_clean == drug_obj.internal_drug_id:
            return "INTERNAL_PROJECT_ID"
        if q_clean.startswith("DB") or q_clean in drug_obj.drugbank_ids:
            return "DRUGBANK_ID"
        if q_clean.startswith("CID") or q_clean in drug_obj.twosides_cids:
            return "TWOSIDES_CID"
        if drug_obj.rxcui and (q_clean == str(drug_obj.rxcui) or q_clean == f"RXCUI_{drug_obj.rxcui}"):
            return "RXCUI"
        if drug_obj.display_name and q_clean.lower() == drug_obj.display_name.lower():
            return "CANONICAL_NAME"
        if drug_obj.rxnorm_name and q_clean.lower() == str(drug_obj.rxnorm_name).lower():
            return "RXNORM_NAME"
        return "MATCHED_NAME_SYNONYM"
