"""
Disambiguation recommender for ambiguous words in Romanian text.

This module provides functionality to generate recommendations for disambiguating
ambiguous words found in Romanian text.
"""

from typing import List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from . import logger
from ..transformers.model_manager import model_manager
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
    
    def select_best_meaning(self, 
                           ambiguous_word: AmbiguousWordDict, 
                           context: str, 
                           model_name: str = "dumitrescustefan/bert-base-romanian-uncased-v1") -> Optional[MeaningDict]:
        """
        Select the best meaning for an ambiguous word based on context
        
        Args:
            ambiguous_word: Dictionary containing ambiguous word information
            context: The surrounding text providing context
            model_name: Name of the transformer model to use
            
        Returns:
            Dictionary with the best meaning
        """
        # Get context embedding
        context_embedding: np.ndarray = model_manager.get_embedding(context, model_name).numpy()
        
        # Calculate similarity between context and each definition
        meanings: List[MeaningDict] = ambiguous_word["potential_meanings"]
        max_similarity: float = -1.0
        best_meaning: Optional[MeaningDict] = None
        
        for meaning in meanings:
            definition: str = meaning["definition"] or " ".join(meaning["synonyms"])
            
            if not definition:
                continue
            
            # Get definition embedding
            definition_embedding: np.ndarray = model_manager.get_embedding(definition, model_name).numpy()
            
            # Calculate cosine similarity
            similarity: float = float(cosine_similarity(
                [context_embedding], 
                [definition_embedding]
            )[0][0])
            
            logger.debug(f"Similarity for meaning '{definition[:30]}...': {similarity:.4f}")
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_meaning = meaning
        
        logger.info(f"Selected best meaning for {ambiguous_word['word']} with similarity {max_similarity:.4f}")
        
        return best_meaning or (meanings[0] if meanings else None) 