"""
Ambiguity detection and disambiguation module for Romanian text.

This module provides functionality to detect ambiguous words in Romanian
text and generate recommendations for disambiguation.
"""

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