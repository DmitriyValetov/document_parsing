"""Модуль для загрузки и управления конфигурацией"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False

class ConverterConfig(BaseModel):
    enable_vlm: bool = False
    vlm_model: str = "granite_docling"
    use_gpu: bool = True

class DoclingConfig(BaseModel):
    max_file_size: int = 104857600  # 100 MB
    temp_dir: str = "/tmp/docling"
    converter: ConverterConfig = Field(default_factory=ConverterConfig)

class JsonOutputConfig(BaseModel):
    pretty: bool = True
    include_metadata: bool = True

class HtmlOutputConfig(BaseModel):
    include_styles: bool = True
    include_images: bool = True

class OutputConfig(BaseModel):
    formats: List[str] = ["markdown", "json", "html"]
    default_format: str = "markdown"
    json: JsonOutputConfig = Field(default_factory=JsonOutputConfig)
    html: HtmlOutputConfig = Field(default_factory=HtmlOutputConfig)

class ModelsConfig(BaseModel):
    cache_dir: Optional[str] = None
    preload: bool = False

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"  # json, text
    file: Optional[str] = None

class AppConfig(BaseModel):
    server: ServerConfig = Field(default_factory=ServerConfig)
    docling: DoclingConfig = Field(default_factory=DoclingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

# Глобальный экземпляр конфигурации
_config: Optional[AppConfig] = None

def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Загружает конфигурацию из YAML файла"""
    global _config
    
    if _config is not None:
        return _config
    
    if config_path is None:
        # Ищем config.yaml в текущей директории или родительской
        current_dir = Path(__file__).parent.parent
        config_path = current_dir / "config.yaml"
        
        if not config_path.exists():
            # Пробуем найти через переменную окружения
            env_config = os.getenv("DOCLING_CONFIG_PATH")
            if env_config and Path(env_config).exists():
                config_path = Path(env_config)
            else:
                # Используем значения по умолчанию
                _config = AppConfig()
                return _config
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f) or {}
        _config = AppConfig(**config_data)
    else:
        _config = AppConfig()
    
    return _config

def get_config() -> AppConfig:
    """Возвращает текущую конфигурацию"""
    if _config is None:
        return load_config()
    return _config

