"""
Type definitions for preprocessing module

This module defines the types used for the Teprolin preprocessing functions.
"""

from typing import List, Optional, TypedDict, Tuple

# Basic types
TokenList = List[str]
POSTagList = List[Tuple[str, str]]
DependencyList = List[Tuple[str, str, str]]
NERList = List[Tuple[str, str]]


# Result types
class AnalysisResultDict(TypedDict):
    """Dictionary representing the results of linguistic analysis"""
    tokens: TokenList
    pos_tags: POSTagList
    dependencies: DependencyList
    ner_results: NERList

class ProcessedTextDict(TypedDict):
    """Dictionary representing processed text with linguistic annotations"""
    original_text: str
    processed_text: str
    processing_time: float
    analysis: AnalysisResultDict

class TeprolinStatusDict(TypedDict):
    """Dictionary representing the status of the Teprolin service"""
    teprolin_status: str
    url: str
    response_time_ms: Optional[float]
    error: Optional[str] 