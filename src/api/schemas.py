from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TaskStartRequest(BaseModel):
    query: str = Field(..., description="Query or topic to research")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning"
            }
        }


class TaskStartResponse(BaseModel):
    context_id: str
    message: str
    query: str


class TaskStatusResponse(BaseModel):
    context_id: str
    status: str
    success: bool
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    results_count: int
    metrics: Dict[str, Any]


class AgentStatus(BaseModel):
    name: str
    running: bool
    input_channel: str
    output_channel: Optional[str]


class AgentsStatusResponse(BaseModel):
    agents: Dict[str, AgentStatus]
    total: int


class MetricsSummaryResponse(BaseModel):
    total_workflows: int
    completed: int
    successful: int
    success_rate: float
    avg_duration: float
    avg_message_latency: float
    total_messages: int


class HealthResponse(BaseModel):
    status: str
    agents_healthy: bool
    timestamp: str
