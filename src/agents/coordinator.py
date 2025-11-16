import asyncio
from typing import Dict, List
from src.agents.researcher_agent import ResearcherAgent
from src.agents.summarizer_agent import SummarizerAgent
from src.agents.validator_agent import ValidatorAgent
from src.utils.logger import get_logger
from src.utils.metrics import metrics_collector

logger = get_logger("Coordinator")


class AgentCoordinator:
    def __init__(self):
        self.agents = {
            "researcher": ResearcherAgent(),
            "summarizer": SummarizerAgent(),
            "validator": ValidatorAgent()
        }
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
    
    async def start_all_agents(self):
        """Start all agents as background tasks."""
        logger.info("Starting all agents...")
        self.running = True
        
        for name, agent in self.agents.items():
            task = asyncio.create_task(agent.start())
            self.agent_tasks[name] = task
            logger.info(f"Agent {name} started")
        
        logger.info(f"All {len(self.agents)} agents running")
    
    async def stop_all_agents(self):
        """Stop all running agents."""
        logger.info("Stopping all agents...")
        self.running = False
        
        for name, agent in self.agents.items():
            await agent.stop()
        
        for name, task in self.agent_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Agent {name} cancelled")
        
        self.agent_tasks.clear()
        logger.info("All agents stopped")
    
    def get_agent_status(self) -> Dict[str, dict]:
        """Get status of all agents."""
        return {
            name: {
                "name": agent.name,
                "running": agent.running,
                "input_channel": agent.input_channel,
                "output_channel": agent.output_channel
            }
            for name, agent in self.agents.items()
        }
    
    async def health_check(self) -> bool:
        """Check if all agents are healthy."""
        return all(agent.running for agent in self.agents.values())


coordinator = AgentCoordinator()
