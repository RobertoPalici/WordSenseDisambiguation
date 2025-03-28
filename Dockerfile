FROM python:3.9-slim-bullseye AS builder

# Install system dependencies required for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.4.2

# Set working directory
WORKDIR /app

# Copy only dependency files first to leverage Docker caching
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use a virtual environment and create wheels
RUN poetry config virtualenvs.create false \
    && poetry export -f requirements.txt --without-hashes > requirements.txt

# Final stage
FROM python:3.9-slim-bullseye

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from builder stage
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./src ./src
COPY run_backend.py ./
COPY .env ./

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "run_backend.py"] 