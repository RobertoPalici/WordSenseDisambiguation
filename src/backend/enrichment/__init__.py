"""
Enrichment package for the Word Sense Disambiguation API.

This package provides functionality to enrich disambiguation results
with explanations and example sentences.
"""

import logging
import os

from ..utils.config import settings

# Set up logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger('backend.enrichment')
logger.setLevel(getattr(logging, settings.LOG_LEVEL))
logger.propagate = True  # Allow propagation to root logger for console output

# Clear any existing handlers
if logger.handlers:
    logger.handlers.clear()

log_file = os.path.join(log_dir, 'enrichment.log')
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

logger.info(f"Enrichment module initialized. Logs will be written to {log_file}")

# Import and re-export the main enrichment function
from .enrichment import enrich_top_meanings

__all__ = [
    'logger',
    'enrich_top_meanings'
] 