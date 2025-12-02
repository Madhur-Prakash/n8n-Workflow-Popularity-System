# Deployment Guide

Complete guide for deploying the n8n Workflow Popularity System in different environments.

## Prerequisites

### Required
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL 12+ (or Docker)
- YouTube Data API v3 key

### Optional
- Docker & Docker Compose
- Redis (for caching in production)
- Nginx (for reverse proxy)

## Environment Setup

### 1. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Restrict the key to YouTube Data API v3

### 2. Environment Variables

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/n8n_workflows
YOUTUBE_API_KEY=your_youtube_api_key_here
LOG_LEVEL=INFO
```

## Local Development

### 1. Install uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Setup Project
```bash
git clone <repository>
cd n8n-workflow-system
uv sync
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb n8n_workflows

# Run migrations
uv run alembic upgrade head

# Load seed data
uv run python scripts/load_seed_data.py
```

### 4. Start Development Server
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Scheduler (Optional)
```bash
# In separate terminal
uv run python scripts/scheduler.py
```

## Docker Deployment

### 1. Quick Start
```bash
# Set API key
export YOUTUBE_API_KEY=your_youtube_api_key

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec api uv run alembic upgrade head
docker-compose exec api uv run python scripts/load_seed_data.py
```

### 2. Check Status
```bash
# View logs
docker-compose logs -f api

# Check health
curl http://localhost:8000/health
```

### 3. Trigger Data Collection
```bash
curl -X POST http://localhost:8000/admin/refresh \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["YouTube", "Forum", "Google"]}'
```

## Production Deployment

### 1. Server Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Ubuntu 20.04+ or similar

**Recommended:**
- 4 CPU cores
- 8GB RAM
- 50GB SSD storage

### 2. Production Docker Compose

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: n8n_workflows
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - app-network

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/n8n_workflows
      YOUTUBE_API_KEY: ${YOUTUBE_API_KEY}
      LOG_LEVEL: INFO
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - app-network

  scheduler:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/n8n_workflows
      YOUTUBE_API_KEY: ${YOUTUBE_API_KEY}
    depends_on:
      - api
    command: uv run python scripts/scheduler.py
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### 3. Nginx Configuration

Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 4. Environment Variables

Create `.env.prod`:
```bash
POSTGRES_PASSWORD=secure_password_here
YOUTUBE_API_KEY=your_youtube_api_key
```

### 5. Deploy
```bash
# Load environment
source .env.prod

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Initialize
docker-compose -f docker-compose.prod.yml exec api uv run alembic upgrade head
```

## Cloud Deployment

### AWS ECS

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name n8n-workflow-system
```

2. **Build and Push Image**
```bash
# Build
docker build -t n8n-workflow-system .

# Tag
docker tag n8n-workflow-system:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/n8n-workflow-system:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/n8n-workflow-system:latest
```

3. **Create ECS Task Definition**
```json
{
  "family": "n8n-workflow-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/n8n-workflow-system:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://user:pass@rds-endpoint:5432/n8n_workflows"
        }
      ],
      "secrets": [
        {
          "name": "YOUTUBE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:youtube-api-key"
        }
      ]
    }
  ]
}
```

### Google Cloud Run

1. **Build and Deploy**
```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/n8n-workflow-system

# Deploy
gcloud run deploy n8n-workflow-system \
  --image gcr.io/PROJECT_ID/n8n-workflow-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql+asyncpg://... \
  --set-secrets YOUTUBE_API_KEY=youtube-api-key:latest
```

## Monitoring Setup

### 1. Health Checks

Add to your monitoring system:
```bash
# API Health
curl -f http://localhost:8000/health || exit 1

# Database Health
curl -f http://localhost:8000/stats || exit 1
```

### 2. Log Monitoring

Configure log aggregation:
```bash
# Docker logs
docker-compose logs -f api | grep ERROR

# Application logs
tail -f /var/log/n8n-workflow-system/app.log
```

### 3. Metrics Collection

Add Prometheus metrics (optional):
```python
# In app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

## Backup Strategy

### 1. Database Backup
```bash
# Create backup
pg_dump n8n_workflows > backup_$(date +%Y%m%d).sql

# Restore backup
psql n8n_workflows < backup_20240101.sql
```

### 2. Automated Backups
```bash
# Add to crontab
0 2 * * * pg_dump n8n_workflows | gzip > /backups/n8n_$(date +\%Y\%m\%d).sql.gz
```

## Scaling Considerations

### 1. Horizontal Scaling
- Run multiple API instances behind load balancer
- Use shared PostgreSQL database
- Implement Redis for session storage

### 2. Database Scaling
- Use read replicas for query performance
- Implement connection pooling
- Consider database sharding for large datasets

### 3. Caching
- Add Redis for API response caching
- Cache frequently accessed workflows
- Implement cache invalidation strategy

## Security Checklist

- [ ] Use strong database passwords
- [ ] Enable SSL/TLS for all connections
- [ ] Implement API rate limiting
- [ ] Add authentication for admin endpoints
- [ ] Use secrets management for API keys
- [ ] Enable database connection encryption
- [ ] Configure firewall rules
- [ ] Regular security updates

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check connection string
echo $DATABASE_URL
```

2. **YouTube API Quota Exceeded**
```bash
# Check quota in Google Cloud Console
# Implement exponential backoff
# Consider multiple API keys
```

3. **High Memory Usage**
```bash
# Monitor memory
docker stats

# Optimize queries
# Add connection pooling
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug
uv run uvicorn app.main:app --reload --log-level debug
```