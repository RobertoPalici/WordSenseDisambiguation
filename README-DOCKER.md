# Docker Setup for Word Sense Disambiguation

This document provides instructions for setting up and running the Word Sense Disambiguation application using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Components

The application consists of three services:

1. **Backend** (FastAPI): Provides the API for word sense disambiguation
2. **Frontend** (Streamlit): Provides the web interface for users
3. **Teprolin**: NLP service for Romanian language processing

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd WordSenseDisambiguation
```

### 2. Configuration

Before building the Docker images, you need to configure your environment variables.

1. Create a `.env` file with the required variables:

```
# API and server settings
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8501
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=False

# Teprolin service (use teprolin as the hostname in Docker)
TEPROLIN_URL=http://teprolin:5000

# Application settings
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production

# OpenAI API settings (required for enrichment)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Testing/Mock settings
ENRICHMENT_MOCK_API=false
MOCK_API=false
```

Make sure to replace `your_openai_api_key` with your actual OpenAI API key.

### 3. Build and Start the Services

```bash
docker-compose up --build
```

This command will:
- Build the images for backend and frontend services
- Pull the Teprolin image from Docker Hub
- Start all three services
- Create a network for the services to communicate

To run the services in the background:

```bash
docker-compose up --build -d
```

### 4. Accessing the Application

- Frontend (Streamlit UI): http://localhost:8501
- Backend API: http://localhost:8000
- Teprolin API: http://localhost:5000

### 5. Health Checks

Health endpoints are available at:
- Backend: http://localhost:8000/health
- Teprolin: http://localhost:5000/status

## Container Management

### Stop the Containers

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f
```

To view logs for a specific service:

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f teprolin
```

### Rebuild a Specific Service

```bash
docker-compose build backend
docker-compose up -d backend
```

## Network Configuration

All services are connected through the `wsd-network` bridge network. The services can communicate with each other using their service names as hostnames:

- Backend: `backend:8000`
- Frontend: `frontend:8501`
- Teprolin: `teprolin:5000`

## Data Persistence

The Teprolin service uses a volume (`teprolin-data`) to persist data across container restarts. This ensures that lexical data and models are preserved.

## Environment Variables in Docker

Docker-specific environment variables are set in the `docker-compose.yml` file. These override any conflicting values in your `.env` file when running in Docker:

```yaml
# Backend service environment variables
environment:
  - TEPROLIN_URL=http://teprolin:5000
  - API_HOST=0.0.0.0
  - API_PORT=8000
  - ENVIRONMENT=production
  - DEBUG=False

# Frontend service environment variables
environment:
  - API_URL=http://backend:8000
```

## Troubleshooting

### Service Unavailable

If you see a 503 Service Unavailable error from the backend, it means that the Teprolin service is not accessible. Check if the Teprolin container is running:

```bash
docker-compose ps teprolin
```

### Container Logs

View container logs for error messages:

```bash
docker-compose logs teprolin
```

### Restart a Service

```bash
docker-compose restart teprolin
```

### Network Issues

If the services can't communicate with each other, check the Docker network:

```bash
docker network inspect wsd-network
```

### Volume Issues

If the Teprolin service is having data persistence issues:

```bash
# Check volumes
docker volume ls

# Inspect the teprolin-data volume
docker volume inspect teprolin-data
```

## Running Without Docker

If you prefer to run the application without Docker, refer to the main [README.md](README.md) for instructions on:

- Setting up Poetry environment
- Running the backend and frontend
- Running individual modules
- Troubleshooting common issues

## Production Deployment

For production deployment, make sure to set appropriate environment variables in your `.env` file or in the `docker-compose.yml` file:

```yaml
environment:
  - ENVIRONMENT=production
  - DEBUG=False
  - LOG_LEVEL=WARNING
```

For a more secure deployment:

1. Configure proper SSL termination
2. Set up a reverse proxy (like Nginx)
3. Implement proper authentication
4. Restrict network access to services
5. Use Docker secrets for sensitive information like API keys 