from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Optional

Base = declarative_base()

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(500), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    country = Column(String(10), nullable=False, index=True)
    
    # Metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    contributors = Column(Integer, default=0)
    search_volume = Column(Integer, default=0)
    
    # Ratios
    like_to_view_ratio = Column(Float, default=0.0)
    comment_to_view_ratio = Column(Float, default=0.0)
    
    # Score
    popularity_score = Column(Float, default=0.0, index=True)
    
    # Metadata
    url = Column(String(1000))
    title = Column(Text)
    description = Column(Text)
    raw_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Composite indexes for performance
    __table_args__ = (
        Index('idx_platform_country', 'platform', 'country'),
        Index('idx_score_platform', 'popularity_score', 'platform'),
    )