from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from src.api.routes import router
from src.agents.coordinator import coordinator
from src.core.db_manager import db_manager
from src.core.redis_manager import redis_manager
from src.utils.logger import get_logger
from src.core.config import settings

logger = get_logger("Main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Multi-Agent Task Automation Platform...")
    
    try:
        db_manager.initialize()
        logger.info("Database initialized")
        
        await redis_manager.connect()
        logger.info("Redis connected")
        
        await coordinator.start_all_agents()
        logger.info("All agents started")
        
        logger.info(f"Platform ready on port {settings.api_port}")
        
        yield
        
    finally:
        logger.info("Shutting down...")
        await coordinator.stop_all_agents()
        await redis_manager.disconnect()
        logger.info("Platform stopped")


app = FastAPI(
    title="Multi-Agent Task Automation Platform",
    description="Autonomous multi-agent system using Model Context Protocol (MCP)",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1", tags=["tasks"])


@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Task Automation Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.environment == "development"
    )
