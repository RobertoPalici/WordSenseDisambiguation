"""
Frontend runner script
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the Streamlit frontend"""
    host = os.getenv("FRONTEND_HOST", "0.0.0.0")
    port = int(os.getenv("FRONTEND_PORT", "8501"))
    
    # Prepare Streamlit command
    cmd = [
        "streamlit",
        "run",
        "src/frontend/main.py",
        "--server.address", host,
        "--server.port", str(port)
    ]
    
    print(f"Starting Streamlit frontend on {host}:{port}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 