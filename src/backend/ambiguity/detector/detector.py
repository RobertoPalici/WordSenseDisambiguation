"""
Ambiguity detector module for Romanian text.

This module provides the main class for detecting ambiguous words in Romanian text
based on their semantic similarity.
"""

import numpy as np
from typing_extensions import Dict, Any, List, Tuple, Optional, Union, Set, cast
from . import logger
from .synset_utils import get_synset_info, get_synsets_for_word
from .similarity import (
    calculate_context_embedding, 
    calculate_definition_embeddings,
    calculate_similarities,
    calculate_similarity_statistics
)
from ..types import SynsetDict, MeaningDict, AmbiguousWordDict
from ..ner_utils import get_named_entities, is_named_entity

class AmbiguityDetector:
    """
    Detects ambiguous words in Romanian text based on RoWordNet and BERT embeddings
    """
    
    def __init__(self, 
                 bert_model: str = "dumitrescustefan/bert-base-romanian-uncased-v1",
                 similarity_threshold: float = 0.15) -> None:
        """
        Initialize the ambiguity detector
        
        Args:
            bert_model: Name of the BERT model to use
            similarity_threshold: Threshold for determining ambiguity
        """
        self.model_name: str = bert_model
        self.similarity_threshold: float = similarity_threshold
        
        logger.info(f"Initialized AmbiguityDetector with model {bert_model}")
    
    def is_ambiguous(self, 
                     similarities: List[float], 
                     synset_count: int) -> bool:
        """
        Determine if a word is ambiguous based on similarity statistics
        
        Args:
            similarities: List of similarity scores
            synset_count: Number of synsets for the word
            
        Returns:
            True if the word is ambiguous, False otherwise
        """
        if not similarities or len(similarities) <= 1:
            return False
            
        max_sim, min_sim, sim_diff, sim_std = calculate_similarity_statistics(similarities)
        
        # Enhanced ambiguity detection logic
        return (
            sim_diff > self.similarity_threshold or           # Different meanings have different similarities
            sim_std > self.similarity_threshold or            # High variance in similarities
            (max_sim < 0.6 and synset_count > 2) or          # Low similarity with multiple meanings
            (synset_count > 5 and sim_diff > 0.1)            # Many meanings with some difference
        )
    
    def create_meaning(self, 
                      synset: SynsetDict, 
                      confidence: float) -> MeaningDict:
        """
        Create a potential meaning entry for an ambiguous word
        
        Args:
            synset: Synset information
            confidence: Confidence score for this meaning
            
        Returns:
            Dictionary with meaning information
        """
        return {
            "id": synset["id"],
            "definition": synset["definition"],
            "pos": synset["pos"],
            "synonyms": synset["literals"],
            "confidence": float(confidence)
        }
    
    def create_ambiguous_word(self, 
                             token: str, 
                             pos: str, 
                             token_index: int,
                             potential_meanings: List[MeaningDict], 
                             best_meaning_idx: int,
                             ambiguity_score: float) -> AmbiguousWordDict:
        """
        Create an ambiguous word entry
        
        Args:
            token: The ambiguous word
            pos: Part of speech
            token_index: Position in the text
            potential_meanings: List of potential meanings
            best_meaning_idx: Index of the best meaning
            ambiguity_score: Score indicating degree of ambiguity
            
        Returns:
            Dictionary with ambiguous word information
        """
        best_meaning: Optional[MeaningDict] = None
        if potential_meanings and 0 <= best_meaning_idx < len(potential_meanings):
            best_meaning = potential_meanings[best_meaning_idx]
            
        return {
            "word": token,
            "pos": pos,
            "position": token_index,
            "potential_meanings": potential_meanings,
            "best_meaning": best_meaning,
            "ambiguity_score": float(ambiguity_score)
        }
    
    def detect_ambiguities(self, tokens: List[str], pos_tags: List[Tuple[str, str]]) -> List[AmbiguousWordDict]:
        """
        Detect ambiguous words in the given preprocessed text
        
        Args:
            tokens: List of tokenized words
            pos_tags: List of (word, pos_tag) tuples
            
        Returns:
            List of ambiguous words with their potential meanings
        """
        logger.info(f"Detecting ambiguities in {len(tokens)} tokens...")
        
        # Map each token to its POS tag
        token_pos_map: Dict[str, str] = self._create_token_pos_map(pos_tags)
        #adaugat
        text: str = " ".join(tokens) 
        ner_entities = get_named_entities(text)
        
        # Store ambiguous words
        ambiguous_words: List[AmbiguousWordDict] = []
        
        # Process each token
        for token_index, token in enumerate(tokens):
            if is_named_entity(token, ner_entities):
                logger.debug(f"Skipping named entity: {token}")
                continue
            # Get POS tag for token
            pos: str = self._get_pos_tag(token, token_pos_map)
            
            # Skip non-content words
            if not self._is_content_word(pos):
                continue
                
            # Get synsets for the token
            synset_ids: List[str] = get_synsets_for_word(token.lower())
            
            logger.debug(f"Word: {token}, POS: {pos}, Found synsets: {len(synset_ids)}")
            
            # Skip words with only one or no synsets
            if len(synset_ids) <= 1:
                continue
            
            # Get synset information
            synsets: List[SynsetDict] = [cast(SynsetDict, get_synset_info(synset_id)) for synset_id in synset_ids]
            
            # Get definitions for each synset
            definitions: List[str] = [synset["definition"] or " ".join(synset["literals"]) for synset in synsets]
            
            # Get embeddings for synset definitions
            definition_embeddings: List[np.ndarray] = calculate_definition_embeddings(definitions, self.model_name)
            
            # Skip if we couldn't get enough embeddings
            if len(definition_embeddings) <= 1:
                continue
            
            # Get embedding for the token in context
            context_embedding: np.ndarray = calculate_context_embedding(tokens, token_index, self.model_name)
            
            # Calculate similarity between token context and each definition
            similarities: List[float] = calculate_similarities(context_embedding, definition_embeddings)
            
            # Debug info for similarity calculations
            max_sim, min_sim, sim_diff, sim_std = calculate_similarity_statistics(similarities)
            logger.debug(f"Word: {token}, Max sim: {max_sim:.4f}, Min sim: {min_sim:.4f}, " 
                         f"Diff: {sim_diff:.4f}, Std: {sim_std:.4f}, Threshold: {self.similarity_threshold}")
            
            # Determine if this word is ambiguous
            if self.is_ambiguous(similarities, len(synset_ids)):
                # Create potential meanings
                best_meaning_idx: int = similarities.index(max(similarities)) if similarities else 0
                potential_meanings: List[MeaningDict] = [
                    self.create_meaning(synset, similarities[i] if i < len(similarities) else 0.0)
                    for i, synset in enumerate(synsets)
                ]
                
                # Create ambiguous word entry
                ambiguous_word: AmbiguousWordDict = self.create_ambiguous_word(
                    token, pos, token_index, potential_meanings, best_meaning_idx, sim_diff
                )
                
                ambiguous_words.append(ambiguous_word)
        
        logger.info(f"Found {len(ambiguous_words)} ambiguous words")
        return ambiguous_words
    
    def _create_token_pos_map(self, pos_tags: List[Tuple[str, str]]) -> Dict[str, str]:
        """Create a mapping from tokens to their POS tags"""
        token_pos_map: Dict[str, str] = {}
        for token_pos in pos_tags:
            if isinstance(token_pos, tuple) and len(token_pos) == 2:
                word, pos = token_pos
                token_pos_map[word] = pos
        
        # If token_pos_map is empty, it means pos_tags is not in the expected format
        if not token_pos_map and pos_tags:
            for item in pos_tags:
                logger.debug(f"POS tag item format: {type(item)}, {item}")
        
        logger.debug(f"Created POS tags map with {len(token_pos_map)} entries")
        return token_pos_map
    
    def _get_pos_tag(self, token: str, token_pos_map: Dict[str, str]) -> str:
        """Get the POS tag for a token, trying different case variations"""
        pos: str = token_pos_map.get(token, "")
        
        # Try with lowercase version if POS tag not found
        if not pos and token.lower() in token_pos_map:
            pos = token_pos_map[token.lower()]
            
        # Try with first letter capitalized version if POS tag not found
        if not pos and token.capitalize() in token_pos_map:
            pos = token_pos_map[token.capitalize()]
            
        return pos
    
    def _is_content_word(self, pos: str) -> bool:
        """Check if a word is a content word based on its POS tag"""
        content_word_prefixes: Set[str] = {"NOUN", "VERB", "ADJ", "ADV"}
        return any(pos.startswith(prefix) for prefix in content_word_prefixes) 