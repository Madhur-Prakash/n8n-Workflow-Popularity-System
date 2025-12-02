import asyncio
import logging
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db.models import Workflow
from collectors.youtube import YouTubeCollector
from collectors.forum import ForumCollector
from collectors.google import GoogleCollector
from services.scoring import WorkflowScorer
from services.normalizer import WorkflowNormalizer

logger = logging.getLogger(__name__)

async def run_pipeline(session: AsyncSession, platforms: List[str] = None, force: bool = False) -> Dict:
    """Run the complete data collection and processing pipeline"""
    
    if platforms is None:
        platforms = ["YouTube", "Forum", "Google"]
    
    logger.info(f"Starting pipeline for platforms: {platforms}")
    
    all_workflows = []
    results = {"collected": 0, "processed": 0, "stored": 0, "errors": []}
    
    # Data Collection Phase
    try:
        if "YouTube" in platforms:
            try:
                youtube_collector = YouTubeCollector()
                youtube_data = await youtube_collector.collect_all()
                all_workflows.extend(youtube_data)
                logger.info(f"Collected {len(youtube_data)} YouTube workflows")
            except Exception as e:
                error_msg = f"YouTube collection failed: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        if "Forum" in platforms:
            try:
                forum_collector = ForumCollector()
                forum_data = await forum_collector.collect_all()
                all_workflows.extend(forum_data)
                await forum_collector.close()
                logger.info(f"Collected {len(forum_data)} Forum workflows")
            except Exception as e:
                error_msg = f"Forum collection failed: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        if "Google" in platforms:
            try:
                google_collector = GoogleCollector()
                google_data = await google_collector.collect_all()
                all_workflows.extend(google_data)
                logger.info(f"Collected {len(google_data)} Google workflows")
            except Exception as e:
                error_msg = f"Google collection failed: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        results["collected"] = len(all_workflows)
        
        if not all_workflows:
            raise Exception("No data collected from any platform")
        
        # Scoring Phase
        for workflow in all_workflows:
            workflow["popularity_score"] = WorkflowScorer.calculate_score(workflow)
        
        # Normalization and Deduplication Phase
        normalized_workflows = WorkflowNormalizer.deduplicate_workflows(all_workflows)
        results["processed"] = len(normalized_workflows)
        
        # Database Storage Phase
        if force:
            # Clear existing data
            await session.execute(delete(Workflow))
            await session.commit()
        
        stored_count = 0
        for workflow_data in normalized_workflows:
            # Check if workflow exists
            stmt = select(Workflow).where(
                Workflow.workflow_name == workflow_data.get("workflow", ""),
                Workflow.platform == workflow_data.get("platform", ""),
                Workflow.country == workflow_data.get("country", "")
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing workflow
                for key, value in workflow_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                # Create new workflow
                workflow = Workflow(
                    workflow_name=workflow_data.get("workflow", ""),
                    platform=workflow_data.get("platform", ""),
                    country=workflow_data.get("country", ""),
                    views=workflow_data.get("views", 0),
                    likes=workflow_data.get("likes", 0),
                    comments=workflow_data.get("comments", 0),
                    replies=workflow_data.get("replies", 0),
                    contributors=workflow_data.get("contributors", 0),
                    search_volume=workflow_data.get("search_volume", 0),
                    like_to_view_ratio=workflow_data.get("like_to_view_ratio", 0.0),
                    comment_to_view_ratio=workflow_data.get("comment_to_view_ratio", 0.0),
                    popularity_score=workflow_data.get("popularity_score", 0.0),
                    url=workflow_data.get("url"),
                    title=workflow_data.get("title"),
                    description=workflow_data.get("description"),
                    raw_data=workflow_data
                )
                session.add(workflow)
                stored_count += 1
        
        await session.commit()
        results["stored"] = stored_count
        
        logger.info(f"Pipeline completed: {results}")
        return results
        
    except Exception as e:
        await session.rollback()
        error_msg = f"Pipeline failed: {e}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
        raise Exception(error_msg)