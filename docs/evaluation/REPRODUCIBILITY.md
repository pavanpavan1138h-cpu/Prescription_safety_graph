# Reproducibility Guide

This guide ensures that the Phase 1 dataset processing can be reproduced identically from raw data.

## 1. Environment Setup
The project requires a specific conda environment.
```bash
conda activate prescription_graph
```
Dependencies:
- pandas
- networkx
- rdkit

## 2. Pipeline Execution
To reproduce the normalized data and crosswalk mappings from the raw files, run the main pipeline script:
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_pipeline.py
```
This script reads from `data/raw/` and outputs to `data/interim/`.

## 3. Audit and Validation
To reproduce the validation and generate audit reports, run the audit script:
```bash
/opt/anaconda3/envs/prescription_graph/bin/python src/run_audit.py
```
Outputs are written to `data/interim/validation/`. Ensure the audit passes successfully without errors.

## 4. Non-Destructive Policy
The pipeline and audit scripts are entirely non-destructive. They do not modify raw data or exploratory notebooks. Rerunning them overwrites interim outputs deterministically.
