"""Master Orchestrator - Coordinates all bots"""

import asyncio
from datetime import datetime
from utils.logger import setup_logger
from utils.redis_client import get_redis
from orchestrator.config import (
    ORCHESTRATOR_CHECK_INTERVAL,
    ORCHESTRATOR_HEALTH_CHECK_TIMEOUT,
    ORCHESTRATOR_TOPIC,
    HEALTH_CHECK_TOPIC
)

logger = setup_logger("Orchestrator", "orchestrator.log")


class Orchestrator:
    """Master orchestrator for bot coordination"""
    
    def __init__(self):
        self.redis = None
        self.pubsub = None
        self.bots_status = {}
        self.is_running = False
    
    async def initialize(self):
        """Initialize orchestrator"""
        try:
            self.redis = await get_redis()
            logger.info("🎼 Orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    async def start(self):
        """Start orchestrator"""
        self.is_running = True
        logger.info("🎼 Orchestrator starting...")
        
        # Subscribe to health checks
        self.pubsub = await self.redis.subscribe([HEALTH_CHECK_TOPIC, ORCHESTRATOR_TOPIC])
        
        # Run orchestrator tasks
        tasks = [
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._message_handler()),
            asyncio.create_task(self._periodic_tasks())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Orchestrator interrupted")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}", exc_info=True)
        finally:
            await self.cleanup()
    
    async def _health_monitor(self):
        """Monitor bot health"""
        while self.is_running:
            try:
                await asyncio.sleep(ORCHESTRATOR_CHECK_INTERVAL)
                
                # Check for stale bots
                now = datetime.now().timestamp()
                stale_bots = []
                
                for bot_name, last_seen in self.bots_status.items():
                    if now - last_seen > ORCHESTRATOR_HEALTH_CHECK_TIMEOUT * 3:
                        stale_bots.append(bot_name)
                
                if stale_bots:
                    logger.warning(f"⚠️ Stale bots detected: {stale_bots}")
                
                # Log current status
                active_bots = len([b for b in self.bots_status.values() if b])
                logger.info(f"✅ Active bots: {active_bots}, Total: {len(self.bots_status)}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _message_handler(self):
        """Handle incoming messages"""
        while self.is_running:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                
                if message and message.get('channel') == HEALTH_CHECK_TOPIC:
                    # Update bot status
                    data = message.get('data')
                    if isinstance(data, str):
                        import json
                        try:
                            data = json.loads(data)
                        except:
                            pass
                    
                    if isinstance(data, dict) and 'bot_name' in data:
                        bot_name = data['bot_name']
                        self.bots_status[bot_name] = datetime.now().timestamp()
                        logger.debug(f"💚 Heartbeat from {bot_name}")
                
                elif message and message.get('channel') == ORCHESTRATOR_TOPIC:
                    # Handle orchestrator commands
                    logger.info(f"📋 Command received: {message.get('data')}")
                
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Message handler error: {e}")
    
    async def _periodic_tasks(self):
        """Run periodic orchestration tasks"""
        while self.is_running:
            try:
                await asyncio.sleep(30)
                logger.info(f"📊 Orchestrator status: {len(self.bots_status)} bots connected")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic tasks error: {e}")
    
    async def send_command(self, command: dict):
        """Send command to all bots"""
        await self.redis.publish(ORCHESTRATOR_TOPIC, command)
        logger.info(f"📤 Sent command: {command}")
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        if self.pubsub:
            await self.pubsub.close()
        logger.info("🎼 Orchestrator shutdown complete")


async def main():
    """Main entry point"""
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    await orchestrator.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Orchestrator terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
