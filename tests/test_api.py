import pytest
from httpx import AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "agents_healthy" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_agents_status():
    """Test get agents status endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/agents")
    
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "total" in data
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_get_metrics():
    """Test metrics endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/metrics")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_workflows" in data
    assert "success_rate" in data
    assert "avg_duration" in data


@pytest.mark.asyncio
async def test_start_task_endpoint():
    """Test task start endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/task/start",
            json={"query": "test query"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "context_id" in data
    assert "message" in data
    assert "query" in data
    assert data["query"] == "test query"


@pytest.mark.asyncio
async def test_get_task_status_not_found():
    """Test getting status of non-existent task."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/task/non-existent-id")
    
    assert response.status_code == 404
