"""
Configuration settings for the backend
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Get the project root directory
project_root = str(Path(__file__).resolve().parents[3])
env_path = os.path.join(project_root, '.env')

# Load environment variables from .env file
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    # If .env file not found in project root, try to find it in current directory
    load_dotenv(override=True)

class Settings(BaseModel):
    """Application settings"""
    APP_NAME: str = "Word Sense Disambiguation"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Teprolin service settings
    TEPROLIN_URL: str = os.getenv("TEPROLIN_URL", "http://localhost:5000")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

# Create a settings instance
settings = Settings()

# Export the settings instance
__all__ = ["settings"] 