import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from db.session import AsyncSessionLocal
from services.orchestrator import run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    async def refresh_job(self):
        """Scheduled refresh job"""
        try:
            logger.info("Starting scheduled data refresh")
            
            async with AsyncSessionLocal() as session:
                results = await run_pipeline(session)
                logger.info(f"Scheduled refresh completed: {results}")
                
        except Exception as e:
            logger.error(f"Scheduled refresh failed: {e}")
    
    async def start(self):
        """Start the scheduler"""
        
        # Daily refresh at 2 AM UTC
        self.scheduler.add_job(
            self.refresh_job,
            CronTrigger(hour=2, minute=0),
            id='daily_refresh',
            name='Daily Workflow Data Refresh'
        )
        
        # Weekly deep refresh on Sundays at 3 AM UTC
        self.scheduler.add_job(
            lambda: self.refresh_job_force(),
            CronTrigger(day_of_week=6, hour=3, minute=0),
            id='weekly_deep_refresh',
            name='Weekly Deep Refresh'
        )
        
        logger.info("Scheduler started with jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name}: {job.trigger}")
            
        self.scheduler.start()
        
        try:
            # Keep the scheduler running
            while True:
                await asyncio.sleep(3600)  # Sleep for 1 hour
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        finally:
            self.scheduler.shutdown()
    
    async def refresh_job_force(self):
        """Forced refresh job (weekly)"""
        try:
            logger.info("Starting weekly forced refresh")
            
            async with AsyncSessionLocal() as session:
                results = await run_pipeline(session, force=True)
                logger.info(f"Weekly refresh completed: {results}")
                
        except Exception as e:
            logger.error(f"Weekly refresh failed: {e}")

async def main():
    """Main scheduler function"""
    scheduler = WorkflowScheduler()
    await scheduler.start()

if __name__ == "__main__":
    asyncio.run(main())