# Data Dictionary - Prescription Safety Graph (Phase 1)

This dictionary documents all normalized outputs generated under `data/interim/normalized/`.

---

## 1. `drugbank_drugs_normalized.csv`
Contains unique DrugBank drugs with their normalized chemical structures.
- **Row Count**: 1,706
- **Columns**:
  - `drugbank_id` (string): Unique DrugBank identifier (e.g. `DB00006`).
  - `source_dataset` (string): Identifies the source dataset (`drugbank`).
  - `raw_smiles` (string): Original SMILES string from raw data.
  - `canonical_smiles` (string): RDKit-generated canonical SMILES (non-isomeric).
  - `isomeric_smiles` (string): RDKit-generated isomeric canonical SMILES.
  - `inchikey` (string): RDKit-generated standard InChIKey.
  - `structure_valid` (boolean): `True` if parsed successfully by RDKit, `False` otherwise.

---

## 2. `drugbank_interactions_normalized.csv`
Contains the normalized directed drug-drug interactions.
- **Row Count**: 191,808
- **Columns**:
  - `source_drugbank_id` (string): DrugBank ID of the first drug.
  - `target_drugbank_id` (string): DrugBank ID of the second drug.
  - `interaction_label` (integer): Binary interaction indicator (typically `1`).
  - `interaction_description` (string): Text description of the interaction.
  - `source_dataset` (string): Identifies source dataset (`drugbank`).

---

## 3. `twosides_drugs_normalized.csv`
Contains unique TWOSIDES drugs with their normalized chemical structures.
- **Row Count**: 645
- **Columns**:
  - `twosides_id` (string): Unique PubChem CID identifier (e.g. `CID000000085`).
  - `source_dataset` (string): Identifies source dataset (`twosides`).
  - `raw_smiles` (string): Original raw SMILES structure.
  - `canonical_smiles` (string): RDKit canonical SMILES (non-isomeric).
  - `isomeric_smiles` (string): RDKit isomeric SMILES.
  - `inchikey` (string): RDKit standard InChIKey.
  - `structure_valid` (boolean): `True` if chemical parse was successful.

---

## 4. `twosides_side_effects_normalized.csv`
Contains the list of unique side effect concepts captured in TWOSIDES.
- **Row Count**: 1,317
- **Columns**:
  - `side_effect_id` (string): UMLS Concept Unique Identifier (CUI) for the side effect (e.g., `C0018932`).
  - `side_effect_name` (string): Human-readable term/name of the side effect.
  - `source_dataset` (string): Identifies source dataset (`twosides`).

---

## 5. `twosides_relationships_normalized.csv`
Contains the normalized directed polypharmacy side-effect instances.
- **Row Count**: 4,649,441
- **Columns**:
  - `drug1` (string): TWOSIDES PubChem CID ID for Drug 1.
  - `drug2` (string): TWOSIDES PubChem CID ID for Drug 2.
  - `side_effect_id` (string): UMLS ID of the side effect.
  - `side_effect_name` (string): Name of the side effect.
  - `source_dataset` (string): Identifies source dataset (`twosides`).

---

## 6. `integrated_drug_nodes.csv`
Contains the integrated drug entity layer serving as a translation bridge.
- **Row Count**: 1,836
- **Columns**:
  - `internal_drug_id` (string): Deterministic ID of the form `DRUG_XXXXXX`.
  - `entity_type` (string): Flags nodes as `CONFIRMED_INTEGRATED_ENTITY` or `AMBIGUOUS_MAPPING_COMPONENT`.
  - `source_membership` (string): `drugbank_only`, `twosides_only`, or `both`.
  - `canonical_smiles` (string): Selected representative canonical SMILES.
  - `inchikey` (string): Selected representative standard InChIKey.

---

## 7. `integrated_drug_source_mappings.csv`
Maps the integrated internal drug IDs back to their source datasets.
- **Row Count**: 2,351
- **Columns**:
  - `internal_drug_id` (string): Deterministic internal drug identifier.
  - `source_dataset` (string): Dataset source (`drugbank` or `twosides`).
  - `source_drug_id` (string): Source drug identifier (DB ID or CID).
  - `mapping_confidence` (string): `HIGH_EXACT`, `MEDIUM_CANONICAL`, `ambiguous`, or `unmapped`.

---

## 8. `integrated_drug_mapping_edges.csv`
Preserves all individual structural mapping edges between datasets for verification.
- **Row Count**: 554
- **Columns**:
  - `drugbank_id` (string): Mapped DrugBank ID.
  - `twosides_id` (string): Mapped TWOSIDES CID ID.
  - `mapping_confidence` (string): Confidence of structural mapping edge (`HIGH_EXACT` or `MEDIUM_CANONICAL`).

---

## 9. Crosswalk files
- **`drugbank_twosides_unified_crosswalk.csv`**: Contains the $554$ raw mappings computed during exploration.
- **`drugbank_twosides_high_confidence_crosswalk.csv`**: Contains the $293$ high confidence mappings confirmed by exact InChIKey matching.
