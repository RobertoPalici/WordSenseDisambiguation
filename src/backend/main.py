"""
FastAPI backend for Word Sense Disambiguation
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .utils.config import settings
from .preprocessing.teprolin_processor import check_teprolin_service
from .preprocessing.teprolin_processor import TeprolinProcessor

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
    return {"status": "active", "message": "Word Sense Disambiguation API is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON object with health status of the API and its dependencies
    """
    # Check Teprolin service
    teprolin_status = check_teprolin_service()
    
    # Determine overall health status
    is_healthy = teprolin_status["teprolin_status"] == "available"
    
    return {
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


class WSDResponse(BaseModel):
    """Response model for text processing"""
    original_text: str = Field(..., description="The original text")
    processed_text: str = Field(..., description="The processed text")
    disambiguated_words: List[Dict[str, Any]] = Field(
        ..., 
        description="List of disambiguated words"
    )
    processing_time: float = Field(
        ..., 
        description="Time taken to process the text in seconds"
    )

class TextRequest(BaseModel):
    """Request model for text processing"""
    text: str = Field(..., description="The text to be processed")
    options: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Optional processing options"
    )

@app.post("/api/disambiguate", response_model=WSDResponse)
async def disambiguate_text(request: TextRequest):
    """
    Disambiguate the senses of words in the provided text
    """
    try:
        # Check if Teprolin service is available
        teprolin_status = check_teprolin_service()
        if teprolin_status["teprolin_status"] != "available":
            # Return 503 Service Unavailable if Teprolin is down
            raise HTTPException(
                status_code=503,
                detail=f"Teprolin service is unavailable: {teprolin_status.get('error', 'Unknown error')}"
            )
        
        # Process the text using TeprolinProcessor
        processor = TeprolinProcessor()
        result = processor.process_for_disambiguation(
            request.text, 
            request.options
        )
        
        # Return the processed result
        return WSDResponse(
            original_text=result["original_text"],
            processed_text=result["processed_text"],
            disambiguated_words=result["disambiguated_words"],
            processing_time=result["processing_time"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like our 503)
        raise
    except Exception as e:
        # Log the error and return a 500 for any other exceptions
        import logging
        logging.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}") 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 

