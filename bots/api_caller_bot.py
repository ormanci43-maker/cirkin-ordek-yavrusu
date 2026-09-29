"""API Caller Bot - Calls external APIs"""

import asyncio
import json
import httpx
from orchestrator.bot_base import BaseBot


class ApiCallerBot(BaseBot):
    """Bot that calls external APIs"""
    
    def __init__(self):
        super().__init__("ApiCallerBot")
        self.api_calls_count = 0
        self.client = None
    
    async def initialize(self):
        """Initialize bot"""
        await super().initialize()
        self.client = httpx.AsyncClient()
    
    async def run(self):
        """Main run loop"""
        await self.subscribe("api:request")
        
        self.logger.info("🌐 ApiCallerBot waiting for API requests...")
        
        while self.is_running:
            message = await self.receive_message(timeout=5)
            
            if message:
                try:
                    # Call external API
                    result = await self.call_api(message)
                    
                    # Publish result
                    await self.publish("api:response", result)
                    self.api_calls_count += 1
                    
                    self.logger.info(f"✅ API call #{self.api_calls_count} completed")
                
                except Exception as e:
                    self.logger.error(f"API call error: {e}")
                    await self.publish("api:error", {"error": str(e)})
            
            await asyncio.sleep(0.1)
    
    async def call_api(self, request: dict) -> dict:
        """
        Call external API
        
        Example request format:
        {
            "url": "https://api.example.com/data",
            "method": "GET",
            "params": {"key": "value"}
        }
        """
        url = request.get("url", "https://jsonplaceholder.typicode.com/posts/1")
        method = request.get("method", "GET").upper()
        params = request.get("params", {})
        
        self.logger.debug(f"Calling API: {method} {url}")
        
        try:
            if method == "GET":
                response = await self.client.get(url, params=params, timeout=10)
            elif method == "POST":
                response = await self.client.post(url, json=params, timeout=10)
            else:
                response = await self.client.request(method, url, params=params, timeout=10)
            
            response.raise_for_status()
            
            return {
                "status": "success",
                "status_code": response.status_code,
                "data": response.json(),
                "caller": self.name
            }
        
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "caller": self.name
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
        await super().cleanup()


async def main():
    """Main entry point"""
    bot = ApiCallerBot()
    await bot.initialize()
    await bot.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
