from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
import statistics


@dataclass
class WorkflowMetrics:
    context_id: str
    start_time: datetime
    end_time: datetime = None
    agent_timings: Dict[str, float] = field(default_factory=dict)
    message_count: int = 0
    success: bool = False
    error_message: str = None
    
    @property
    def total_duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def to_dict(self) -> dict:
        return {
            "context_id": self.context_id,
            "total_duration": self.total_duration,
            "agent_timings": self.agent_timings,
            "message_count": self.message_count,
            "success": self.success,
            "error_message": self.error_message
        }


class MetricsCollector:
    def __init__(self):
        self.workflows: Dict[str, WorkflowMetrics] = {}
        self.message_latencies: List[float] = []
    
    def start_workflow(self, context_id: str) -> WorkflowMetrics:
        metrics = WorkflowMetrics(
            context_id=context_id,
            start_time=datetime.utcnow()
        )
        self.workflows[context_id] = metrics
        return metrics
    
    def end_workflow(self, context_id: str, success: bool = True, error: str = None):
        if context_id in self.workflows:
            self.workflows[context_id].end_time = datetime.utcnow()
            self.workflows[context_id].success = success
            self.workflows[context_id].error_message = error
    
    def record_agent_timing(self, context_id: str, agent_name: str, duration: float):
        if context_id in self.workflows:
            self.workflows[context_id].agent_timings[agent_name] = duration
    
    def increment_message_count(self, context_id: str):
        if context_id in self.workflows:
            self.workflows[context_id].message_count += 1
    
    def record_message_latency(self, latency: float):
        self.message_latencies.append(latency)
    
    def get_summary(self) -> dict:
        completed = [w for w in self.workflows.values() if w.end_time]
        successful = [w for w in completed if w.success]
        
        if not completed:
            return {
                "total_workflows": len(self.workflows),
                "completed": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0
            }
        
        return {
            "total_workflows": len(self.workflows),
            "completed": len(completed),
            "successful": len(successful),
            "success_rate": len(successful) / len(completed) if completed else 0.0,
            "avg_duration": statistics.mean([w.total_duration for w in completed]),
            "avg_message_latency": statistics.mean(self.message_latencies) if self.message_latencies else 0.0,
            "total_messages": sum(w.message_count for w in self.workflows.values())
        }


metrics_collector = MetricsCollector()
