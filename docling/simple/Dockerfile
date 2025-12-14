FROM python:3.11-slim

# docker build -t docling-simple .
# docker run --rm -it -v $(pwd):/develop --name docling-simple docling-simple



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

RUN pip install docling==2.64.1
RUN pip install onnx onnxruntime
RUN pip install rapidocr easyocr


WORKDIR /develop
