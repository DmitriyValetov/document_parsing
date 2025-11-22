# Быстрый тест сервиса

## Запуск

```bash
cd docling_exp
docker-compose up -d
```

## Проверка статуса

```bash
# Проверка здоровья
curl http://localhost:8000/health

# Проверка статуса моделей
curl http://localhost:8000/models/status

# Информация о сервисе
curl http://localhost:8000/
```

## Тестирование парсинга PDF

### Вариант 1: Парсинг по URL (проще)

```bash
curl -X POST "http://localhost:8000/parse/url?url=https://arxiv.org/pdf/2408.09869&output_format=markdown" | jq
```

### Вариант 2: Загрузка файла

```bash
# Скачиваем тестовый PDF
curl -o test.pdf https://arxiv.org/pdf/2408.09869

curl.exe -X POST "http://localhost:8000/parse?output_format=markdown" -F "file=@test.pdf"

# Или в JSON формате:
curl.exe -X POST "http://localhost:8000/parse?output_format=json" -F "file=@test.pdf"
```

## Просмотр логов

```bash
docker-compose logs -f docling-service
```

## Остановка

```bash
docker-compose down
```

