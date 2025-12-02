#!/usr/bin/env python3
"""Load seed data into the database"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from db.session import AsyncSessionLocal, create_tables
from db.models import Workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_seed_data():
    """Load seed data from JSON file"""
    try:
        # Ensure tables exist
        await create_tables()
        
        # Load seed data
        seed_file = project_root / "seed_data.json"
        with open(seed_file, 'r') as f:
            workflows_data = json.load(f)
        
        async with AsyncSessionLocal() as session:
            # Clear existing data
            await session.execute("DELETE FROM workflows")
            await session.commit()
            
            # Insert seed data
            for workflow_data in workflows_data:
                metrics = workflow_data.get("popularity_metrics", {})
                
                workflow = Workflow(
                    workflow_name=workflow_data.get("workflow", ""),
                    platform=workflow_data.get("platform", ""),
                    country=workflow_data.get("country", ""),
                    views=metrics.get("views", 0),
                    likes=metrics.get("likes", 0),
                    comments=metrics.get("comments", 0),
                    replies=metrics.get("replies", 0),
                    contributors=metrics.get("contributors", 0),
                    search_volume=metrics.get("search_volume", 0),
                    like_to_view_ratio=metrics.get("like_to_view_ratio", 0.0),
                    comment_to_view_ratio=metrics.get("comment_to_view_ratio", 0.0),
                    popularity_score=workflow_data.get("popularity_score", 0.0),
                    url=workflow_data.get("url"),
                    title=workflow_data.get("workflow"),
                    description=f"Popular {workflow_data.get('workflow')} workflow",
                    raw_data=workflow_data
                )
                session.add(workflow)
            
            await session.commit()
            logger.info(f"Loaded {len(workflows_data)} workflows into database")
            
    except Exception as e:
        logger.error(f"Error loading seed data: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(load_seed_data())