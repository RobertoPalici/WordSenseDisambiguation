"""
Enrichment module for the Word Sense Disambiguation API.

This module provides functionality to enrich disambiguation results with
explanations and example sentences using OpenAI.
"""

import json
import logging
import time
import os
from pathlib import Path

from .format_results import convert_to_frontend_format
# from .openai_client import generate_batch_explanations, generate_batch_examples
from .deepseek_client import generate_batch_explanations, generate_batch_examples
from ..ambiguity.types import (
    ResultDict,
)
from .types import (
    FrontendResultDict,
)

logger = logging.getLogger('backend.enrichment')


def enrich_top_meanings(result_dict: ResultDict, batch_size: int = 3) -> FrontendResultDict:
    """
    Enrich top meanings for each ambiguous word in the result
    
    This enhanced version enriches multiple meanings per word
    instead of just the best one, allowing for more detailed frontend display.
    
    Args:
        result_dict: The ResultDict containing ambiguous words
        batch_size: Number of meanings to process in a single API call
        
    Returns:
        The enriched ResultDict with enrichment for top meanings
    """
    start_time = time.time()
    
    # Extract the ambiguous words from the response
    ambiguous_words = result_dict.get("ambiguous_words", [])
    
    # Collect all meanings that need to be enriched
    all_meanings_to_enrich = []
    
    # Process each ambiguous word to collect meanings that need enrichment
    for word_idx, word_data in enumerate(ambiguous_words):
        # Skip if no potential meanings
        potential_meanings = word_data.get("potential_meanings", [])
        if not potential_meanings:
            continue
            
        # Get word information
        word = word_data.get("word", "")
        
        # Sort meanings by confidence (highest first)
        sorted_meanings = sorted(
            potential_meanings, 
            key=lambda x: x.get("confidence", 0.0), 
            reverse=True
        )
        word_data["potential_meanings"] = sorted_meanings[:9]    
        
        # Add each meaning to the collection with metadata to track it
        for meaning in sorted_meanings[:9]:
            all_meanings_to_enrich.append({
                "word_idx": word_idx,
                "word": word,
                "sense_id": meaning.get("id", ""),
                "definition": meaning.get("definition", ""),
                "pos": meaning.get("pos", ""),
                "confidence": meaning.get("confidence", 0.0)
            })
    # Process meanings in batches
    for i in range(0, len(all_meanings_to_enrich), batch_size):
        batch = all_meanings_to_enrich[i:i+batch_size]
        
        try:
            # Generate explanations for the batch
            explanations = generate_batch_explanations(batch)
            
            # Generate examples for the batch
            examples = generate_batch_examples(batch)
            
            # Associate explanations and examples with the original words
            for j, meaning_data in enumerate(batch):
                word_idx = meaning_data["word_idx"]
                word = meaning_data["word"]
                sense_id = meaning_data["sense_id"]
                
                # Get the explanation and examples for this meaning
                explanation = explanations.get(j, f"Nu am putut genera o explicație pentru sensul cuvântului '{word}'.")
                example_list = examples.get(j, [f"Nu am putut genera exemple pentru sensul cuvântului '{word}'."])
                
                # Ensure the meaning_enrichments list exists
                if "meaning_enrichments" not in ambiguous_words[word_idx]:
                    ambiguous_words[word_idx]["meaning_enrichments"] = []
                
                # Add the enrichment
                ambiguous_words[word_idx]["meaning_enrichments"].append({
                    "id": sense_id,
                    "enrichment": {
                        "explanation": explanation,
                        "examples": example_list
                    }
                })
                
        except Exception as e:
            logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
            
            # Add empty enrichments for this batch
            for meaning_data in batch:
                word_idx = meaning_data["word_idx"]
                word = meaning_data["word"]
                sense_id = meaning_data["sense_id"]
                
                if "meaning_enrichments" not in ambiguous_words[word_idx]:
                    ambiguous_words[word_idx]["meaning_enrichments"] = []
                
                ambiguous_words[word_idx]["meaning_enrichments"].append({
                    "id": sense_id,
                    "enrichment": {
                        "explanation": f"Nu am putut genera o explicație pentru acest sens al cuvântului '{word}'.",
                        "examples": [f"Nu am putut genera exemple pentru acest sens al cuvântului '{word}'."]
                    }
                })
    
    enrichment_time = time.time() - start_time
    result_dict["enrichment_time"] = enrichment_time
    logger.info(f"Enrichment completed in {enrichment_time:.2f} seconds")
    
    front_end_result = convert_to_frontend_format(result_dict)

    # Save output to a JSON file using platform-independent path handling
    try:
        # Create a Path object for the logs directory
        logs_dir = Path(__file__).parent / "logs"
        
        # Ensure the logs directory exists
        logs_dir.mkdir(exist_ok=True, parents=True)
        
        # Create the output file path
        output_file = logs_dir / "output.json"
        
        # Write the JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(front_end_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Frontend result saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save output JSON: {str(e)}")

    return front_end_result
