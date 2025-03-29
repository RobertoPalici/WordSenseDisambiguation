"""
Type definitions for the ambiguity detection and disambiguation system.

This module provides centralized type definitions used throughout the system.
"""

from typing import List, Tuple, Optional, TypedDict

# Synset information types
class SynsetDict(TypedDict):
    """Dictionary representation of a RoWordNet synset"""
    id: str
    definition: str
    pos: str
    literals: List[str]

# Meaning and ambiguous word types
class MeaningDict(TypedDict):
    """Dictionary representation of a potential meaning for an ambiguous word"""
    id: str
    definition: str
    pos: str
    synonyms: List[str]
    confidence: float

class AmbiguousWordDict(TypedDict):
    """Dictionary representation of an ambiguous word with its potential meanings"""
    word: str
    pos: str
    position: int
    potential_meanings: List[MeaningDict]
    best_meaning: Optional[MeaningDict]
    ambiguity_score: float

# Recommendation types
class RecommendationOptionDict(TypedDict):
    """Dictionary representation of a recommendation option"""
    meaning: str
    synonyms: List[str]

class RecommendationDict(TypedDict):
    """Dictionary representation of a recommendation for an ambiguous word"""
    word: str
    pos: str
    recommendation: str
    options: List[RecommendationOptionDict]

# Analysis types
class AnalysisDict(TypedDict):
    """Dictionary representation of text analysis results"""
    tokens: List[str]
    pos_tags: List[Tuple[str, str]]

class ResultDict(TypedDict):
    """Dictionary representation of the complete ambiguity analysis result"""
    text: str
    analysis: AnalysisDict
    ambiguous_words: List[AmbiguousWordDict]
    recommendations: List[RecommendationDict] 