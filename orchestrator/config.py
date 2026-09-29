"""Configuration for Bot Orchestration"""

import os
from typing import Optional

# Redis Configuration
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

# Bot Configuration
BOT_TIMEOUT: int = int(os.getenv("BOT_TIMEOUT", 30))
BOT_HEARTBEAT_INTERVAL: int = int(os.getenv("BOT_HEARTBEAT_INTERVAL", 5))
BOT_MAX_RETRIES: int = int(os.getenv("BOT_MAX_RETRIES", 3))

# Logging Configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR: str = os.getenv("LOG_DIR", "logs")
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Orchestrator Configuration
ORCHESTRATOR_CHECK_INTERVAL: int = int(os.getenv("ORCHESTRATOR_CHECK_INTERVAL", 10))
ORCHESTRATOR_HEALTH_CHECK_TIMEOUT: int = int(os.getenv("ORCHESTRATOR_HEALTH_CHECK_TIMEOUT", 5))

# Topics
ORCHESTRATOR_TOPIC: str = "orchestrator:commands"
HEALTH_CHECK_TOPIC: str = "system:health"
RESULT_TOPIC: str = "system:results"

# Environment
ENV: str = os.getenv("ENV", "development")
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
