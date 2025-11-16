import asyncio
from typing import List
from src.agents.base_agent import BaseAgent
from src.core.mcp_protocol import MCPMessage
from src.core.db_manager import db_manager


class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="researcher_agent",
            input_channel="researcher_input",
            output_channel="summarizer_input"
        )
    
    async def handle_message(self, message: MCPMessage):
        """Handle incoming research requests."""
        query = message.payload.get("query", "")
        self.logger.info(f"Researching: {query}", context_id=message.context_id)
        
        data = await self.run(message.context_id, query=query)
        
        await self.send_message(
            context_id=message.context_id,
            receiver="summarizer_agent",
            payload={"data": data, "query": query}
        )
    
    async def run(self, context_id: str, query: str = "", **kwargs) -> List[str]:
        """Simulate data gathering from multiple sources."""
        self.logger.info(f"Gathering data for query: {query}", context_id=context_id)
        
        await asyncio.sleep(0.5)
        
        sample_data = [
            f"Research finding 1: {query} is a complex topic with multiple facets. Recent studies show significant progress in understanding its core principles.",
            f"Research finding 2: Industry experts believe {query} will transform how we approach problem-solving in the coming years.",
            f"Research finding 3: Academic research on {query} has increased by 300% over the last decade, indicating growing interest.",
            f"Research finding 4: Practical applications of {query} are already being deployed in production environments.",
            f"Research finding 5: Future directions for {query} include enhanced automation and integration with existing systems."
        ]
        
        db_manager.log_agent_action(
            context_id=context_id,
            agent_name=self.name,
            action="data_gathered",
            details=f"Collected {len(sample_data)} data points for query: {query}"
        )
        
        self.logger.info(f"Gathered {len(sample_data)} data points", context_id=context_id)
        return sample_data
