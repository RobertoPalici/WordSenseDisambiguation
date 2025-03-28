"""
Backend runner script
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the backend FastAPI server"""
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    reload = os.getenv("BACKEND_RELOAD", "False").lower() in ("true", "1", "t")
    
    print(f"Starting FastAPI backend server on {host}:{port}")
    uvicorn.run(
        "src.backend.main:app",
        host=host,
        port=port,
        reload=reload
    )

if __name__ == "__main__":
    main() 