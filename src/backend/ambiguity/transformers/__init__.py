"""
Transformers module for the ambiguity detection system.

This module initializes the transformer models used by other components
and ensures they are only loaded once.
"""

import logging
import os

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "transformers.log")

logger = logging.getLogger("ambiguity.transformers")
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Export logger
__all__ = ["logger"] 