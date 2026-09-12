"""
test_openfda_ingestion.py

Unit tests for OpenFDA risk data ingestion, preprocessing, indicator derivation,
and dataset generation for Box 9.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from src.data.openfda_ingestion import (
    extract_openfda_record,
    process_openfda_json,
    run_openfda_pipeline,
    OUTPUT_COLUMNS,
)


def test_openfda_naproxen_extraction():
    """Verify exact extraction and risk tier derivation on raw OpenFDA Naproxen record."""
    raw_path = Path("data/raw/openfda_risk_data.json")
    assert raw_path.exists(), "Raw OpenFDA JSON must exist"

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    record = extract_openfda_record(data)
    assert record is not None
    assert record["drug_name"] == "NAPROXEN"
    assert record["rxcui"] == "198014"
    assert record["risk_tier"] == "Boxed Warning"
    assert record["boxed_warning_present"] is True
    assert record["contraindication_present"] is True
    assert record["warning_present"] is True
    assert record["source"] == "openFDA"
    assert record["label_id"] == "8c45ef1f-f708-485b-bc20-60aa87ce6289"
    assert record["set_id"] == "000155a8-709c-44e5-a75f-cd890f3a7caf"
    assert record["effective_time"] == "20260129"
    assert "CARDIOVASCULAR" in record["boxed_warning"]
    assert "CONTRAINDICATIONS" in record["contraindications"]
    assert "PRECAUTIONS" in record["warnings_and_cautions"]


def test_openfda_indicator_derivation_standard_tier():
    """Verify that a record without boxed warnings is classified as Standard tier (never High-Alert)."""
    synthetic_record = {
        "drug_name": ["AMOXICILLIN"],
        "rxcui": ["723"],
        "boxed_warning": [],
        "contraindications": ["Known hypersensitivity to penicillins."],
        "warnings_and_cautions": ["Clostridioides difficile-associated diarrhea."],
        "effective_time": "20250101",
        "label_id": "test-label-id",
        "set_id": "test-set-id",
    }
    res = extract_openfda_record(synthetic_record)
    assert res is not None
    assert res["drug_name"] == "AMOXICILLIN"
    assert res["rxcui"] == "723"
    assert res["boxed_warning_present"] is False
    assert res["risk_tier"] == "Standard"
    assert res["contraindication_present"] is True
    assert res["warning_present"] is True


def test_openfda_pipeline_artifacts(tmp_path):
    """Verify pipeline output files, schema columns, and quality metrics."""
    raw_path = Path("data/raw/openfda_risk_data.json")
    csv_file, json_file, metrics = run_openfda_pipeline(raw_file_path=raw_path, output_dir=tmp_path)

    assert csv_file.exists()
    assert json_file.exists()

    df = pd.read_csv(csv_file)
    assert list(df.columns) == OUTPUT_COLUMNS
    assert len(df) == 1
    assert df.iloc[0]["drug_name"] == "NAPROXEN"
    assert str(df.iloc[0]["rxcui"]) == "198014"
    assert df.iloc[0]["risk_tier"] == "Boxed Warning"

    assert metrics["total_raw_records_processed"] == 1
    assert metrics["total_cleaned_records"] == 1
    assert metrics["total_unique_records"] == 1
    assert metrics["number_with_rxcui"] == 1
    assert metrics["number_with_boxed_warnings"] == 1
    assert metrics["number_classified_as_boxed_warning"] == 1
    assert metrics["number_classified_as_standard"] == 0
    assert metrics["number_missing_drug_name_or_rxcui"] == 0
