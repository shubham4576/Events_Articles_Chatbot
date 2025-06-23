# Docker Deployment Guide

This guide explains how to deploy the Events Articles Chatbot using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)
- Google Gemini API key

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd Events_Articles_Chatbot

# Build and start the container
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The application will be available at `http://localhost:8000`

### 2. Using Docker directly

```bash
# Build the image
docker build -t events-chatbot .

# Run the container
docker run -d \
  --name events-chatbot \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e GOOGLE_API_KEY=your_api_key_here \
  events-chatbot
```

## Configuration

### Environment Variables

The following environment variables can be configured:

- `GOOGLE_API_KEY`: Your Google Gemini API key (required)
- `SQLITE_DB_PATH`: Path to SQLite database (default: data/events_articles.db)
- `CHROMADB_PATH`: Path to ChromaDB storage (default: data/chromadb)
- `DEBUG`: Enable debug mode (default: false)

### Using .env file

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_actual_api_key_here
DEBUG=false
```

Then use docker-compose:

```bash
docker-compose --env-file .env up -d
```

## Data Persistence

The Docker setup includes volume mounts to persist data:

- `./data:/app/data` - SQLite database and ChromaDB storage
- `./logs:/app/logs` - Application logs (optional)

## Management Commands

### Start the application
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Restart the application
```bash
docker-compose restart
```

### Update the application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Health Checks

The container includes health checks that verify the application is running properly:

- Health check endpoint: `http://localhost:8000/`
- Check interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

## Troubleshooting

### Container won't start
1. Check logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Ensure ports are not already in use

### Database issues
1. Check if data directory has proper permissions
2. Verify volume mounts are working: `docker-compose exec events-chatbot ls -la /app/data`

### API key issues
1. Verify your Google Gemini API key is valid
2. Check environment variable is properly set: `docker-compose exec events-chatbot env | grep GOOGLE`

## Production Deployment

For production deployment, consider:

1. **Security**: Remove or secure the API credentials
2. **Reverse Proxy**: Use nginx or similar for SSL termination
3. **Monitoring**: Add logging and monitoring solutions
4. **Backup**: Implement regular backups of the data directory
5. **Resource Limits**: Set appropriate CPU and memory limits

Example production docker-compose.yml additions:

```yaml
services:
  events-chatbot:
    # ... existing configuration
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
