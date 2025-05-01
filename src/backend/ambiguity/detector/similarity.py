"""
Similarity calculation utilities for ambiguity detection.

This module provides functions for calculating semantic similarity between 
texts using BERT embeddings.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing_extensions import List, Tuple, Dict, Any, Optional, Union, cast, TypeVar
from . import logger
from ..transformers.model_manager import model_manager

import re

# Type variable for generic numpy arrays
NDArray = TypeVar('NDArray', bound=np.ndarray)

def split_into_sentences(text: str) -> List[str]:
    return re.split(r"(?<=[.!?])\s+", text)

def calculate_context_embedding(
    tokens: List[str], 
    token_index: int, 
    model_name: str
) -> np.ndarray:
    """
    Calculate embedding for a token in its context
    
    Args:
        tokens: List of tokens in the text
        token_index: Index of the target token
        model_name: Name of the transformer model to use
        
    Returns:
        Context embedding for the token
    """
    # Use a window of text around the token for context
    window_size: int = 5
    start_idx: int = max(0, token_index - window_size)
    end_idx: int = min(len(tokens), token_index + window_size + 1)
    context: str = " ".join(tokens[start_idx:end_idx])
    
    # Get embedding for the context
    embedding: np.ndarray = model_manager.get_embedding(context, model_name).numpy()
    embedding = embedding / np.linalg.norm(embedding)  # Normalize the embedding
    return embedding

def calculate_definition_embeddings(
    definitions: List[str], 
    model_name: str
) -> List[np.ndarray]:
    """
    Calculate embeddings for a list of definitions
    
    Args:
        definitions: List of definition texts
        model_name: Name of the transformer model to use
        
    Returns:
        List of embeddings for the definitions
    """
    embeddings: List[np.ndarray] = []
    for definition in definitions:
        if definition:
            embedding: np.ndarray = model_manager.get_embedding(definition, model_name).numpy()
            embeddings.append(embedding)
    
    return embeddings

def calculate_similarities(
    context_embedding: np.ndarray, 
    definition_embeddings: List[np.ndarray]
) -> List[float]:
    """
    Calculate cosine similarities between context and definitions
    
    Args:
        context_embedding: Embedding of the token in context
        definition_embeddings: Embeddings of potential meanings
        
    Returns:
        List of similarity scores
    """
    similarities: List[float] = []
    for definition_embedding in definition_embeddings:
        sim: float = float(cosine_similarity([context_embedding], [definition_embedding])[0][0])
        similarities.append(sim)
    
    return similarities

def calculate_similarity_statistics(
    similarities: List[float]
) -> Tuple[float, float, float, float]:
    """
    Calculate statistical measures for the similarities
    
    Args:
        similarities: List of similarity values
        
    Returns:
        Tuple of (max_sim, min_sim, sim_diff, sim_std)
    """
    if not similarities:
        return 0.0, 0.0, 0.0, 0.0
    
    max_sim: float = max(similarities)
    min_sim: float = min(similarities)
    sim_diff: float = max_sim - min_sim
    
    # Calculate standard deviation
    sim_mean: float = sum(similarities) / len(similarities)
    sim_variance: float = sum((s - sim_mean) ** 2 for s in similarities) / len(similarities)
    sim_std: float = float(np.sqrt(sim_variance))
    
    return max_sim, min_sim, sim_diff, sim_std 