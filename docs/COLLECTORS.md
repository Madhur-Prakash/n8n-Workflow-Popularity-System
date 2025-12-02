# Data Collectors Documentation

## Overview

The system uses three specialized async collectors to gather workflow popularity data from different platforms. Each collector implements platform-specific APIs and handles rate limiting, error recovery, and data normalization.

## YouTube Collector

### API Integration
- **Service**: YouTube Data API v3
- **Authentication**: API Key
- **Endpoints Used**:
  - `search().list()` - Video search
  - `videos().list()` - Video statistics
- **Rate Limits**: 10,000 units/day (default quota)

### Implementation Details

```python
class YouTubeCollector:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
```

### Keyword Generation Strategy

The collector automatically generates 250+ keywords using a systematic approach:

```python
def generate_keywords(self) -> List[str]:
    integrations = [
        "google sheets", "slack", "discord", "notion", "airtable", 
        "trello", "gmail", "outlook", "salesforce", "hubspot"
        # ... 24 total integrations
    ]
    
    actions = ["automation", "integration", "sync", "connect", "workflow"]
    
    # Base keywords
    keywords = ["n8n", "n8n workflow", "n8n automation", "n8n tutorial"]
    
    # Integration combinations
    for integration in integrations:
        keywords.extend([
            f"{integration} n8n",
            f"n8n {integration}",
            f"{integration} automation n8n"
        ])
    
    # Action-based combinations
    for integration in integrations[:15]:
        for action in actions[:3]:
            keywords.append(f"{integration} {action} n8n")
```

### Data Collection Process

1. **Search Phase**: For each keyword and region (US, IN):
   ```python
   request = self.youtube.search().list(
       part="snippet",
       q=query,
       type="video",
       maxResults=10,
       regionCode=region,
       relevanceLanguage="en",
       order="relevance"
   )
   ```

2. **Statistics Phase**: Batch fetch video statistics:
   ```python
   request = self.youtube.videos().list(
       part="statistics",
       id=",".join(video_ids)  # Batch request
   )
   ```

3. **Metrics Calculation**:
   ```python
   views = int(video_stats.get("viewCount", 0))
   likes = int(video_stats.get("likeCount", 0))
   comments = int(video_stats.get("commentCount", 0))
   
   like_to_view_ratio = likes / views if views > 0 else 0
   comment_to_view_ratio = comments / views if views > 0 else 0
   ```

### Rate Limiting Strategy

```python
# Between API calls
await asyncio.sleep(0.1)

# Between keyword searches  
await asyncio.sleep(0.2)

# Error handling with exponential backoff
try:
    response = request.execute()
except HttpError as e:
    if e.resp.status == 403:  # Quota exceeded
        await asyncio.sleep(60)  # Wait 1 minute
        continue
```

### Workflow Name Extraction

```python
def extract_workflow_name(self, title: str) -> str:
    title_lower = title.lower()
    
    # Look for integration patterns
    integrations = ["sheets", "slack", "discord", "notion", "gmail"]
    found = [i for i in integrations if i in title_lower]
    
    if len(found) >= 2:
        return f"{found[0].title()} → {found[1].title()} Automation"
    elif len(found) == 1:
        return f"{found[0].title()} Integration"
    
    # Fallback to cleaned title
    words = [w for w in title.split()[:4] if w.isalpha()]
    return " ".join(word.title() for word in words) or "n8n Workflow"
```

## Forum Collector

### API Integration
- **Service**: Discourse API (n8n Community)
- **Base URL**: https://community.n8n.io
- **Authentication**: Public API (no key required)
- **Endpoints Used**:
  - `/latest.json` - Recent topics
  - `/t/{id}.json` - Topic details

### Implementation Details

```python
class ForumCollector:
    def __init__(self):
        self.base_url = "https://community.n8n.io"
        self.client = httpx.AsyncClient(timeout=30.0)
```

### Data Collection Process

1. **Topic Discovery**:
   ```python
   async def get_topics(self, page: int = 0) -> List[Dict]:
       url = f"{self.base_url}/latest.json"
       params = {"page": page}
       
       response = await self.client.get(url, params=params)
       data = response.json()
       
       # Filter for workflow-related topics
       workflow_keywords = ["workflow", "automation", "integration", "connect", "sync"]
       
       for topic in data.get("topic_list", {}).get("topics", []):
           title = topic.get("title", "").lower()
           if any(keyword in title for keyword in workflow_keywords):
               # Process topic...
   ```

2. **Topic Details**:
   ```python
   async def get_topic_details(self, topic_id: int) -> Dict:
       url = f"{self.base_url}/t/{topic_id}.json"
       response = await self.client.get(url)
       data = response.json()
       
       # Count unique contributors
       user_ids = set()
       posts = data.get("post_stream", {}).get("posts", [])
       for post in posts:
           if post.get("user_id"):
               user_ids.add(post.get("user_id"))
       
       return {
           "contributors": len(user_ids),
           "posts_count": len(posts),
           "tags": data.get("tags", [])
       }
   ```

### Country Inference Algorithm

```python
def infer_country(self, title: str) -> str:
    text = title.lower()
    
    us_indicators = ["dollar", "usd", "$", "america", "us"]
    india_indicators = ["rupee", "inr", "₹", "india", "indian"]
    
    us_count = sum(1 for indicator in us_indicators if indicator in text)
    india_count = sum(1 for indicator in india_indicators if indicator in text)
    
    if us_count > india_count:
        return "US"
    elif india_count > us_count:
        return "IN"
    return "Unknown"
```

### Workflow Detection

Topics are considered workflow-related if they contain:
- **Primary Keywords**: "workflow", "automation", "integration"
- **Action Keywords**: "connect", "sync", "n8n"
- **Service Keywords**: Integration service names

### Rate Limiting

```python
# Between topic requests
await asyncio.sleep(0.5)

# Between detail requests
await asyncio.sleep(0.3)

# Respect Discourse rate limits
# Typically 60 requests per minute for anonymous users
```

## Google Trends Collector

### API Integration
- **Service**: Google Trends (via PyTrends)
- **Library**: pytrends (unofficial API)
- **Rate Limits**: Aggressive (requires careful handling)
- **Timeframe**: Last 3 months

### Implementation Details

```python
class GoogleCollector:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
```

### Keyword Strategy

```python
def get_workflow_keywords(self) -> List[str]:
    return [
        "n8n workflow", "n8n automation", "n8n tutorial",
        "google sheets n8n", "slack n8n", "discord n8n",
        "notion n8n", "airtable n8n", "gmail n8n",
        "webhook n8n", "api n8n", "database n8n",
        # ... 18 total targeted keywords
    ]
```

### Data Collection Process

1. **Interest Over Time**:
   ```python
   async def get_interest_over_time(self, keywords: List[str], geo: str = "US") -> Dict:
       # Limit to 5 keywords per request (Google Trends limitation)
       keyword_batch = keywords[:5]
       
       await asyncio.to_thread(
           self.pytrends.build_payload,
           keyword_batch,
           cat=0,
           timeframe='today 3-m',
           geo=geo,
           gprop=''
       )
       
       interest_data = await asyncio.to_thread(self.pytrends.interest_over_time)
   ```

2. **Trend Analysis**:
   ```python
   # Calculate trend change over 60 days
   if len(values) >= 4:
       recent_avg = values[-4:].mean()  # Last 4 weeks
       older_avg = values[:-4].mean()   # Earlier weeks
       trend_change = recent_avg - older_avg
   else:
       trend_change = 0
   ```

3. **Search Volume Estimation**:
   ```python
   # Convert relative interest to estimated volume
   search_volume = int(avg_interest * 1000)
   ```

### Rate Limiting Strategy

```python
# Random delays to avoid detection
await asyncio.sleep(random.uniform(2, 4))

# Batch processing to minimize requests
for i in range(0, min(len(keywords), 25), 5):
    batch = keywords[i:i+5]
    # Process batch...
```

### Error Handling

```python
try:
    # Google Trends request
    trends_data = await self.get_interest_over_time(batch, geo)
except Exception as e:
    logger.error(f"Google Trends error for {geo}: {e}")
    # Continue with next batch
    continue
```

## Cross-Collector Patterns

### Error Handling Strategy

All collectors implement consistent error handling:

```python
async def collect_all(self) -> List[Dict]:
    logger.info(f"Starting {self.__class__.__name__} data collection")
    
    try:
        # Collection logic...
        all_data = []
        
        # Process data...
        
        logger.info(f"Collected {len(all_data)} items")
        return all_data
        
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        return []  # Return empty list, don't crash system
```

### Data Normalization

Each collector outputs standardized data format:

```python
{
    "platform": "YouTube|Forum|Google",
    "country": "US|IN|Unknown",
    "workflow": "Extracted workflow name",
    "views": 0,
    "likes": 0,
    "comments": 0,
    "url": "Source URL",
    # Platform-specific fields...
}
```

### Performance Optimization

1. **Async Operations**: All I/O operations are async
2. **Batch Processing**: Multiple items processed together
3. **Connection Pooling**: Reuse HTTP connections
4. **Memory Efficiency**: Stream processing where possible

### Monitoring and Logging

```python
# Structured logging with metrics
logger.info("Collection completed", extra={
    "platform": self.platform,
    "items_collected": len(results),
    "duration_seconds": time.time() - start_time,
    "success_rate": success_count / total_attempts
})
```

## Quality Assurance

### Data Validation

Each collector validates collected data:

```python
def validate_workflow_data(self, data: Dict) -> bool:
    required_fields = ["workflow", "platform", "country"]
    
    # Check required fields
    if not all(field in data for field in required_fields):
        return False
    
    # Validate numeric fields
    if data.get("views", 0) < 0:
        return False
    
    # Validate URL format
    if data.get("url") and not data["url"].startswith("http"):
        return False
    
    return True
```

### Deduplication

Cross-collector deduplication prevents duplicate entries:

```python
def is_duplicate(self, new_item: Dict, existing_items: List[Dict]) -> bool:
    for existing in existing_items:
        if (existing["platform"] == new_item["platform"] and
            existing["url"] == new_item["url"]):
            return True
    return False
```

This collector architecture ensures reliable, scalable data collection from multiple sources while maintaining data quality and system performance.