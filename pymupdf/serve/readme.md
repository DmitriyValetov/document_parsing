# PyMuPDF - Парсинг PDF документов

PyMuPDF - высокопроизводительная библиотека для извлечения данных, анализа, конвертации и манипуляций с PDF документами.

## Быстрый старт

### Запуск сервиса

```bash
# Запуск в фоновом режиме
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Проверка доступности

```bash
# Проверка здоровья
curl http://localhost:8000/health

# Или откройте интерактивную документацию API в браузере:
# http://localhost:8000/docs
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
- Обрабатывает все PDF файлы из папки `input/`
- Сохраняет результаты в папку `output/`

### cURL (Windows PowerShell)

```powershell
# Проверка здоровья
curl http://localhost:8000/health

# Извлечение текста
curl -X POST "http://localhost:8000/extract_text" `
    -F "file=@input/document.pdf" `
    -o output/text.json

# Извлечение метаданных
curl -X POST "http://localhost:8000/extract_metadata" `
    -F "file=@input/document.pdf" `
    -o output/metadata.json

# Извлечение всего содержимого
curl -X POST "http://localhost:8000/extract_all" `
    -F "file=@input/document.pdf" `
    -o output/all.json
```

### cURL (Linux/Mac)

```bash
# Запуск примеров
bash examples.sh

# Или вручную:
curl -X POST "http://localhost:8000/extract_text" \
    -F "file=@input/document.pdf" \
    -o output/text.json
```

## Структура проекта

```
pymupdf/serve/
├── Dockerfile           # Образ для сборки контейнера
├── docker-compose.yaml  # Конфигурация Docker Compose
├── app.py               # FastAPI приложение
├── test.py              # Python примеры использования
├── examples.sh          # Bash примеры использования
├── requirements.txt     # Python зависимости
├── input/               # Входные PDF файлы для обработки
└── output/              # Результаты парсинга (создается автоматически)
```

## API Endpoints

### Интерактивная документация

После запуска сервиса доступна интерактивная документация API (Swagger UI):
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные эндпоинты

#### POST /extract_text
Извлечение текста из PDF документа

**Параметры:**
- `file`: PDF файл для загрузки (multipart/form-data)

**Пример:**
```bash
curl -X POST "http://localhost:8000/extract_text" \
    -F "file=@document.pdf"
```

**Ответ:**
```json
{
  "filename": "document.pdf",
  "pages": 10,
  "text": [
    {
      "page": 1,
      "content": "Текст первой страницы..."
    }
  ]
}
```

#### POST /extract_metadata
Извлечение метаданных из PDF документа

**Параметры:**
- `file`: PDF файл для загрузки (multipart/form-data)

**Пример:**
```bash
curl -X POST "http://localhost:8000/extract_metadata" \
    -F "file=@document.pdf"
```

**Ответ:**
```json
{
  "filename": "document.pdf",
  "pages": 10,
  "metadata": {
    "title": "Название документа",
    "author": "Автор",
    "subject": "Тема",
    "creator": "Создатель",
    "producer": "Программа создания",
    "creation_date": "Дата создания",
    "modification_date": "Дата изменения"
  }
}
```

#### POST /extract_images
Извлечение информации об изображениях из PDF документа

**Параметры:**
- `file`: PDF файл для загрузки (multipart/form-data)

**Пример:**
```bash
curl -X POST "http://localhost:8000/extract_images" \
    -F "file=@document.pdf"
```

#### POST /extract_all
Извлечение всего содержимого: текст, метаданные и информация об изображениях

**Параметры:**
- `file`: PDF файл для загрузки (multipart/form-data)

**Пример:**
```bash
curl -X POST "http://localhost:8000/extract_all" \
    -F "file=@document.pdf"
```

#### GET /health
Проверка состояния сервиса

**Пример:**
```bash
curl http://localhost:8000/health
```

#### GET /
Информация о сервисе и доступных эндпоинтах

**Пример:**
```bash
curl http://localhost:8000/
```

## Возможности

- **Извлечение текста** - полный текст со всех страниц PDF
- **Метаданные** - информация о документе (автор, название, даты и др.)
- **Изображения** - информация об изображениях в документе
- **Высокая производительность** - быстрая обработка больших PDF файлов
- **REST API** - удобный HTTP интерфейс для интеграции

## Поддерживаемые форматы

- **PDF** - основной формат (все версии PDF)

## Документация

- [GitHub репозиторий PyMuPDF](https://github.com/pymupdf/PyMuPDF)
- [Официальная документация PyMuPDF](https://pymupdf.readthedocs.io/)
