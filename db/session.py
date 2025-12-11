import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from .models import Base
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/n8n_workflows")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        if "postgresql" in DATABASE_URL:
            # Extract database name
            db_name = DATABASE_URL.split("/")[-1]
            admin_url = DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
            
            admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
            async with admin_engine.connect() as conn:
                result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
                if not result.fetchone():
                    await conn.execute(text(f"CREATE DATABASE {db_name}"))
            await admin_engine.dispose()
    except Exception as e:
        logger.warning(f"Could not create database: {e}")

async def create_tables():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()