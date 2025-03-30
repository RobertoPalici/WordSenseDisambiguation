"""
Formatting module for the Word Sense Disambiguation API.

This module provides functionality to format enriched disambiguation results
into optimized structures for frontend consumption.
"""

import logging
from typing import List

from ..ambiguity.types import ResultDict
from .types import (
    EnrichedMeaningDict,
    FrontendAmbiguousWordDict,
    FrontendResultDict,
)

logger = logging.getLogger('backend.enrichment.format')

def convert_to_frontend_format(enriched_result: ResultDict) -> FrontendResultDict:
    """
    Convert an enriched ResultDict to a FrontendResultDict
    
    This function restructures the disambiguation results to be optimized for frontend display,
    separating the top 3 meanings with their enrichments from other potential meanings.
    
    Args:
        enriched_result: The ResultDict containing enriched ambiguous words
        
    Returns:
        A FrontendResultDict with top meanings separated and enriched
    """
    # Get the original text and timing information
    text = enriched_result.get("text", "")
    enrichment_time = enriched_result.get("enrichment_time", 0)
    
    # Process each ambiguous word
    frontend_ambiguous_words: List[FrontendAmbiguousWordDict] = []
    
    for word_data in enriched_result.get("ambiguous_words", []):
        word = word_data.get("word", "")
        pos = word_data.get("pos", "")
        position = word_data.get("position", 0)
        ambiguity_score = word_data.get("ambiguity_score", 0.0)
        
        # Get all potential meanings and sort by confidence
        potential_meanings = word_data.get("potential_meanings", [])
        sorted_meanings = sorted(
            potential_meanings, 
            key=lambda x: x.get("confidence", 0.0), 
            reverse=True
        )
        
        # Separate into top meanings (max 3) and other meanings
    
        # Get default enrichment data for this word
        default_enrichment = word_data.get("enrichment", {})
        default_explanation = default_enrichment.get("explanation", "")
        default_examples = default_enrichment.get("examples", [])
        
        # Check if we have individual meaning enrichments
        meaning_enrichments = word_data.get("meaning_enrichments", [])
        enrichment_by_id = {}
        
        # Create a dictionary mapping sense IDs to their enrichments
        if meaning_enrichments:
            for item in meaning_enrichments:
                sense_id = item.get("id", "")
                if sense_id:
                    enrichment_by_id[sense_id] = item.get("enrichment", {})
        
        # Create enriched meanings for top 3
        enriched_meanings: List[EnrichedMeaningDict] = []
        for meaning in sorted_meanings:
            sense_id = meaning.get("id", "")
            
            # Use specific enrichment if available, otherwise default
            specific_enrichment = enrichment_by_id.get(sense_id, {})
            explanation = specific_enrichment.get("explanation", default_explanation)
            examples = specific_enrichment.get("examples", default_examples)
            
            enriched_meaning: EnrichedMeaningDict = {
                "id": sense_id,
                "definition": meaning.get("definition", ""),
                "synonyms": meaning.get("synonyms", []),
                "confidence": meaning.get("confidence", 0.0),
                "enrichment": {
                    "explanation": explanation,
                    "examples": examples
                }
            }
            enriched_meanings.append(enriched_meaning)
        
        
        top_meanings = enriched_meanings[:3]
        other_meanings = enriched_meanings[3:] if len(enriched_meanings) > 3 else []
        
        # Create frontend ambiguous word entry
        frontend_word: FrontendAmbiguousWordDict = {
            "word": word,
            "pos": pos,
            "position": position,
            "ambiguity_score": ambiguity_score,
            "top_meanings": top_meanings,
            "other_meanings": other_meanings
        }
        
        frontend_ambiguous_words.append(frontend_word)
    
    # Create final frontend result
    frontend_result: FrontendResultDict = {
        "text": text,
        "ambiguous_words": frontend_ambiguous_words,
        "enrichment_time": enrichment_time
    }
    
    return frontend_result 