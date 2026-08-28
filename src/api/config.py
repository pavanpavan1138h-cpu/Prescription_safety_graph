"""
src/api/config.py

Configuration settings for Phase 7 FastAPI service using Pydantic Settings.
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_title: str = "Prescription Safety Graph Reasoning API"
    api_version: str = "v1.0.0"
    
    # Project paths
    project_root: Path = Path(__file__).resolve().parent.parent.parent
    graph_data_dir: Path = project_root / "data" / "interim" / "graph"
    reasoning_data_dir: Path = project_root / "data" / "interim" / "prescription_reasoning"
    
    # CORS origins
    cors_origins: List[str] = ["*"]
    
    # Limits
    max_medications: int = 20
    max_input_string_length: int = 250

settings = Settings()
