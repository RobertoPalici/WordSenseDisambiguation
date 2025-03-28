"""
Teprolin processor for text preprocessing
"""

import time
import requests
from typing import Dict, Any, Optional, List, Tuple
import logging

from ..utils.config import settings

logger = logging.getLogger(__name__)

class TeprolinProcessor:
    """
    Client for the Teprolin NLP service
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the Teprolin processor
        
        Args:
            base_url: Base URL for the Teprolin service. If None, uses the URL from config.
        """
        self.base_url = base_url or settings.TEPROLIN_URL
        logger.info(f"Initialized Teprolin processor with base URL: {self.base_url}")
    
    def process_text(self, text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process text using Teprolin
        
        Args:
            text: The text to process
            options: Additional processing options
            
        Returns:
            Dict containing the processed results
        """
        options = options or {}
        
        try:
            start_time = time.time()
            
            # Prepare the request data
            data = {
                "text": text,
                **options
            }
            
            # Send request to Teprolin
            response = requests.post(
                f"{self.base_url}/process",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            
            processing_time = time.time() - start_time
            logger.debug(f"Processed text in {processing_time:.4f} seconds")
            
            result = response.json()
            result["processing_time"] = processing_time
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error processing text with Teprolin: {str(e)}")
            raise RuntimeError(f"Failed to process text: {str(e)}")
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text using Teprolin
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        try:
            logger.debug(f"Tokenizing text: {text[:50]}...")
            
            data = {
                "text": text,
                "exec": "tokenization"
            }
            
            response = requests.post(
                f"{self.base_url}/process",
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                tokens = []
                
                # Extract tokens from response
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
    
    def pos_tagging(self, text: str) -> List[Tuple[str, str]]:
        """
        Perform POS tagging on text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (word, pos_tag) tuples
        """
        try:
            logger.debug(f"POS tagging text: {text[:50]}...")
            
            data = {
                "text": text,
                "exec": "pos-tagging"
            }
            
            response = requests.post(
                f"{self.base_url}/process",
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                pos_tags = []
                
                # Extract POS tags from response
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
    
    def named_entity_recognition(self, text: str) -> List[Tuple[str, str]]:
        """
        Perform Named Entity Recognition (NER) on text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (word, entity_type) tuples
        """
        try:
            logger.debug(f"Performing NER on text: {text[:50]}...")
            
            data = {
                "text": text,
                "exec": "named-entity-recognition"
            }
            
            response = requests.post(
                f"{self.base_url}/process",
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
    
    def dependency_parsing(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Perform dependency parsing on text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (word, dependency_relation, head) tuples
        """
        try:
            logger.debug(f"Performing dependency parsing on text: {text[:50]}...")
            
            data = {
                "text": text,
                "exec": "dependency-parsing",
                "model": "udpipe-ufal"
            }
            
            response = requests.post(
                f"{self.base_url}/process",
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
    
    def process_for_disambiguation(self, text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Pre-processing pipeline using Teprolin for Word Sense Disambiguation
        
        This method performs the linguistic analysis pre-processing steps:
        1. Tokenization - splits text into individual words
        2. POS Tagging - identifies parts of speech for each word
        3. Syntactic Parsing - analyzes grammatical relationships
        
        Args:
            text: Text to process
            options: Processing options
            
        Returns:
            Dict with processed text and linguistic analysis results
        """
        start_time = time.time()
        
        try:
            # Step 1: Tokenization
            logger.info(f"Starting preprocessing pipeline for text: {text[:50]}...")
            tokens = self.tokenize(text)
            logger.debug(f"Tokenization complete: {len(tokens)} tokens identified")
            
            # Step 2: POS Tagging
            pos_tags = self.pos_tagging(text)
            logger.debug(f"POS tagging complete: {len(pos_tags)} tags identified")
            
            # Step 3: Syntactic Parsing (Dependency Parsing)
            dependencies = self.dependency_parsing(text)
            logger.debug(f"Dependency parsing complete: {len(dependencies)} dependencies identified")
            
            # Prepare results in a structure matching our response model
            # Each "disambiguated word" will contain linguistic information about the word
            analyzed_words = []
            
            for i, (word, pos) in enumerate(pos_tags):
                # Focus on content words (nouns, verbs, adjectives, adverbs)
                # as they are typically the ones needing disambiguation
                if pos in ["NOUN", "VERB", "ADJ", "ADV"]:
                    # Find this word's dependencies
                    word_deps = [dep for dep in dependencies if dep[0] == word]
                    
                    # Create a representation of the word with its linguistic information
                    analyzed_word = {
                        "word": word,
                        "lemma": word.lower(),  # Simplified lemma for now
                        "position": i,
                        "pos": pos,
                        "senses": [
                            {
                                "id": "linguistic_analysis",
                                "definition": f"Analiză lingvistică pentru '{word}'",
                                "pos": pos,
                                "confidence": 1.0
                            }
                        ],
                        "selected_sense": {
                            "id": "linguistic_analysis",
                            "definition": f"Analiză lingvistică pentru '{word}'",
                            "pos": pos,
                            "dependencies": [
                                {"relation": dep[1], "head": dep[2]} for dep in word_deps
                            ],
                            "confidence": 1.0
                        }
                    }
                    
                    analyzed_words.append(analyzed_word)
            
            processing_time = time.time() - start_time
            logger.info(f"Preprocessing pipeline completed in {processing_time:.4f} seconds")
            
            # Create annotated text version
            # This creates a simple HTML-like representation with POS tags as subscripts
            annotated_text = ""
            for word, pos in pos_tags:
                annotated_text += f"{word}<sub>{pos}</sub> "
            
            return {
                "original_text": text,
                "processed_text": annotated_text.strip(),
                "disambiguated_words": analyzed_words,
                "processing_time": processing_time,
                # Additional preprocessing results for potential further use
                "preprocessing_data": {
                    "tokens": tokens,
                    "pos_tags": pos_tags,
                    "dependencies": dependencies
                }
            }
                
        except Exception as e:
            logger.error(f"Error during preprocessing pipeline: {str(e)}")
            raise RuntimeError(f"Failed to process text: {str(e)}")
    
    def extract_disambiguated_words(self, teprolin_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract disambiguated words from Teprolin result
        
        Args:
            teprolin_result: The result from Teprolin processing
            
        Returns:
            List of disambiguated words with their senses
        """
        # This is a placeholder - the actual implementation will depend on
        # the structure of Teprolin's response
        disambiguated_words = []
        
        # Check if we already have disambiguated words in the result
        if "disambiguated_words" in teprolin_result:
            return teprolin_result["disambiguated_words"]
        
        # Example extraction logic (to be adjusted based on actual Teprolin output)
        if "words" in teprolin_result:
            for word_info in teprolin_result["words"]:
                if "senses" in word_info:
                    disambiguated_words.append({
                        "word": word_info.get("word", ""),
                        "lemma": word_info.get("lemma", ""),
                        "position": word_info.get("position", 0),
                        "senses": word_info.get("senses", []),
                        "selected_sense": word_info.get("selected_sense", {})
                    })
        
        return disambiguated_words


def check_teprolin_service(base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if the Teprolin service is available and return status details
    
    Args:
        base_url: The base URL for the Teprolin service. If None, uses URL from settings.
        
    Returns:
        Dictionary with service status information
    """
    service_url = base_url or settings.TEPROLIN_URL
    
    try:
        response = requests.get(f"{service_url}/status", timeout=3)
        
        if response.status_code == 200:
            logger.info(f"Teprolin service is available at {service_url}")
            service_info = response.json()
            return {
                "teprolin_status": "available",
                "url": service_url,
                "details": service_info,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        else:
            logger.warning(f"Teprolin service returned status {response.status_code}")
            return {
                "teprolin_status": "unavailable",
                "url": service_url,
                "error": f"Service returned status code {response.status_code}",
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
            
    except requests.RequestException as e:
        logger.error(f"Could not connect to Teprolin service: {str(e)}")
        return {
            "teprolin_status": "unavailable",
            "url": service_url,
            "error": f"Connection error: {str(e)}",
            "response_time_ms": None
        }


if __name__ == "__main__":
    # For command-line usage, print the status check result
    status = check_teprolin_service()
    if status["teprolin_status"] == "available":
        print(f"✅ Teprolin service is available at {status['url']}")
        print(f"Service info: {status.get('details', {})}")
        
        # If service is available, demonstrate using the processor
        processor = TeprolinProcessor()
        
        # Test text
        test_text = "Banca a refuzat împrumutul pentru că nu credeau că aș putea conduce o afacere de succes."
        print("\n------- Testing Teprolin processor -------")
        
        # Test tokenization
        print("\n1. Tokenization:")
        tokens = processor.tokenize(test_text)
        print(f"Tokens: {tokens}")
        
        # Test POS tagging
        print("\n2. POS Tagging:")
        pos_tags = processor.pos_tagging(test_text)
        print(f"POS Tags: {pos_tags}")
        
        # Test NER
        print("\n3. Named Entity Recognition:")
        ner_results = processor.named_entity_recognition(test_text)
        print(f"NER Results: {ner_results}")
        
        # Test dependency parsing
        print("\n4. Dependency Parsing:")
        dependencies = processor.dependency_parsing(test_text)
        print(f"Dependencies: {dependencies}")
        
        # Test word sense disambiguation
        print("\n5. Word Sense Disambiguation:")
        wsd_results = processor.process_for_disambiguation(test_text)
        print(f"WSD Results: {wsd_results}")
    else:
        print(f"❌ Teprolin service is unavailable: {status.get('error', 'Unknown error')}")