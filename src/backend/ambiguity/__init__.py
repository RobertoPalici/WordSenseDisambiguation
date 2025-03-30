"""
Ambiguity Module for Romanian Word Sense Disambiguation

This module provides functionality for detecting ambiguous words in Romanian text
and retrieving possible meanings for those words.
"""

import logging
from pathlib import Path

from ..utils.config import settings

# Create logging directory if it doesn't exist
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True, parents=True)

logger = logging.getLogger('backend.ambiguity')
logger.setLevel(getattr(logging, settings.LOG_LEVEL))
logger.propagate = True  # Allow propagation to root logger for console output

if logger.handlers:
    logger.handlers.clear()

log_file = log_dir / 'ambiguity.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

logger.info(f"Ambiguity module initialized. Logs will be written to {log_file}")

from .detector import AmbiguityDetector
from .recommendations import DisambiguationRecommender
from .main import process_text
from .types import (
    MeaningDict, 
    AmbiguousWordDict, 
    RecommendationOptionDict, 
    RecommendationDict, 
    SynsetDict,
    ResultDict
)

from .types import (
    MeaningDict, 
    AmbiguousWordDict, 
    RecommendationOptionDict, 
    RecommendationDict, 
    SynsetDict,
    ResultDict
)

__all__ = [
    "AmbiguityDetector", 
    "DisambiguationRecommender", 
    "process_text",
    "MeaningDict", 
    "AmbiguousWordDict", 
    "RecommendationOptionDict", 
    "RecommendationDict", 
    "SynsetDict",
    "ResultDict"
] 