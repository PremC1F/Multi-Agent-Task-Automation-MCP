from abc import ABC, abstractmethod
import asyncio
from typing import Optional
from datetime import datetime
from src.core.mcp_protocol import MCPMessage, encode_message, decode_message, create_message
from src.core.redis_manager import redis_manager
from src.core.db_manager import db_manager
from src.utils.logger import get_logger
from src.utils.metrics import metrics_collector


class BaseAgent(ABC):
    def __init__(self, name: str, input_channel: str, output_channel: Optional[str] = None):
        self.name = name
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.logger = get_logger(f"Agent.{name}")
        self.running = False
    
    async def start(self):
        """Start the agent and begin listening for messages."""
        self.running = True
        self.logger.info(f"Starting agent {self.name}, listening on {self.input_channel}")
        await redis_manager.connect()
        await redis_manager.subscribe(self.input_channel, self._message_handler)
    
    async def stop(self):
        """Stop the agent."""
        self.running = False
        self.logger.info(f"Stopping agent {self.name}")
    
    async def _message_handler(self, raw_message: str):
        """Internal message handler that wraps the abstract handle_message."""
        try:
            message = decode_message(raw_message)
            self.logger.info(f"Received message", context_id=message.context_id)
            
            start_time = datetime.utcnow()
            await self.handle_message(message)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            metrics_collector.record_agent_timing(message.context_id, self.name, duration)
            metrics_collector.increment_message_count(message.context_id)
            
            db_manager.log_agent_action(
                context_id=message.context_id,
                agent_name=self.name,
                action="processed_message",
                duration=duration
            )
        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def send_message(self, context_id: str, receiver: str, payload: dict):
        """Send a message to another agent."""
        if not self.output_channel:
            self.logger.warning(f"No output channel configured for {self.name}")
            return
        
        message = create_message(
            context_id=context_id,
            sender=self.name,
            receiver=receiver,
            payload=payload
        )
        
        encoded = encode_message(message)
        await redis_manager.publish(self.output_channel, encoded)
        self.logger.info(f"Sent message to {receiver}", context_id=context_id)
    
    @abstractmethod
    async def handle_message(self, message: MCPMessage):
        """Process incoming message. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def run(self, context_id: str, **kwargs):
        """Execute agent's main task. Must be implemented by subclasses."""
        pass
