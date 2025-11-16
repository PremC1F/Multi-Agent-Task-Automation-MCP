import asyncio
import uuid
from typing import Optional
from src.core.mcp_protocol import create_message, encode_message
from src.core.redis_manager import redis_manager
from src.core.db_manager import db_manager
from src.utils.logger import get_logger
from src.utils.metrics import metrics_collector

logger = get_logger("WorkflowRunner")


class WorkflowRunner:
    def __init__(self):
        self.active_workflows = {}
    
    async def start_workflow(self, query: str, context_id: Optional[str] = None) -> str:
        """Start a new workflow."""
        if not context_id:
            context_id = str(uuid.uuid4())
        
        logger.info(f"Starting workflow for query: {query}", context_id=context_id)
        
        metrics_collector.start_workflow(context_id)
        db_manager.create_task(context_id)
        
        message = create_message(
            context_id=context_id,
            sender="workflow_runner",
            receiver="researcher_agent",
            payload={"query": query}
        )
        
        encoded = encode_message(message)
        await redis_manager.publish("researcher_input", encoded)
        
        self.active_workflows[context_id] = {
            "query": query,
            "status": "running"
        }
        
        logger.info(f"Workflow initiated", context_id=context_id)
        return context_id
    
    async def get_workflow_status(self, context_id: str) -> Optional[dict]:
        """Get workflow status from database."""
        task = db_manager.get_task(context_id)
        if not task:
            return None
        
        results = db_manager.get_results(context_id)
        
        workflow_metrics = metrics_collector.workflows.get(context_id)
        metrics_data = workflow_metrics.to_dict() if workflow_metrics else {}
        
        return {
            "context_id": context_id,
            "status": task.status,
            "success": task.success,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": task.error_message,
            "results_count": len(results),
            "metrics": metrics_data
        }
    
    async def wait_for_completion(self, context_id: str, timeout: float = 30.0) -> bool:
        """Wait for workflow to complete."""
        logger.info(f"Waiting for workflow completion", context_id=context_id)
        
        elapsed = 0.0
        poll_interval = 0.5
        
        while elapsed < timeout:
            task = db_manager.get_task(context_id)
            if task and task.status == "completed":
                logger.info(f"Workflow completed successfully", context_id=context_id)
                metrics_collector.end_workflow(context_id, success=task.success)
                return task.success
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        logger.warning(f"Workflow timeout after {timeout}s", context_id=context_id)
        metrics_collector.end_workflow(context_id, success=False, error="Timeout")
        return False


workflow_runner = WorkflowRunner()
