"""
openfda_ingestion.py

Automated, deterministic ingestion and preprocessing pipeline for OpenFDA drug-label risk data.
Extracts label evidence (boxed warnings, contraindications, warnings & cautions),
derives risk indicators, and generates clean interim datasets (CSV and JSON)
for Box 9 (Risk & Patient-Context Analysis).
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

logger = logging.getLogger(__name__)

# Required output fields per Master Prompt specification
OUTPUT_COLUMNS = [
    "drug_name",
    "rxcui",
    "risk_tier",
    "boxed_warning_present",
    "boxed_warning",
    "contraindication_present",
    "contraindications",
    "warning_present",
    "warnings_and_cautions",
    "effective_time",
    "label_id",
    "set_id",
    "source",
]


def _has_usable_content(field: Any) -> bool:
    """
    Determines if an OpenFDA field has usable textual content.
    Returns True if field has non-whitespace characters, False otherwise.
    """
    if field is None:
        return False
    if isinstance(field, list):
        if not field:
            return False
        # If list contains non-empty strings or objects
        text = " ".join(str(item).strip() for item in field if item is not None)
        return len(text.strip()) > 0
    if isinstance(field, str):
        return len(field.strip()) > 0
    return bool(field)


def _preserve_field_text(field: Any) -> str:
    """
    Preserves exact OpenFDA evidence text without rewriting or reinterpreting.
    If multiple paragraphs/items exist in an array, joins them with newline characters.
    """
    if field is None:
        return ""
    if isinstance(field, list):
        return "\n\n".join(str(item) for item in field if item is not None).strip()
    return str(field).strip()


def _extract_single_or_first(val: Any) -> str:
    """
    Extracts canonical string representation for identifier/name fields.
    If given a list, prefers the first non-empty element.
    """
    if val is None:
        return ""
    if isinstance(val, list):
        for item in val:
            if item is not None and str(item).strip():
                return str(item).strip()
        return ""
    return str(val).strip()


def extract_openfda_record(raw_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extracts, cleans, and derives risk indicators for a single OpenFDA record.
    Handles both direct API result objects (with nested 'openfda') and
    pre-extracted staging dicts.
    """
    if not isinstance(raw_item, dict):
        return None

    # Handle nested openfda dictionary if present
    openfda_obj = raw_item.get("openfda", {})
    if not isinstance(openfda_obj, dict):
        openfda_obj = {}

    # 1. drug_name: prefer openfda.generic_name, fallback to raw_item["drug_name"] or brand_name
    raw_drug_name = (
        openfda_obj.get("generic_name")
        or raw_item.get("drug_name")
        or openfda_obj.get("brand_name")
        or raw_item.get("brand_name")
        or ""
    )
    drug_name = _extract_single_or_first(raw_drug_name)

    # 2. rxcui: prefer openfda.rxcui, fallback to raw_item["rxcui"]
    raw_rxcui = openfda_obj.get("rxcui") or raw_item.get("rxcui") or ""
    rxcui = _extract_single_or_first(raw_rxcui)

    # 3. Evidence fields (original OpenFDA text preserved)
    raw_boxed_warning = raw_item.get("boxed_warning") or []
    raw_contraindications = raw_item.get("contraindications") or []
    raw_warnings_and_cautions = (
        raw_item.get("warnings_and_cautions")
        or raw_item.get("warnings")
        or []
    )

    boxed_warning_text = _preserve_field_text(raw_boxed_warning)
    contraindications_text = _preserve_field_text(raw_contraindications)
    warnings_cautions_text = _preserve_field_text(raw_warnings_and_cautions)

    # 4. Deterministic indicator derivation
    boxed_warning_present = _has_usable_content(raw_boxed_warning)
    contraindication_present = _has_usable_content(raw_contraindications)
    warning_present = _has_usable_content(raw_warnings_and_cautions)

    # 5. Risk tier derivation:
    # risk_tier = "Boxed Warning" if boxed_warning_present == True, else "Standard"
    risk_tier = "Boxed Warning" if boxed_warning_present else "Standard"

    # 6. Provenance & metadata
    effective_time = _extract_single_or_first(raw_item.get("effective_time"))
    label_id = _extract_single_or_first(raw_item.get("label_id") or raw_item.get("id"))
    set_id = _extract_single_or_first(raw_item.get("set_id"))

    return {
        "drug_name": drug_name,
        "rxcui": rxcui,
        "risk_tier": risk_tier,
        "boxed_warning_present": boxed_warning_present,
        "boxed_warning": boxed_warning_text,
        "contraindication_present": contraindication_present,
        "contraindications": contraindications_text,
        "warning_present": warning_present,
        "warnings_and_cautions": warnings_cautions_text,
        "effective_time": effective_time,
        "label_id": label_id,
        "set_id": set_id,
        "source": "openFDA",
    }


def process_openfda_json(
    input_path: Union[str, Path]
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Reads an OpenFDA JSON file, performs deduplication and structural cleaning,
    and returns a DataFrame and data quality metrics dict.
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"OpenFDA raw file not found at: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Accommodate top-level list, {"results": [...]}, or a single record dict
    if isinstance(data, dict):
        if "results" in data and isinstance(data["results"], list):
            raw_records = data["results"]
        else:
            raw_records = [data]
    elif isinstance(data, list):
        raw_records = data
    else:
        raise ValueError(f"Unsupported JSON root type: {type(data)}")

    total_raw = len(raw_records)

    extracted_records: List[Dict[str, Any]] = []
    for rec in raw_records:
        parsed = extract_openfda_record(rec)
        if parsed:
            extracted_records.append(parsed)

    total_cleaned = len(extracted_records)

    # Deduplication: prefer (rxcui, label_id, set_id) or (drug_name, label_id)
    seen_keys = set()
    unique_records: List[Dict[str, Any]] = []
    for r in extracted_records:
        rxcui = r.get("rxcui", "")
        label_id = r.get("label_id", "")
        set_id = r.get("set_id", "")
        drug_name = r.get("drug_name", "").upper()

        if rxcui and (label_id or set_id):
            dedup_key = f"RX_{rxcui}_{label_id}_{set_id}"
        elif rxcui:
            dedup_key = f"RX_{rxcui}"
        elif label_id:
            dedup_key = f"LID_{label_id}"
        elif drug_name:
            dedup_key = f"NAME_{drug_name}"
        else:
            # Fallback hash of record
            dedup_key = str(hash(json.dumps(r, sort_keys=True)))

        if dedup_key not in seen_keys:
            seen_keys.add(dedup_key)
            unique_records.append(r)

    total_unique = len(unique_records)

    df = pd.DataFrame(unique_records, columns=OUTPUT_COLUMNS)

    # Compute quality metrics accurately without fabrication
    has_rxcui_count = int((df["rxcui"].str.len() > 0).sum()) if not df.empty else 0
    boxed_warning_count = int((df["boxed_warning_present"] == True).sum()) if not df.empty else 0
    contraindications_count = int((df["contraindication_present"] == True).sum()) if not df.empty else 0
    warnings_count = int((df["warning_present"] == True).sum()) if not df.empty else 0
    boxed_tier_count = int((df["risk_tier"] == "Boxed Warning").sum()) if not df.empty else 0
    standard_tier_count = int((df["risk_tier"] == "Standard").sum()) if not df.empty else 0
    missing_name_or_rxcui_count = (
        int(((df["drug_name"].str.len() == 0) | (df["rxcui"].str.len() == 0)).sum())
        if not df.empty
        else 0
    )

    metrics = {
        "total_raw_records_processed": total_raw,
        "total_cleaned_records": total_cleaned,
        "total_unique_records": total_unique,
        "number_with_rxcui": has_rxcui_count,
        "number_with_boxed_warnings": boxed_warning_count,
        "number_with_contraindications": contraindications_count,
        "number_with_warnings_cautions": warnings_count,
        "number_classified_as_boxed_warning": boxed_tier_count,
        "number_classified_as_standard": standard_tier_count,
        "number_missing_drug_name_or_rxcui": missing_name_or_rxcui_count,
    }

    return df, metrics


def run_openfda_pipeline(
    raw_file_path: Union[str, Path] = "data/raw/openfda_risk_data.json",
    output_dir: Union[str, Path] = "data/interim",
) -> Tuple[Path, Path, Dict[str, Any]]:
    """
    Executes the ingestion pipeline:
    - Reads raw OpenFDA JSON
    - Cleans and extracts fields
    - Derives risk indicators
    - Writes data/interim/openfda_risk_records.csv and data/interim/openfda_risk_records.json
    - Returns output paths and quality metrics dict
    """
    raw_path = Path(raw_file_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df, metrics = process_openfda_json(raw_path)

    csv_path = out_dir / "openfda_risk_records.csv"
    json_path = out_dir / "openfda_risk_records.json"

    df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

    logger.info(f"OpenFDA risk records saved to {csv_path} and {json_path}")
    return csv_path, json_path, metrics


if __name__ == "__main__":
    import pprint
    csv_file, json_file, quality_metrics = run_openfda_pipeline()
    print(f"\n--- OpenFDA Ingestion Completed Successfully ---")
    print(f"CSV Output : {csv_file}")
    print(f"JSON Output: {json_file}\n")
    print("Data Quality Metrics:")
    pprint.pprint(quality_metrics)
