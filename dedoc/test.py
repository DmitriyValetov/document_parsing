"""
Примеры использования Dedoc REST API
"""
import requests
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


BASE_URL = "http://localhost:1231"
INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"


def check_health() -> bool:
    """
    Проверка доступности сервиса через попытку подключения
    """
    try:
        # Простая проверка доступности порта
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✓ Сервис доступен на {BASE_URL}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"✗ Сервис недоступен. Убедитесь, что контейнер запущен:")
        print(f"  docker-compose up -d")
        return False
    except Exception as e:
        # Если сервис отвечает (даже с ошибкой), значит он доступен
        print(f"✓ Сервис доступен на {BASE_URL}")
        return True


def parse_file(file_path: Path, output_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Парсинг документа из файла
    
    Args:
        file_path: Путь к файлу
        output_format: Формат вывода (опционально)
    
    Returns:
        Результат парсинга
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    url = f"{BASE_URL}/upload"
    files = {"file": (file_path.name, open(file_path, "rb"), "application/octet-stream")}
    
    params = {}
    if output_format:
        params["output_format"] = output_format
    
    print(f"Отправка файла: {file_path.name}")
    response = requests.post(url, files=files, params=params)
    files["file"][1].close()
    
    response.raise_for_status()
    return response.json()


def save_result(result: Dict[str, Any], output_file: Path):
    """
    Сохранение результата в файл
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Результат сохранен: {output_file}")


def main():
    """
    Основная функция с примерами использования
    """
    print("=" * 60)
    print("Тестирование Dedoc API")
    print("=" * 60)
    
    # Проверка доступности сервиса
    if not check_health():
        print("\nУбедитесь, что сервис запущен:")
        print("docker-compose up -d")
        return
    
    print()
    
    # Поиск файлов в папке input
    input_files = list(INPUT_DIR.glob("*"))
    input_files = [f for f in input_files if f.is_file()]
    
    if not input_files:
        print(f"Файлы не найдены в папке: {INPUT_DIR}")
        return
    
    # Обработка каждого файла
    for file_path in input_files:
        print(f"\n{'=' * 60}")
        print(f"Обработка: {file_path.name}")
        print(f"{'=' * 60}")
        
        try:
            # Парсинг файла
            result = parse_file(file_path)
            
            # Сохранение результата
            output_file = OUTPUT_DIR / f"{file_path.stem}_result.json"
            save_result(result, output_file)
            
            # Вывод краткой информации
            if "structure" in result:
                print(f"Структура документа: {len(result.get('structure', {}).get('subparagraphs', []))} элементов")
            if "tables" in result:
                print(f"Найдено таблиц: {len(result.get('tables', []))}")
            if "metadata" in result:
                print(f"Метаданные: {result.get('metadata', {})}")
            
        except Exception as e:
            print(f"Ошибка при обработке {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("Обработка завершена")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
