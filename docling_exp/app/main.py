"""Основной модуль FastAPI приложения"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import os
import tempfile
import logging
import json
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

# Импорты для VLM и PipelineOptions (могут быть недоступны в некоторых версиях)
try:
    from docling.datamodel.pipeline_options import VlmPipelineOptions, PdfPipelineOptions
    from docling.datamodel.settings import settings as docling_settings
    VLM_AVAILABLE = True
    PIPELINE_OPTIONS_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False
    PIPELINE_OPTIONS_AVAILABLE = False

try:
    from docling import PdfPipeline
    PDF_PIPELINE_AVAILABLE = True
except ImportError:
    PDF_PIPELINE_AVAILABLE = False

from app.config import get_config, load_config

# Загружаем конфигурацию
config = load_config()

# Настройка логирования
log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
if config.logging.format == "json":
    import json
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=[
            logging.FileHandler(config.logging.file) if config.logging.file else logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logging.file) if config.logging.file else logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Docling Document Parsing Service",
    version="1.0.0",
    description="Веб-сервис для парсинга документов на основе Docling"
)

# Создаем временную директорию если её нет
os.makedirs(config.docling.temp_dir, exist_ok=True)

# Глобальный экземпляр конвертера (ленивая инициализация)
_converter = None

def get_converter() -> DocumentConverter:
    """Ленивая инициализация конвертера с настройками из конфига"""
    global _converter
    if _converter is None:
        logger.info("Инициализация DocumentConverter...")
        
        # Настройка кэша моделей
        if config.models.cache_dir:
            os.environ["HF_HOME"] = config.models.cache_dir
            os.environ["DOCLING_CACHE_DIR"] = config.models.cache_dir
        
        # Настройка GPU если указано в конфиге
        if config.docling.converter.use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    logger.info(f"GPU доступен: {torch.cuda.get_device_name(0)}")
                    logger.info(f"CUDA версия: {torch.version.cuda}")
                    # Устанавливаем устройство по умолчанию для PyTorch
                    torch.cuda.set_device(0)
                    # Настраиваем ONNX Runtime для использования GPU
                    os.environ["ORT_DEVICE"] = "cuda"
                    os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")
                else:
                    logger.warning("GPU запрошен в конфиге, но не доступен. Используется CPU.")
            except ImportError:
                logger.warning("PyTorch не установлен. GPU не может быть использован.")
            except Exception as e:
                logger.warning(f"Ошибка при настройке GPU: {e}. Используется CPU.")
        else:
            logger.info("Использование CPU (use_gpu=false)")
        
        # Настройка параметров конвертера
        converter_kwargs = {}
        pipeline_options_list = []
        
        # Включение VLM если указано в конфиге
        if config.docling.converter.enable_vlm:
            if VLM_AVAILABLE:
                logger.info(f"Включение VLM с моделью: {config.docling.converter.vlm_model}")
                
                # Настройка VLM через VlmPipelineOptions
                vlm_options = VlmPipelineOptions(
                    enable_remote_services=False,  # Используем локальную модель
                    vlm_options={
                        "model": config.docling.converter.vlm_model,
                        "max_tokens": 4096,
                    }
                )
                pipeline_options_list.append(vlm_options)
                
                # Настройка размера батча для производительности
                if PIPELINE_OPTIONS_AVAILABLE:
                    docling_settings.perf.page_batch_size = 4
                
            elif PDF_PIPELINE_AVAILABLE:
                # Альтернативный способ через PdfPipeline
                logger.info(f"Включение VLM через PdfPipeline с моделью: {config.docling.converter.vlm_model}")
                converter_kwargs["pipeline"] = PdfPipeline.VLM
            else:
                logger.warning("VLM запрошен в конфиге, но не доступен в этой версии Docling")
        
        # Передаем pipeline_options если они есть
        if pipeline_options_list:
            # Если несколько опций, объединяем их или используем первую
            # В зависимости от API Docling может потребоваться другой подход
            converter_kwargs["pipeline_options"] = pipeline_options_list[0] if len(pipeline_options_list) == 1 else pipeline_options_list
        
        # Логируем настройки из конфига (для отладки и мониторинга)
        logger.info(f"Настройки конвертера из config.yaml:")
        logger.info(f"  - VLM: {config.docling.converter.enable_vlm} ({config.docling.converter.vlm_model if config.docling.converter.enable_vlm else 'N/A'})")
        logger.info(f"  - GPU: {config.docling.converter.use_gpu}")
        logger.info(f"  - Передано в DocumentConverter: {list(converter_kwargs.keys())}")
        
        # Создаем конвертер с настройками из конфига
        # Примечание: VLM настройки передаются через pipeline_options или pipeline.
        # Другие настройки (OCR, таблицы, формулы, код) применяются автоматически
        # через стандартный pipeline Docling, но их значения логируются для мониторинга.
        _converter = DocumentConverter(**converter_kwargs)
        
        logger.info("DocumentConverter инициализирован")
        if config.docling.converter.enable_vlm:
            logger.info(f"VLM включен: {config.docling.converter.vlm_model}")
        
        # Предзагрузка моделей если указано в конфиге
        if config.models.preload:
            logger.info("Предзагрузка моделей...")
            # Просто создаем конвертер, модели загрузятся при первом использовании
            # или можно сделать тестовый конверт для предзагрузки
    
    return _converter

@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    logger.info("Запуск Docling Service...")
    logger.info(f"Конфигурация загружена: temp_dir={config.docling.temp_dir}")
    
    if config.models.preload:
        logger.info("Предзагрузка моделей...")
        get_converter()

@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "message": "Docling Document Parsing Service",
        "version": "1.0.0",
        "config": {
            "max_file_size": config.docling.max_file_size,
            "output_formats": config.output.formats,
            "default_format": config.output.default_format
        }
    }

@app.get("/health")
async def health():
    """Проверка состояния сервиса"""
    return {"status": "healthy"}

@app.get("/models/status")
async def models_status():
    """Проверка статуса загрузки моделей"""
    global _converter
    if _converter is None:
        return {
            "status": "not_loaded",
            "message": "Модели будут загружены при первом запросе на парсинг"
        }
    return {
        "status": "loaded",
        "message": "Модели загружены и готовы к использованию"
    }

@app.post("/parse")
async def parse_document(
    file: UploadFile = File(...),
    output_format: Optional[str] = None
):
    """
    Парсит загруженный документ и возвращает результат в указанном формате.
    
    Поддерживаемые форматы: markdown, json, html
    """
    # Используем формат из параметра или из конфига
    if output_format is None:
        output_format = config.output.default_format
    
    if output_format not in config.output.formats:
        raise HTTPException(
            status_code=400, 
            detail=f"output_format должен быть одним из: {', '.join(config.output.formats)}"
        )
    
    # Проверка размера файла
    file_content = await file.read()
    if len(file_content) > config.docling.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимальный размер: {config.docling.max_file_size} байт"
        )
    
    temp_file = None
    try:
        # Сохраняем загруженный файл во временную директорию
        suffix = Path(file.filename).suffix if file.filename else ""
        temp_file = os.path.join(config.docling.temp_dir, f"{os.urandom(16).hex()}{suffix}")
        
        with open(temp_file, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Обработка файла: {file.filename}, формат: {output_format}")
        
        # Конвертируем документ (модели загружаются при первом вызове)
        converter = get_converter()
        result = converter.convert(temp_file)
        
        # Экспортируем в нужный формат с учетом настроек из конфига
        if output_format == "markdown":
            output = result.document.export_to_markdown()
        elif output_format == "json":
            output_dict = result.document.export_to_dict()
            # Применяем настройки JSON из конфига
            if config.output.json.pretty:
                output = json.dumps(output_dict, indent=2, ensure_ascii=False)
            else:
                output = json.dumps(output_dict, ensure_ascii=False)
        elif output_format == "html":
            # Пробуем передать параметры HTML экспорта (если API поддерживает)
            try:
                # Пробуем вызвать с параметрами из конфига, если поддерживается
                try:
                    output = result.document.export_to_html(
                        include_styles=config.output.html.include_styles,
                        include_images=config.output.html.include_images
                    )
                except TypeError:
                    # Если параметры не поддерживаются, вызываем без них
                    output = result.document.export_to_html()
            except Exception as e:
                logger.warning(f"Ошибка при экспорте HTML с параметрами: {e}, используем значения по умолчанию")
                output = result.document.export_to_html()
        else:
            output = result.document.export_to_markdown()
        
        logger.info(f"Файл успешно обработан: {file.filename}")
        
        response_data = {
            "filename": file.filename,
            "format": output_format,
            "content": output
        }
        
        # Добавляем метаданные если нужно (согласно конфигу)
        if config.output.json.include_metadata and output_format == "json":
            # Для JSON метаданные могут быть включены в сам content
            if isinstance(output, str):
                # Если output - строка (pretty JSON), добавляем метаданные отдельно
                response_data["metadata"] = {
                    "pages": len(result.document.pages) if hasattr(result.document, 'pages') else None
                }
        elif output_format != "json":
            # Для не-JSON форматов всегда добавляем метаданные
            response_data["metadata"] = {
                "pages": len(result.document.pages) if hasattr(result.document, 'pages') else None
            }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        logger.error(f"Ошибка при обработке документа {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке документа: {str(e)}")
    
    finally:
        # Удаляем временный файл
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {temp_file}: {e}")

@app.post("/parse/url")
async def parse_from_url(
    url: str,
    output_format: Optional[str] = None
):
    """
    Парсит документ по URL и возвращает результат в указанном формате.
    
    Поддерживаемые форматы: markdown, json, html
    """
    # Используем формат из параметра или из конфига
    if output_format is None:
        output_format = config.output.default_format
    
    if output_format not in config.output.formats:
        raise HTTPException(
            status_code=400, 
            detail=f"output_format должен быть одним из: {', '.join(config.output.formats)}"
        )
    
    try:
        logger.info(f"Обработка URL: {url}, формат: {output_format}")
        
        # Конвертируем документ по URL (модели загружаются при первом вызове)
        converter = get_converter()
        result = converter.convert(url)
        
        # Экспортируем в нужный формат с учетом настроек из конфига
        if output_format == "markdown":
            output = result.document.export_to_markdown()
        elif output_format == "json":
            output_dict = result.document.export_to_dict()
            # Применяем настройки JSON из конфига
            if config.output.json.pretty:
                output = json.dumps(output_dict, indent=2, ensure_ascii=False)
            else:
                output = json.dumps(output_dict, ensure_ascii=False)
        elif output_format == "html":
            # Пробуем передать параметры HTML экспорта (если API поддерживает)
            try:
                try:
                    output = result.document.export_to_html(
                        include_styles=config.output.html.include_styles,
                        include_images=config.output.html.include_images
                    )
                except TypeError:
                    # Если параметры не поддерживаются, вызываем без них
                    output = result.document.export_to_html()
            except Exception as e:
                logger.warning(f"Ошибка при экспорте HTML с параметрами: {e}, используем значения по умолчанию")
                output = result.document.export_to_html()
        else:
            output = result.document.export_to_markdown()
        
        logger.info(f"URL успешно обработан: {url}")
        
        response_data = {
            "url": url,
            "format": output_format,
            "content": output
        }
        
        # Добавляем метаданные если нужно (согласно конфигу)
        if config.output.json.include_metadata and output_format == "json":
            # Для JSON метаданные могут быть включены в сам content
            if isinstance(output, str):
                # Если output - строка (pretty JSON), добавляем метаданные отдельно
                response_data["metadata"] = {
                    "pages": len(result.document.pages) if hasattr(result.document, 'pages') else None
                }
        elif output_format != "json":
            # Для не-JSON форматов всегда добавляем метаданные
            response_data["metadata"] = {
                "pages": len(result.document.pages) if hasattr(result.document, 'pages') else None
            }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        logger.error(f"Ошибка при обработке URL {url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке документа: {str(e)}")

