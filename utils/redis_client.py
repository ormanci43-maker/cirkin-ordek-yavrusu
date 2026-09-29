"""Redis client wrapper for Bot Orchestration"""

import json
import asyncio
from typing import Any, Optional, Dict
import redis.asyncio as redis
from orchestrator.config import REDIS_HOST, REDIS_PORT, REDIS_DB
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RedisClient:
    """Async Redis client wrapper"""
    
    _instance: Optional['RedisClient'] = None
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
    
    @classmethod
    async def get_instance(cls) -> 'RedisClient':
        """Get or create Redis client instance"""
        if cls._instance is None:
            cls._instance = RedisClient()
            await cls._instance.connect()
        return cls._instance
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def publish(self, channel: str, message: Any):
        """Publish message to channel"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        if isinstance(message, dict):
            message = json.dumps(message)
        
        await self.redis.publish(channel, message)
        logger.debug(f"Published to {channel}: {message}")
    
    async def subscribe(self, channels: list) -> redis.client.PubSub:
        """Subscribe to channels"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(*channels)
        logger.info(f"Subscribed to channels: {channels}")
        return pubsub
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        return await self.redis.get(key)
    
    async def set(self, key: str, value: Any, ex: int = None):
        """Set key-value pair"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        if isinstance(value, dict):
            value = json.dumps(value)
        
        await self.redis.set(key, value, ex=ex)
        logger.debug(f"Set {key} = {value}")
    
    async def delete(self, key: str):
        """Delete key"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        await self.redis.delete(key)
        logger.debug(f"Deleted {key}")
    
    async def incr(self, key: str) -> int:
        """Increment value"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        return await self.redis.incr(key)
    
    async def hset(self, name: str, mapping: Dict[str, Any]):
        """Set hash fields"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        await self.redis.hset(name, mapping=mapping)
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        return await self.redis.hget(name, key)
    
    async def hgetall(self, name: str) -> Dict:
        """Get all hash fields"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        return await self.redis.hgetall(name)


async def get_redis() -> RedisClient:
    """Convenience function to get Redis client"""
    return await RedisClient.get_instance()
