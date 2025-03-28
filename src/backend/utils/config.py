"""
Configuration settings for the backend
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """Application settings"""
    APP_NAME: str = "Word Sense Disambiguation"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Teprolin service settings
    TEPROLIN_URL: str = os.getenv("TEPROLIN_URL", "http://localhost:5000")
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = os.getenv("API_PORT", 8000)

# Create a settings instance
settings = Settings()

# Export the settings instance
__all__ = ["settings"] 