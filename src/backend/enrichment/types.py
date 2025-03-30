"""
Type definitions for the enrichment module.

This module provides data types used for enriching disambiguation results.
"""

from typing import List, TypedDict

class EnrichmentDict(TypedDict, total=False):
    """Dictionary representing enrichment data for a word meaning"""
    explanation: str
    examples: List[str]

class EnrichedMeaningDict(TypedDict):
    """Dictionary representing an enriched word meaning"""
    id: str
    definition: str
    synonyms: List[str]
    confidence: float
    definition: str
    enrichment: EnrichmentDict

class FrontendAmbiguousWordDict(TypedDict):
    """Dictionary representing an ambiguous word optimized for frontend display"""
    word: str
    pos: str
    position: int
    ambiguity_score: float
    top_meanings: List[EnrichedMeaningDict]  
    other_meanings: List[EnrichedMeaningDict] 

class FrontendResultDict(TypedDict):
    """Dictionary representing the enriched disambiguation result optimized for frontend"""
    text: str
    ambiguous_words: List[FrontendAmbiguousWordDict]
    enrichment_time: float
    total_execution_time: float

