"""
risk_classifier.py

Box 9 — Risk & Patient-Context Analysis: Drug Risk Classifier.
Deterministically loads OpenFDA regulatory risk records and ISMP high-alert records,
evaluates resolved prescription drug entities against the multi-level matching hierarchy,
and derives the primary risk tier with complete provenance.

Matching Hierarchy:
For ISMP:
1. matched_canonical_id / internal_drug_id
2. matched_rxcui / rxcui
3. normalized medication name

For OpenFDA:
1. rxcui
2. normalized medication name

Risk Tier Precedence:
Boxed Warning > High-Alert > Standard
Both evidence attachments are retained in full without summarization or rewriting.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from src.prescription.advanced_intelligence_schema import (
    RiskTier,
    DrugRiskAssessment,
)

logger = logging.getLogger(__name__)


def _normalize_name_key(name: Optional[str]) -> str:
    """Normalizes drug name for deterministic index lookup."""
    if not name:
        return ""
    text = name.lower().strip()
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r",\s*(iv|im|subcutaneous|oral|parenteral|transdermal|intraosseous|injection|concentrate).*", "", text)
    text = re.sub(r"\s+(for injection concentrate|for injection|injection concentrate|injection|tincture|anhydrous|liposomal|tablets|capsules|hcl|sodium)$", "", text)
    return text.strip()


class DrugRiskClassifier:
    """
    Deterministic offline risk classifier for Box 9.
    Loads preprocessed OpenFDA risk records and ISMP high-alert datasets.
    """

    def __init__(
        self,
        openfda_records_path: Union[str, Path] = "data/interim/openfda_risk_records.csv",
        ismp_records_path: Union[str, Path] = "data/interim/ismp_high_alert.csv",
    ):
        self.openfda_path = Path(openfda_records_path)
        self.ismp_path = Path(ismp_records_path)

        # OpenFDA indexes: by rxcui and by normalized name
        self.openfda_by_rxcui: Dict[str, Dict[str, Any]] = {}
        self.openfda_by_name: Dict[str, Dict[str, Any]] = {}

        # ISMP indexes: by canonical ID, by rxcui, and by normalized name
        self.ismp_by_canonical_id: Dict[str, Dict[str, Any]] = {}
        self.ismp_by_rxcui: Dict[str, Dict[str, Any]] = {}
        self.ismp_by_name: Dict[str, Dict[str, Any]] = {}

        self._load_datasets()

    def _load_datasets(self):
        """Loads and indexes interim OpenFDA and ISMP datasets."""
        # 1. OpenFDA
        if self.openfda_path.exists():
            try:
                df_fda = pd.read_csv(self.openfda_path)
                for _, r in df_fda.iterrows():
                    rec = {
                        "drug_name": str(r.get("drug_name") or "").strip(),
                        "rxcui": str(r.get("rxcui") or "").strip(),
                        "risk_tier": str(r.get("risk_tier") or "Standard").strip(),
                        "boxed_warning_present": bool(r.get("boxed_warning_present")),
                        "boxed_warning": str(r.get("boxed_warning") or "").strip() if pd.notna(r.get("boxed_warning")) else "",
                        "contraindication_present": bool(r.get("contraindication_present")),
                        "contraindications": str(r.get("contraindications") or "").strip() if pd.notna(r.get("contraindications")) else "",
                        "warning_present": bool(r.get("warning_present")),
                        "warnings_and_cautions": str(r.get("warnings_and_cautions") or "").strip() if pd.notna(r.get("warnings_and_cautions")) else "",
                        "effective_time": str(r.get("effective_time") or "").strip(),
                        "label_id": str(r.get("label_id") or "").strip(),
                        "set_id": str(r.get("set_id") or "").strip(),
                        "source": str(r.get("source") or "openFDA").strip(),
                    }
                    if rec["rxcui"]:
                        self.openfda_by_rxcui[rec["rxcui"]] = rec
                    norm_n = _normalize_name_key(rec["drug_name"])
                    if norm_n:
                        self.openfda_by_name[norm_n] = rec
                logger.info(f"Loaded {len(self.openfda_by_rxcui)} OpenFDA records by RxCUI, {len(self.openfda_by_name)} by name.")
            except Exception as e:
                logger.error(f"Failed to load OpenFDA records from {self.openfda_path}: {e}")
        else:
            logger.warning(f"OpenFDA records file not found at {self.openfda_path}")

        # 2. ISMP
        if self.ismp_path.exists():
            try:
                df_ismp = pd.read_csv(self.ismp_path)
                for _, r in df_ismp.iterrows():
                    rec = {
                        "drug_name": str(r.get("drug_name") or "").strip(),
                        "normalized_drug_name": str(r.get("normalized_drug_name") or "").strip(),
                        "ismp_high_alert": bool(r.get("ismp_high_alert")),
                        "ismp_category": str(r.get("ismp_category") or "").strip() if pd.notna(r.get("ismp_category")) else None,
                        "entry_type": str(r.get("entry_type") or "").strip(),
                        "matched_canonical_id": str(r.get("matched_canonical_id") or "").strip() if pd.notna(r.get("matched_canonical_id")) else "",
                        "matched_display_name": str(r.get("matched_display_name") or "").strip() if pd.notna(r.get("matched_display_name")) else "",
                        "matched_rxcui": str(r.get("matched_rxcui") or "").strip() if pd.notna(r.get("matched_rxcui")) else "",
                        "is_matched_in_graph": bool(r.get("is_matched_in_graph")),
                        "source": str(r.get("source") or "ISMP").strip(),
                    }
                    # Clean float string representation if any (e.g. '3992.0' -> '3992')
                    if rec["matched_rxcui"].endswith(".0"):
                        rec["matched_rxcui"] = rec["matched_rxcui"][:-2]

                    if rec["matched_canonical_id"]:
                        self.ismp_by_canonical_id[rec["matched_canonical_id"]] = rec
                    if rec["matched_rxcui"]:
                        self.ismp_by_rxcui[rec["matched_rxcui"]] = rec
                    norm_n = _normalize_name_key(rec["normalized_drug_name"] or rec["drug_name"])
                    if norm_n:
                        self.ismp_by_name[norm_n] = rec
                logger.info(f"Loaded {len(self.ismp_by_canonical_id)} ISMP records by canonical ID, {len(self.ismp_by_name)} by name.")
            except Exception as e:
                logger.error(f"Failed to load ISMP records from {self.ismp_path}: {e}")
        else:
            logger.warning(f"ISMP records file not found at {self.ismp_path}")

    def classify_drug(
        self,
        internal_drug_id: str,
        rxcui: Optional[str],
        drug_name: str,
    ) -> DrugRiskAssessment:
        """
        Deterministically classifies a single drug entity.
        Evaluates OpenFDA and ISMP evidence against matching hierarchy,
        applies risk tier precedence, and retains full evidence text.
        """
        clean_drug_id = str(internal_drug_id or "").strip()
        clean_rxcui = str(rxcui or "").strip()
        if clean_rxcui.endswith(".0"):
            clean_rxcui = clean_rxcui[:-2]
        clean_name = str(drug_name or "").strip()
        norm_name = _normalize_name_key(clean_name)

        # 1. Match against OpenFDA
        # Hierarchy: 1. rxcui, 2. normalized drug name
        fda_rec = None
        if clean_rxcui and clean_rxcui in self.openfda_by_rxcui:
            fda_rec = self.openfda_by_rxcui[clean_rxcui]
        elif norm_name and norm_name in self.openfda_by_name:
            fda_rec = self.openfda_by_name[norm_name]

        has_boxed_warning = False
        boxed_warning_text = None
        contraindications_text = None
        warnings_cautions_text = None

        if fda_rec:
            has_boxed_warning = bool(fda_rec.get("boxed_warning_present"))
            boxed_warning_text = fda_rec.get("boxed_warning") or None
            contraindications_text = fda_rec.get("contraindications") or None
            warnings_cautions_text = fda_rec.get("warnings_and_cautions") or None

        # 2. Match against ISMP
        # Hierarchy: 1. matched_canonical_id / internal_drug_id, 2. matched_rxcui / rxcui, 3. normalized medication name
        ismp_rec = None
        if clean_drug_id and clean_drug_id in self.ismp_by_canonical_id:
            ismp_rec = self.ismp_by_canonical_id[clean_drug_id]
        elif clean_rxcui and clean_rxcui in self.ismp_by_rxcui:
            ismp_rec = self.ismp_by_rxcui[clean_rxcui]
        elif norm_name and norm_name in self.ismp_by_name:
            ismp_rec = self.ismp_by_name[norm_name]

        is_ismp_high_alert = False
        ismp_category = None
        if ismp_rec:
            is_ismp_high_alert = bool(ismp_rec.get("ismp_high_alert"))
            ismp_category = ismp_rec.get("ismp_category")

        # 3. Derive Risk Tier Precedence:
        # Boxed Warning > High-Alert > Standard
        if has_boxed_warning:
            risk_tier = RiskTier.BOXED_WARNING
        elif is_ismp_high_alert:
            risk_tier = RiskTier.HIGH_ALERT
        else:
            risk_tier = RiskTier.STANDARD

        # 4. Evidence Source Provenance
        if fda_rec and ismp_rec:
            evidence_source = "openFDA+ISMP"
        elif fda_rec:
            evidence_source = "openFDA"
        elif ismp_rec:
            evidence_source = "ISMP"
        else:
            evidence_source = "Standard"

        return DrugRiskAssessment(
            drug_id=clean_drug_id,
            drug_name=clean_name,
            rxcui=clean_rxcui or None,
            risk_tier=risk_tier,
            is_ismp_high_alert=is_ismp_high_alert,
            ismp_category=ismp_category,
            has_boxed_warning=has_boxed_warning,
            boxed_warning_text=boxed_warning_text,
            contraindications_text=contraindications_text,
            warnings_cautions_text=warnings_cautions_text,
            evidence_source=evidence_source,
        )
