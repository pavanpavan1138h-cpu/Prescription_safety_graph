# Phase 2: RxNorm Clinical Enrichment

This document details the Phase 2 clinical enrichment module which integrates internal drug entities with standardized RxCUI values and clinical drug properties using the NLM RxNorm/RxNav API services.

## 1. Purpose
The clinical reasoning engine requires standardized identifiers to reason across external clinical concept layers. Phase 2 bridges internal structure-normalized entities to RxCUIs.

## 2. API Dependencies
- **RxNav REST API**: Base URL `https://rxnav.nlm.nih.gov/REST`
  - `/rxcui.json` (exact name lookup and DrugBank external ID mapping)
  - `/rxcui/{rxcui}/properties.json` (fetching standardized properties)
  - `/approximateTerm.json` (approximate phonetic or string distance search)
- **PubChem PUG REST API**: Base URL `https://pubchem.ncbi.nlm.nih.gov/rest/pug`
  - `/compound/cid/{cid}/property/Title/JSON` (retrieving compound title for CIDs)
  - `/compound/inchikey/{inchikey}/property/Title/JSON` (retrieving compound title for InChIKeys)

## 3. Name Resolution Hierarchy
Since Phase 1 normalized drug nodes do not have pre-mapped names, name candidates are resolved using the following cascade:
1. **RxNav DrugBank ID Query**: Retrieve RxCUI and concept name directly using the source DrugBank ID (`idtype=DRUGBANK`). Status: `AUTHORITATIVE_NAME`.
2. **PubChem CID Query**: For TWOSIDES entities, query PubChem REST API with the CID to get the Title. Status: `PUBCHEM_TITLE_CANDIDATE`.
3. **PubChem InChIKey Query**: For entities missing IDs, query PubChem Title by InChIKey. Status: `PUBCHEM_TITLE_CANDIDATE`.
4. If unresolved: `NO_NAME_CANDIDATE`.

## 4. Match Confidence Levels
We classify matching results strictly:
- `HIGH_EXACT`: Unambiguous matching via exact identifier mapping or exact name match.
- `LOW_APPROXIMATE`: Unambiguous match resolved via controlled approximate/phonetic search.
- `AMBIGUOUS_CLINICAL_MAPPING`: One entity matches to conflicting RxCUIs across its source identifiers.
- `NO_MATCH`: No RxNorm concept resolved.

## 5. Caching Strategy
API responses are cached to disk in `data/interim/rxnorm_cache/` in subdirectories:
- `drugbank_identifier_lookup/`
- `pubchem_cid_lookup/`
- `pubchem_inchikey_lookup/`
- `name_lookup/`
- `approximate_lookup/`
- `rxcui_properties/`

## 6. Reproducibility
To rerun Phase 2 enrichment:
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_rxnorm_enrichment.py
```
To validate the outputs:
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_rxnorm_audit.py
```
Outputs are saved in `data/interim/enriched/` and validation results in `data/interim/validation/`.
