import asyncio
import logging
from typing import List, Dict
from pytrends.request import TrendReq
import random

logger = logging.getLogger(__name__)

class GoogleCollector:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    def get_workflow_keywords(self) -> List[str]:
        """Get n8n workflow keywords for trends"""
        return [
            "n8n workflow", "n8n automation", "n8n tutorial",
            "google sheets n8n", "slack n8n", "discord n8n",
            "notion n8n", "airtable n8n", "gmail n8n",
            "webhook n8n", "api n8n", "database n8n",
            "salesforce n8n", "hubspot n8n", "stripe n8n",
            "shopify n8n", "wordpress n8n", "github n8n"
        ]
    
    async def get_interest_over_time(self, keywords: List[str], geo: str = "US") -> Dict:
        """Get search interest data"""
        try:
            # Limit to 5 keywords per request
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
            
            if interest_data.empty:
                return {}
                
            results = {}
            for keyword in keyword_batch:
                if keyword in interest_data.columns:
                    values = interest_data[keyword].values
                    avg_interest = float(values.mean())
                    
                    # Calculate trend change
                    if len(values) >= 4:
                        recent_avg = values[-4:].mean()
                        older_avg = values[:-4].mean() if len(values) > 4 else values.mean()
                        trend_change = recent_avg - older_avg
                    else:
                        trend_change = 0
                        
                    results[keyword] = {
                        "avg_interest": avg_interest,
                        "trend_change_60d": float(trend_change),
                        "search_volume": int(avg_interest * 1000),  # Estimated
                        "max_interest": float(values.max())
                    }
                    
            await asyncio.sleep(random.uniform(2, 4))  # Rate limiting
            return results
            
        except Exception as e:
            logger.error(f"Error getting Google Trends data for {geo}: {e}")
            return {}
    
    def extract_workflow_name(self, keyword: str) -> str:
        """Extract workflow name from keyword"""
        keyword_clean = keyword.lower().replace("n8n", "").strip()
        
        integrations = ["sheets", "slack", "discord", "notion", "gmail", "trello"]
        found = [i for i in integrations if i in keyword_clean]
        
        if found:
            return f"{found[0].title()} Integration"
            
        words = [w for w in keyword_clean.split() if w.isalpha() and len(w) > 2]
        return " ".join(word.title() for word in words[:2]) or "General Workflow"
    
    async def collect_all(self) -> List[Dict]:
        """Collect all Google Trends data"""
        logger.info("Starting Google Trends data collection")
        
        keywords = self.get_workflow_keywords()
        all_data = []
        
        # Process for both US and India
        for geo in ["US", "IN"]:
            # Process in batches of 5
            for i in range(0, min(len(keywords), 25), 5):
                batch = keywords[i:i+5]
                trends_data = await self.get_interest_over_time(batch, geo)
                
                for keyword, data in trends_data.items():
                    workflow_data = {
                        "platform": "Google",
                        "country": geo,
                        "workflow": self.extract_workflow_name(keyword),
                        "keyword": keyword,
                        "search_volume": data["search_volume"],
                        "trend_change_60d": data["trend_change_60d"],
                        "avg_interest": data["avg_interest"],
                        "views": data["search_volume"],  # Use as views
                        "url": f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '%20')}"
                    }
                    all_data.append(workflow_data)
                    
        logger.info(f"Collected {len(all_data)} Google Trends entries")
        return all_data