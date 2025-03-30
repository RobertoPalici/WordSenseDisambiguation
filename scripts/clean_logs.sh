#!/bin/bash
# Script to clean logs for the Word Sense Disambiguation project

# Set the project root directory (adjust if needed)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Cleaning logs in: $PROJECT_ROOT"

# Clean specific module log directories based on actual project structure
echo "Cleaning module-specific log directories..."

# Clean ambiguity module logs
AMBIGUITY_LOGS="$PROJECT_ROOT/src/backend/ambiguity/logs"
if [ -d "$AMBIGUITY_LOGS" ]; then
    echo "Cleaning ambiguity module logs..."
    rm -f "$AMBIGUITY_LOGS"/*.log
fi

# Clean enrichment module logs
ENRICHMENT_LOGS="$PROJECT_ROOT/src/backend/enrichment/logs"
if [ -d "$ENRICHMENT_LOGS" ]; then
    echo "Cleaning enrichment module logs..."
    rm -f "$ENRICHMENT_LOGS"/*.log
fi

# Clean preprocessing module logs
PREPROCESSING_LOGS="$PROJECT_ROOT/src/backend/preprocessing/logs"
if [ -d "$PREPROCESSING_LOGS" ]; then
    echo "Cleaning preprocessing module logs..."
    rm -f "$PREPROCESSING_LOGS"/*.log
fi

# Clean any log files at the project root
echo "Cleaning log files at project root..."
rm -f "$PROJECT_ROOT"/*.log

# Clean generated JSON files (like frontend_dict.json)
echo "Cleaning generated JSON files..."
rm -f "$PROJECT_ROOT"/frontend_dict.json

# Clean any potential tempfiles
echo "Cleaning temporary files..."
find "$PROJECT_ROOT" -name "*.tmp" -type f -delete

# Clean __pycache__ directories to ensure clean Python bytecode
echo "Cleaning Python cache files..."
find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} +

echo "Log cleaning completed successfully!" 