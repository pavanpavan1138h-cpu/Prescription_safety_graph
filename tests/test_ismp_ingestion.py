"""
test_ismp_ingestion.py

Unit tests for ISMP High-Alert medication ingestion, text extraction,
deterministic canonical matching, and reference dataset generation for Box 9.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from src.data.ismp_ingestion import (
    extract_ismp_raw_text_from_pdf,
    normalize_name,
    process_ismp_reference_dataset,
    run_ismp_pipeline,
    OUTPUT_COLUMNS,
)


def test_ismp_pdf_extraction():
    """Verify that text can be extracted from the official ISMP PDF."""
    pdf_path = Path("data/raw/ISMP_HighAlert_AcuteCare_List_010924_MS5760.pdf")
    assert pdf_path.exists(), "Official ISMP PDF must exist in data/raw"

    text = extract_ismp_raw_text_from_pdf(pdf_path)
    assert "ISMP List of High-Alert Medications" in text
    assert "Acute Care Settings" in text
    assert "adrenergic agonists" in text
    assert "potassium chloride" in text


def test_normalize_name():
    """Verify deterministic normalization of drug names."""
    assert normalize_name("EPINEPHrine, IM, and subcutaneous") == "epinephrine"
    assert normalize_name("epoprostenol (e.g., Flolan), IV") == "epoprostenol"
    assert normalize_name("promethazine injection") == "promethazine"
    assert normalize_name("potassium chloride for injection concentrate") == "potassium chloride"


def test_ismp_deterministic_matching_and_dataset(tmp_path):
    """Verify ISMP reference dataset generation and deterministic canonical graph matches."""
    csv_file, json_file, metrics = run_ismp_pipeline(output_dir=tmp_path)

    assert csv_file.exists()
    assert json_file.exists()

    df = pd.read_csv(csv_file)
    assert list(df.columns) == OUTPUT_COLUMNS

    # Provenance and values
    assert (df["source"] == "ISMP").all()
    assert (df["ismp_high_alert"] == True).all()

    # Metrics verification
    assert metrics["total_ismp_entries_extracted"] == len(df)
    assert metrics["number_of_medication_classes"] == 25
    assert metrics["number_of_specific_medications"] == 59
    assert metrics["number_successfully_matched_to_graph"] > 0
    assert metrics["number_unmatched"] > 0

    # Key exemplar drug matches
    matched_drugs = dict(zip(df["normalized_drug_name"], df["matched_canonical_id"]))
    assert matched_drugs.get("warfarin") == "DRUG_000496"
    assert matched_drugs.get("epinephrine") == "DRUG_000483"
    assert matched_drugs.get("methotrexate") == "DRUG_000392"
    assert matched_drugs.get("promethazine") == "DRUG_000841"
    assert matched_drugs.get("digoxin") == "DRUG_000230"
    assert matched_drugs.get("potassium chloride") == "DRUG_000569"
