"""
Service utilities for Teprolin NLP service

This module provides functions for checking the status and availability
of the Teprolin NLP service.
"""

import requests
import logging
from typing_extensions import Optional

from ..utils.config import settings
from .types import TeprolinStatusDict

logger = logging.getLogger('backend.preprocessing.service')

def checkService(base_url: Optional[str] = None) -> TeprolinStatusDict:
    """
    Check if the Teprolin service is available and return status details
    
    Args:
        base_url: The base URL for the Teprolin service. If None, uses URL from settings.
        
    Returns:
        Dictionary with service status information
    """
    service_url = base_url or settings.TEPROLIN_URL
    
    logger.debug(f"Checking Teprolin service availability at {service_url}")
    
    try:
        response = requests.get(f"{service_url}/operations", timeout=3)
        
        if response.status_code == 200:
            result = {
                "teprolin_status": "available",
                "url": service_url,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "error": None
            }
            logger.debug(f"Teprolin service is available. Response time: {result['response_time_ms']}ms")
            return result
        else:
            result = {
                "teprolin_status": "unavailable",
                "url": service_url,
                "error": f"Service returned status code {response.status_code}",
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
            logger.warning(f"Teprolin service returned status code {response.status_code}")
            return result
            
    except requests.RequestException as e:
        result = {
            "teprolin_status": "unavailable",
            "url": service_url,
            "error": f"Connection error: {str(e)}",
            "response_time_ms": None
        }
        logger.error(f"Failed to connect to Teprolin service: {str(e)}")
        return result 