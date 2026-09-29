"""Data Processor Bot - Processes and transforms data"""

import asyncio
import json
from orchestrator.bot_base import BaseBot


class DataProcessorBot(BaseBot):
    """Bot that processes and transforms data"""
    
    def __init__(self):
        super().__init__("DataProcessorBot")
        self.processed_count = 0
    
    async def run(self):
        """Main run loop"""
        await self.subscribe("data:input")
        
        self.logger.info("🔄 DataProcessorBot waiting for data...")
        
        while self.is_running:
            message = await self.receive_message(timeout=5)
            
            if message:
                try:
                    # Process the data
                    processed = await self.process_data(message)
                    
                    # Publish result
                    await self.publish("data:processed", processed)
                    self.processed_count += 1
                    
                    self.logger.info(f"✅ Processed data #{self.processed_count}")
                
                except Exception as e:
                    self.logger.error(f"Error processing data: {e}")
                    await self.publish("data:error", {"error": str(e)})
            
            await asyncio.sleep(0.1)
    
    async def process_data(self, data: dict) -> dict:
        """
        Process data
        
        This is a simple example that adds processing metadata
        """
        self.logger.debug(f"Processing: {data}")
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Add processing metadata
        if isinstance(data, dict):
            processed = {
                **data,
                "processed": True,
                "processor": self.name,
                "status": "success"
            }
        else:
            processed = {
                "data": data,
                "processed": True,
                "processor": self.name,
                "status": "success"
            }
        
        return processed


async def main():
    """Main entry point"""
    bot = DataProcessorBot()
    await bot.initialize()
    await bot.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
