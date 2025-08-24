import sys
import os
from loguru import logger

# Remove default logger
logger.remove()

# Add console logger for Railway
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# Add file logger only in development
if os.environ.get("RAILWAY_ENVIRONMENT") != "production":
    logger.add(
        "logs/appointment_agent.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

# Export logger
__all__ = ["logger"]