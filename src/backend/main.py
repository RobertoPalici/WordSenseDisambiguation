"""
FastAPI backend for Word Sense Disambiguation
"""

import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .utils.config import settings
from .preprocessing import analyze_text, checkService
from .ambiguity import process_text, AmbiguousWordDict, RecommendationDict

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


class MeaningOption(BaseModel):
    """Model for a potential meaning of an ambiguous word"""
    id: str = Field(..., description="Synset ID")
    definition: str = Field(..., description="Definition of the meaning")
    pos: str = Field(..., description="Part of speech")
    synonyms: List[str] = Field(..., description="List of synonyms")
    confidence: float = Field(..., description="Confidence score")

class AmbiguousWord(BaseModel):
    """Model for an ambiguous word"""
    word: str = Field(..., description="The ambiguous word")
    pos: str = Field(..., description="Part of speech")
    position: int = Field(..., description="Position in text")
    potential_meanings: List[MeaningOption] = Field(..., description="Potential meanings")

class RecommendationOption(BaseModel):
    """Model for a recommendation option"""
    meaning: str = Field(..., description="Definition of the meaning")
    synonymous: List[str] = Field(..., description="Confidence score")

class Recommendation(BaseModel):
    """Model for a disambiguation recommendation"""
    word: str = Field(..., description="The ambiguous word")
    position: int = Field(..., description="Position in text")
    options: List[RecommendationOption] = Field(..., description="Recommendation options")

class WSDResponse(BaseModel):
    """Response model for text processing"""
    original_text: str = Field(..., description="The original text")
    processed_text: str = Field(..., description="The processed text with POS tags")
    ambiguous_words: List[Any] = Field(..., description="List of ambiguous words detected")
    recommendations: List[Any] = Field(..., description="Disambiguation recommendations")
    processing_time: float = Field(..., description="Time taken to process the text in seconds")

class TextRequest(BaseModel):
    """Request model for text processing"""
    text: str = Field(..., description="The text to be processed")
    similarity_threshold: Optional[float] = Field(
        0.15, 
        description="Threshold for determining ambiguity (0.0-1.0)"
    )

@app.post("/api/disambiguate", response_model=WSDResponse)
async def disambiguate_text(request: TextRequest):
    """
    Disambiguate the senses of words in the provided text
    
    This endpoint processes Romanian text to:
    1. Analyze it linguistically (tokenization, POS tagging, etc.)
    2. Detect ambiguous words based on semantic similarity
    3. Generate recommendations for disambiguation
    
    Returns a structured response with:
    - The original and processed text
    - A list of detected ambiguous words with their potential meanings
    - Recommendations for disambiguation
    """
    logger.info(f"Processing disambiguation request for text of length {len(request.text)}")
    
    try:
        start_time = time.time()
        
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
        
        processing_time = time.time() - start_time
        logger.info(f"Text processed successfully in {processing_time:.2f} seconds")
        
        # Return the processed result
        return WSDResponse(
            original_text=result["text"],
            processed_text=preprocessing_result["processed_text"],
            ambiguous_words=result["ambiguous_words"],
            recommendations=result["recommendations"],
            processing_time=processing_time
        )
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

