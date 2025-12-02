# API Documentation

Complete reference for the n8n Workflow Popularity System REST API.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Docker**: `http://localhost:8000`

## Authentication

No authentication required for read endpoints. Admin endpoints are open (add authentication in production).

## Endpoints

### Health & Info

#### `GET /`
Root endpoint with basic system information.

**Response:**
```json
{
  "message": "n8n Workflow Popularity System",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "n8n-workflow-system"
}
```

### Workflows

#### `GET /workflows`
List workflows with filtering and pagination.

**Query Parameters:**
- `platform` (optional): Filter by platform (`YouTube`, `Forum`, `Google`)
- `country` (optional): Filter by country (`US`, `IN`, `Unknown`)
- `limit` (optional): Results per page (1-100, default: 20)
- `offset` (optional): Results to skip (default: 0)

**Example Request:**
```bash
curl "http://localhost:8000/workflows?platform=YouTube&country=US&limit=10"
```

**Response:**
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
      "like_to_view_ratio": 0.05,
      "comment_to_view_ratio": 0.007,
      "popularity_score": 15.2,
      "url": "https://youtube.com/watch?v=example1",
      "title": "Google Sheets → Slack Automation",
      "description": "Popular Google Sheets → Slack Automation workflow",
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

#### `GET /workflows/{id}`
Get specific workflow by ID.

**Path Parameters:**
- `id`: Workflow ID (integer)

**Example Request:**
```bash
curl "http://localhost:8000/workflows/1"
```

**Response:**
```json
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
  "description": "Popular Google Sheets → Slack Automation workflow",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Statistics

#### `GET /stats`
Get system statistics and metrics.

**Example Request:**
```bash
curl "http://localhost:8000/stats"
```

**Response:**
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

### Admin

#### `POST /admin/refresh`
Trigger data collection and refresh.

**Request Body:**
```json
{
  "platforms": ["YouTube", "Forum", "Google"],
  "force": false
}
```

**Parameters:**
- `platforms` (optional): List of platforms to refresh (default: all)
- `force` (optional): Clear existing data before refresh (default: false)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/admin/refresh" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["YouTube"], "force": false}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Refreshed 45 workflows",
  "collected": 120,
  "processed": 45,
  "stored": 12,
  "errors": [],
  "platforms": ["YouTube"]
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `404`: Resource not found
- `422`: Validation error
- `500`: Internal server error

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Rate Limiting

No rate limiting implemented in current version. Add rate limiting middleware for production use.

## Pagination

All list endpoints support pagination:
- Use `limit` and `offset` parameters
- Check `has_next` and `has_prev` in response
- Maximum `limit` is 100

## Filtering

Workflows can be filtered by:
- **Platform**: `YouTube`, `Forum`, `Google`
- **Country**: `US`, `IN`, `Unknown`

Filters are case-insensitive and support partial matching.