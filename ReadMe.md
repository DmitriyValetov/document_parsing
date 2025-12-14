# Document Parsing Project

Проект для парсинга документов на основе Docling, Dedoc и PyMuPDF.

## Компоненты

### Docling

- **simple** - простые скрипты для обработки PDF
- **serve** - веб-сервис с API (`http://localhost:5001`)
- **vllm_serve** - обработка через vLLM с GPU ускорением

### Dedoc

- **dedoc** - универсальный веб-сервис для парсинга документов (`http://localhost:1231`)
  - Поддержка множества форматов (DOCX, PDF, изображения с OCR и др.)
  - Извлечение структуры, таблиц и метаданных
  - Интерактивная документация API: http://localhost:1231/docs

### PyMuPDF

- **pymupdf/serve** - высокопроизводительный веб-сервис для парсинга PDF (`http://localhost:8000`)
  - Извлечение текста, метаданных и информации об изображениях
  - Быстрая обработка PDF документов
  - Интерактивная документация API: http://localhost:8000/docs

## Документация

- **Docling**: [docling/readme.md](docling/readme.md)
- **Dedoc**: [dedoc/readme.md](dedoc/readme.md)
- **PyMuPDF**: [pymupdf/serve/readme.md](pymupdf/serve/readme.md)
