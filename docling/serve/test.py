"""
CLI утилита для тестирования Docling API (синхронные и асинхронные запросы)
"""
import argparse
import requests
import asyncio
import httpx
import json
import sys
import time
import base64
import os
from pathlib import Path
from typing import Optional, Dict, Any


BASE_URL = "http://localhost:5001/v1"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}


# ==================== СИНХРОННЫЕ ЗАПРОСЫ (requests) ====================

def async_convert_from_url(url: str, output_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Асинхронная конвертация PDF из URL
    
    Args:
        url: URL PDF файла
        output_format: Формат вывода (например, "markdown")
    
    Returns:
        Ответ с task_id
    """
    payload = {
        "sources": [{"kind": "http", "url": url}]
    }
    
    if output_format:
        payload["options"] = {"output_format": output_format}
    
    response = requests.post(
        f"{BASE_URL}/convert/source/async",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def sync_convert_from_url(url: str, output_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Синхронная конвертация PDF из URL
    
    Args:
        url: URL PDF файла
        output_format: Формат вывода (например, "markdown")
    
    Returns:
        Результат конвертации
    """
    payload = {
        "sources": [{"kind": "http", "url": url}]
    }
    
    if output_format:
        payload["options"] = {"output_format": output_format}
    
    response = requests.post(
        f"{BASE_URL}/convert/source",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Проверка статуса задачи
    
    Args:
        task_id: ID задачи
    
    Returns:
        Статус задачи
    """
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}",
        headers={"accept": "application/json"}
    )
    response.raise_for_status()
    return response.json()


def get_task_result(task_id: str) -> Dict[str, Any]:
    """
    Получение результата задачи
    
    Args:
        task_id: ID задачи
    
    Returns:
        Результат конвертации
    """
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}/result",
        headers={"accept": "application/json"}
    )
    response.raise_for_status()
    return response.json()


def sync_convert_from_file(file_path: str, output_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Синхронная конвертация из локального файла или файла в контейнере
    
    Args:
        file_path: Путь к файлу (локальный или в контейнере, например, "/app/input/your_file.pdf")
        output_format: Формат вывода (например, "markdown")
    
    Returns:
        Результат конвертации
    """
    # Проверяем, является ли путь локальным файлом
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Локальный файл - загружаем через base64
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        filename = os.path.basename(file_path)
        payload = {
            "sources": [{
                "kind": "file",
                "base64_string": file_base64,
                "filename": filename
            }]
        }
    else:
        # Путь в контейнере
        payload = {
            "sources": [{"kind": "file", "path": file_path}]
        }
    
    if output_format:
        payload["options"] = {"output_format": output_format}
    
    response = requests.post(
        f"{BASE_URL}/convert/source",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def wait_for_task_completion(task_id: str, timeout: int = 300, poll_interval: int = 2, quiet: bool = False) -> Dict[str, Any]:
    """
    Ожидание завершения задачи с периодической проверкой статуса
    
    Args:
        task_id: ID задачи
        timeout: Максимальное время ожидания в секундах
        poll_interval: Интервал проверки статуса в секундах
        quiet: Не выводить статус в консоль
    
    Returns:
        Результат задачи
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = get_task_status(task_id)
        task_status = status.get("task_status", "unknown")
        
        if not quiet:
            print(f"Статус задачи: {task_status}", file=sys.stderr)
        
        if task_status == "completed":
            return get_task_result(task_id)
        elif task_status == "failed":
            raise Exception(f"Задача завершилась с ошибкой: {status}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Задача не завершилась за {timeout} секунд")


# ==================== АСИНХРОННЫЕ ЗАПРОСЫ (httpx) ====================

async def async_convert_from_file_async(file_path: str, output_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Асинхронная конвертация из локального файла или файла в контейнере (async версия)
    
    Args:
        file_path: Путь к файлу (локальный или в контейнере, например, "/app/input/your_file.pdf")
        output_format: Формат вывода (например, "markdown")
    
    Returns:
        Ответ с task_id
    """
    # Проверяем, является ли путь локальным файлом
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Локальный файл - загружаем через base64
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        filename = os.path.basename(file_path)
        payload = {
            "sources": [{
                "kind": "file",
                "base64_string": file_base64,
                "filename": filename
            }]
        }
    else:
        # Путь в контейнере
        payload = {
            "sources": [{"kind": "file", "path": file_path}]
        }
    
    if output_format:
        payload["options"] = {"output_format": output_format}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/convert/source/async",
            headers=HEADERS,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def async_convert_from_url_async(url: str, output_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Асинхронная конвертация PDF из URL (async версия)
    
    Args:
        url: URL PDF файла
        output_format: Формат вывода (например, "markdown")
    
    Returns:
        Ответ с task_id
    """
    payload = {
        "sources": [{"kind": "http", "url": url}]
    }
    
    if output_format:
        payload["options"] = {"output_format": output_format}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/convert/source/async",
            headers=HEADERS,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def get_task_status_async(task_id: str) -> Dict[str, Any]:
    """
    Проверка статуса задачи (async версия)
    
    Args:
        task_id: ID задачи
    
    Returns:
        Статус задачи
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tasks/{task_id}",
            headers={"accept": "application/json"},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()


async def get_task_result_async(task_id: str) -> Dict[str, Any]:
    """
    Получение результата задачи (async версия)
    
    Args:
        task_id: ID задачи
    
    Returns:
        Результат конвертации
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tasks/{task_id}/result",
            headers={"accept": "application/json"},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def sync_convert_from_file_async(file_path: str) -> Dict[str, Any]:
    """
    Синхронная конвертация из локального файла или файла в контейнере (async версия)
    
    Args:
        file_path: Путь к файлу (локальный или в контейнере, например, "/app/input/your_file.pdf")
    
    Returns:
        Результат конвертации
    """
    # Проверяем, является ли путь локальным файлом
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Локальный файл - загружаем через base64
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        filename = os.path.basename(file_path)
        payload = {
            "sources": [{
                "kind": "file",
                "base64_string": file_base64,
                "filename": filename
            }]
        }
    else:
        # Путь в контейнере
        payload = {
            "sources": [{"kind": "file", "path": file_path}]
        }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/convert/source",
            headers=HEADERS,
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()


async def wait_for_task_completion_async(
    task_id: str, 
    timeout: int = 300, 
    poll_interval: int = 2,
    quiet: bool = False
) -> Dict[str, Any]:
    """
    Ожидание завершения задачи с периодической проверкой статуса (async версия)
    
    Args:
        task_id: ID задачи
        timeout: Максимальное время ожидания в секундах
        poll_interval: Интервал проверки статуса в секундах
        quiet: Не выводить статус в консоль
    
    Returns:
        Результат задачи
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = await get_task_status_async(task_id)
        task_status = status.get("task_status", "unknown")
        
        if not quiet:
            print(f"Статус задачи: {task_status}", file=sys.stderr)
        
        if task_status == "completed":
            return await get_task_result_async(task_id)
        elif task_status == "failed":
            raise Exception(f"Задача завершилась с ошибкой: {status}")
        
        await asyncio.sleep(poll_interval)
    
    raise TimeoutError(f"Задача не завершилась за {timeout} секунд")


# ==================== CLI КОМАНДЫ ====================

def cmd_convert_url(args):
    """Команда: конвертация из URL"""
    try:
        result = async_convert_from_url(args.url, args.format)
        task_id = result["task_id"]
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Task ID: {task_id}")
            if args.wait:
                print("Ожидание завершения...", file=sys.stderr)
                result = wait_for_task_completion(
                    task_id, 
                    timeout=args.timeout, 
                    poll_interval=args.poll_interval,
                    quiet=args.quiet
                )
                
                # Сохранение результата в файл, если указан
                if args.output:
                    output_data = result
                    if not args.json and "document" in result:
                        doc = result.get("document", {})
                        if doc.get("md_content"):
                            output_data = doc["md_content"]
                        elif doc.get("text_content"):
                            output_data = doc["text_content"]
                        elif doc.get("html_content"):
                            output_data = doc["html_content"]
                    
                    with open(args.output, 'w', encoding='utf-8') as f:
                        if isinstance(output_data, str):
                            f.write(output_data)
                        else:
                            json.dump(output_data, f, indent=2, ensure_ascii=False)
                    print(f"Результат сохранен в: {args.output}", file=sys.stderr)
                
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    if "document" in result:
                        doc = result.get("document", {})
                        if doc.get("md_content"):
                            # Выводим только markdown в консоль
                            print(doc["md_content"])
                        elif doc.get("text_content"):
                            print(doc["text_content"])
                        elif doc.get("html_content"):
                            print(doc["html_content"])
                        else:
                            print("Конвертация завершена, но содержимое недоступно")
                    else:
                        print("Конвертация завершена!")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_convert_file(args):
    """Команда: синхронная конвертация из файла"""
    try:
        # Проверяем существование файла
        if not os.path.exists(args.file) and not args.file.startswith('/'):
            print(f"Предупреждение: файл '{args.file}' не найден. Используется как путь в контейнере.", file=sys.stderr)
        
        result = sync_convert_from_file(args.file, args.format)
        
        # Сохранение результата в файл, если указан
        if args.output:
            output_data = result
            if not args.json and "document" in result:
                # Сохраняем только содержимое документа
                doc = result.get("document", {})
                if doc.get("md_content"):
                    output_data = doc["md_content"]
                elif doc.get("text_content"):
                    output_data = doc["text_content"]
                elif doc.get("html_content"):
                    output_data = doc["html_content"]
            
            with open(args.output, 'w', encoding='utf-8') as f:
                if isinstance(output_data, str):
                    f.write(output_data)
                else:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"Результат сохранен в: {args.output}", file=sys.stderr)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if "document" in result:
                doc = result.get("document", {})
                if doc.get("md_content"):
                    # Выводим только markdown в консоль
                    print(doc["md_content"])
                elif doc.get("text_content"):
                    print(doc["text_content"])
                elif doc.get("html_content"):
                    print(doc["html_content"])
                else:
                    print("Конвертация завершена, но содержимое недоступно")
            else:
                print("Конвертация завершена!")
    except FileNotFoundError as e:
        print(f"Ошибка: файл не найден - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_convert_url_sync(args):
    """Команда: синхронная конвертация из URL"""
    try:
        result = sync_convert_from_url(args.url, args.format)
        
        # Сохранение результата в файл, если указан
        if args.output:
            output_data = result
            if not args.json and "document" in result:
                doc = result.get("document", {})
                if doc.get("md_content"):
                    output_data = doc["md_content"]
                elif doc.get("text_content"):
                    output_data = doc["text_content"]
                elif doc.get("html_content"):
                    output_data = doc["html_content"]
            
            with open(args.output, 'w', encoding='utf-8') as f:
                if isinstance(output_data, str):
                    f.write(output_data)
                else:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"Результат сохранен в: {args.output}", file=sys.stderr)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if "document" in result:
                doc = result.get("document", {})
                if doc.get("md_content"):
                    print(doc["md_content"])
                elif doc.get("text_content"):
                    print(doc["text_content"])
                elif doc.get("html_content"):
                    print(doc["html_content"])
                else:
                    print("Конвертация завершена, но содержимое недоступно")
            else:
                print("Конвертация завершена!")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_convert_file_async(args):
    """Команда: асинхронная конвертация из файла"""
    try:
        # Проверяем существование файла
        if not os.path.exists(args.file) and not args.file.startswith('/'):
            print(f"Предупреждение: файл '{args.file}' не найден. Используется как путь в контейнере.", file=sys.stderr)
        
        result = await async_convert_from_file_async(args.file, args.format)
        task_id = result["task_id"]
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Task ID: {task_id}")
            if args.wait:
                print("Ожидание завершения...", file=sys.stderr)
                result = await wait_for_task_completion_async(
                    task_id,
                    timeout=args.timeout,
                    poll_interval=args.poll_interval,
                    quiet=args.quiet
                )
                
                # Сохранение результата в файл, если указан
                if args.output:
                    output_data = result
                    if not args.json and "document" in result:
                        doc = result.get("document", {})
                        if doc.get("md_content"):
                            output_data = doc["md_content"]
                        elif doc.get("text_content"):
                            output_data = doc["text_content"]
                        elif doc.get("html_content"):
                            output_data = doc["html_content"]
                    
                    with open(args.output, 'w', encoding='utf-8') as f:
                        if isinstance(output_data, str):
                            f.write(output_data)
                        else:
                            json.dump(output_data, f, indent=2, ensure_ascii=False)
                    print(f"Результат сохранен в: {args.output}", file=sys.stderr)
                
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    if "document" in result:
                        doc = result.get("document", {})
                        if doc.get("md_content"):
                            print(doc["md_content"])
                        elif doc.get("text_content"):
                            print(doc["text_content"])
                        elif doc.get("html_content"):
                            print(doc["html_content"])
                        else:
                            print("Конвертация завершена, но содержимое недоступно")
                    else:
                        print("Конвертация завершена!")
    except FileNotFoundError as e:
        print(f"Ошибка: файл не найден - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_status(args):
    """Команда: проверка статуса задачи"""
    try:
        result = get_task_status(args.task_id)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            status = result.get("task_status", "unknown")
            print(f"Статус: {status}")
            if "task_id" in result:
                print(f"Task ID: {result['task_id']}")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_result(args):
    """Команда: получение результата задачи"""
    try:
        result = get_task_result(args.task_id)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Результат получен")
            if "output" in result:
                output = result.get("output", "")
                if isinstance(output, str):
                    print(f"Длина результата: {len(output)} символов")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_wait(args):
    """Команда: ожидание завершения задачи"""
    try:
        result = wait_for_task_completion(
            args.task_id,
            timeout=args.timeout,
            poll_interval=args.poll_interval,
            quiet=args.quiet
        )
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Задача завершена!")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_convert_url_async(args):
    """Команда: асинхронная конвертация из URL (async)"""
    try:
        result = await async_convert_from_url_async(args.url, args.format)
        task_id = result["task_id"]
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Task ID: {task_id}")
            if args.wait:
                print("Ожидание завершения...", file=sys.stderr)
                result = await wait_for_task_completion_async(
                    task_id,
                    timeout=args.timeout,
                    poll_interval=args.poll_interval,
                    quiet=args.quiet
                )
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print("Конвертация завершена!")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


# ==================== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ====================

def example_sync():
    """Пример синхронного использования"""
    print("=== Синхронные запросы ===\n")
    
    # 1. Асинхронная конвертация из URL
    print("1. Запуск асинхронной конвертации из URL...")
    result = async_convert_from_url("https://arxiv.org/pdf/2501.17887")
    task_id = result["task_id"]
    print(f"   Task ID: {task_id}\n")
    
    # 2. Проверка статуса
    print("2. Проверка статуса...")
    status = get_task_status(task_id)
    print(f"   Статус: {status.get('task_status')}\n")
    
    # 3. Ожидание завершения и получение результата
    print("3. Ожидание завершения задачи...")
    try:
        result = wait_for_task_completion(task_id, timeout=60)
        print(f"   Задача завершена! Результат получен.\n")
    except TimeoutError as e:
        print(f"   {e}\n")
    
    # 4. Конвертация с указанием формата вывода
    print("4. Конвертация в markdown...")
    result = async_convert_from_url("https://arxiv.org/pdf/2501.17887", output_format="markdown")
    print(f"   Task ID: {result['task_id']}\n")
    
    # 5. Синхронная конвертация из файла
    print("5. Синхронная конвертация из файла...")
    try:
        result = sync_convert_from_file("/app/input/your_file.pdf")
        print(f"   Результат получен: {len(str(result))} символов\n")
    except Exception as e:
        print(f"   Ошибка: {e}\n")


async def example_async():
    """Пример асинхронного использования"""
    print("=== Асинхронные запросы ===\n")
    
    # 1. Асинхронная конвертация из URL
    print("1. Запуск асинхронной конвертации из URL...")
    result = await async_convert_from_url_async("https://arxiv.org/pdf/2501.17887")
    task_id = result["task_id"]
    print(f"   Task ID: {task_id}\n")
    
    # 2. Проверка статуса
    print("2. Проверка статуса...")
    status = await get_task_status_async(task_id)
    print(f"   Статус: {status.get('task_status')}\n")
    
    # 3. Ожидание завершения и получение результата
    print("3. Ожидание завершения задачи...")
    try:
        result = await wait_for_task_completion_async(task_id, timeout=60)
        print(f"   Задача завершена! Результат получен.\n")
    except TimeoutError as e:
        print(f"   {e}\n")
    
    # 4. Параллельная обработка нескольких задач
    print("4. Параллельная обработка нескольких URL...")
    urls = [
        "https://arxiv.org/pdf/2501.17887",
        "https://arxiv.org/pdf/2501.17887"
    ]
    
    tasks = [async_convert_from_url_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"   Задача {i+1}: Task ID = {result['task_id']}")
    print()


# ==================== CLI ИНТЕРФЕЙС ====================

def create_parser():
    """Создание парсера аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="CLI утилита для работы с Docling API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Конвертация из URL
  python test.py convert-url https://arxiv.org/pdf/2501.17887
  
  # Конвертация с ожиданием результата
  python test.py convert-url https://arxiv.org/pdf/2501.17887 --wait
  
  # Конвертация в markdown
  python test.py convert-url https://arxiv.org/pdf/2501.17887 --format markdown
  
  # Проверка статуса
  python test.py status <task_id>
  
  # Получение результата
  python test.py result <task_id>
  
  # Ожидание завершения
  python test.py wait <task_id>
  
  # Синхронная конвертация из локального файла
  python test.py convert-file ./input/file.pdf
  
  # Или из файла в контейнере
  python test.py convert-file /app/input/file.pdf
  
  # Асинхронная конвертация из файла
  python test.py convert-file-async ./input/file.pdf --wait
  
  # Синхронная конвертация из URL
  python test.py convert-url-sync https://arxiv.org/pdf/2501.17887
        """
    )
    
    parser.add_argument(
        "--base-url",
        default="http://localhost:5001/v1",
        help="Базовый URL API (по умолчанию: http://localhost:5001/v1)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Выводить результат в формате JSON"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Не выводить промежуточные сообщения"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Команды")
    
    # Команда convert-url (асинхронная)
    parser_convert_url = subparsers.add_parser("convert-url", help="Асинхронная конвертация из URL")
    parser_convert_url.add_argument("url", help="URL PDF файла")
    parser_convert_url.add_argument("--format", help="Формат вывода (например, markdown)")
    parser_convert_url.add_argument("--wait", action="store_true", help="Ожидать завершения конвертации")
    parser_convert_url.add_argument("--timeout", type=int, default=300, help="Таймаут ожидания в секундах (по умолчанию: 300)")
    parser_convert_url.add_argument("--poll-interval", type=int, default=2, help="Интервал проверки статуса в секундах (по умолчанию: 2)")
    parser_convert_url.add_argument("--output", "-o", help="Путь к файлу для сохранения результата")
    parser_convert_url.set_defaults(func=cmd_convert_url)
    
    # Команда convert-url-sync (синхронная)
    parser_convert_url_sync = subparsers.add_parser("convert-url-sync", help="Синхронная конвертация из URL")
    parser_convert_url_sync.add_argument("url", help="URL PDF файла")
    parser_convert_url_sync.add_argument("--format", help="Формат вывода (например, markdown)")
    parser_convert_url_sync.add_argument("--output", "-o", help="Путь к файлу для сохранения результата")
    parser_convert_url_sync.set_defaults(func=cmd_convert_url_sync)
    
    # Команда convert-file (синхронная)
    parser_convert_file = subparsers.add_parser("convert-file", help="Синхронная конвертация из файла")
    parser_convert_file.add_argument("file", help="Путь к файлу (локальный или в контейнере, например, ./input/file.pdf или /app/input/file.pdf)")
    parser_convert_file.add_argument("--format", help="Формат вывода (например, markdown)")
    parser_convert_file.add_argument("--output", "-o", help="Путь к файлу для сохранения результата")
    parser_convert_file.set_defaults(func=cmd_convert_file)
    
    # Команда convert-file-async (асинхронная)
    parser_convert_file_async = subparsers.add_parser("convert-file-async", help="Асинхронная конвертация из файла")
    parser_convert_file_async.add_argument("file", help="Путь к файлу (локальный или в контейнере, например, ./input/file.pdf или /app/input/file.pdf)")
    parser_convert_file_async.add_argument("--format", help="Формат вывода (например, markdown)")
    parser_convert_file_async.add_argument("--wait", action="store_true", help="Ожидать завершения конвертации")
    parser_convert_file_async.add_argument("--timeout", type=int, default=300, help="Таймаут ожидания в секундах (по умолчанию: 300)")
    parser_convert_file_async.add_argument("--poll-interval", type=int, default=2, help="Интервал проверки статуса в секундах (по умолчанию: 2)")
    parser_convert_file_async.add_argument("--output", "-o", help="Путь к файлу для сохранения результата")
    parser_convert_file_async.set_defaults(func=lambda args: asyncio.run(cmd_convert_file_async(args)))
    
    # Команда status
    parser_status = subparsers.add_parser("status", help="Проверка статуса задачи")
    parser_status.add_argument("task_id", help="ID задачи")
    parser_status.set_defaults(func=cmd_status)
    
    # Команда result
    parser_result = subparsers.add_parser("result", help="Получение результата задачи")
    parser_result.add_argument("task_id", help="ID задачи")
    parser_result.set_defaults(func=cmd_result)
    
    # Команда wait
    parser_wait = subparsers.add_parser("wait", help="Ожидание завершения задачи")
    parser_wait.add_argument("task_id", help="ID задачи")
    parser_wait.add_argument("--timeout", type=int, default=300, help="Таймаут ожидания в секундах (по умолчанию: 300)")
    parser_wait.add_argument("--poll-interval", type=int, default=2, help="Интервал проверки статуса в секундах (по умолчанию: 2)")
    parser_wait.set_defaults(func=cmd_wait)
    
    # Команда convert-url-async
    parser_convert_url_async = subparsers.add_parser("convert-url-async", help="Асинхронная конвертация из URL (async)")
    parser_convert_url_async.add_argument("url", help="URL PDF файла")
    parser_convert_url_async.add_argument("--format", help="Формат вывода (например, markdown)")
    parser_convert_url_async.add_argument("--wait", action="store_true", help="Ожидать завершения конвертации")
    parser_convert_url_async.add_argument("--timeout", type=int, default=300, help="Таймаут ожидания в секундах (по умолчанию: 300)")
    parser_convert_url_async.add_argument("--poll-interval", type=int, default=2, help="Интервал проверки статуса в секундах (по умолчанию: 2)")
    parser_convert_url_async.set_defaults(func=lambda args: asyncio.run(cmd_convert_url_async(args)))
    
    # Команда examples
    parser_examples = subparsers.add_parser("examples", help="Запуск примеров использования")
    parser_examples.set_defaults(func=lambda args: (example_sync(), asyncio.run(example_async())))
    
    return parser


def main():
    """Главная функция CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Обновление BASE_URL если указан
    if hasattr(args, "base_url") and args.base_url:
        global BASE_URL
        BASE_URL = args.base_url.rstrip("/")
    
    # Если команда не указана, показываем help
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Выполнение команды
    try:
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nПрервано пользователем", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
