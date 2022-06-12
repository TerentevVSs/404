from loguru import logger

from config import get_settings

settings = get_settings()

logger.add('app.log', format='{time} {name} {level} {message}',
           level="DEBUG" if settings.DEBUG else "INFO",)

