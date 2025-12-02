<div align="center">

# 🔌 API Documentation

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapi-initiative&logoColor=white" alt="OpenAPI">
  <img src="https://img.shields.io/badge/REST-02569B?style=for-the-badge&logo=rest&logoColor=white" alt="REST">
</p>

<p align="center">
  <strong>Complete REST API reference for the n8n Workflow Popularity System</strong>
</p>

</div>

---

## 🌐 **Base Configuration**

<div align="center">

| Environment | Base URL | Status |
|-------------|----------|--------|
| **Local Development** | `http://localhost:8000` | 🟢 Active |
| **Docker** | `http://localhost:8000` | 🟢 Active |
| **Production** | `https://your-domain.com` | 🔧 Configure |

</div>

### 🔐 **Authentication**
- **Current**: No authentication required
- **Production**: Add API key authentication for admin endpoints

---

## 📋 **Quick Reference**

<div align="center">

<table>
<tr>
<td align="center" width="25%">
<strong>🏠 Health & Info</strong><br>
<code>GET /</code><br>
<code>GET /health</code>
</td>
<td align="center" width="25%">
<strong>📊 Workflows</strong><br>
<code>GET /workflows</code><br>
<code>GET /workflows/{id}</code>
</td>
<td align="center" width="25%">
<strong>📈 Statistics</strong><br>
<code>GET /stats</code>
</td>
<td align="center" width="25%">
<strong>⚙️ Admin</strong><br>
<code>POST /admin/refresh</code>
</td>
</tr>
</table>

</div>

---

## 🏠 **Health & Information Endpoints**

### `GET /` - Root Information

<details>
<summary><b>📋 Endpoint Details</b></summary>

**Description**: Get basic system information and navigation links.

**Response**:
```json
{
  "message": "n8n Workflow Popularity System",
  "version": "1.0.0",
  "docs": "/docs"
}
```

**Example**:
```bash
curl http://localhost:8000/
```

</details>

### `GET /health` - Health Check

<details>
<summary><b>🏥 Health Status</b></summary>

**Description**: Monitor system health and uptime.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "n8n-workflow-system"
}
```

**Use Cases**:
- Load balancer health checks
- Monitoring system integration
- Service discovery

</details>

---

## 📊 **Workflow Endpoints**

### `GET /workflows` - List Workflows

<details>
<summary><b>📋 Query Parameters</b></summary>

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `platform` | string | `null` | Filter by platform (`YouTube`, `Forum`, `Google`) |
| `country` | string | `null` | Filter by country (`US`, `IN`, `Unknown`) |
| `limit` | integer | `20` | Results per page (1-100) |
| `offset` | integer | `0` | Results to skip |

</details>

<details>
<summary><b>🎯 Example Requests</b></summary>

```bash
# Get top 10 workflows
curl "http://localhost:8000/workflows?limit=10"

# Filter by YouTube videos from US
curl "http://localhost:8000/workflows?platform=YouTube&country=US"

# Pagination - page 3 with 20 results per page
curl "http://localhost:8000/workflows?limit=20&offset=40"

# Complex filtering
curl "http://localhost:8000/workflows?platform=Forum&limit=5"
```

</details>

<details>
<summary><b>📄 Response Schema</b></summary>

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
      "replies": 0,
      "contributors": 0,
      "search_volume": 0,
      "like_to_view_ratio": 0.05,
      "comment_to_view_ratio": 0.007,
      "popularity_score": 15.2,
      "url": "https://youtube.com/watch?v=example1",
      "title": "Google Sheets → Slack Automation",
      "description": "Popular workflow description",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "has_next": true,
  "has_prev": false
}
```

</details>

### `GET /workflows/{id}` - Get Specific Workflow

<details>
<summary><b>🔍 Path Parameters</b></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | ✅ | Workflow ID |

</details>

<details>
<summary><b>📋 Example Usage</b></summary>

```bash
# Get workflow with ID 1
curl "http://localhost:8000/workflows/1"

# Get workflow with ID 42
curl "http://localhost:8000/workflows/42"
```

**Success Response (200)**:
```json
{
  "id": 1,
  "workflow_name": "Google Sheets → Slack Automation",
  "platform": "YouTube",
  "country": "US",
  "views": 12500,
  "likes": 630,
  "comments": 88,
  "popularity_score": 15.2,
  "url": "https://youtube.com/watch?v=example1",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Response (404)**:
```json
{
  "detail": "Workflow not found"
}
```

</details>

---

## 📈 **Statistics Endpoint**

### `GET /stats` - System Statistics

<details>
<summary><b>📊 Statistics Overview</b></summary>

**Description**: Get comprehensive system metrics and analytics.

**Example Request**:
```bash
curl "http://localhost:8000/stats"
```

**Response**:
```json
{
  "total_workflows": 150,
  "platforms": {
    "YouTube": 80,
    "Forum": 45,
    "Google": 25
  },
  "countries": {
    "US": 90,
    "IN": 60
  },
  "avg_popularity_score": 8.5,
  "top_workflow": "Google Sheets → Slack Automation",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

</details>

<details>
<summary><b>📋 Metrics Explained</b></summary>

| Metric | Description |
|--------|-------------|
| `total_workflows` | Total number of workflows in database |
| `platforms` | Count of workflows per platform |
| `countries` | Count of workflows per country |
| `avg_popularity_score` | Average popularity score across all workflows |
| `top_workflow` | Name of highest-scoring workflow |
| `last_updated` | Timestamp of most recent data update |

</details>

---

## ⚙️ **Admin Endpoints**

### `POST /admin/refresh` - Trigger Data Collection

<details>
<summary><b>🔄 Request Schema</b></summary>

**Content-Type**: `application/json`

```json
{
  "platforms": ["YouTube", "Forum", "Google"],
  "force": false
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `platforms` | array | `["YouTube", "Forum", "Google"]` | Platforms to refresh |
| `force` | boolean | `false` | Clear existing data before refresh |

</details>

<details>
<summary><b>🎯 Example Requests</b></summary>

```bash
# Refresh all platforms (incremental)
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["YouTube", "Forum", "Google"], "force": false}'

# Refresh only YouTube data
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["YouTube"]}'

# Force refresh (clear existing data)
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Default refresh (all platforms, incremental)
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{}'
```

</details>

<details>
<summary><b>📄 Response Schema</b></summary>

**Success Response (200)**:
```json
{
  "status": "success",
  "message": "Refreshed 45 workflows",
  "collected": 120,
  "processed": 45,
  "stored": 12,
  "errors": [],
  "platforms": ["YouTube", "Forum", "Google"]
}
```

**Error Response (500)**:
```json
{
  "detail": "Refresh failed: YouTube API quota exceeded"
}
```

| Field | Description |
|-------|-------------|
| `collected` | Total items collected from all platforms |
| `processed` | Items after scoring and normalization |
| `stored` | New items added to database |
| `errors` | List of any collection errors |

</details>

---

## 🚨 **Error Handling**

<div align="center">

### **HTTP Status Codes**

| Code | Status | Description |
|------|--------|-------------|
| `200` | ✅ OK | Request successful |
| `404` | ❌ Not Found | Resource not found |
| `422` | ⚠️ Validation Error | Invalid request parameters |
| `500` | 🔥 Internal Error | Server error |

</div>

<details>
<summary><b>📋 Error Response Format</b></summary>

All errors return consistent JSON format:

```json
{
  "detail": "Error message description"
}
```

**Validation Error Example**:
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 100}
    }
  ]
}
```

</details>

---

## 🔍 **Advanced Usage**

### **Pagination Best Practices**

<details>
<summary><b>📄 Pagination Strategy</b></summary>

```bash
# Get first page
curl "http://localhost:8000/workflows?limit=20&offset=0"

# Check has_next in response, then get next page
curl "http://localhost:8000/workflows?limit=20&offset=20"

# Calculate total pages
# total_pages = ceil(total / per_page)
```

**Pagination Response Fields**:
- `has_next`: Boolean indicating if more results exist
- `has_prev`: Boolean indicating if previous page exists
- `total`: Total number of results
- `page`: Current page number (1-indexed)

</details>

### **Filtering Combinations**

<details>
<summary><b>🎯 Advanced Filtering</b></summary>

```bash
# YouTube videos from US, top 5
curl "http://localhost:8000/workflows?platform=YouTube&country=US&limit=5"

# Forum posts only, paginated
curl "http://localhost:8000/workflows?platform=Forum&limit=10&offset=20"

# All workflows from India
curl "http://localhost:8000/workflows?country=IN"

# Case-insensitive platform matching
curl "http://localhost:8000/workflows?platform=youtube"  # Works!
```

**Filter Notes**:
- Filters are case-insensitive
- Partial matching supported
- Multiple filters are combined with AND logic

</details>

---

## 🌐 **Interactive Documentation**

<div align="center">

<table>
<tr>
<td align="center" width="50%">
<strong>📱 Swagger UI</strong><br>
<a href="http://localhost:8000/docs">http://localhost:8000/docs</a><br>
<em>Interactive API testing</em>
</td>
<td align="center" width="50%">
<strong>📚 ReDoc</strong><br>
<a href="http://localhost:8000/redoc">http://localhost:8000/redoc</a><br>
<em>Beautiful documentation</em>
</td>
</tr>
</table>

### **Features**:
- 🧪 **Try It Out**: Test endpoints directly in browser
- 📋 **Schema Validation**: Real-time request/response validation
- 🔍 **Search**: Find endpoints quickly
- 📱 **Mobile Friendly**: Responsive design

</div>

---

## 🚀 **Rate Limiting & Performance**

<details>
<summary><b>⚡ Performance Guidelines</b></summary>

### **Current Limits**
- **No rate limiting** implemented (add in production)
- **Max page size**: 100 workflows per request
- **Timeout**: 30 seconds for admin refresh

### **Optimization Tips**
```bash
# Use pagination for large datasets
curl "http://localhost:8000/workflows?limit=50"

# Filter to reduce response size
curl "http://localhost:8000/workflows?platform=YouTube&limit=10"

# Cache stats endpoint (updates infrequently)
curl "http://localhost:8000/stats"
```

### **Production Recommendations**
- Implement rate limiting (100 requests/minute)
- Add response caching for `/stats`
- Use CDN for static documentation
- Monitor API performance metrics

</details>

---

<div align="center">

## 🎯 **Ready to Use the API?**

<p>
<a href="http://localhost:8000/docs"><img src="https://img.shields.io/badge/🧪-Try%20Interactive%20Docs-blue?style=for-the-badge&logo=swagger" alt="Try Docs"></a>
<a href="http://localhost:8000/workflows?limit=5"><img src="https://img.shields.io/badge/📊-View%20Sample%20Data-green?style=for-the-badge&logo=json" alt="Sample Data"></a>
<a href="../README.md"><img src="https://img.shields.io/badge/📚-Back%20to%20Main%20Docs-orange?style=for-the-badge&logo=gitbook" alt="Main Docs"></a>
</p>

---

*Complete API reference for the n8n Workflow Popularity System*

</div>