"""CemilAbi - The Master Orchestrator"""

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

logger = setup_logger("CemilAbi", "cemilabi.log")


class CemilAbi:
    """Master Orchestrator - The Boss Bot"""
    
    def __init__(self):
        self.redis = None
        self.pubsub = None
        self.bots_status = {}
        self.is_running = False
        self.commands_received = 0
        self.decisions_made = 0
    
    async def initialize(self):
        """Initialize CemilAbi"""
        try:
            self.redis = await get_redis()
            logger.info("👔 CemilAbi initialized - The Boss is here!")
        except Exception as e:
            logger.error(f"Failed to initialize CemilAbi: {e}")
            raise
    
    async def start(self):
        """Start CemilAbi"""
        self.is_running = True
        logger.info("=" * 60)
        logger.info("👔 CemilAbi STARTING - Boss Mode Activated!")
        logger.info("=" * 60)
        
        # Subscribe to health checks and commands
        self.pubsub = await self.redis.subscribe([HEALTH_CHECK_TOPIC, ORCHESTRATOR_TOPIC])
        
        # Run CemilAbi tasks
        tasks = [
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._message_handler()),
            asyncio.create_task(self._decision_maker()),
            asyncio.create_task(self._status_report())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("👔 CemilAbi received shutdown signal")
        except Exception as e:
            logger.error(f"CemilAbi error: {e}", exc_info=True)
        finally:
            await self.cleanup()
    
    async def _health_monitor(self):
        """Monitor bot health - CemilAbi watches everything"""
        while self.is_running:
            try:
                await asyncio.sleep(ORCHESTRATOR_CHECK_INTERVAL)
                
                now = datetime.now().timestamp()
                stale_bots = []
                healthy_bots = []
                
                for bot_name, last_seen in self.bots_status.items():
                    if now - last_seen > ORCHESTRATOR_HEALTH_CHECK_TIMEOUT * 3:
                        stale_bots.append(bot_name)
                    else:
                        healthy_bots.append(bot_name)
                
                if stale_bots:
                    logger.warning(f"⚠️  CemilAbi: Stale bots detected: {stale_bots}")
                    for bot in stale_bots:
                        logger.warning(f"   → {bot} will be restarted soon")
                
                if healthy_bots:
                    logger.info(f"✅ CemilAbi: All systems operational - {len(healthy_bots)} active bots")
                    for bot in healthy_bots:
                        logger.debug(f"   → {bot} is healthy")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _message_handler(self):
        """Handle incoming messages - CemilAbi listens to everyone"""
        while self.is_running:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                
                if message and message.get('channel') == HEALTH_CHECK_TOPIC:
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
                        logger.debug(f"💚 CemilAbi: {bot_name} checked in")
                
                elif message and message.get('channel') == ORCHESTRATOR_TOPIC:
                    data = message.get('data')
                    logger.info(f"📋 CemilAbi: New command received: {data}")
                    self.commands_received += 1
                
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Message handler error: {e}")
    
    async def _decision_maker(self):
        """CemilAbi makes decisions - The Boss decides what to do"""
        while self.is_running:
            try:
                await asyncio.sleep(15)
                
                if len(self.bots_status) > 0:
                    logger.info("🤔 CemilAbi: Making strategic decisions...")
                    
                    # Analyze bot performance
                    decision = {
                        "timestamp": datetime.now().isoformat(),
                        "active_bots": len(self.bots_status),
                        "commands_processed": self.commands_received,
                        "status": "all_systems_operational"
                    }
                    
                    logger.info(f"💼 CemilAbi Decision: {decision}")
                    self.decisions_made += 1
                    
                    # Send decision to all bots
                    await self.redis.publish("cemilabi:decision", decision)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Decision maker error: {e}")
    
    async def _status_report(self):
        """Generate status report - CemilAbi reports to the board"""
        while self.is_running:
            try:
                await asyncio.sleep(30)
                
                logger.info("=" * 60)
                logger.info("📊 CemilAbi STATUS REPORT")
                logger.info("=" * 60)
                logger.info(f"👔 Boss: CemilAbi")
                logger.info(f"⏰ Time: {datetime.now().isoformat()}")
                logger.info(f"🤖 Active Bots: {len(self.bots_status)}")
                logger.info(f"📋 Commands Received: {self.commands_received}")
                logger.info(f"💼 Decisions Made: {self.decisions_made}")
                
                for bot_name, last_seen in self.bots_status.items():
                    uptime = datetime.now().timestamp() - last_seen
                    logger.info(f"   • {bot_name}: {uptime:.1f}s ago")
                
                logger.info("=" * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Status report error: {e}")
    
    async def send_command(self, command: dict):
        """Send command to all bots"""
        await self.redis.publish(ORCHESTRATOR_TOPIC, command)
        logger.info(f"📤 CemilAbi: Sent command: {command}")
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        if self.pubsub:
            await self.pubsub.close()
        logger.info("=" * 60)
        logger.info("👔 CemilAbi SHUTDOWN - Goodbye from the Boss")
        logger.info("=" * 60)


async def main():
    """Main entry point"""
    cemilabi = CemilAbi()
    await cemilabi.initialize()
    await cemilabi.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👔 CemilAbi terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
