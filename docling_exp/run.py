"""Скрипт запуска сервиса"""
import uvicorn
from app.config import get_config

if __name__ == "__main__":
    config = get_config()
    
    uvicorn.run(
        "app.main:app",
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers if not config.server.reload else 1,
        reload=config.server.reload,
        log_level=config.logging.level.lower()
    )

