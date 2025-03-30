# Word Sense Disambiguation with Teprolin

This project uses Teprolin, a text processing platform for Romanian language, to detect and disambiguate ambiguous words in a given text. The system analyzes input text, identifies potentially ambiguous words, and provides explanations about different possible meanings based on context.

## Project Structure

The project is divided into backend and frontend components:

### Backend

1. **Preprocessing Pipeline (Teprolin)**
   - Tokenization
   - POS tagging
   - Syntactic parsing

2. **Ambiguity Detection**
   - Identifies words with multiple possible meanings
   - Analyzes different contexts where ambiguous words can appear

3. **Sense Disambiguation**
   - Selects the most probable sense of a word based on context
   - Uses word vectorization and cosine similarity
   
4. **Enrichment**
   - Uses OpenAI API to generate explanations and examples for word senses
   - Formats results for frontend presentation

### Frontend

- Web interface built with Streamlit
- Displays input text analysis
- Explains ambiguities found in the text
- Provides visualizations for better understanding

## Setup and Installation

### Prerequisites

- Python 3.9+ (recommended 3.9.8)
- [Poetry](https://python-poetry.org/) for dependency management
- Docker (optional, for running Teprolin service)

### Installing Poetry

1. Install Poetry if you don't have it:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Verify installation:
   ```bash
   poetry --version
   ```

### Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd WordSenseDisambiguation
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   # Use this for Poetry environments
   poetry env activate
   
   # If the above doesn't work, try using:
   source $(poetry env info --path)/bin/activate
   ```

4. Check if Teprolin service is running:
   ```bash
   poetry run teprolin-check
   ```
   
   If not running, start it using Docker:
   ```bash
   docker run -p 5000:5000 raduion/teprolin:1.1
   ```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# API and server settings
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8501
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=False

# Teprolin service
TEPROLIN_URL=http://localhost:5000

# Application settings
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=development

# OpenAI API settings (required for enrichment module)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Testing/Mock settings
ENRICHMENT_MOCK_API=false
MOCK_API=false
```

## Running the Application

### Using Poetry (Recommended)

For the main applications, use the Poetry scripts:

Run the backend:
```bash
poetry run backend
```

Run the frontend:
```bash
poetry run frontend
```

### Running Individual Modules

First activate the Poetry environment:
```bash
poetry env activate
# OR if that doesn't work, try using:
source $(poetry env info --path)/bin/activate
```

#### Run Modules as Python Modules:

Run the preprocessing module:
```bash
python -m src.backend.preprocessing.main
```

Run the ambiguity module:
```bash
python -m src.backend.ambiguity.main
```

Run the enrichment module:
```bash
python -m src.backend.enrichment.main
```


### Using Docker Compose

See the [README-DOCKER.md](README-DOCKER.md) file for Docker-specific instructions.

## Utility Scripts

### Cleaning Logs

The project includes a script to clean logs and temporary files:

```bash
# Make the script executable
chmod +x scripts/clean_logs.sh

# Run the script
./scripts/clean_logs.sh
```

This script will:
- Remove all `.log` files from module-specific log directories
- Clean log files at the project root
- Remove generated JSON files
- Clean temporary files
- Remove Python cache files

## Development

Add new dependencies:
```bash
poetry add package-name
```

Activate the virtual environment:
```bash
poetry env activate

# If the above doesn't work, try using:
source $(poetry env info --path)/bin/activate
```

## Troubleshooting

### 1. Backend Not Starting

If the backend doesn't start, check the following:

- Make sure Teprolin Docker service is running:
  ```bash
  poetry run teprolin-check
  ```

- Check if Python path is correct:
  ```bash
  echo $PYTHONPATH
  ```
  
  If needed, set it to include the project root:
  ```bash
  export PYTHONPATH=$PYTHONPATH:$(pwd)
  ```


## Technical Details

The project uses the following technologies:
- FastAPI for the backend API
- Streamlit for the frontend
- Teprolin for Romanian language processing
- OpenAI API for generating explanations and examples
- Poetry for dependency management
- Docker for containerization 