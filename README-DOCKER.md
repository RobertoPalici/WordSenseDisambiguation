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

The default configuration is in the `.env` file. You can modify this file to change the settings.

### 3. Build and Start the Services

```bash
docker-compose up --build
```

This command will:
- Build the images for backend and frontend services
- Pull the Teprolin image from Docker Hub
- Start all three services
- Create a network for the services to communicate

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

The Teprolin service uses a volume (`teprolin-data`) to persist data across container restarts.

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

## Production Deployment

For production deployment, update the environment variables in the `docker-compose.yml` file:

```yaml
environment:
  - ENVIRONMENT=production
  - DEBUG=False
``` 