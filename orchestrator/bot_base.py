"""Base class for all bots in the orchestration"""

import asyncio
import json
from typing import Any, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from utils.logger import setup_logger
from utils.redis_client import get_redis
from orchestrator.config import BOT_TIMEOUT, BOT_HEARTBEAT_INTERVAL, HEALTH_CHECK_TOPIC


class BaseBot(ABC):
    """Base class for all bots"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = setup_logger(name, f"{name.lower()}.log")
        self.redis = None
        self.pubsub = None
        self.is_running = False
        self.message_handlers = {}
    
    async def initialize(self):
        """Initialize bot connections"""
        try:
            self.redis = await get_redis()
            self.logger.info(f"✅ {self.name} initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {e}")
            raise
    
    async def register_handler(self, topic: str, handler: Callable):
        """Register a message handler for a topic"""
        self.message_handlers[topic] = handler
        self.logger.debug(f"Registered handler for {topic}")
    
    async def start(self):
        """Start the bot"""
        self.is_running = True
        self.logger.info(f"🚀 {self.name} started")
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(self._heartbeat())
        
        try:
            await self.run()
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {e}", exc_info=True)
        finally:
            self.is_running = False
            heartbeat_task.cancel()
            self.logger.info(f"⏹️ {self.name} stopped")
    
    async def _heartbeat(self):
        """Send periodic heartbeat"""
        while self.is_running:
            try:
                await asyncio.sleep(BOT_HEARTBEAT_INTERVAL)
                status = {
                    "bot_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "status": "alive"
                }
                await self.redis.publish(HEALTH_CHECK_TOPIC, status)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
    
    @abstractmethod
    async def run(self):
        """Main bot logic - must be implemented by subclasses"""
        pass
    
    async def subscribe(self, *topics: str):
        """Subscribe to topics"""
        self.pubsub = await self.redis.subscribe(list(topics))
        self.logger.info(f"Subscribed to: {topics}")
    
    async def receive_message(self, timeout: int = BOT_TIMEOUT) -> Optional[dict]:
        """
        Receive message from subscribed topics
        
        Returns:
            Message dict or None if timeout
        """
        if not self.pubsub:
            raise RuntimeError("Not subscribed to any topic")
        
        try:
            message = await asyncio.wait_for(
                self.pubsub.get_message(ignore_subscribe_messages=True),
                timeout=timeout
            )
            if message and message.get('data'):
                data = message['data']
                # Try to parse as JSON
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return {"data": data}
            return message
        except asyncio.TimeoutError:
            return None
    
    async def publish(self, topic: str, message: Any):
        """Publish message to topic"""
        await self.redis.publish(topic, message)
        self.logger.debug(f"Published to {topic}: {message}")
    
    async def get_from_store(self, key: str) -> Optional[Any]:
        """Get value from Redis store"""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set_to_store(self, key: str, value: Any, expire: int = None):
        """Set value to Redis store"""
        await self.redis.set(key, value, ex=expire)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.pubsub:
            await self.pubsub.close()
        self.logger.info(f"Cleaned up resources for {self.name}")
