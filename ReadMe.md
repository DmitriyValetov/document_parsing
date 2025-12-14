# Document Parsing Project

Проект для парсинга документов на основе Docling и Dedoc.

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

## Документация

- **Docling**: [docling/readme.md](docling/readme.md)
- **Dedoc**: [dedoc/readme.md](dedoc/readme.md)
