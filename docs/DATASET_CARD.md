# Dataset Card: Prescription Safety Graph (Phase 1)

This dataset card describes the consolidated, normalized, and integrated data assets compiled during Phase 1 of the Prescription Safety Graph project.

## 1. Project Context
The Prescription Safety Graph project aims to build a unified medical knowledge graph to support clinical decision-making and reasoning regarding drug-drug interactions (DDI) and polypharmacy side effects. Phase 1 focuses on extracting, cleaning, chemically normalizing, and bridging the DrugBank DDI dataset and the TWOSIDES side-effect dataset.

## 2. Dataset Names & Purposes
- **DrugBank DDI Dataset**: Used to capture directed, text-described drug-drug interaction alerts (e.g. synergistic toxicities, metabolic inhibitions).
- **TWOSIDES Dataset**: Used to capture epidemiological or observed polypharmacy side-effect associations when two drugs are co-prescribed.
- **Integrated Drug Entity Layer**: Serves as a unified translation bridge connecting DrugBank identifiers (`DBxxxxx`) and TWOSIDES identifiers (`CIDxxxxxxxxx`) based on chemically validated structural equivalence.

## 3. Data Source Directories
- Raw files:
  - DrugBank: `data/raw/tdc/drugbank.tab` (TAB-separated)
  - TWOSIDES: `data/raw/twosides/twosides.csv` (Comma-separated)
  - Crosswalk: `data/interim/normalized/drugbank_twosides_unified_crosswalk.csv`
- Normalized outputs: `data/interim/normalized/`
- Validation reports: `data/interim/validation/`

## 4. Schemas and Statistics

### A. Raw DrugBank DDI Dataset
- **Record Count**: $191,808$
- **Unique Drugs**: $1,706$
- **Columns**:
  - `ID1`: DrugBank ID for Drug 1
  - `ID2`: DrugBank ID for Drug 2
  - `Y`: Interaction binary label
  - `Map`: Textual description of the interaction
  - `X1`: SMILES structure for Drug 1
  - `X2`: SMILES structure for Drug 2

### B. Raw TWOSIDES Dataset
- **Record Count**: $4,649,441$
- **Unique Drugs**: $645$
- **Columns**:
  - `ID1`: PubChem CID ID for Drug 1
  - `ID2`: PubChem CID ID for Drug 2
  - `Y`: UMLS Concept ID for side effect
  - `Side Effect Name`: Human-readable name of the side effect
  - `X1`: SMILES structure for Drug 1
  - `X2`: SMILES structure for Drug 2

---

## 5. Chemical Normalization and Cross-Dataset Integration
Because the raw identifier systems have zero direct overlap ($0\%$), integration is accomplished via chemical structure validation using **RDKit (v2023.09.6)**:
1. SMILES strings are parsed into RDKit molecules.
2. Canonical SMILES (without stereochemistry) and Isomeric Canonical SMILES (with stereochemistry) are generated.
3. Standard InChIKeys are generated.
4. Mappings are classified by confidence:
   - **`HIGH_EXACT`**: Confirmed by exact InChIKey skeleton and stereochemical matching.
   - **`MEDIUM_CANONICAL`**: Mapped by canonical molecular skeletal structure, but stereochemical representation differs.

## 6. Ambiguity Handling and Validation
- **Candidate Components**: Bipartite mapping graphs are built using connected components.
- **Unambiguous Merges**: If a mapping component represents a strict $1:1$ equivalence, it is merged into a single `CONFIRMED_INTEGRATED_ENTITY` node.
- **Ambiguity Preservation**: If a mapping is $N:1$, $1:M$, or many-to-many, the drugs are kept unmerged. Each drug retains its independent node, flagged with `AMBIGUOUS_MAPPING_COMPONENT`, and all individual mapping edges are written separately to `integrated_drug_mapping_edges.csv`.

## 7. Known Data Issues
- **`DB11630`**: The only invalid structure in the DrugBank dataset that fails RDKit parsing (marked as `structure_valid=False`).
- **Directional Duplication**: DrugBank has $289$ repeated directed pairs containing varying textual descriptions.
- **TWOSIDES Associations**: TWOSIDES polypharmacy relationships are co-occurrence associations, not clinically proven causal mechanisms.
