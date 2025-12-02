import os
import asyncio
import logging
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable required")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        
    def generate_keywords(self) -> List[str]:
        """Generate 200+ n8n workflow keywords"""
        integrations = [
            "google sheets", "slack", "discord", "notion", "airtable", "trello",
            "gmail", "outlook", "salesforce", "hubspot", "stripe", "paypal", 
            "shopify", "wordpress", "github", "jira", "asana", "monday",
            "webhook", "api", "database", "mysql", "postgresql", "mongodb"
        ]
        
        actions = ["automation", "integration", "sync", "connect", "workflow"]
        
        keywords = ["n8n", "n8n workflow", "n8n automation", "n8n tutorial"]
        
        # Integration combinations
        for integration in integrations:
            keywords.extend([
                f"{integration} n8n",
                f"n8n {integration}",
                f"{integration} automation n8n"
            ])
            
        # Action combinations
        for integration in integrations[:15]:
            for action in actions[:3]:
                keywords.append(f"{integration} {action} n8n")
                
        return keywords[:250]
    
    async def search_videos(self, query: str, region: str = "US") -> List[Dict]:
        """Search YouTube videos"""
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=10,
                regionCode=region,
                relevanceLanguage="en",
                order="relevance"
            )
            response = request.execute()
            
            videos = []
            video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
            
            if video_ids:
                stats = await self.get_video_stats(video_ids)
                
                for item in response.get("items", []):
                    video_id = item["id"]["videoId"]
                    snippet = item["snippet"]
                    video_stats = stats.get(video_id, {})
                    
                    views = int(video_stats.get("viewCount", 0))
                    likes = int(video_stats.get("likeCount", 0))
                    comments = int(video_stats.get("commentCount", 0))
                    
                    video_data = {
                        "id": video_id,
                        "title": snippet["title"],
                        "description": snippet.get("description", ""),
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "views": views,
                        "likes": likes,
                        "comments": comments,
                        "like_to_view_ratio": likes / views if views > 0 else 0,
                        "comment_to_view_ratio": comments / views if views > 0 else 0,
                        "platform": "YouTube",
                        "country": region,
                        "workflow": self.extract_workflow_name(snippet["title"])
                    }
                    videos.append(video_data)
                    
            await asyncio.sleep(0.1)  # Rate limiting
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error for '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube for '{query}': {e}")
            return []
    
    async def get_video_stats(self, video_ids: List[str]) -> Dict:
        """Get statistics for multiple videos"""
        try:
            request = self.youtube.videos().list(
                part="statistics",
                id=",".join(video_ids)
            )
            response = request.execute()
            
            stats = {}
            for item in response.get("items", []):
                stats[item["id"]] = item["statistics"]
            return stats
            
        except Exception as e:
            logger.error(f"Error getting video stats: {e}")
            return {}
    
    def extract_workflow_name(self, title: str) -> str:
        """Extract workflow name from title"""
        title_lower = title.lower()
        
        # Look for integration patterns
        integrations = ["sheets", "slack", "discord", "notion", "gmail", "trello", "airtable"]
        found = [i for i in integrations if i in title_lower]
        
        if len(found) >= 2:
            return f"{found[0].title()} → {found[1].title()} Automation"
        elif len(found) == 1:
            return f"{found[0].title()} Integration"
            
        # Fallback
        words = [w for w in title.split()[:4] if w.isalpha()]
        return " ".join(word.title() for word in words) or "n8n Workflow"
    
    async def collect_all(self) -> List[Dict]:
        """Collect all YouTube data"""
        logger.info("Starting YouTube data collection")
        
        keywords = self.generate_keywords()
        all_videos = []
        
        for region in ["US", "IN"]:
            for keyword in keywords[:30]:  # Limit for quota
                videos = await self.search_videos(keyword, region)
                all_videos.extend(videos)
                await asyncio.sleep(0.2)  # Rate limiting
                
        logger.info(f"Collected {len(all_videos)} YouTube videos")
        return all_videos