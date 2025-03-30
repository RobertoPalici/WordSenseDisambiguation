"""
FastAPI backend for Word Sense Disambiguation
"""

import logging
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .preprocessing.service import checkService
from .preprocessing import analyze_text

from .ambiguity import process_text

from .enrichment import enrich_top_meanings, create_test_data
from .enrichment.types import FrontendResultDict

from .utils.config import settings

# Configure root logger
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Create module logger
logger = logging.getLogger("backend.main")
logger.info(f"Starting backend application with log level: {settings.LOG_LEVEL}")

app = FastAPI(
    title="Word Sense Disambiguation API",
    description="API for word sense disambiguation using Teprolin",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    """Root endpoint returning API status"""
    logger.debug("Root endpoint called")
    return {"status": "active", "message": "Word Sense Disambiguation API is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON object with health status of the API and its dependencies
    """
    logger.debug("Health check endpoint called")
    
    # Check Teprolin service
    teprolin_status = checkService()
    
    # Determine overall health status
    is_healthy = teprolin_status["teprolin_status"] == "available"
    
    
    response = {
        "status": "healthy" if is_healthy else "degraded",
        "api": {
            "status": "running",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        },
        "dependencies": {
            "teprolin": teprolin_status
        }
    }
    
    logger.debug(f"Health check result: {response['status']}")
    return response

class TextRequest(BaseModel):
    """Request model for text processing"""
    text: str = Field(..., description="The text to be processed")
    similarity_threshold: Optional[float] = Field(
        0.15, 
        description="Threshold for determining ambiguity (0.0-1.0)"
    )

@app.post("/api/disambiguate", response_model=FrontendResultDict)
async def disambiguate_text(request: TextRequest):
    """
    Disambiguate the senses of words in the provided text
    
    This endpoint processes Romanian text to:
    1. Analyze it linguistically (tokenization, POS tagging, etc.)
    2. Detect ambiguous words based on semantic similarity
    3. Generate recommendations for disambiguation
    4. Enrich results with AI-generated explanations and examples
    
    Parameters:
        request: The text to process and configuration options
        
    Options:
        - text: The Romanian text to process
        - similarity_threshold: Threshold for determining ambiguity (0.0-1.0)
    
    Returns:
        A FrontendResultDict containing:
        - text: The original text
        - ambiguous_words: List of ambiguous words with:
          - word: The ambiguous word
          - pos: Part of speech
          - position: Position in text
          - ambiguity_score: How ambiguous the word is (0.0-1.0)
          - top_meanings: List of top meanings with enriched explanations and examples
          - other_meanings: Additional meanings without enrichment
        - enrichment_time: Time taken for enrichment in seconds
        - total_execution_time: Total time taken for the entire process
    """
    start_time = time.time()
    logger.info(f"Processing disambiguation request for text of length {len(request.text)}")
    
    try:
        if settings.MOCK_API:
            test_data = create_test_data()
            logger.debug(f"Created test data with {len(test_data.get('ambiguous_words', []))} ambiguous words")
            
            frontend_result = enrich_top_meanings(test_data)
            
            # Calculate total execution time
            total_execution_time = time.time() - start_time
            frontend_result["total_execution_time"] = total_execution_time
            logger.info(f"Total execution time: {total_execution_time:.4f} seconds")

            return frontend_result


        # Step 1: Process text with preprocessing module
        logger.debug("Calling preprocessing module")
        preprocessing_result = analyze_text(request.text)
        
        # Step 2: Process with ambiguity detection module
        logger.debug("Calling ambiguity detection module")
        result = process_text(
            text=request.text,
            preprocessed_data={
                "tokens": preprocessing_result["analysis"]["tokens"],
                "pos_tags": preprocessing_result["analysis"]["pos_tags"],
                "dependencies": preprocessing_result["analysis"]["dependencies"],
                "processed_text": preprocessing_result["processed_text"]
            },
            similarity_threshold=request.similarity_threshold
        )

        # Step 3: Enrich results with AI-generated explanations and examples
        frontend_result = enrich_top_meanings(result)

        total_execution_time = time.time() - start_time
        frontend_result["total_execution_time"] = total_execution_time    
        logger.info(f"Total execution time: {total_execution_time:.4f} seconds")

        return frontend_result

    except HTTPException:
        # Re-raise HTTP exceptions
        logger.error("HTTP exception occurred during text processing")
        raise
    except Exception as e:
        # Log the error and return a 500 for any other exceptions
        error_msg = f"Error processing text: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting uvicorn server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 

