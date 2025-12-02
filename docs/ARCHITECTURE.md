# System Architecture

## Overview

The n8n Workflow Popularity System is built as a modern, async-first Python application using FastAPI, SQLAlchemy, and PostgreSQL. The system follows a layered architecture with clear separation of concerns.

## Architecture Layers

### 1. API Layer (`app/`)

**FastAPI Application** (`main.py`)
- Async request handling with proper dependency injection
- OpenAPI/Swagger documentation generation
- CORS middleware for cross-origin requests
- Comprehensive error handling and logging
- Pydantic schema validation for all endpoints

**Schemas** (`schemas.py`)
- Type-safe request/response models
- Input validation with Pydantic
- Automatic JSON serialization/deserialization
- API documentation generation

### 2. Data Collection Layer (`collectors/`)

**YouTube Collector** (`youtube.py`)
- YouTube Data API v3 integration
- Async video search and statistics retrieval
- Intelligent keyword generation (250+ terms)
- Rate limiting and quota management
- Multi-region support (US, India)

**Forum Collector** (`forum.py`)
- Discourse API integration for n8n Community
- Async HTTP client with proper connection pooling
- Workflow-specific content filtering
- Country inference from content analysis
- Contributor and engagement metrics

**Google Collector** (`google.py`)
- PyTrends integration for Google Trends data
- Async trend analysis and search volume estimation
- Batch processing for API efficiency
- Regional interest comparison
- Trend momentum calculation

### 3. Business Logic Layer (`services/`)

**Orchestrator** (`orchestrator.py`)
- Coordinates entire data pipeline
- Async workflow execution
- Error handling and recovery
- Transaction management
- Result aggregation and reporting

**Scoring Service** (`scoring.py`)
- Platform-specific scoring algorithms
- Mathematical popularity calculations
- Cross-platform score merging
- Weighted combination strategies

**Normalizer Service** (`normalizer.py`)
- Workflow name standardization
- Levenshtein distance-based deduplication
- Service extraction and canonicalization
- Similarity threshold management

### 4. Data Layer (`db/`)

**Models** (`models.py`)
- SQLAlchemy ORM models with async support
- Optimized database indexes
- JSON field for raw data storage
- Automatic timestamp management

**Session Management** (`session.py`)
- Async database session handling
- Connection pooling configuration
- Database creation and migration support
- Dependency injection for FastAPI

### 5. Automation Layer (`scripts/`)

**Scheduler** (`scheduler.py`)
- APScheduler with async job execution
- Cron-based scheduling (daily/weekly)
- Job monitoring and error handling
- Graceful shutdown handling

**Data Loading** (`load_seed_data.py`)
- Seed data initialization
- Bulk data insertion
- Database preparation utilities

## Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   YouTube API   │    │   Forum API     │    │  Google Trends  │
│   (Data v3)     │    │   (Discourse)   │    │   (PyTrends)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Collection Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   YouTube   │  │    Forum    │  │        Google           │ │
│  │  Collector  │  │  Collector  │  │      Collector          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Scoring   │  │ Normalizer  │  │     Orchestrator        │ │
│  │   Service   │  │   Service   │  │       Service           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Layer                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   PostgreSQL                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │  Workflows  │  │   Indexes   │  │     JSON Data       │ │ │
│  │  │    Table    │  │             │  │                     │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI                                  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │  Endpoints  │  │ Validation  │  │    Documentation    │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Async Architecture Benefits

### Performance
- **Non-blocking I/O**: All API calls and database operations are async
- **Concurrent Processing**: Multiple collectors can run simultaneously
- **Connection Pooling**: Efficient resource utilization
- **Batch Operations**: Optimized database interactions

### Scalability
- **Horizontal Scaling**: Stateless design allows multiple API instances
- **Resource Efficiency**: Lower memory and CPU usage
- **Queue Support**: Ready for message queue integration
- **Load Balancing**: Compatible with standard load balancers

### Reliability
- **Error Isolation**: Failures in one collector don't affect others
- **Graceful Degradation**: System continues with partial data
- **Transaction Safety**: Database consistency guaranteed
- **Retry Logic**: Automatic recovery from transient failures

## Database Design

### Schema Optimization
```sql
-- Primary table with optimized indexes
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(500) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    country VARCHAR(10) NOT NULL,
    -- Metrics columns...
    popularity_score FLOAT DEFAULT 0.0,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_platform_country ON workflows(platform, country);
CREATE INDEX idx_score_platform ON workflows(popularity_score DESC, platform);
CREATE INDEX idx_workflow_name ON workflows USING gin(workflow_name gin_trgm_ops);
```

### Query Patterns
- **Filtering**: Platform and country-based filtering with indexes
- **Sorting**: Popularity score descending with covering indexes
- **Pagination**: Offset/limit with total count optimization
- **Search**: Full-text search on workflow names with GIN indexes

## Security Architecture

### API Security
- **Input Validation**: Pydantic schemas prevent injection attacks
- **Rate Limiting**: Built-in protection against abuse
- **CORS Configuration**: Controlled cross-origin access
- **Error Handling**: No sensitive information leakage

### Data Security
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
- **Environment Variables**: Secure configuration management
- **Connection Encryption**: TLS for database connections
- **API Key Management**: Secure external API authentication

### Infrastructure Security
- **Container Isolation**: Docker container security
- **Network Segmentation**: Service-to-service communication
- **Secret Management**: Environment-based secrets
- **Audit Logging**: Comprehensive activity tracking

## Monitoring and Observability

### Application Metrics
- **Request Metrics**: Response times, error rates, throughput
- **Business Metrics**: Collection success rates, data quality
- **Resource Metrics**: Memory usage, CPU utilization
- **Database Metrics**: Query performance, connection pool status

### Logging Strategy
```python
# Structured logging with context
logger.info("Collection started", extra={
    "platform": "YouTube",
    "keywords_count": 250,
    "region": "US"
})
```

### Health Checks
- **Liveness Probe**: Basic application health
- **Readiness Probe**: Database connectivity
- **Dependency Checks**: External API availability
- **Custom Metrics**: Business logic health

## Deployment Architecture

### Container Strategy
```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim as base
# Install uv and dependencies
FROM base as runtime
# Application code and configuration
```

### Service Orchestration
```yaml
# Docker Compose for local development
services:
  postgres:    # Database service
  api:         # FastAPI application
  scheduler:   # Background job processor
```

### Production Considerations
- **Load Balancing**: Multiple API instances behind load balancer
- **Database Scaling**: Read replicas for query performance
- **Caching Layer**: Redis for frequently accessed data
- **Message Queue**: Celery/RQ for background processing
- **Monitoring Stack**: Prometheus + Grafana for metrics
- **Log Aggregation**: ELK stack for centralized logging

## Extension Points

### New Data Sources
```python
# Interface for new collectors
class BaseCollector:
    async def collect_all(self) -> List[Dict]:
        pass
```

### Custom Scoring
```python
# Pluggable scoring algorithms
class CustomScorer:
    def calculate_score(self, data: Dict) -> float:
        pass
```

### Additional APIs
```python
# FastAPI router extension
router = APIRouter(prefix="/v2")
app.include_router(router)
```

This architecture provides a solid foundation for a production-ready system that can scale, maintain high availability, and adapt to changing requirements.