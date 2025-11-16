import redis.asyncio as redis
import asyncio
from typing import Callable, Optional
from src.core.config import settings
from src.utils.logger import get_logger

logger = get_logger("RedisManager")


class RedisManager:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.reconnect_delay = 1
        self.max_reconnect_delay = 30
    
    async def connect(self):
        """Establish connection to Redis."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            await self.redis_client.ping()
            logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
            self.reconnect_delay = 1
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected from Redis")
    
    async def publish(self, channel: str, message: str):
        """Publish message to a channel."""
        if not self.redis_client:
            await self.connect()
        
        try:
            await self.redis_client.publish(channel, message)
            logger.debug(f"Published to {channel}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            await self._handle_reconnect()
            raise
    
    async def subscribe(self, channel: str, callback: Callable[[str], asyncio.Task]):
        """Subscribe to a channel and process messages with callback."""
        if not self.redis_client:
            await self.connect()
        
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(channel)
        logger.info(f"Subscribed to channel: {channel}")
        
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    data = message['data']
                    logger.debug(f"Received message from {channel}")
                    await callback(data)
        except asyncio.CancelledError:
            logger.info(f"Subscription to {channel} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in subscription to {channel}: {e}", exc_info=True)
            await self._handle_reconnect()
    
    async def _handle_reconnect(self):
        """Handle reconnection with exponential backoff."""
        logger.warning(f"Attempting reconnect in {self.reconnect_delay}s...")
        await asyncio.sleep(self.reconnect_delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
        await self.connect()


redis_manager = RedisManager()
