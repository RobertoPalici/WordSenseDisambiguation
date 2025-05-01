"""
Disambiguation recommender for ambiguous words in Romanian text.

This module provides functionality to generate recommendations for disambiguating
ambiguous words found in Romanian text.
"""

from typing_extensions import List
from . import logger
from ..types import (
    MeaningDict, 
    AmbiguousWordDict, 
    RecommendationOptionDict, 
    RecommendationDict
)

class DisambiguationRecommender:
    """
    Generates recommendations for disambiguating ambiguous words
    """
    
    def __init__(self) -> None:
        """
        Initialize the disambiguation recommender
        """
        logger.info("Initialized DisambiguationRecommender")
    
    def get_recommendations(self, ambiguous_words: List[AmbiguousWordDict]) -> List[RecommendationDict]:
        """
        Generate recommendations for disambiguating the ambiguous words
        
        Args:
            ambiguous_words: List of ambiguous words from AmbiguityDetector
            
        Returns:
            List of recommendations for disambiguating the words
        """
        recommendations: List[RecommendationDict] = []
        
        for word_info in ambiguous_words:
            word: str = word_info["word"]
            meanings: List[MeaningDict] = word_info["potential_meanings"]
            pos: str = word_info.get("pos", "")
            
            if len(meanings) <= 1:
                continue
                
            # Sort meanings by confidence
            sorted_meanings: List[MeaningDict] = sorted(
                meanings, key=lambda x: x["confidence"], reverse=True
            )
            top_meanings: List[MeaningDict] = sorted_meanings[:3]  # Top 3 meanings
            
            # Create recommendation
            recommendation: RecommendationDict = {
                "word": word,
                "pos": pos,
                "recommendation": f"The word '{word}' is ambiguous. Consider using a more specific synonym based on the intended meaning:",
                "options": []
            }
            
            # Add options based on potential meanings
            for meaning in top_meanings:
                synonyms: List[str] = meaning["synonyms"]
                other_synonyms: List[str] = [s for s in synonyms if s.lower() != word.lower()]
                
                option: RecommendationOptionDict = {
                    "meaning": meaning["definition"] or "No definition available",
                    "synonyms": other_synonyms if other_synonyms else ["No direct synonyms available"]
                }
                recommendation["options"].append(option)
            
            recommendations.append(recommendation)
            
            logger.debug(f"Generated recommendation for ambiguous word: {word}")
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations