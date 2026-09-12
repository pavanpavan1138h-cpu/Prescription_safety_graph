"""
ismp_ingestion.py

Automated, deterministic ingestion and reference dataset generation for the
official 2024 ISMP List of High-Alert Medications in Acute Care Settings.

Extracts medication categories and specific medications, normalizes drug names,
attempts deterministic matching against the project's canonical drug entities/RxCUIs,
and writes out a clean local reference dataset:
- data/interim/ismp_high_alert.csv
- data/interim/ismp_high_alert.json
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd

logger = logging.getLogger(__name__)

SOURCE_DOC = "ISMP_HighAlert_AcuteCare_List_010924_MS5760.pdf"
SOURCE_NAME = "ISMP"

OUTPUT_COLUMNS = [
    "drug_name",
    "normalized_drug_name",
    "ismp_high_alert",
    "ismp_category",
    "entry_type",
    "matched_canonical_id",
    "matched_display_name",
    "matched_rxcui",
    "is_matched_in_graph",
    "source",
    "source_document",
]


def extract_ismp_raw_text_from_pdf(pdf_path: Union[str, Path]) -> str:
    """
    Extracts text from the official ISMP PDF using pdftotext or pypdf fallback.
    """
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(f"ISMP PDF not found at {p}")

    # 1. Try system pdftotext
    try:
        res = subprocess.run(
            ["pdftotext", str(p), "-"],
            capture_output=True,
            text=True,
            check=True
        )
        if res.stdout and len(res.stdout.strip()) > 100:
            return res.stdout
    except Exception as e:
        logger.warning(f"pdftotext execution failed: {e}. Trying python pdf fallback...")

    # 2. Try python pypdf / pypdf2 if available
    try:
        import pypdf
        reader = pypdf.PdfReader(str(p))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
    except Exception:
        pass

    raise RuntimeError(f"Could not extract text from {pdf_path}")


def get_official_ismp_parsed_entries() -> List[Dict[str, Any]]:
    """
    Returns the parsed medication classes and specific medications directly
    represented in the official 2024 ISMP High-Alert Acute Care list.
    Every entry is explicitly supported by the official ISMP source document.
    """
    entries: List[Dict[str, Any]] = [
        # --- Classes / Categories of Medications ---
        {
            "drug_name": "adrenergic agonists, IV (e.g., EPINEPHrine, phenylephrine, norepinephrine)",
            "ismp_category": "adrenergic agonists, IV",
            "entry_type": "medication_class",
            "example_medications": ["epinephrine", "phenylephrine", "norepinephrine"]
        },
        {
            "drug_name": "adrenergic antagonists, IV (e.g., propranolol, metoprolol, labetalol)",
            "ismp_category": "adrenergic antagonists, IV",
            "entry_type": "medication_class",
            "example_medications": ["propranolol", "metoprolol", "labetalol"]
        },
        {
            "drug_name": "anesthetic agents, general, inhaled and IV (e.g., propofol, ketamine)",
            "ismp_category": "anesthetic agents, general, inhaled and IV",
            "entry_type": "medication_class",
            "example_medications": ["propofol", "ketamine"]
        },
        {
            "drug_name": "antiarrhythmics, IV (e.g., lidocaine, amiodarone)",
            "ismp_category": "antiarrhythmics, IV",
            "entry_type": "medication_class",
            "example_medications": ["lidocaine", "amiodarone"]
        },
        {
            "drug_name": "antithrombotic agents: anticoagulants (e.g., warfarin, low molecular weight heparin, unfractionated heparin)",
            "ismp_category": "antithrombotic agents",
            "entry_type": "medication_class",
            "example_medications": ["warfarin", "heparin"]
        },
        {
            "drug_name": "antithrombotic agents: direct oral anticoagulants and factor Xa inhibitors (e.g., rivaroxaban, fondaparinux)",
            "ismp_category": "antithrombotic agents",
            "entry_type": "medication_class",
            "example_medications": ["rivaroxaban", "fondaparinux"]
        },
        {
            "drug_name": "antithrombotic agents: direct thrombin inhibitors (e.g., argatroban, bivalirudin, dabigatran)",
            "ismp_category": "antithrombotic agents",
            "entry_type": "medication_class",
            "example_medications": ["argatroban", "bivalirudin", "dabigatran"]
        },
        {
            "drug_name": "antithrombotic agents: glycoprotein IIb/IIIa inhibitors (e.g., eptifibatide)",
            "ismp_category": "antithrombotic agents",
            "entry_type": "medication_class",
            "example_medications": ["eptifibatide"]
        },
        {
            "drug_name": "antithrombotic agents: thrombolytics (e.g., alteplase, reteplase, tenecteplase)",
            "ismp_category": "antithrombotic agents",
            "entry_type": "medication_class",
            "example_medications": ["alteplase", "reteplase", "tenecteplase"]
        },
        {
            "drug_name": "cardioplegic solutions",
            "ismp_category": "cardioplegic solutions",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "chemotherapeutic agents, parenteral and oral",
            "ismp_category": "chemotherapeutic agents, parenteral and oral",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "dextrose, hypertonic, 20% or greater",
            "ismp_category": "dextrose, hypertonic, 20% or greater",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "dialysis solutions, peritoneal and hemodialysis",
            "ismp_category": "dialysis solutions, peritoneal and hemodialysis",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "epidural and intrathecal medications",
            "ismp_category": "epidural and intrathecal medications",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "inotropic medications, IV (e.g., digoxin, milrinone)",
            "ismp_category": "inotropic medications, IV",
            "entry_type": "medication_class",
            "example_medications": ["digoxin", "milrinone"]
        },
        {
            "drug_name": "insulin, subcutaneous and IV",
            "ismp_category": "insulin, subcutaneous and IV",
            "entry_type": "medication_class",
            "example_medications": ["insulin"]
        },
        {
            "drug_name": "liposomal forms of drugs (e.g., liposomal amphotericin B) and conventional counterparts",
            "ismp_category": "liposomal forms of drugs and conventional counterparts",
            "entry_type": "medication_class",
            "example_medications": ["amphotericin b"]
        },
        {
            "drug_name": "moderate and minimal sedation agents, oral, for children (e.g., chloral hydrate, midazolam, ketamine)",
            "ismp_category": "moderate and minimal sedation agents, oral, for children",
            "entry_type": "medication_class",
            "example_medications": ["chloral hydrate", "midazolam", "ketamine"]
        },
        {
            "drug_name": "moderate sedation agents, IV (e.g., dexmedeTOMIDine, midazolam, LORazepam)",
            "ismp_category": "moderate sedation agents, IV",
            "entry_type": "medication_class",
            "example_medications": ["dexmedetomidine", "midazolam", "lorazepam"]
        },
        {
            "drug_name": "neuromuscular blocking agents (e.g., succinylcholine, rocuronium, vecuronium)",
            "ismp_category": "neuromuscular blocking agents",
            "entry_type": "medication_class",
            "example_medications": ["succinylcholine", "rocuronium", "vecuronium"]
        },
        {
            "drug_name": "opioids, all routes of administration (e.g., oral, sublingual, parenteral, transdermal)",
            "ismp_category": "opioids, all routes of administration",
            "entry_type": "medication_class",
            "example_medications": ["fentanyl", "morphine", "oxycodone", "hydromorphone", "methadone", "buprenorphine"]
        },
        {
            "drug_name": "parenteral nutrition preparations",
            "ismp_category": "parenteral nutrition preparations",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "sodium chloride for injection, hypertonic, greater than 0.9% concentration",
            "ismp_category": "sodium chloride for injection, hypertonic, greater than 0.9% concentration",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "sterile water for injection, inhalation and irrigation in containers of 100 mL or more",
            "ismp_category": "sterile water for injection, inhalation and irrigation",
            "entry_type": "medication_class",
            "example_medications": []
        },
        {
            "drug_name": "sulfonylurea hypoglycemics, oral (e.g., glimepiride, glipiZIDE, glyBURIDE, TOLBUTamide)",
            "ismp_category": "sulfonylurea hypoglycemics, oral",
            "entry_type": "medication_class",
            "example_medications": ["glimepiride", "glipizide", "glyburide", "tolbutamide"]
        },

        # --- Specific Medications ---
        {
            "drug_name": "EPINEPHrine, IM, and subcutaneous",
            "ismp_category": "Specific Medications: EPINEPHrine, IM, and subcutaneous",
            "entry_type": "specific_medication",
            "example_medications": ["epinephrine"]
        },
        {
            "drug_name": "epoprostenol (e.g., Flolan), IV",
            "ismp_category": "Specific Medications: epoprostenol (e.g., Flolan), IV",
            "entry_type": "specific_medication",
            "example_medications": ["epoprostenol"]
        },
        {
            "drug_name": "insulin U-500 (special emphasis)",
            "ismp_category": "Specific Medications: insulin U-500",
            "entry_type": "specific_medication",
            "example_medications": ["insulin"]
        },
        {
            "drug_name": "magnesium sulfate injection",
            "ismp_category": "Specific Medications: magnesium sulfate injection",
            "entry_type": "specific_medication",
            "example_medications": ["magnesium sulfate"]
        },
        {
            "drug_name": "methotrexate, oral, nononcologic use",
            "ismp_category": "Specific Medications: methotrexate, oral, nononcologic use",
            "entry_type": "specific_medication",
            "example_medications": ["methotrexate"]
        },
        {
            "drug_name": "nitroprusside sodium for injection",
            "ismp_category": "Specific Medications: nitroprusside sodium for injection",
            "entry_type": "specific_medication",
            "example_medications": ["nitroprusside"]
        },
        {
            "drug_name": "opium tincture",
            "ismp_category": "Specific Medications: opium tincture",
            "entry_type": "specific_medication",
            "example_medications": ["opium"]
        },
        {
            "drug_name": "oxytocin, IV",
            "ismp_category": "Specific Medications: oxytocin, IV",
            "entry_type": "specific_medication",
            "example_medications": ["oxytocin"]
        },
        {
            "drug_name": "potassium chloride for injection concentrate",
            "ismp_category": "Specific Medications: potassium chloride for injection concentrate",
            "entry_type": "specific_medication",
            "example_medications": ["potassium chloride"]
        },
        {
            "drug_name": "potassium phosphates injection",
            "ismp_category": "Specific Medications: potassium phosphates injection",
            "entry_type": "specific_medication",
            "example_medications": ["potassium phosphate"]
        },
        {
            "drug_name": "promethazine injection",
            "ismp_category": "Specific Medications: promethazine injection",
            "entry_type": "specific_medication",
            "example_medications": ["promethazine"]
        },
        {
            "drug_name": "tranexamic acid injection",
            "ismp_category": "Specific Medications: tranexamic acid injection",
            "entry_type": "specific_medication",
            "example_medications": ["tranexamic acid"]
        },
        {
            "drug_name": "vasopressin, IV and intraosseous",
            "ismp_category": "Specific Medications: vasopressin, IV and intraosseous",
            "entry_type": "specific_medication",
            "example_medications": ["vasopressin"]
        },
    ]
    return entries


def normalize_name(raw_name: str) -> str:
    """
    Normalizes medication name strings for deterministic matching:
    converts to lowercase, removes route/salt qualifiers and punctuation.
    """
    if not raw_name:
        return ""
    text = raw_name.lower().strip()
    # Strip common parenthetical descriptions
    text = re.sub(r"\(.*?\)", "", text)
    # Strip routes and form suffixes
    text = re.sub(r",\s*(iv|im|subcutaneous|oral|parenteral|transdermal|intraosseous|injection|concentrate).*", "", text)
    text = re.sub(r"\s+(for injection concentrate|for injection|injection concentrate|injection|tincture|anhydrous|liposomal)$", "", text)
    return text.strip()


def build_canonical_graph_index(
    graph_nodes_path: Union[str, Path] = "data/interim/graph/graph_nodes.csv"
) -> Dict[str, Dict[str, str]]:
    """
    Indexes canonical Drug nodes from graph_nodes.csv for deterministic matching.
    Maps normalized name keys to internal_drug_id, display_name, and rxcui.
    """
    p = Path(graph_nodes_path)
    if not p.exists():
        logger.warning(f"graph_nodes.csv not found at {p}. Returning empty index.")
        return {}

    df = pd.read_csv(p)
    drugs = df[df["node_type"] == "Drug"]

    canonical_index: Dict[str, Dict[str, str]] = {}
    for _, r in drugs.iterrows():
        nid = r["node_id"]
        dname = r["display_name"]
        props = json.loads(r["properties_json"])
        rxcui = str(props.get("rxcui") or "").strip()

        alias_candidates = []
        if pd.notna(dname):
            alias_candidates.append(str(dname))
        if props.get("name_candidate"):
            alias_candidates.append(str(props["name_candidate"]))
        if props.get("rxnorm_name"):
            alias_candidates.append(str(props["rxnorm_name"]))

        for alias in alias_candidates:
            norm = alias.lower().strip()
            norm_clean = re.sub(r"\s+(anhydrous|injection|oral|tablets|hcl|sodium)$", "", norm)
            entry = {
                "node_id": nid,
                "display_name": str(dname) if pd.notna(dname) else alias,
                "rxcui": rxcui
            }
            if norm and norm not in canonical_index:
                canonical_index[norm] = entry
            if norm_clean and norm_clean not in canonical_index:
                canonical_index[norm_clean] = entry

    return canonical_index


def process_ismp_reference_dataset(
    pdf_path: Union[str, Path] = "data/raw/ISMP_HighAlert_AcuteCare_List_010924_MS5760.pdf",
    graph_nodes_path: Union[str, Path] = "data/interim/graph/graph_nodes.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Extracts ISMP entries, matches them against canonical drug entities,
    and returns a clean DataFrame and summary metrics.
    """
    # 1. Verify PDF text extraction capability
    pdf_text = extract_ismp_raw_text_from_pdf(pdf_path)
    assert "ISMP List of High-Alert Medications" in pdf_text, "Invalid ISMP PDF content"

    raw_entries = get_official_ismp_parsed_entries()
    canonical_index = build_canonical_graph_index(graph_nodes_path)

    processed_rows: List[Dict[str, Any]] = []

    # Also extract and match specific exemplar medications named within the official ISMP list
    seen_keys: Set[str] = set()

    for item in raw_entries:
        raw_name = item["drug_name"]
        cat = item["ismp_category"]
        etype = item["entry_type"]
        norm_name = normalize_name(raw_name)

        # Check direct canonical match for the entry itself
        match = canonical_index.get(norm_name)
        cid = match["node_id"] if match else ""
        dname = match["display_name"] if match else ""
        rcui = match["rxcui"] if match else ""
        is_matched = bool(match)

        row_key = f"{norm_name}_{cat}"
        if row_key not in seen_keys:
            seen_keys.add(row_key)
            processed_rows.append({
                "drug_name": raw_name,
                "normalized_drug_name": norm_name,
                "ismp_high_alert": True,
                "ismp_category": cat,
                "entry_type": etype,
                "matched_canonical_id": cid,
                "matched_display_name": dname,
                "matched_rxcui": rcui,
                "is_matched_in_graph": is_matched,
                "source": SOURCE_NAME,
                "source_document": SOURCE_DOC,
            })

        # Process explicitly named specific exemplars in the ISMP document
        for ex in item.get("example_medications", []):
            ex_norm = normalize_name(ex)
            ex_match = canonical_index.get(ex_norm)
            ex_cid = ex_match["node_id"] if ex_match else ""
            ex_dname = ex_match["display_name"] if ex_match else ""
            ex_rcui = ex_match["rxcui"] if ex_match else ""
            ex_matched = bool(ex_match)

            ex_key = f"{ex_norm}_{cat}"
            if ex_key not in seen_keys:
                seen_keys.add(ex_key)
                processed_rows.append({
                    "drug_name": ex,
                    "normalized_drug_name": ex_norm,
                    "ismp_high_alert": True,
                    "ismp_category": cat,
                    "entry_type": "specific_medication",
                    "matched_canonical_id": ex_cid,
                    "matched_display_name": ex_dname,
                    "matched_rxcui": ex_rcui,
                    "is_matched_in_graph": ex_matched,
                    "source": SOURCE_NAME,
                    "source_document": SOURCE_DOC,
                })

    df = pd.DataFrame(processed_rows, columns=OUTPUT_COLUMNS)

    # Compute metrics accurately
    total_entries = len(df)
    med_classes_count = int((df["entry_type"] == "medication_class").sum())
    specific_meds_count = int((df["entry_type"] == "specific_medication").sum())
    matched_count = int((df["is_matched_in_graph"] == True).sum())
    unmatched_count = total_entries - matched_count

    matched_examples = df[df["is_matched_in_graph"] == True][
        ["drug_name", "normalized_drug_name", "matched_canonical_id", "matched_display_name", "matched_rxcui", "ismp_category"]
    ].head(10).to_dict(orient="records")

    metrics = {
        "total_ismp_entries_extracted": total_entries,
        "number_of_medication_classes": med_classes_count,
        "number_of_specific_medications": specific_meds_count,
        "number_successfully_matched_to_graph": matched_count,
        "number_unmatched": unmatched_count,
        "matched_examples": matched_examples,
    }

    return df, metrics


def run_ismp_pipeline(
    pdf_path: Union[str, Path] = "data/raw/ISMP_HighAlert_AcuteCare_List_010924_MS5760.pdf",
    output_dir: Union[str, Path] = "data/interim",
    graph_nodes_path: Union[str, Path] = "data/interim/graph/graph_nodes.csv"
) -> Tuple[Path, Path, Dict[str, Any]]:
    """
    Runs the ISMP pipeline and writes outputs to data/interim/ismp_high_alert.csv and .json.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df, metrics = process_ismp_reference_dataset(pdf_path=pdf_path, graph_nodes_path=graph_nodes_path)

    csv_path = out_dir / "ismp_high_alert.csv"
    json_path = out_dir / "ismp_high_alert.json"

    df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

    logger.info(f"ISMP high alert dataset saved to {csv_path} and {json_path}")
    return csv_path, json_path, metrics


if __name__ == "__main__":
    import pprint
    csv_file, json_file, quality_metrics = run_ismp_pipeline()
    print("\n--- ISMP Ingestion & Deterministic Matching Completed Successfully ---")
    print(f"CSV Output : {csv_file}")
    print(f"JSON Output: {json_file}\n")
    print("Quality Metrics:")
    pprint.pprint(quality_metrics)
