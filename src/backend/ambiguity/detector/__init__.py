"""
Detector module for ambiguity detection in Romanian text.

This module provides functionality to detect ambiguous words in Romanian
text based on their semantic similarity.
"""

import logging
from pathlib import Path

from ...utils.config import settings

# Create logging directory if it doesn't exist
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True, parents=True)

# Set up logger for the detector module
logger = logging.getLogger('backend.ambiguity.detector')
logger.setLevel(getattr(logging, settings.LOG_LEVEL))
logger.propagate = True  # Allow propagation to root logger for console output

# Clear any existing handlers to avoid duplicates
if logger.handlers:
    logger.handlers.clear()

# Set up file handler
log_file = log_dir / 'detector.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Log initialization
logger.info(f"Detector module initialized. Logs will be written to {log_file}")

# Import and export the detector class
from .detector import AmbiguityDetector

__all__ = ["logger", "AmbiguityDetector"] 