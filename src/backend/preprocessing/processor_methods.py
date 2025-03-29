"""
Processing methods for Teprolin NLP operations

This module provides specialized text processing methods for the Teprolin NLP service,
including tokenization, POS tagging, named entity recognition, and dependency parsing.
"""

import requests
import logging
from typing import Optional

from ..utils.config import settings
from .types import (
    TokenList, POSTagList, DependencyList, NERList
)

logger = logging.getLogger('backend.preprocessing.processor_methods')

def tokenize(text: str, base_url: Optional[str] = None) -> TokenList:
    """
    Tokenize text using Teprolin
    
    Args:
        text: Text to tokenize
        base_url: Optional base URL for the Teprolin service
        
    Returns:
        List of tokens
    """
    base_url = base_url or settings.TEPROLIN_URL
    
    try:
        logger.debug(f"Tokenizing text: {text[:50]}...")
        
        data = {
            "text": text,
            "exec": "tokenization"
        }
        
        response = requests.post(
            f"{base_url}/process",
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            tokens = []
            
            tokenized_data = result.get("teprolin-result", {}).get("tokenized", [])
            for sentence in tokenized_data:
                for token_info in sentence:
                    word = token_info.get("_wordform", "")
                    if word:
                        tokens.append(word)
            
            logger.debug(f"Tokenized {len(tokens)} tokens")
            return tokens
        else:
            logger.error(f"Tokenization failed: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error during tokenization: {str(e)}")
        return []

def pos_tagging(text: str, base_url: Optional[str] = None) -> POSTagList:
    """
    Perform POS tagging on text
    
    Args:
        text: Text to analyze
        base_url: Optional base URL for the Teprolin service
        
    Returns:
        List of (word, pos_tag) tuples
    """
    base_url = base_url or settings.TEPROLIN_URL
    
    try:
        logger.debug(f"POS tagging text: {text[:50]}...")
        
        data = {
            "text": text,
            "exec": "pos-tagging"
        }
        
        response = requests.post(
            f"{base_url}/process",
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            pos_tags = []
            
            tagged_data = result.get("teprolin-result", {}).get("tokenized", [])
            if tagged_data:
                # Flatten and extract word and POS
                pos_tags = [(word["_wordform"], word["_ctg"]) 
                            for sentence in tagged_data 
                            for word in sentence]
            
            logger.debug(f"Tagged {len(pos_tags)} words")
            return pos_tags
        else:
            logger.error(f"POS tagging failed: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error during POS tagging: {str(e)}")
        return []

def named_entity_recognition(text: str, base_url: Optional[str] = None) -> NERList:
    """
    Perform Named Entity Recognition (NER) on text
    
    Args:
        text: Text to analyze
        base_url: Optional base URL for the Teprolin service
        
    Returns:
        List of (word, entity_type) tuples
    """
    base_url = base_url or settings.TEPROLIN_URL
    
    try:
        logger.debug(f"Performing NER on text: {text[:50]}...")
        
        data = {
            "text": text,
            "exec": "named-entity-recognition"
        }
        
        response = requests.post(
            f"{base_url}/process",
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            ner_results = []
            
            # Extract NER results from response
            ner_data = result.get("teprolin-result", {}).get("tokenized", [])
            if ner_data:
                ner_results = [(word["_wordform"], word["_ner"]) 
                              for sentence in ner_data 
                              for word in sentence]
            
            logger.debug(f"Found {len(ner_results)} named entities")
            return ner_results
        else:
            logger.error(f"NER failed: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error during NER: {str(e)}")
        return []

def dependency_parsing(text: str, base_url: Optional[str] = None) -> DependencyList:
    """
    Perform dependency parsing on text
    
    Args:
        text: Text to analyze
        base_url: Optional base URL for the Teprolin service
        
    Returns:
        List of (word, dependency_relation, head) tuples
    """
    base_url = base_url or settings.TEPROLIN_URL
    
    try:
        logger.debug(f"Performing dependency parsing on text: {text[:50]}...")
        
        data = {
            "text": text,
            "exec": "dependency-parsing",
        }
        
        response = requests.post(
            f"{base_url}/process",
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            dependencies = []
            
            # Extract dependency information from tokenized data
            dependencies_data = result.get("teprolin-result", {}).get("tokenized", [])
            for sentence in dependencies_data:
                for token_info in sentence:
                    word = token_info.get("_wordform", "")
                    dependency_relation = token_info.get("_deprel", "")
                    head = token_info.get("_head", "")

                    if word:
                        dependencies.append((word, dependency_relation, head))
            
            logger.debug(f"Found {len(dependencies)} dependencies")
            return dependencies
        else:
            logger.error(f"Dependency parsing failed: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error during dependency parsing: {str(e)}")
        return []
