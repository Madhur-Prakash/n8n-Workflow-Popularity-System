import math
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class WorkflowScorer:
    """Calculate popularity scores using platform-specific algorithms"""
    
    @staticmethod
    def calculate_youtube_score(data: Dict) -> float:
        """YouTube: score = log(views+1) * (1 + engagement * 10)"""
        views = int(data.get("views", 0))
        likes = int(data.get("likes", 0))
        comments = int(data.get("comments", 0))
        
        if views == 0:
            return 0.0
            
        like_ratio = likes / views
        comment_ratio = comments / views
        
        engagement = 0.6 * like_ratio + 0.4 * comment_ratio
        score = math.log(views + 1) * (1 + engagement * 10)
        
        return round(score, 2)
    
    @staticmethod
    def calculate_forum_score(data: Dict) -> float:
        """Forum: score = log(views) + replies*0.4 + contributors*0.6 + upvotes*0.5"""
        views = int(data.get("views", 0))
        replies = int(data.get("replies", 0))
        contributors = int(data.get("contributors", 0))
        likes = int(data.get("likes", 0))
        
        if views == 0:
            return 0.0
            
        score = (
            math.log(views + 1) +
            replies * 0.4 +
            contributors * 0.6 +
            likes * 0.5
        )
        
        return round(score, 2)
    
    @staticmethod
    def calculate_google_score(data: Dict) -> float:
        """Google: score = search_volume * 0.001 + trend_change_60d * 10"""
        search_volume = int(data.get("search_volume", 0))
        trend_change = float(data.get("trend_change_60d", 0))
        
        score = search_volume * 0.001 + trend_change * 10
        
        return round(max(score, 0), 2)
    
    @classmethod
    def calculate_score(cls, data: Dict) -> float:
        """Calculate score based on platform"""
        platform = data.get("platform", "").lower()
        
        if platform == "youtube":
            return cls.calculate_youtube_score(data)
        elif platform == "forum":
            return cls.calculate_forum_score(data)
        elif platform == "google":
            return cls.calculate_google_score(data)
        else:
            return 0.0
    
    @staticmethod
    def merge_workflow_scores(workflows: List[Dict]) -> List[Dict]:
        """Merge scores for same workflow across platforms"""
        workflow_groups = {}
        
        # Group by normalized workflow name
        for workflow in workflows:
            name = workflow.get("workflow", "").lower().strip()
            if name not in workflow_groups:
                workflow_groups[name] = []
            workflow_groups[name].append(workflow)
        
        merged_workflows = []
        
        for name, group in workflow_groups.items():
            if not group:
                continue
                
            # Use highest scoring entry as base
            base_workflow = max(group, key=lambda x: x.get("popularity_score", 0))
            
            # Aggregate metrics
            total_views = sum(int(w.get("views", 0)) for w in group)
            total_likes = sum(int(w.get("likes", 0)) for w in group)
            total_comments = sum(int(w.get("comments", 0)) for w in group)
            
            # Calculate combined score
            platform_scores = [w.get("popularity_score", 0) for w in group]
            combined_score = sum(platform_scores) * 0.7 + max(platform_scores) * 0.3
            
            merged_workflow = base_workflow.copy()
            merged_workflow.update({
                "views": total_views,
                "likes": total_likes,
                "comments": total_comments,
                "popularity_score": round(combined_score, 2),
                "platforms": [w.get("platform") for w in group],
                "platform_count": len(set(w.get("platform") for w in group))
            })
            
            merged_workflows.append(merged_workflow)
        
        return sorted(merged_workflows, key=lambda x: x.get("popularity_score", 0), reverse=True)