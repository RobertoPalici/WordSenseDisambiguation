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

### Frontend

- Web interface built with Streamlit
- Displays input text analysis
- Explains ambiguities found in the text
- Provides visualizations for better understanding

## Setup and Installation

### Using Poetry

1. Install Poetry if you don't have it:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```
   poetry install
   ```

3. Check if Teprolin service is running:
   ```
   poetry run teprolin-check
   ```
   
   If not running, start it:
   ```
   docker run -p 5000:5000 racai/teprolin
   ```

## Running the Application

### Using Poetry (Recommended)

Run the backend:
```
poetry run backend
```

Run the frontend:
```
poetry run frontend
```

### Alternative Methods

Backend:
```
python run_backend.py
```
or
```
poetry run uvicorn src.backend.main:app --reload
```

Frontend:
```
python run_frontend.py
```
or
```
poetry run streamlit run src/frontend/app/app.py
```

### Using Docker Compose

```
docker-compose up
```

## Troubleshooting

### 1. Backend Not Starting

If the backend doesn't start, check the following:

- Make sure Teprolin Docker service is running:
  ```
  poetry run teprolin-check
  ```

- Check if Python path is correct:
  ```
  echo $PYTHONPATH
  ```
  
  If needed, set it to include the project root:
  ```
  export PYTHONPATH=$PYTHONPATH:$(pwd)
  ```

- Check for errors in the log file:
  ```
  cat backend.log
  ```

### 2. Import Errors

If you see import errors, it's likely a Python path issue. Use the helper scripts:
```
python run_backend.py
```

Or set PYTHONPATH manually:
```
PYTHONPATH=$(pwd) poetry run uvicorn src.backend.main:app --reload
```

### 3. Poetry Issues

If Poetry is causing problems:

- Update Poetry:
  ```
  poetry self update
  ```

- Clear Poetry cache:
  ```
  poetry cache clear pypi --all
  ```

- Recreate the virtual environment:
  ```
  poetry env remove --all
  poetry install
  ```

## Development

Add new dependencies:
```
poetry add package-name
```

Run tests:
```
poetry run pytest
```

Activate the virtual environment:
```
poetry shell
```

## Technical Challenges

- Integration of NLP-specific tools: word vectorization, cosine similarity, named entity recognition
- Using technologies like BERT, Teprolin, FastAPI, and Streamlit
- Ensuring high-quality responses from the application
- Managing communication with the Teprolin Docker service 