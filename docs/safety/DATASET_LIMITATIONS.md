# Dataset Limitations and Assumptions

This document outlines the known limitations, assumptions, and edge cases present in the Phase 1 dataset.

## 1. Chemical Entity Ambiguity
During the crosswalk mapping between DrugBank and TWOSIDES, several ambiguous cases were encountered:
- **Stereochemistry Mismatches**: Some drugs match on Canonical SMILES but differ in InChIKeys, representing stereoisomer variations. These are explicitly tracked.
- **Salt/Charge Variations**: Some mappings involve different salt forms or charged states.
- **Unresolved Structural Differences**: Certain mappings could not be fully resolved using structural evidence and remain flagged as `UNRESOLVED_STRUCTURE_DIFFERENCE`.

## 2. Connected Component Limitations
We identified instances where mapping identifiers led to many-to-one or one-to-many relationships. 
- **Ambiguous Mapping Components**: Connected components with complex structures are flagged as `AMBIGUOUS_MAPPING_COMPONENT`. They are NOT automatically merged into a single integrated biological entity.
- Only structurally unambiguous 1-to-1 components are elevated to `CONFIRMED_INTEGRATED_ENTITY`.

## 3. Scope of Current Data
- The dataset relies on the provided versions of DrugBank and TWOSIDES.
- Excipients and non-active ingredients are generally not mapped or analyzed unless they act as active drugs in these databases.
- The TWOSIDES dataset captures adverse events which may be subject to reporting biases.

## 4. Normalization Constraints
- Drug synonyms have been normalized to lowercase alphanumeric strings. Some edge-case special characters might lead to multiple synonyms mapping to the same normalized string.
