import pytest
import asyncio
from unittest.mock import Mock, patch
from src.agents.researcher_agent import ResearcherAgent
from src.agents.summarizer_agent import SummarizerAgent
from src.agents.validator_agent import ValidatorAgent
from src.core.mcp_protocol import create_message


@pytest.fixture(autouse=True)
def mock_db_manager():
    """Mock database manager to avoid needing PostgreSQL for tests."""
    with patch('src.core.db_manager.db_manager') as mock_db:
        mock_db.log_agent_action = Mock()
        mock_db.save_result = Mock()
        mock_db.update_task_status = Mock()
        yield mock_db


@pytest.mark.asyncio
async def test_researcher_agent_run():
    """Test researcher agent data gathering."""
    agent = ResearcherAgent()
    context_id = "test-001"
    query = "artificial intelligence"
    
    data = await agent.run(context_id, query=query)
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, str) for item in data)
    assert query in data[0].lower()


@pytest.mark.asyncio
async def test_summarizer_agent_run():
    """Test summarizer agent text summarization."""
    agent = SummarizerAgent()
    context_id = "test-002"
    data = [
        "This is a test sentence about machine learning.",
        "Another sentence discussing neural networks.",
        "Final sentence about deep learning applications."
    ]
    
    summary = await agent.run(context_id, data=data, query="machine learning")
    
    assert isinstance(summary, str)
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_validator_agent_run():
    """Test validator agent validation logic."""
    agent = ValidatorAgent()
    context_id = "test-003"
    
    valid_summary = "This is a valid summary with sufficient length and content about machine learning."
    is_valid, report = await agent.run(context_id, summary=valid_summary, query="machine learning")
    
    assert isinstance(is_valid, bool)
    assert isinstance(report, str)
    assert len(report) > 0


@pytest.mark.asyncio
async def test_validator_rejects_short_summary():
    """Test that validator rejects summaries that are too short."""
    agent = ValidatorAgent()
    context_id = "test-004"
    
    short_summary = "Too short"
    is_valid, report = await agent.run(context_id, summary=short_summary, query="test")
    
    assert is_valid is False
    assert "too short" in report.lower()


def test_mcp_message_creation():
    """Test MCP message protocol."""
    message = create_message(
        context_id="test-005",
        sender="test_sender",
        receiver="test_receiver",
        payload={"key": "value"}
    )
    
    assert message.context_id == "test-005"
    assert message.sender == "test_sender"
    assert message.receiver == "test_receiver"
    assert message.payload["key"] == "value"
    assert message.message_id is not None
