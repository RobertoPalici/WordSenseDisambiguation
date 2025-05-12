"""
Utilities for working with RoWordNet synsets.

This module provides functions for retrieving and formatting synset information
from RoWordNet.
"""
import spacy
import rowordnet as rwn
from typing_extensions import Dict, Any, List
from . import logger
from rowordnet import Synset

# Initialize RoWordNet
wordnet = rwn.RoWordNet()
nlp = spacy.load("ro_core_news_sm")

POS_MAP = {
    "NOUN": Synset.Pos.NOUN,
    "VERB": Synset.Pos.VERB,
    "ADJ": Synset.Pos.ADJECTIVE,
    "ADV": Synset.Pos.ADVERB
}

def get_synset_info(synset_id: str) -> Dict[str, Any]:
    """
    Get information about a synset
    
    Args:
        synset_id: The ID of the synset to get information for
        
    Returns:
        Dictionary with synset information
    """
    synset = wordnet.synset(synset_id)
    
    return {
        "id": synset_id,
        "definition": synset.definition,
        "pos": str(synset.pos),  # Convert Pos enum to string
        "literals": synset.literals  # Literals are strings, not objects
    }

def get_synsets_for_word(word: str) -> List[str]:
    """
    Get all synsets for a given word
    
    Args:
        word: The word to look up synsets for
        
    Returns:
        List of synset IDs
    """

    normalized_word= word.lower()
    print(f"Normalized word: {normalized_word}")
    synset_ids = wordnet.synsets(literal=normalized_word)  

    logger.debug(f"Found {len(synset_ids)} synsets for word: {word}")

    return synset_ids 