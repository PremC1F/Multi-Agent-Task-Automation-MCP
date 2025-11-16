from fastapi import APIRouter, HTTPException
from datetime import datetime
from src.api.schemas import (
    TaskStartRequest, TaskStartResponse, TaskStatusResponse,
    AgentsStatusResponse, AgentStatus, MetricsSummaryResponse, HealthResponse
)
from src.core.workflow_runner import workflow_runner
from src.agents.coordinator import coordinator
from src.utils.metrics import metrics_collector
from src.utils.logger import get_logger

logger = get_logger("API")
router = APIRouter()


@router.post("/task/start", response_model=TaskStartResponse)
async def start_task(request: TaskStartRequest):
    """Start a new workflow task."""
    try:
        context_id = await workflow_runner.start_workflow(request.query)
        logger.info(f"Task started via API", context_id=context_id)
        
        return TaskStartResponse(
            context_id=context_id,
            message=f"Workflow started: {context_id}",
            query=request.query
        )
    except Exception as e:
        logger.error(f"Failed to start task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{context_id}", response_model=TaskStatusResponse)
async def get_task_status(context_id: str):
    """Get status of a specific task."""
    try:
        status = await workflow_runner.get_workflow_status(context_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskStatusResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=AgentsStatusResponse)
async def get_agents_status():
    """Get status of all agents."""
    try:
        agent_statuses = coordinator.get_agent_status()
        
        agents = {
            name: AgentStatus(**info)
            for name, info in agent_statuses.items()
        }
        
        return AgentsStatusResponse(
            agents=agents,
            total=len(agents)
        )
    except Exception as e:
        logger.error(f"Failed to get agents status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=MetricsSummaryResponse)
async def get_metrics():
    """Get system metrics summary."""
    try:
        summary = metrics_collector.get_summary()
        return MetricsSummaryResponse(**summary)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        agents_healthy = await coordinator.health_check()
        
        return HealthResponse(
            status="healthy" if agents_healthy else "degraded",
            agents_healthy=agents_healthy,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            agents_healthy=False,
            timestamp=datetime.utcnow().isoformat()
        )
