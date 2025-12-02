# n8n Workflow Popularity System

A production-ready system that automatically identifies the most popular n8n workflows across YouTube, n8n Forum, and Google Search trends using real APIs.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- YouTube Data API v3 key ([Get one here](https://console.cloud.google.com/))

### 1-Minute Setup
```bash
# Clone and install
git clone <repository>
cd n8n-workflow-system
uv sync

# Configure
cp .env.example .env
# Edit .env with your YOUTUBE_API_KEY

# Initialize database
uv run alembic upgrade head
uv run python scripts/load_seed_data.py

# Start API
uv run uvicorn app.main:app --reload
```

**🎉 Access your API at http://localhost:8000/docs**

### Docker Quick Start
```bash
export YOUTUBE_API_KEY=your_key
docker-compose up -d
docker-compose exec api uv run alembic upgrade head
docker-compose exec api uv run python scripts/load_seed_data.py
```

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Setup Guide](#-setup-guide)
- [API Usage](#-api-usage)
- [Data Collection](#-data-collection)
- [Automation](#-automation)
- [Documentation](#-documentation)
- [Development](#-development)
- [Production](#-production)

## ✨ Features

### 🔌 **Real API Integration**
- **YouTube Data API v3**: Video metrics, engagement ratios, multi-region
- **Discourse API**: n8n Community forum posts, replies, contributors
- **Google Trends**: Search volume, trend analysis, regional interest

### 🧮 **Intelligent Scoring**
- **Platform-specific algorithms**: YouTube engagement, Forum activity, Google trends
- **Cross-platform merging**: Combine scores from multiple sources
- **Smart deduplication**: Levenshtein distance-based workflow normalization

### 🚀 **Production Ready**
- **Async FastAPI**: High-performance API with automatic documentation
- **PostgreSQL**: Robust database with optimized indexes
- **Type Safety**: Full type hints with Pydantic validation
- **Containerized**: Docker Compose with all services
- **Automated**: APScheduler for daily/weekly data refresh

### 📊 **Rich Data**
- **250+ Keywords**: Auto-generated from common integrations
- **50+ Workflows**: Realistic seed dataset included
- **Multi-region**: US and India data collection
- **Comprehensive Metrics**: Views, likes, comments, engagement ratios

## 📁 Project Structure

```
n8n-workflow-system/
├── 📱 app/                    # FastAPI application
│   ├── main.py               # API endpoints and server
│   └── schemas.py            # Pydantic models
├── 🔄 collectors/            # Data collection modules
│   ├── youtube.py            # YouTube Data API v3
│   ├── forum.py              # Discourse API (n8n Community)
│   └── google.py             # Google Trends (PyTrends)
├── ⚙️ services/              # Business logic
│   ├── scoring.py            # Popularity algorithms
│   ├── normalizer.py         # Deduplication logic
│   └── orchestrator.py       # Pipeline coordinator
├── 🗄️ db/                    # Database layer
│   ├── models.py             # SQLAlchemy models
│   └── session.py            # Database sessions
├── 🤖 scripts/               # Automation & utilities
│   ├── scheduler.py          # APScheduler automation
│   ├── load_seed_data.py     # Seed data loader
│   └── cron_refresh.sh       # Cron alternative
├── 🔄 alembic/               # Database migrations
├── 📚 docs/                  # Documentation
│   ├── API.md                # API reference
│   ├── ARCHITECTURE.md       # System design
│   ├── COLLECTORS.md         # Data collection details
│   ├── SCORING.md            # Algorithm documentation
│   └── DEPLOYMENT.md         # Production deployment
├── 🐳 docker-compose.yml     # Container orchestration
├── 📦 pyproject.toml         # uv dependencies
└── 📊 seed_data.json         # Sample workflows
```

## 🛠 Setup Guide

### Local Development

#### 1. Install uv Package Manager
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

#### 2. Clone and Install Dependencies
```bash
git clone <repository>
cd n8n-workflow-system
uv sync  # Installs all dependencies from pyproject.toml
```

#### 3. Get YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project or select existing
3. Enable **YouTube Data API v3**
4. Create **API Key** credentials
5. Restrict key to YouTube Data API v3

#### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/n8n_workflows
YOUTUBE_API_KEY=your_youtube_api_key_here
LOG_LEVEL=INFO
```

#### 5. Setup Database
```bash
# Create PostgreSQL database (if using local PostgreSQL)
createdb n8n_workflows

# Run database migrations
uv run alembic upgrade head

# Load sample data (50 workflows)
uv run python scripts/load_seed_data.py
```

#### 6. Start Development Server
```bash
# Start API server with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at:
# - Main API: http://localhost:8000
# - Interactive Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

#### 7. Start Automation (Optional)
```bash
# In separate terminal - starts daily/weekly data collection
uv run python scripts/scheduler.py
```

### Docker Development

#### 1. Quick Start
```bash
# Set your YouTube API key
export YOUTUBE_API_KEY=your_youtube_api_key_here

# Start all services (PostgreSQL + API + Scheduler)
docker-compose up -d

# Initialize database
docker-compose exec api uv run alembic upgrade head
docker-compose exec api uv run python scripts/load_seed_data.py
```

#### 2. View Logs
```bash
# View API logs
docker-compose logs -f api

# View all services
docker-compose logs -f
```

#### 3. Stop Services
```bash
docker-compose down
```

## 🔌 API Usage

### Core Endpoints

#### List Workflows
```bash
# Get top 10 workflows
curl "http://localhost:8000/workflows?limit=10"

# Filter by platform and country
curl "http://localhost:8000/workflows?platform=YouTube&country=US"

# Pagination
curl "http://localhost:8000/workflows?limit=20&offset=40"
```

#### Get Specific Workflow
```bash
curl "http://localhost:8000/workflows/1"
```

#### System Statistics
```bash
curl "http://localhost:8000/stats"
```

#### Trigger Data Collection
```bash
# Collect from all platforms
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["YouTube", "Forum", "Google"]}'

# Collect from specific platform
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["YouTube"]}'
```

### Response Examples

**Workflow List Response:**
```json
{
  "workflows": [
    {
      "id": 1,
      "workflow_name": "Google Sheets → Slack Automation",
      "platform": "YouTube",
      "country": "US",
      "views": 12500,
      "likes": 630,
      "comments": 88,
      "popularity_score": 15.2,
      "url": "https://youtube.com/watch?v=example1"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "has_next": true
}
```

**Statistics Response:**
```json
{
  "total_workflows": 150,
  "platforms": {"YouTube": 80, "Forum": 45, "Google": 25},
  "countries": {"US": 90, "IN": 60},
  "avg_popularity_score": 8.5,
  "top_workflow": "Google Sheets → Slack Automation"
}
```

## 📊 Data Collection

### Platforms Supported

| Platform | API | Metrics Collected | Regions |
|----------|-----|-------------------|---------|
| **YouTube** | Data API v3 | Views, likes, comments, engagement ratios | US, India |
| **n8n Forum** | Discourse API | Views, replies, contributors, likes | Content-based inference |
| **Google Trends** | PyTrends | Search volume, trend changes, interest | US, India |

### Collection Process

1. **Keyword Generation**: 250+ keywords auto-generated from integrations
2. **Data Gathering**: Parallel collection from all platforms
3. **Scoring**: Platform-specific popularity algorithms
4. **Normalization**: Deduplication using Levenshtein distance
5. **Storage**: Upsert to PostgreSQL with full audit trail

### Scoring Algorithms

#### YouTube Score
```
engagement = 0.6 × like_ratio + 0.4 × comment_ratio
score = log(views + 1) × (1 + engagement × 10)
```

#### Forum Score
```
score = log(views + 1) + replies×0.4 + contributors×0.6 + likes×0.5
```

#### Google Score
```
score = search_volume×0.001 + trend_change_60d×10
```

#### Cross-Platform Merging
```
combined = sum(platform_scores)×0.7 + max(platform_scores)×0.3
```

## 🤖 Automation

### APScheduler (Recommended)
```bash
# Start scheduler with daily/weekly refresh
uv run python scripts/scheduler.py
```

**Schedule:**
- **Daily refresh**: 2 AM UTC (incremental update)
- **Weekly deep refresh**: Sunday 3 AM UTC (full refresh)

### Cron Alternative
```bash
# Add to system crontab for daily 2 AM refresh
0 2 * * * /path/to/scripts/cron_refresh.sh
```

### Manual Refresh
```bash
# Trigger immediate refresh via API
curl -X POST "http://localhost:8000/admin/refresh"
```

## 📚 Documentation

### Complete Documentation Set

| Document | Description | Link |
|----------|-------------|------|
| **API Reference** | Complete endpoint documentation | [docs/API.md](docs/API.md) |
| **Architecture** | System design and patterns | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Data Collectors** | API integration details | [docs/COLLECTORS.md](docs/COLLECTORS.md) |
| **Scoring Algorithms** | Mathematical formulas | [docs/SCORING.md](docs/SCORING.md) |
| **Deployment Guide** | Production deployment | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Development

### Code Quality
```bash
# Type checking
uv run mypy .

# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

### Testing
```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov=collectors --cov=services
```

### Database Operations
```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

### Adding New Collectors
1. Create collector in `collectors/` following the pattern
2. Implement `collect_all()` method returning standardized data
3. Add to orchestrator in `services/orchestrator.py`
4. Update API endpoint to include new platform

## 🚀 Production

### Quick Production Deploy
```bash
# Set environment variables
export YOUTUBE_API_KEY=your_key
export POSTGRES_PASSWORD=secure_password

# Deploy with production compose
docker-compose -f docker-compose.prod.yml up -d
```

### Production Checklist
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS certificates
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up monitoring and logging
- [ ] Implement backup strategy
- [ ] Add rate limiting
- [ ] Configure firewall rules

### Scaling Options
- **Horizontal**: Multiple API instances behind load balancer
- **Database**: Read replicas for query performance
- **Caching**: Redis for frequently accessed data
- **Queue**: Celery/RQ for background processing

## 🔍 Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# System stats
curl http://localhost:8000/stats
```

### Logging
- Structured JSON logging
- Configurable log levels
- Error tracking and metrics
- Performance monitoring

### Metrics Available
- Collection success rates per platform
- API response times and error rates
- Database query performance
- Data quality indicators

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run quality checks: `uv run ruff check . && uv run mypy .`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [docs/](docs/) folder

### Common Issues
- **YouTube API quota**: Check Google Cloud Console quotas
- **Database connection**: Verify DATABASE_URL format
- **Collection failures**: Check API keys and network access

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
uv run uvicorn app.main:app --reload --log-level debug
```

---

**🎯 Ready to discover the most popular n8n workflows? Start with the [Quick Start](#-quick-start) guide!**