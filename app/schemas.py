from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class WorkflowBase(BaseModel):
    workflow_name: str = Field(..., description="Name of the workflow")
    platform: str = Field(..., description="Platform (YouTube, Forum, Google)")
    country: str = Field(..., description="Country code (US, IN, Unknown)")
    views: int = Field(default=0, description="View count")
    likes: int = Field(default=0, description="Like count")
    comments: int = Field(default=0, description="Comment count")
    replies: int = Field(default=0, description="Reply count (Forum)")
    contributors: int = Field(default=0, description="Contributor count (Forum)")
    search_volume: int = Field(default=0, description="Search volume (Google)")
    like_to_view_ratio: float = Field(default=0.0, description="Like to view ratio")
    comment_to_view_ratio: float = Field(default=0.0, description="Comment to view ratio")
    popularity_score: float = Field(default=0.0, description="Calculated popularity score")
    url: Optional[str] = Field(None, description="URL to the content")
    title: Optional[str] = Field(None, description="Title of the content")
    description: Optional[str] = Field(None, description="Description of the content")

class WorkflowCreate(WorkflowBase):
    raw_data: Optional[Dict[str, Any]] = None

class WorkflowResponse(WorkflowBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowListResponse(BaseModel):
    workflows: List[WorkflowResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class StatsResponse(BaseModel):
    total_workflows: int
    platforms: Dict[str, int]
    countries: Dict[str, int]
    avg_popularity_score: float
    top_workflow: Optional[str]
    last_updated: Optional[datetime]

class RefreshRequest(BaseModel):
    platforms: Optional[List[str]] = Field(default=None, description="Platforms to refresh")
    force: bool = Field(default=False, description="Force refresh (clear existing data)")

class RefreshResponse(BaseModel):
    status: str
    message: str
    collected: int
    processed: int
    stored: int
    errors: List[str]
    platforms: List[str]