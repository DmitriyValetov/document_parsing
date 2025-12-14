# Simple


## Prepear

```
cd docling/simple

docker build -t docling-simple .
```

## Run

cpu:
```
docker run --rm -v ${PWD}:/develop --name docling-simple docling-simple python simple_call.py
```

gpu:
```
docker run --rm --gpus all -v ${PWD}:/develop --name docling-simple docling-simple python simple_call.py
docker run --rm --gpus all -v ${PWD}:/develop --name docling-simple docling-simple python vlm_call.py
```

cd E:\document_parsing\docling\simple; docker run --rm -v ${PWD}:/develop --name docling-simple docling-simple python simple_call.py





# Serve

Веб-сервис Docling с API и веб-интерфейсом для обработки документов.

## Prepare

```bash
cd docling/serve
```

## Run

### Запуск сервиса

```bash
# Запуск в фоновом режиме
docker-compose -f docker-compose.yaml up -d

# Запуск с выводом логов
docker-compose -f docker-compose.yaml up
```

### Переменные окружения

- `DOCLING_SERVE_PORT` - порт сервиса (по умолчанию: 5001)
- `CUDA_VISIBLE_DEVICES` - номер GPU (по умолчанию: 0)
- `GPU_COUNT` - количество GPU (по умолчанию: 1)

### Windows PowerShell

```powershell
cd docling\serve
docker-compose -f docker-compose.yaml up -d
```

## Доступ к сервису

После запуска сервис доступен по адресам:

- **API документация (Swagger)**: `http://localhost:5001/docs`
- **Веб-интерфейс**: `http://localhost:5001/ui`
- **Scalar документация**: `http://localhost:5001/scalar`
- **API endpoint**: `http://localhost:5001/v1/`

## Test

### Тестирование через API

Используйте CLI утилиту `test.py` для работы с API. Установите зависимости:

```bash
cd docling/serve
python -m venv env
.\env\Scripts\activate.bat
pip install -r requirements.txt
```

#### Основные команды

Доступны 4 варианта конвертации:

**1. Асинхронная конвертация из URL** (рекомендуется для больших файлов):
```bash
# Запуск конвертации (возвращает task_id, обработка выполняется на сервере)
python test.py convert-url https://arxiv.org/pdf/2501.17887

# С ожиданием результата (блокирует выполнение до завершения)
python test.py convert-url https://arxiv.org/pdf/2501.17887 --wait

# Конвертация в markdown с ожиданием результата
python test.py convert-url https://arxiv.org/pdf/2501.17887 --format markdown --wait --output result.md
```

**2. Синхронная конвертация из URL** (для небольших файлов):
```bash
# Синхронная конвертация из URL (блокирует до завершения)
python test.py convert-url-sync https://arxiv.org/pdf/2501.17887

# С сохранением результата
python test.py convert-url-sync https://arxiv.org/pdf/2501.17887 --output result.md

# С форматом вывода
python test.py convert-url-sync https://arxiv.org/pdf/2501.17887 --format markdown --output result.md
```

**3. Синхронная конвертация из файла** (рекомендуется для небольших файлов):
```bash
# Конвертация с выводом в консоль
python test.py convert-file ./input/your_file.pdf

# Сохранение результата в файл
python test.py convert-file ./input/your_file.pdf --output result.md

# С форматом вывода
python test.py convert-file ./input/your_file.pdf --format markdown --output result.md
```

**4. Асинхронная конвертация из файла** (для больших файлов):
```bash
# Запуск асинхронной конвертации из файла
python test.py convert-file-async ./input/your_file.pdf

# С ожиданием результата
python test.py convert-file-async ./input/your_file.pdf --wait

# С форматом вывода и сохранением
python test.py convert-file-async ./input/your_file.pdf --format markdown --wait --output result.md
```

**Проверка статуса задачи:**
```bash
python test.py status <task_id>
```

**Получение результата:**
```bash
python test.py result <task_id>
```

**Ожидание завершения задачи:**
```bash
python test.py wait <task_id> --timeout 300
```

**Вывод в формате JSON:**
```bash
python test.py --json convert-url https://arxiv.org/pdf/2501.17887
```

**Сохранение результата в файл:**
```bash
# Сохранение markdown результата
python test.py convert-url https://arxiv.org/pdf/2501.17887 --wait --output result.md

# Сохранение JSON результата
python test.py --json convert-url https://arxiv.org/pdf/2501.17887 --wait --output result.json
```

**Запуск примеров:**
```bash
python test.py examples
```

#### Дополнительные опции

- `--base-url` - указание базового URL API (по умолчанию: http://localhost:5001/v1)
- `--json` - вывод результата в формате JSON
- `--quiet` - не выводить промежуточные сообщения
- `--timeout` - таймаут ожидания в секундах (по умолчанию: 300)
- `--poll-interval` - интервал проверки статуса в секундах (по умолчанию: 2)
- `--output` / `-o` - путь к файлу для сохранения результата (для команд convert-url и convert-file)

#### Использование функций в своих скриптах

```python
# Импорт функций из test.py
from test import (
    async_convert_from_url,
    get_task_status,
    get_task_result,
    wait_for_task_completion,
    sync_convert_from_file,
    async_convert_from_url_async,
    wait_for_task_completion_async
)

# Пример использования
result = async_convert_from_url("https://arxiv.org/pdf/2501.17887")
task_id = result["task_id"]
result = wait_for_task_completion(task_id)
```

### Проверка статуса

```bash
# Проверка статуса контейнера
docker ps --filter "name=docling-serve"

# Просмотр логов
docker logs -f docling-serve

# Остановка сервиса
docker-compose -f docker-compose.yaml down
```

```powershell
# Проверка статуса контейнера
docker ps --filter "name=docling-serve"

# Просмотр логов
docker logs -f docling-serve

# Остановка сервиса
docker-compose -f docker-compose.yaml down
```

## Конфигурация

### Директории

- `./input` - входные файлы (монтируется как `/app/input:ro`)
- `./output` - выходные файлы (монтируется как `/app/output`)

### Volumes

- `docling-models-cache` - кэш моделей Docling
- `docling-hf-cache` - кэш моделей HuggingFace

## Troubleshooting

### Сервис не запускается

1. Проверьте, что порт 5001 свободен
2. Убедитесь, что директории `input` и `output` существуют
3. Проверьте логи: `docker logs docling-serve`

### GPU не используется

1. Проверьте, что установлен NVIDIA Container Toolkit
2. Убедитесь, что переменные окружения NVIDIA установлены в docker-compose.yaml
3. Проверьте доступность GPU: `docker exec docling-serve nvidia-smi`


# vllm_serve

Использование vLLM сервера для обработки PDF через VLM (Visual Language Model) pipeline.

## Prepare

```bash
cd docling/vllm_serve
```

## Run

### Запуск vLLM сервера и обработка документа

```bash
# Запуск всех сервисов (vLLM сервер + обработка)
docker-compose up --build

# Или только vLLM сервер в фоне
docker-compose up -d vllm-server

# Затем обработка отдельно
docker-compose up infer
```

### Переменные окружения

- `CUDA_VISIBLE_DEVICES` - номер GPU (по умолчанию: 0)
- `GPU_COUNT` - количество GPU (по умолчанию: 1)
- `INPUT_DOC_PATH` - путь к PDF файлу (по умолчанию: `/app/files/2408.09869v5.pdf`)

Пример:
```bash
CUDA_VISIBLE_DEVICES=0 GPU_COUNT=1 INPUT_DOC_PATH=/app/files/your_file.pdf docker-compose up infer
```

```powershell
$env:CUDA_VISIBLE_DEVICES=0; $env:GPU_COUNT=1; $env:INPUT_DOC_PATH="/app/files/your_file.pdf"; docker-compose up infer
```

### Windows PowerShell

```powershell
cd docling\vllm_serve
docker-compose up --build
```

## Конфигурация

### Параметры vLLM сервера (docker-compose.yml)

- `--max-num-batched-tokens` - максимальное количество токенов в батче (по умолчанию: 8192)
- `--gpu-memory-utilization` - использование памяти GPU (по умолчанию: 0.7)
- `--max-num-seqs` - максимальное количество последовательностей (по умолчанию: 512)

### Параметры обработки (infer.py)

- `BATCH_SIZE` - размер батча страниц для параллельной обработки (по умолчанию: 64)
- `timeout` - таймаут запроса к vLLM (по умолчанию: 90 сек)

## Результаты

Результаты обработки сохраняются в:
- Docker volume: `infer-output`
- Локально: `docling/vllm_serve/output/` (если смонтирован)

Файлы результатов:
- `result-timings-gpu-vlm-YYYY-MM-DD_HH-MM-SS.json` - детальная статистика по времени обработки

## Проверка GPU

```bash
# Проверка доступности GPU в контейнере
docker exec vllm-granite-server nvidia-smi

# Мониторинг использования GPU
docker exec vllm-granite-server watch -n 1 nvidia-smi
```

## Troubleshooting

### GPU не используется

1. Проверьте, что установлен NVIDIA Container Toolkit
2. Убедитесь, что переменные окружения NVIDIA установлены в docker-compose.yml:
   - `NVIDIA_VISIBLE_DEVICES=all`
   - `NVIDIA_DRIVER_CAPABILITIES=compute,utility`

### Медленная обработка

- Увеличьте `--max-num-batched-tokens` (до 32768 или 65536)
- Увеличьте `--gpu-memory-utilization` (до 0.9-0.95)
- Увеличьте `BATCH_SIZE` в infer.py (до 128-256)

### Ошибки памяти GPU

- Уменьшите `--gpu-memory-utilization` (до 0.6-0.7)
- Уменьшите `--max-num-batched-tokens` (до 4096-8192)
- Уменьшите `BATCH_SIZE` в infer.py (до 32-64)
