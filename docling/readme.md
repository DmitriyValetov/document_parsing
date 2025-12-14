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


## Prepear


## Serve


## Test


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
