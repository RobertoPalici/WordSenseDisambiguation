import time
import logging
import os
from typing import Optional

from fastapi import HTTPException

from ..utils.config import settings
from .types import ProcessedTextDict
from .service import checkService
from .processor_methods import tokenize, pos_tagging, named_entity_recognition, dependency_parsing

logger = logging.getLogger('backend.preprocessing.main')

def analyze_text(text: str, base_url: Optional[str] = None) -> ProcessedTextDict:
    """
    Process text with core NLP functions (tokenization, POS tagging, dependency parsing, NER)
    
    This function first checks if the Teprolin service is available, then performs basic 
    linguistic analysis steps:
    1. Tokenization - splits text into individual words
    2. POS Tagging - identifies parts of speech for each word
    3. Dependency Parsing - analyzes grammatical relationships
    4. Named Entity Recognition - identifies entities
    
    Args:
        text: Text to process
        base_url: Optional base URL for the Teprolin service
        
    Returns:
        Dict with processed text and linguistic analysis results        
    """
    base_url = base_url or settings.TEPROLIN_URL
    
    logger.info(f"Analyzing text (length: {len(text)}) with Teprolin service")
    
    # First check if the Teprolin service is available
    status = checkService(base_url)
    if status["teprolin_status"] != "available":
        error_msg = f"Teprolin service is unavailable: {status.get('error', 'Unknown error')}"
        logger.error(error_msg)
        raise HTTPException(
                status_code=503,
                detail=error_msg
            )
    
    start_time = time.time()
    
    try:
        logger.debug("Performing tokenization")
        tokens = tokenize(text, base_url)
        
        logger.debug("Performing POS tagging")
        pos_tags = pos_tagging(text, base_url)
        
        logger.debug("Performing dependency parsing")
        dependencies = dependency_parsing(text, base_url)
        
        logger.debug("Performing named entity recognition")
        ner_results = named_entity_recognition(text, base_url)
        
        logger.debug("Creating annotated text")
        annotated_text = ""
        for word, pos in pos_tags:
            annotated_text += f"{word}<sub>{pos}</sub> "
        
        processing_time = time.time() - start_time
        
        logger.info(f"Analysis completed in {processing_time:.2f} seconds")
        
        return {
            "original_text": text,
            "processed_text": annotated_text.strip(),
            "processing_time": processing_time,
            "analysis": {
                "tokens": tokens,
                "pos_tags": pos_tags,
                "dependencies": dependencies,
                "ner_results": ner_results
            }
        }
            
    except Exception as e:
        error_msg = f"Failed to process text: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

if __name__ == "__main__":
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    output_logger = logging.getLogger('backend.preprocessing.output')
    output_logger.setLevel(logging.INFO)
    
    output_file = os.path.join(log_dir, 'output.log')
    file_handler = logging.FileHandler(output_file, mode='w')  # 'w' mode to overwrite each time
    file_handler.setFormatter(logging.Formatter('%(message)s'))  # Simple format with just the message
    output_logger.addHandler(file_handler)
    
    try:
        sample_text = "Banca a refuzat împrumutul pentru că nu credeau că aș putea conduce o afacere de succes."
        output_logger.info(f"Using sample text: \"{sample_text}\"\n")
        
        result = analyze_text(sample_text)
        
        output_logger.info("\n=== PROCESSED TEXT WITH POS TAGS ===")  
        output_logger.info(result["processed_text"])
        
        output_logger.info("\n=== PROCESSING TIME ===")        
        output_logger.info(f"{result['processing_time']:.4f} seconds")
        
        output_logger.info("\n=== ANALYSIS RESULTS ===")
        output_logger.info(f"Tokens: {len(result['analysis']['tokens'])}")
        
        output_logger.info(f"POS tags: {len(result['analysis']['pos_tags'])}")
        
        output_logger.info(f"Dependencies: {len(result['analysis']['dependencies'])}")
        
        output_logger.info(f"NER results: {len(result['analysis']['ner_results'])}")
        
        output_logger.info("\nTeprolin processing completed successfully!")
                
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        output_logger.error(error_msg) 