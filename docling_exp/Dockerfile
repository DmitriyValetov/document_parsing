FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
# Примечание: для GPU поддержки требуется запуск контейнера с nvidia-docker runtime
# PyTorch и onnxruntime-gpu автоматически используют GPU если доступен
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY app/ ./app/
COPY config.yaml .
COPY run.py .

# Создание директорий для временных файлов и кэша моделей
RUN mkdir -p /tmp/docling /app/models_cache

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DOCLING_CACHE_DIR=/app/models_cache
ENV HF_HOME=/app/models_cache

# Порт
EXPOSE 8000

# Команда запуска
CMD ["python", "run.py"]

