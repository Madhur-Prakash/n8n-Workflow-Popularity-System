from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
import logging
from datetime import datetime
import os

from db.session import get_db, create_tables, create_database_if_not_exists
from db.models import Workflow
from app.schemas import (
    WorkflowResponse, WorkflowListResponse, StatsResponse, 
    RefreshRequest, RefreshResponse
)
from services.orchestrator import run_pipeline

# Setup logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="n8n Workflow Popularity API",
    description="API for tracking popular n8n workflows across platforms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await create_database_if_not_exists()
    await create_tables()
    logger.info("Application started successfully")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "n8n Workflow Popularity System",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "n8n-workflow-system"
    }

@app.get("/workflows", response_model=WorkflowListResponse, tags=["Workflows"])
async def get_workflows(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    country: Optional[str] = Query(None, description="Filter by country"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
):
    """Get workflows with filtering and pagination"""
    
    # Build query
    query = select(Workflow)
    
    # Apply filters
    if platform:
        query = query.where(Workflow.platform.ilike(f"%{platform}%"))
    if country:
        query = query.where(Workflow.country.ilike(f"%{country}%"))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(desc(Workflow.popularity_score)).offset(offset).limit(limit)
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    page = offset // limit + 1
    
    return WorkflowListResponse(
        workflows=workflows,
        total=total,
        page=page,
        per_page=limit,
        has_next=offset + limit < total,
        has_prev=offset > 0
    )

@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse, tags=["Workflows"])
async def get_workflow(workflow_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific workflow by ID"""
    
    query = select(Workflow).where(Workflow.id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow

@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get system statistics"""
    
    # Total workflows
    total_result = await db.execute(select(func.count(Workflow.id)))
    total_workflows = total_result.scalar()
    
    # Platform distribution
    platform_query = select(Workflow.platform, func.count(Workflow.id)).group_by(Workflow.platform)
    platform_result = await db.execute(platform_query)
    platforms = {platform: count for platform, count in platform_result.all()}
    
    # Country distribution
    country_query = select(Workflow.country, func.count(Workflow.id)).group_by(Workflow.country)
    country_result = await db.execute(country_query)
    countries = {country: count for country, count in country_result.all()}
    
    # Average popularity score
    avg_query = select(func.avg(Workflow.popularity_score))
    avg_result = await db.execute(avg_query)
    avg_score = avg_result.scalar() or 0.0
    
    # Top workflow
    top_query = select(Workflow.workflow_name).order_by(desc(Workflow.popularity_score)).limit(1)
    top_result = await db.execute(top_query)
    top_workflow = top_result.scalar()
    
    # Last updated
    last_updated_query = select(func.max(Workflow.updated_at))
    last_updated_result = await db.execute(last_updated_query)
    last_updated = last_updated_result.scalar()
    
    return StatsResponse(
        total_workflows=total_workflows,
        platforms=platforms,
        countries=countries,
        avg_popularity_score=round(avg_score, 2),
        top_workflow=top_workflow,
        last_updated=last_updated
    )

@app.post("/admin/refresh", response_model=RefreshResponse, tags=["Admin"])
async def refresh_data(
    request: RefreshRequest = RefreshRequest(),
    db: AsyncSession = Depends(get_db)
):
    """Trigger data collection and refresh"""
    
    logger.info(f"Starting data refresh: {request}")
    
    try:
        platforms = request.platforms or ["YouTube", "Forum", "Google"]
        results = await run_pipeline(db, platforms, request.force)
        
        return RefreshResponse(
            status="success",
            message=f"Refreshed {results['processed']} workflows",
            collected=results["collected"],
            processed=results["processed"],
            stored=results["stored"],
            errors=results["errors"],
            platforms=platforms
        )
        
    except Exception as e:
        logger.error(f"Data refresh failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)