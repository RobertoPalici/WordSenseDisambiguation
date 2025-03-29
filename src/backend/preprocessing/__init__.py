"""
Preprocessing Module for Romanian Text Analysis

This module provides functionality for analyzing Romanian text using the Teprolin NLP service,
which includes operations such as tokenization, part-of-speech tagging, dependency parsing,
named entity recognition, and more.
"""

import os
import logging

from ..utils.config import settings

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger('backend.preprocessing')
logger.setLevel(getattr(logging, settings.LOG_LEVEL))
logger.propagate = True  # Allow propagation to root logger for console output

if logger.handlers:
    logger.handlers.clear()

log_file = os.path.join(log_dir, 'preprocessing.log')
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

logger.info(f"Preprocessing module initialized. Logs will be written to {log_file}")

from .main import analyze_text
from .service import checkService


from .types import (
    ProcessedTextDict, 
    TeprolinStatusDict,
    TokenList,
    POSTagList,
    DependencyList,
    NERList,
)

__all__ = [
    'logger',
    'analyze_text',
    'checkService',
    'ProcessedTextDict',
    'TeprolinStatusDict',
    'TokenList',
    'POSTagList',
    'DependencyList',
    'NERList',
] 