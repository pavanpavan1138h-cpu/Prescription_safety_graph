import logging
import pandas as pd
from rdkit import Chem
from rdkit.Chem import inchi

logger = logging.getLogger(__name__)

def generate_structure_identifiers(smiles) -> dict:
    """
    Generate canonical SMILES, isomeric SMILES, and InChIKey for a given SMILES string.
    
    Returns:
        dict: {
            "canonical_smiles": str or None,
            "isomeric_smiles": str or None,
            "inchikey": str or None,
            "structure_valid": bool
        }
    """
    result = {
        "canonical_smiles": None,
        "isomeric_smiles": None,
        "inchikey": None,
        "structure_valid": False
    }
    
    if pd.isna(smiles) or not isinstance(smiles, str) or not smiles.strip():
        return result
        
    try:
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is not None:
            result["canonical_smiles"] = Chem.MolToSmiles(
                mol,
                canonical=True,
                isomericSmiles=False
            )
            result["isomeric_smiles"] = Chem.MolToSmiles(
                mol,
                canonical=True,
                isomericSmiles=True
            )
            result["inchikey"] = inchi.MolToInchiKey(mol)
            result["structure_valid"] = True
    except Exception as e:
        logger.debug(f"Error normalizing SMILES {smiles}: {e}")
        
    return result

def normalize_drugbank(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Normalize DrugBank drugs and interactions.
    
    Returns:
        (drugs_df, interactions_df)
    """
    logger.info("Normalizing DrugBank datasets...")
    
    # 1. Normalize Drugs
    # Combine ID1/X1 and ID2/X2 to get all unique drugs
    d1 = df[["ID1", "X1"]].rename(columns={"ID1": "drugbank_id", "X1": "raw_smiles"})
    d2 = df[["ID2", "X2"]].rename(columns={"ID2": "drugbank_id", "X2": "raw_smiles"})
    
    drugs_df = pd.concat([d1, d2], ignore_index=True)
    drugs_df = drugs_df.dropna(subset=["drugbank_id", "raw_smiles"]).drop_duplicates(subset=["drugbank_id"])
    
    # Generate chemical identifiers
    logger.info(f"Generating chemical identifiers for {len(drugs_df)} unique DrugBank drugs...")
    identifiers = drugs_df["raw_smiles"].apply(generate_structure_identifiers)
    identifiers_df = pd.DataFrame(list(identifiers))
    
    drugs_normalized = pd.concat([
        drugs_df.reset_index(drop=True),
        identifiers_df
    ], axis=1)
    
    drugs_normalized["source_dataset"] = "drugbank"
    
    # Reorder columns
    drugs_normalized = drugs_normalized[[
        "drugbank_id", "source_dataset", "raw_smiles", 
        "canonical_smiles", "isomeric_smiles", "inchikey", "structure_valid"
    ]]
    
    # 2. Normalize Interactions
    interactions_normalized = df[["ID1", "ID2", "Y", "Map"]].copy()
    interactions_normalized.columns = [
        "source_drugbank_id", "target_drugbank_id", 
        "interaction_label", "interaction_description"
    ]
    interactions_normalized["source_dataset"] = "drugbank"
    
    logger.info("Finished normalizing DrugBank data.")
    return drugs_normalized, interactions_normalized

def normalize_twosides(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Normalize TWOSIDES drugs, side effects, and relationships.
    
    Returns:
        (drugs_df, side_effects_df, relationships_df)
    """
    logger.info("Normalizing TWOSIDES datasets...")
    
    # 1. Normalize Drugs
    d1 = df[["ID1", "X1"]].rename(columns={"ID1": "twosides_id", "X1": "raw_smiles"})
    d2 = df[["ID2", "X2"]].rename(columns={"ID2": "twosides_id", "X2": "raw_smiles"})
    
    drugs_df = pd.concat([d1, d2], ignore_index=True)
    drugs_df = drugs_df.dropna(subset=["twosides_id", "raw_smiles"]).drop_duplicates(subset=["twosides_id"])
    
    logger.info(f"Generating chemical identifiers for {len(drugs_df)} unique TWOSIDES drugs...")
    identifiers = drugs_df["raw_smiles"].apply(generate_structure_identifiers)
    identifiers_df = pd.DataFrame(list(identifiers))
    
    drugs_normalized = pd.concat([
        drugs_df.reset_index(drop=True),
        identifiers_df
    ], axis=1)
    
    drugs_normalized["source_dataset"] = "twosides"
    
    drugs_normalized = drugs_normalized[[
        "twosides_id", "source_dataset", "raw_smiles",
        "canonical_smiles", "isomeric_smiles", "inchikey", "structure_valid"
    ]]
    
    # 2. Normalize Side Effects
    side_effects_normalized = df[["Y", "Side Effect Name"]].copy()
    side_effects_normalized.columns = ["side_effect_id", "side_effect_name"]
    side_effects_normalized = side_effects_normalized.drop_duplicates(subset=["side_effect_id"])
    side_effects_normalized["source_dataset"] = "twosides"
    
    # 3. Normalize Relationships
    relationships_normalized = df[["ID1", "ID2", "Y", "Side Effect Name"]].copy()
    relationships_normalized.columns = [
        "drug1", "drug2", "side_effect_id", "side_effect_name"
    ]
    relationships_normalized["source_dataset"] = "twosides"
    
    logger.info("Finished normalizing TWOSIDES data.")
    return drugs_normalized, side_effects_normalized, relationships_normalized
