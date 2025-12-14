# Dedoc - Парсинг документов

Dedoc - универсальная система для конвертации документов в единый формат. Извлекает логическую структуру, содержимое, таблицы и метаданные из документов.

## Быстрый старт

### Запуск сервиса

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Проверка доступности

```bash
# Проверка через попытку подключения
curl http://localhost:1231/

# Или откройте интерактивную документацию API в браузере:
# http://localhost:1231/docs
```

## Примеры использования

### Python

```bash
# Установка зависимостей (если нужно)
pip install requests

# Запуск примера
python test.py
```

Скрипт `test.py` автоматически:
- Проверяет доступность сервиса
- Обрабатывает все файлы из папки `input/`
- Сохраняет результаты в папку `output/`

### cURL (Windows PowerShell)

```powershell
# Парсинг файла
curl -X POST "http://localhost:1231/upload" `
    -F "file=@input/classic_mem.jpg" `
    -o output/result.json
```

### cURL (Linux/Mac)

```bash
# Запуск примеров
bash examples.sh

# Или вручную:
curl -X POST "http://localhost:1231/upload" \
    -F "file=@input/classic_mem.jpg" \
    -o output/result.json
```

## Структура проекта

```
dedoc/
├── docker-compose.yaml  # Конфигурация Docker Compose
├── test.py              # Python примеры использования
├── examples.sh          # Bash примеры использования
├── input/               # Входные файлы для обработки
│   └── classic_mem.jpg
└── output/              # Результаты парсинга (создается автоматически)
```

## API Endpoints

### Интерактивная документация

После запуска сервиса доступна интерактивная документация API (Swagger UI):
- **Swagger UI**: http://localhost:1231/docs
- **ReDoc**: http://localhost:1231/redoc

### Основные эндпоинты

#### POST /upload
Загрузка и парсинг документа

**Параметры:**
- `file`: файл для загрузки (multipart/form-data)
- Дополнительные параметры (опционально):
  - `pdf_with_text_layer`: способ обработки PDF с текстовым слоем
  - `document_type`: тип документа (diploma, article и др.)
  - `language`: язык документа (rus, eng и др.)
  - `need_pdf_table_analysis`: анализ таблиц в PDF
  - `need_header_footer_analysis`: анализ заголовков и подвалов
  - `is_one_column_document`: одноколоночный документ
  - `return_format`: формат вывода (html, json и др.)

**Пример:**
```bash
curl -X POST "http://localhost:1231/upload" \
    -F "file=@document.pdf"
```

#### GET /version
Получение версии сервиса

**Пример:**
```bash
curl http://localhost:1231/version
```

#### GET /upload_example
Пример использования API

**Пример:**
```bash
curl http://localhost:1231/upload_example
```

## Поддерживаемые форматы

- **Офисные форматы**: DOCX, XLSX, PPTX, ODT
- **PDF**: с текстовым слоем и без (OCR)
- **Изображения**: PNG, JPG и др. (с OCR)
- **Текстовые**: TXT, HTML, EML, MHTML
- **Архивы**: ZIP, RAR и др.

## Документация

- [GitHub репозиторий](https://github.com/ispras/dedoc)
- [Статья на Habr](https://habr.com/ru/companies/isp_ras/articles/779390/)
