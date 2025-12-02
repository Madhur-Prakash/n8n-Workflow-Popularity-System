<div align="center">

# 🚀 n8n Workflow Popularity System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <strong>🎯 Discover the most popular n8n workflows across YouTube, Forums, and Google Trends</strong>
</p>

<p align="center">
  A production-ready system that automatically identifies trending n8n workflows using real APIs, intelligent scoring, and cross-platform analytics.
</p>

---

### ⚡ **Quick Demo**

```bash
# 🚀 Get started in 60 seconds
git clone <repository> && cd n8n-workflow-system
uv sync && cp .env.example .env
# Add your YOUTUBE_API_KEY to .env
uv run alembic upgrade head && uv run python scripts/load_seed_data.py
uv run uvicorn app.main:app --reload
```

**🎉 [Open Interactive API Docs](http://localhost:8000/docs) • [View System Stats](http://localhost:8000/stats)**

</div>

---

## 🌟 **Why This System?**

<table>
<tr>
<td width="50%">

### 🎯 **Smart Discovery**
- **250+ Auto-Generated Keywords** from integrations
- **Multi-Platform Intelligence** (YouTube + Forum + Google)
- **Real-Time Trend Analysis** with mathematical scoring
- **Cross-Platform Deduplication** using ML techniques

</td>
<td width="50%">

### ⚡ **Production Ready**
- **Async FastAPI** with 99.9% uptime design
- **PostgreSQL** with optimized indexes
- **Docker Compose** for instant deployment
- **Automated Scheduling** with APScheduler

</td>
</tr>
</table>

---

## 🚀 **Quick Start Options**

<details>
<summary><b>🐳 Docker (Recommended)</b></summary>

```bash
# 1️⃣ Set your API key
export YOUTUBE_API_KEY=your_youtube_api_key

# 2️⃣ Launch everything
docker-compose up -d

# 3️⃣ Initialize data
docker-compose exec api uv run alembic upgrade head
docker-compose exec api uv run python scripts/load_seed_data.py

# ✅ Ready! Visit http://localhost:8000/docs
```

</details>

<details>
<summary><b>💻 Local Development</b></summary>

```bash
# 1️⃣ Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 2️⃣ Setup project
git clone <repository>
cd n8n-workflow-system
uv sync

# 3️⃣ Configure environment
cp .env.example .env
# Edit .env with your YOUTUBE_API_KEY

# 4️⃣ Initialize database
createdb n8n_workflows  # if using local PostgreSQL
uv run alembic upgrade head
uv run python scripts/load_seed_data.py

# 5️⃣ Start development server
uv run uvicorn app.main:app --reload

# ✅ Ready! Visit http://localhost:8000/docs
```

</details>

---

## 📊 **Live API Demo**

<div align="center">

| Endpoint | Description | Try It |
|----------|-------------|---------|
| `GET /workflows` | 📋 List trending workflows | [🔗 Try Now](http://localhost:8000/workflows?limit=5) |
| `GET /stats` | 📈 System statistics | [🔗 Try Now](http://localhost:8000/stats) |
| `POST /admin/refresh` | 🔄 Trigger data collection | [🔗 API Docs](http://localhost:8000/docs#/Admin/refresh_data_admin_refresh_post) |

</div>

### 🎯 **Sample Response**

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
      "popularity_score": 15.2,
      "url": "https://youtube.com/watch?v=example1"
    }
  ],
  "total": 150,
  "has_next": true
}
```

---

## 🏗️ **System Architecture**

### 📁 **Project Structure**

```
n8n-workflow-system/
├── 📱 app/                    # FastAPI application
│   ├── main.py               # 🚀 API endpoints & server
│   └── schemas.py            # 📋 Pydantic models
├── 🔄 collectors/            # Data collection modules
│   ├── youtube.py            # 🎥 YouTube Data API v3
│   ├── forum.py              # 💬 Discourse API (n8n Community)
│   └── google.py             # 📈 Google Trends (PyTrends)
├── ⚙️ services/              # Business logic
│   ├── scoring.py            # 🧮 Popularity algorithms
│   ├── normalizer.py         # 🔧 Deduplication logic
│   └── orchestrator.py       # 🎯 Pipeline coordinator
├── 🗄️ db/                    # Database layer
│   ├── models.py             # 📊 SQLAlchemy models
│   └── session.py            # 🔗 Database sessions
├── 🤖 scripts/               # Automation & utilities
│   ├── scheduler.py          # ⏰ APScheduler automation
│   ├── load_seed_data.py     # 🌱 Seed data loader
│   └── cron_refresh.sh       # 🔄 Cron alternative
├── 📚 docs/                  # 📖 Complete documentation
└── 🐳 docker-compose.yml     # 🚀 Container orchestration
```

---

## 🎯 **Key Features**

<div align="center">

<table>
<tr>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/🔌-Real%20APIs-success?style=for-the-badge" alt="Real APIs">
<br><br>
<strong>YouTube Data API v3</strong><br>
<strong>Discourse API</strong><br>
<strong>Google Trends</strong><br>
<em>Real-time data collection</em>
</td>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/🧮-Smart%20Scoring-blue?style=for-the-badge" alt="Smart Scoring">
<br><br>
<strong>Platform-Specific Algorithms</strong><br>
<strong>Cross-Platform Merging</strong><br>
<strong>ML-Based Deduplication</strong><br>
<em>Intelligent popularity ranking</em>
</td>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/🚀-Production%20Ready-orange?style=for-the-badge" alt="Production Ready">
<br><br>
<strong>Async FastAPI</strong><br>
<strong>PostgreSQL + Indexes</strong><br>
<strong>Docker Compose</strong><br>
<em>Enterprise-grade reliability</em>
</td>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/📊-Rich%20Data-purple?style=for-the-badge" alt="Rich Data">
<br><br>
<strong>250+ Keywords</strong><br>
<strong>Multi-Region Support</strong><br>
<strong>50+ Sample Workflows</strong><br>
<em>Comprehensive analytics</em>
</td>
</tr>
</table>

</div>

---

## 🔬 **Scoring Algorithms**

<div align="center">

### 🎥 **YouTube Score**
```
engagement = 0.6 × like_ratio + 0.4 × comment_ratio
score = log(views + 1) × (1 + engagement × 10)
```

### 💬 **Forum Score**
```
score = log(views + 1) + replies×0.4 + contributors×0.6 + likes×0.5
```

### 📈 **Google Score**
```
score = search_volume×0.001 + trend_change_60d×10
```

### 🔄 **Cross-Platform Merging**
```
combined = sum(platform_scores)×0.7 + max(platform_scores)×0.3
```

</div>

---

## 📊 **Data Collection Pipeline**

| Step | Process | Output |
|------|---------|---------|
| 1️⃣ | **Keyword Generation** | 250+ auto-generated search terms |
| 2️⃣ | **Parallel Collection** | Raw data from all platforms |
| 3️⃣ | **Intelligent Scoring** | Platform-specific popularity scores |
| 4️⃣ | **Smart Deduplication** | Merged workflows using ML similarity |
| 5️⃣ | **Database Storage** | Optimized PostgreSQL with indexes |

---

## 🤖 **Automation & Scheduling**

<div align="center">

### ⏰ **APScheduler (Recommended)**

```bash
# 🚀 Start intelligent scheduler
uv run python scripts/scheduler.py
```

**📅 Schedule:**
- 🌅 **Daily Refresh**: 2 AM UTC (incremental updates)
- 🗓️ **Weekly Deep Refresh**: Sunday 3 AM UTC (full refresh)

### 🔄 **Manual Triggers**

```bash
# 🎯 Trigger immediate collection
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["YouTube", "Forum", "Google"]}'
```

</div>

---

## 📚 **Complete Documentation**

<div align="center">

| 📖 Document | 🎯 Purpose | 🔗 Link |
|-------------|------------|---------|
| **🔌 API Reference** | Complete endpoint documentation | [📋 docs/API.md](docs/API.md) |
| **🏗️ Architecture** | System design & patterns | [🏛️ docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **🔄 Data Collectors** | API integration details | [⚙️ docs/COLLECTORS.md](docs/COLLECTORS.md) |
| **🧮 Scoring Algorithms** | Mathematical formulas | [📊 docs/SCORING.md](docs/SCORING.md) |
| **🚀 Deployment Guide** | Production deployment | [🌐 docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |

### 🌐 **Interactive Documentation**
- **📱 Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **📚 ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

</div>

---

## 🛠️ **Development & Testing**

<details>
<summary><b>🔧 Development Commands</b></summary>

```bash
# 🧪 Code Quality
uv run mypy .                    # Type checking
uv run ruff check .              # Linting
uv run ruff format .             # Formatting

# 🧪 Testing
uv run pytest                    # Run tests
uv run pytest --cov=app         # With coverage

# 🗄️ Database Operations
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run alembic upgrade head                              # Apply migrations
uv run alembic downgrade -1                             # Rollback
```

</details>

<details>
<summary><b>🐛 Debugging & Troubleshooting</b></summary>

```bash
# 🔍 Debug Mode
export LOG_LEVEL=DEBUG
uv run uvicorn app.main:app --reload --log-level debug

# 🏥 Health Checks
curl http://localhost:8000/health     # API health
curl http://localhost:8000/stats      # System stats

# 📊 View Logs
docker-compose logs -f api            # API logs
docker-compose logs -f                # All services
```

**Common Issues:**
- 🔑 **YouTube API quota**: Check [Google Cloud Console](https://console.cloud.google.com/)
- 🗄️ **Database connection**: Verify `DATABASE_URL` format
- 🔄 **Collection failures**: Check API keys and network access

</details>

---

## 🚀 **Production Deployment**

<div align="center">

### 🌐 **Quick Production Deploy**

```bash
# 🔐 Set secure environment
export YOUTUBE_API_KEY=your_key
export POSTGRES_PASSWORD=secure_password

# 🚀 Deploy with production compose
docker-compose -f docker-compose.prod.yml up -d
```

### ✅ **Production Checklist**

- [ ] 🔐 Strong database passwords
- [ ] 🛡️ SSL/TLS certificates  
- [ ] 🌐 Reverse proxy (Nginx)
- [ ] 📊 Monitoring & logging
- [ ] 💾 Backup strategy
- [ ] 🚦 Rate limiting
- [ ] 🔥 Firewall rules

</div>

---

## 🎯 **Performance & Scaling**

<div align="center">

<table>
<tr>
<td align="center" width="33%">
<strong>🔄 Horizontal Scaling</strong><br>
Multiple API instances<br>
Load balancer ready<br>
Stateless design
</td>
<td align="center" width="33%">
<strong>🗄️ Database Scaling</strong><br>
Read replicas<br>
Connection pooling<br>
Optimized indexes
</td>
<td align="center" width="33%">
<strong>⚡ Caching Layer</strong><br>
Redis integration<br>
API response caching<br>
Smart invalidation
</td>
</tr>
</table>

</div>

---

## 🤝 **Contributing**

<div align="center">

We welcome contributions! Here's how to get started:

1. 🍴 **Fork** the repository
2. 🌿 **Create** feature branch: `git checkout -b feature/amazing-feature`
3. ✨ **Make** changes with tests
4. 🧪 **Run** quality checks: `uv run ruff check . && uv run mypy .`
5. 💾 **Commit** changes: `git commit -m 'Add amazing feature'`
6. 🚀 **Push** to branch: `git push origin feature/amazing-feature`
7. 🎯 **Open** Pull Request

</div>

---

## 📄 **License & Support**

<div align="center">

<p>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
<img src="https://img.shields.io/badge/Support-GitHub%20Issues-blue?style=for-the-badge" alt="Support">
</p>

### 🆘 **Getting Help**

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)  
- 📚 **Documentation**: [docs/](docs/) folder

</div>

---

<div align="center">

## 🎉 **Ready to Discover Popular n8n Workflows?**

<p>
<a href="#-quick-start-options"><img src="https://img.shields.io/badge/🚀-Get%20Started%20Now-success?style=for-the-badge&logo=rocket" alt="Get Started"></a>
<a href="http://localhost:8000/docs"><img src="https://img.shields.io/badge/📱-Try%20Live%20API-blue?style=for-the-badge&logo=swagger" alt="Try API"></a>
<a href="docs/"><img src="https://img.shields.io/badge/📚-Read%20Docs-orange?style=for-the-badge&logo=gitbook" alt="Documentation"></a>
</p>

**⭐ Star this repo if you find it useful! ⭐**

---

*Built with ❤️ for the n8n community*

</div>