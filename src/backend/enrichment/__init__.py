"""
Enrichment Module for Romanian Word Sense Disambiguation

This module provides functionality for enriching Romanian text with word sense information,
specifically handling ambiguous words and providing possible meanings.
"""

import logging
from pathlib import Path

from ..utils.config import settings

# Create logging directory if it doesn't exist
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True, parents=True)

logger = logging.getLogger('backend.enrichment')
logger.setLevel(getattr(logging, settings.LOG_LEVEL))
logger.propagate = True  # Allow propagation to root logger for console output

# Clear any existing handlers
if logger.handlers:
    logger.handlers.clear()

log_file = log_dir / 'enrichment.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

logger.info(f"Enrichment module initialized. Logs will be written to {log_file}")

# Import and re-export the main enrichment function
from .enrichment import enrich_top_meanings
from .main import create_test_data

__all__ = [
    'logger',
    'enrich_top_meanings',
    'create_test_data'
] 