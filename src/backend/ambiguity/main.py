#!/usr/bin/env python
"""
Main entry point for the ambiguity detection and disambiguation system.

This module provides core text processing functionality for ambiguity detection
and writes formatted results to an output log file.
"""

import json
import logging
from pathlib import Path
from typing_extensions import Dict, Any, List, Union, Optional

from ..utils.config import settings
from .detector import AmbiguityDetector
from .recommendations import DisambiguationRecommender
from ..preprocessing import analyze_text 
from .types import (
    AmbiguousWordDict, 
    RecommendationDict, 
    ResultDict
)

# Use the module logger
module_logger = logging.getLogger('backend.ambiguity.main')

# Set up output logging
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True, parents=True)

# Create a logger specifically for the output
output_logger = logging.getLogger('backend.ambiguity.output')
output_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# Clear any existing handlers to avoid duplicates
if output_logger.handlers:
    output_logger.handlers.clear()

# Create file handler for output.log
output_file = log_dir / 'output.log'
file_handler = logging.FileHandler(output_file, mode='w')  # 'w' mode to overwrite each time
file_handler.setFormatter(logging.Formatter('%(message)s'))  # Simple format with just the message
output_logger.addHandler(file_handler)

def process_text(
    text: str, 
    preprocessed_data: Optional[Dict[str, Any]] = None,
    bert_model: str = "dumitrescustefan/bert-base-romanian-uncased-v1", 
    similarity_threshold: float = 0.15
) -> ResultDict:
    """
    Process Romanian text to detect ambiguities and provide recommendations
    
    Args:
        text: The Romanian text to analyze
        preprocessed_data: Optional dictionary with preprocessed data (tokens, pos_tags, etc.)
        bert_model: Name of the BERT model to use
        similarity_threshold: Threshold for determining ambiguity
        
    Returns:
        Dictionary with analysis results
    """
    module_logger.info(f"Processing text: {text[:50]}...")
    
    # Initialize components
    module_logger.debug("Initializing ambiguity detection components")
    detector = AmbiguityDetector(bert_model, similarity_threshold)
    recommender = DisambiguationRecommender()
    
    # Process text with preprocessing module if not provided
    if preprocessed_data is None:
        module_logger.debug("No preprocessed data provided, using preprocessing module")
        processed_result = analyze_text(text)
        tokens = processed_result["analysis"]["tokens"]
        pos_tags = processed_result["analysis"]["pos_tags"]
        print(f"Pos tags: {pos_tags}")
    else:
        module_logger.debug("Using provided preprocessed data")
        tokens = preprocessed_data["tokens"]
        pos_tags = preprocessed_data["pos_tags"]
        lemmas = preprocessed_data["lemmas"]
        print(f"Pos tags: {pos_tags}")

    
    module_logger.debug("Detecting ambiguities")
    ambiguous_words: List[AmbiguousWordDict] = detector.detect_ambiguities(tokens, pos_tags,lemmas)
    
    module_logger.debug("Generating recommendations")
    recommendations: List[RecommendationDict] = []
    if ambiguous_words:
        recommendations = recommender.get_recommendations(ambiguous_words)
    
    result: ResultDict = {
        "text": text,
        "ambiguous_words": ambiguous_words,
        "recommendations": recommendations
    }
    
    # Log the formatted output
    # log_formatted_output(result)
    
    module_logger.info(f"Processing completed. Found {len(ambiguous_words)} ambiguous words.")
    return result

def log_formatted_output(result: ResultDict) -> None:
    """
    Log formatted results to output.log
    
    Args:
        result: The result from process_text
    """
    def log_separator(title: str) -> None:
        output_logger.info("\n" + "=" * 80)
        output_logger.info(f" {title} ".center(80, "="))
        output_logger.info("=" * 80 + "\n")
    
    def log_pretty(obj: Union[Dict, List, str]) -> None:
        if isinstance(obj, (dict, list)):
            output_logger.info(json.dumps(obj, indent=2, ensure_ascii=False))
        else:
            output_logger.info(obj)
    
    log_separator(f"ANALYZING: {result['text']}")
    
    output_logger.info("Text analysis:")
    output_logger.info(f"- Tokens: {len(result['analysis']['tokens'])} tokens")
    output_logger.info(f"- POS tags: {len(result['analysis']['pos_tags'])} tags")
    
    log_separator("AMBIGUOUS WORDS")
    if result["ambiguous_words"]:
        log_pretty(result["ambiguous_words"])
    else:
        output_logger.info("No ambiguous words detected.")
        
    log_separator("RECOMMENDATIONS")
    if result["recommendations"]:
        log_pretty(result["recommendations"])
    else:
        output_logger.info("No recommendations available.")

def main() -> None:
    """
    Main function for processing example texts
    """
    module_logger.info("Starting ambiguity detection demo")
    
    # Example texts with potential ambiguities
    example_texts: List[str] = [
        "Banca a refuzat împrumutul pentru că nu credeau că aș putea conduce o afacere de succes.",
        # "M-am așezat pe o bancă în parc să citesc o carte.",
        # "M-am dus la bancă să depun niște bani.",
        # "Am văzut un cal care alerga pe câmp.",
        # "Ion a luat o notă bună la examen.",
        # "Maria a cerut un pahar de vin la restaurant.",
        # "Acesta este un test pentru a vedea cum se comportă sistemul.",
        # "Merg la masă să mănânc.",
        # "Masa aceasta este făcută din lemn de stejar."
    ]
    
    output_logger.info("\n" + "=" * 80)
    output_logger.info(" AMBIGUITY DETECTION AND DISAMBIGUATION SYSTEM DEMO ".center(80, "="))
    output_logger.info("=" * 80 + "\n")
    
    # Process each example text
    for text in example_texts:
        # For the demo, we'll let process_text handle preprocessing
        process_text(text)
        
    output_logger.info("\n" + "=" * 80)
    output_logger.info(" DEMO COMPLETED ".center(80, "="))
    output_logger.info("=" * 80 + "\n")
    
    module_logger.info(f"Demo completed. Results written to {output_file}")
        
if __name__ == "__main__":
    main() 
