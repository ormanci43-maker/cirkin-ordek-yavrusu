"""Notification Bot - Sends notifications"""

import asyncio
import json
from datetime import datetime
from orchestrator.bot_base import BaseBot


class NotificationBot(BaseBot):
    """Bot that sends notifications"""
    
    def __init__(self):
        super().__init__("NotificationBot")
        self.notifications_sent = 0
    
    async def run(self):
        """Main run loop"""
        # Subscribe to multiple topics for notifications
        await self.subscribe("data:processed", "api:response", "system:alerts")
        
        self.logger.info("📢 NotificationBot waiting for notifications...")
        
        while self.is_running:
            message = await self.receive_message(timeout=5)
            
            if message:
                try:
                    # Send notification
                    await self.send_notification(message)
                    self.notifications_sent += 1
                    
                    self.logger.info(f"✅ Notification #{self.notifications_sent} sent")
                
                except Exception as e:
                    self.logger.error(f"Notification error: {e}")
            
            await asyncio.sleep(0.1)
    
    async def send_notification(self, message: dict):
        """
        Send notification
        
        In a real system, this could send to:
        - Email
        - Slack
        - Discord
        - WebSocket
        - Database logging
        """
        timestamp = datetime.now().isoformat()
        
        # Format message
        notification = {
            "timestamp": timestamp,
            "message": message,
            "sender": self.name,
            "type": "notification"
        }
        
        # Simulate sending to different channels
        await self._log_notification(notification)
    
    async def _log_notification(self, notification: dict):
        """Log notification (could be Slack, email, etc.)"""
        self.logger.info(f"📧 NOTIFICATION: {json.dumps(notification, indent=2)}")
        
        # Save to notification store
        key = f"notification:{notification['timestamp']}"
        await self.set_to_store(key, notification, expire=86400)  # 24 hour expiry
    
    async def _send_email(self, notification: dict):
        """Send email notification"""
        self.logger.info(f"📧 Email: {notification}")
        # Implementation would go here
    
    async def _send_slack(self, notification: dict):
        """Send Slack notification"""
        self.logger.info(f"💬 Slack: {notification}")
        # Implementation would go here
    
    async def _send_discord(self, notification: dict):
        """Send Discord notification"""
        self.logger.info(f"🎮 Discord: {notification}")
        # Implementation would go here


async def main():
    """Main entry point"""
    bot = NotificationBot()
    await bot.initialize()
    await bot.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
