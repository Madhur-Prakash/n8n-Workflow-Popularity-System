import asyncio
import logging
from typing import List, Dict
import httpx
import re

logger = logging.getLogger(__name__)

class ForumCollector:
    def __init__(self):
        self.base_url = "https://community.n8n.io"
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def get_topics(self, page: int = 0) -> List[Dict]:
        """Get topics from n8n forum using Discourse API"""
        try:
            url = f"{self.base_url}/latest.json"
            params = {"page": page}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            topics = []
            
            for topic in data.get("topic_list", {}).get("topics", []):
                # Filter for workflow-related topics
                title = topic.get("title", "").lower()
                workflow_keywords = ["workflow", "automation", "integration", "connect", "sync"]
                
                if any(keyword in title for keyword in workflow_keywords):
                    topic_data = {
                        "id": topic["id"],
                        "title": topic["title"],
                        "slug": topic.get("slug", ""),
                        "url": f"{self.base_url}/t/{topic.get('slug', '')}/{topic['id']}",
                        "views": topic.get("views", 0),
                        "replies": topic.get("reply_count", 0),
                        "likes": topic.get("like_count", 0),
                        "posts_count": topic.get("posts_count", 0),
                        "created_at": topic.get("created_at"),
                        "platform": "Forum",
                        "country": self.infer_country(topic["title"]),
                        "workflow": self.extract_workflow_name(topic["title"])
                    }
                    topics.append(topic_data)
                    
            await asyncio.sleep(0.5)  # Rate limiting
            return topics
            
        except Exception as e:
            logger.error(f"Error fetching forum topics: {e}")
            return []
    
    async def get_topic_details(self, topic_id: int) -> Dict:
        """Get detailed topic information"""
        try:
            url = f"{self.base_url}/t/{topic_id}.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
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
            
        except Exception as e:
            logger.error(f"Error fetching topic {topic_id} details: {e}")
            return {}
    
    def infer_country(self, title: str) -> str:
        """Infer country from content"""
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
    
    def extract_workflow_name(self, title: str) -> str:
        """Extract workflow name from forum title"""
        title_lower = title.lower()
        
        integrations = [
            "google sheets", "slack", "discord", "notion", "airtable", "trello",
            "gmail", "webhook", "api", "database", "mysql", "postgresql"
        ]
        
        found = [i for i in integrations if i in title_lower]
        
        if len(found) >= 2:
            return f"{found[0].title()} → {found[1].title()} Integration"
        elif len(found) == 1:
            return f"{found[0].title()} Workflow"
            
        # Fallback
        words = [w for w in title.split()[:3] if w.isalpha() and len(w) > 2]
        return " ".join(word.title() for word in words) or "n8n Workflow"
    
    async def collect_all(self) -> List[Dict]:
        """Collect all forum data"""
        logger.info("Starting forum data collection")
        
        all_topics = []
        
        # Get topics from first 3 pages
        for page in range(3):
            topics = await self.get_topics(page)
            if not topics:
                break
                
            for topic in topics:
                # Get additional details for workflow topics
                details = await self.get_topic_details(topic["id"])
                topic.update(details)
                all_topics.append(topic)
                await asyncio.sleep(0.3)
                
        logger.info(f"Collected {len(all_topics)} forum topics")
        return all_topics
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()