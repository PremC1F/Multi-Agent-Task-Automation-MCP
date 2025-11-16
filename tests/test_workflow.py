import pytest
import asyncio
from src.core.workflow_runner import WorkflowRunner
from src.utils.metrics import MetricsCollector
from src.core.mcp_protocol import encode_message, decode_message, create_message


@pytest.mark.asyncio
async def test_workflow_runner_start():
    """Test workflow runner can start a workflow."""
    runner = WorkflowRunner()
    query = "test workflow"
    
    context_id = await runner.start_workflow(query)
    
    assert context_id is not None
    assert len(context_id) > 0
    assert context_id in runner.active_workflows
    assert runner.active_workflows[context_id]["query"] == query


@pytest.mark.asyncio
async def test_workflow_status_retrieval():
    """Test retrieving workflow status."""
    runner = WorkflowRunner()
    
    status = await runner.get_workflow_status("non-existent-id")
    assert status is None


def test_metrics_collector():
    """Test metrics collector functionality."""
    collector = MetricsCollector()
    context_id = "metrics-test-001"
    
    metrics = collector.start_workflow(context_id)
    assert metrics.context_id == context_id
    assert metrics.success is False
    
    collector.record_agent_timing(context_id, "test_agent", 1.5)
    collector.increment_message_count(context_id)
    collector.end_workflow(context_id, success=True)
    
    assert metrics.success is True
    assert "test_agent" in metrics.agent_timings
    assert metrics.message_count == 1


def test_mcp_encode_decode():
    """Test MCP message encoding and decoding."""
    original = create_message(
        context_id="encode-test-001",
        sender="sender_agent",
        receiver="receiver_agent",
        payload={"data": "test", "count": 42}
    )
    
    encoded = encode_message(original)
    assert isinstance(encoded, str)
    
    decoded = decode_message(encoded)
    assert decoded.context_id == original.context_id
    assert decoded.sender == original.sender
    assert decoded.receiver == original.receiver
    assert decoded.payload == original.payload


def test_metrics_summary():
    """Test metrics summary generation."""
    collector = MetricsCollector()
    
    for i in range(3):
        context_id = f"summary-test-{i}"
        collector.start_workflow(context_id)
        collector.record_agent_timing(context_id, "agent1", 0.5)
        collector.increment_message_count(context_id)
        collector.end_workflow(context_id, success=True)
    
    summary = collector.get_summary()
    
    assert summary["total_workflows"] == 3
    assert summary["completed"] == 3
    assert summary["successful"] == 3
    assert summary["success_rate"] == 1.0
    assert summary["total_messages"] == 3
