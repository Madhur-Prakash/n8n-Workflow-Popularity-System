import re
import logging
from typing import List, Dict
from Levenshtein import distance

logger = logging.getLogger(__name__)

class WorkflowNormalizer:
    """Normalize and deduplicate workflow names"""
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize workflow name for comparison"""
        if not name:
            return ""
            
        # Lowercase and strip
        name = name.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes = ["how to", "n8n", "tutorial", "guide", "setup"]
        suffixes = ["automation", "workflow", "integration", "tutorial"]
        
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
                
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        
        # Normalize separators
        name = re.sub(r'[→\-\>\<\|]+', ' to ', name)
        name = re.sub(r'[&+]', ' and ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    @staticmethod
    def extract_services(name: str) -> List[str]:
        """Extract service names from workflow"""
        services = [
            "google sheets", "sheets", "slack", "discord", "notion", "airtable",
            "trello", "gmail", "outlook", "salesforce", "hubspot", "stripe",
            "webhook", "api", "database", "mysql", "postgresql"
        ]
        
        name_lower = name.lower()
        found = [service for service in services if service in name_lower]
        return found
    
    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> float:
        """Calculate similarity between workflow names"""
        norm1 = WorkflowNormalizer.normalize_name(name1)
        norm2 = WorkflowNormalizer.normalize_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
            
        # Levenshtein similarity
        max_len = max(len(norm1), len(norm2))
        if max_len == 0:
            return 1.0
            
        lev_similarity = 1 - (distance(norm1, norm2) / max_len)
        
        # Service overlap similarity
        services1 = set(WorkflowNormalizer.extract_services(norm1))
        services2 = set(WorkflowNormalizer.extract_services(norm2))
        
        if services1 and services2:
            service_similarity = len(services1 & services2) / len(services1 | services2)
        else:
            service_similarity = 0.0
            
        # Combined similarity
        return 0.7 * lev_similarity + 0.3 * service_similarity
    
    @staticmethod
    def deduplicate_workflows(workflows: List[Dict], threshold: float = 0.75) -> List[Dict]:
        """Remove duplicate workflows based on similarity"""
        if not workflows:
            return []
            
        deduplicated = []
        processed = set()
        
        for i, workflow in enumerate(workflows):
            if i in processed:
                continue
                
            similar_workflows = [workflow]
            processed.add(i)
            
            for j, other in enumerate(workflows[i+1:], i+1):
                if j in processed:
                    continue
                    
                similarity = WorkflowNormalizer.calculate_similarity(
                    workflow.get("workflow", ""),
                    other.get("workflow", "")
                )
                
                if similarity >= threshold:
                    similar_workflows.append(other)
                    processed.add(j)
            
            # Merge similar workflows
            if len(similar_workflows) > 1:
                merged = WorkflowNormalizer.merge_similar_workflows(similar_workflows)
                deduplicated.append(merged)
            else:
                deduplicated.append(workflow)
                
        return deduplicated
    
    @staticmethod
    def merge_similar_workflows(workflows: List[Dict]) -> Dict:
        """Merge similar workflows into one"""
        if not workflows:
            return {}
            
        # Use highest scoring workflow as base
        base = max(workflows, key=lambda x: x.get("popularity_score", 0))
        
        # Aggregate metrics
        total_views = sum(int(w.get("views", 0)) for w in workflows)
        total_likes = sum(int(w.get("likes", 0)) for w in workflows)
        total_comments = sum(int(w.get("comments", 0)) for w in workflows)
        
        # Calculate merged score
        scores = [w.get("popularity_score", 0) for w in workflows]
        merged_score = sum(scores) * 0.8 + max(scores) * 0.2
        
        merged = base.copy()
        merged.update({
            "views": total_views,
            "likes": total_likes,
            "comments": total_comments,
            "popularity_score": round(merged_score, 2),
            "platforms": list(set(w.get("platform") for w in workflows)),
            "merged_count": len(workflows)
        })
        
        return merged
    
    @staticmethod
    def canonicalize_workflow_name(name: str) -> str:
        """Create canonical workflow name"""
        normalized = WorkflowNormalizer.normalize_name(name)
        services = WorkflowNormalizer.extract_services(normalized)
        
        if len(services) >= 2:
            return f"{services[0].title()} → {services[1].title()} Integration"
        elif len(services) == 1:
            return f"{services[0].title()} Automation"
        else:
            words = [w.title() for w in normalized.split() if w.isalpha() and len(w) > 2]
            return " ".join(words[:3]) or "Unknown Workflow"