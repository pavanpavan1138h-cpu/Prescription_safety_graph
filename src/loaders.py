import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

def load_drugbank_ddi(path: Path) -> pd.DataFrame:
    """
    Load the DrugBank DDI dataset from a tab-separated file.
    
    Expected columns: ID1, ID2, Y, Map, X1, X2
    """
    if not path.exists():
        raise FileNotFoundError(f"DrugBank dataset not found at {path}")
    
    logger.info(f"Loading DrugBank DDI from {path}...")
    
    # Load with tab delimiter
    try:
        # First attempt with standard tab separator
        df = pd.read_csv(path, sep='\t', quotechar='"')
    except Exception as e:
        logger.warning(f"Failed to load with standard tab separator: {e}. Trying raw backslash tab...")
        df = pd.read_csv(path, sep=r"\\t", engine="python")
        
    # Clean up column names in case they have tab characters
    df.columns = [col.replace("\\t", "").replace("\t", "").strip() for col in df.columns]
    
    # Validate columns
    expected_cols = {"ID1", "ID2", "Y", "Map", "X1", "X2"}
    missing_cols = expected_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"DrugBank dataset missing expected columns: {missing_cols}. Found: {list(df.columns)}")
        
    logger.info(f"Successfully loaded DrugBank DDI with {len(df)} rows.")
    return df

def load_twosides(path: Path) -> pd.DataFrame:
    """
    Load the TWOSIDES dataset from a CSV file.
    
    Expected columns: ID1, ID2, Y, Side Effect Name, X1, X2
    """
    if not path.exists():
        raise FileNotFoundError(f"TWOSIDES dataset not found at {path}")
        
    logger.info(f"Loading TWOSIDES from {path}...")
    df = pd.read_csv(path, sep=',', quotechar='"')
    
    # Clean up column names
    df.columns = [col.strip() for col in df.columns]
    
    # Validate columns
    expected_cols = {"ID1", "ID2", "Y", "Side Effect Name", "X1", "X2"}
    missing_cols = expected_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"TWOSIDES dataset missing expected columns: {missing_cols}. Found: {list(df.columns)}")
        
    logger.info(f"Successfully loaded TWOSIDES with {len(df)} rows.")
    return df
