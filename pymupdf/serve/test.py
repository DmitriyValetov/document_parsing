"""
Примеры использования PyMuPDF REST API
"""
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any


BASE_URL = "http://localhost:8000"
INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"


def check_health() -> bool:
    """
    Проверка доступности сервиса
    """
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print(f"✓ Сервис доступен: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Сервис недоступен: {e}")
        print(f"  Убедитесь, что контейнер запущен: docker-compose up -d")
        return False


def extract_text(file_path: Path) -> Dict[str, Any]:
    """
    Извлечение текста из PDF
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    url = f"{BASE_URL}/extract_text"
    files = {"file": (file_path.name, open(file_path, "rb"), "application/pdf")}
    
    print(f"Извлечение текста из: {file_path.name}")
    response = requests.post(url, files=files)
    files["file"][1].close()
    
    response.raise_for_status()
    return response.json()


def extract_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Извлечение метаданных из PDF
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    url = f"{BASE_URL}/extract_metadata"
    files = {"file": (file_path.name, open(file_path, "rb"), "application/pdf")}
    
    print(f"Извлечение метаданных из: {file_path.name}")
    response = requests.post(url, files=files)
    files["file"][1].close()
    
    response.raise_for_status()
    return response.json()


def extract_images(file_path: Path) -> Dict[str, Any]:
    """
    Извлечение информации об изображениях из PDF
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    url = f"{BASE_URL}/extract_images"
    files = {"file": (file_path.name, open(file_path, "rb"), "application/pdf")}
    
    print(f"Извлечение информации об изображениях из: {file_path.name}")
    response = requests.post(url, files=files)
    files["file"][1].close()
    
    response.raise_for_status()
    return response.json()


def extract_all(file_path: Path) -> Dict[str, Any]:
    """
    Извлечение всего содержимого из PDF
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    url = f"{BASE_URL}/extract_all"
    files = {"file": (file_path.name, open(file_path, "rb"), "application/pdf")}
    
    print(f"Извлечение всего содержимого из: {file_path.name}")
    response = requests.post(url, files=files)
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
    print("Тестирование PyMuPDF API")
    print("=" * 60)
    
    # Проверка доступности сервиса
    if not check_health():
        return
    
    print()
    
    # Поиск PDF файлов в папке input
    input_files = list(INPUT_DIR.glob("*.pdf"))
    
    if not input_files:
        print(f"PDF файлы не найдены в папке: {INPUT_DIR}")
        print("Добавьте PDF файлы в папку input/")
        return
    
    # Обработка каждого файла
    for file_path in input_files:
        print(f"\n{'=' * 60}")
        print(f"Обработка: {file_path.name}")
        print(f"{'=' * 60}")
        
        try:
            # Извлечение всего содержимого
            result = extract_all(file_path)
            
            # Сохранение результата
            output_file = OUTPUT_DIR / f"{file_path.stem}_result.json"
            save_result(result, output_file)
            
            # Вывод краткой информации
            print(f"Страниц: {result.get('pages', 0)}")
            if "metadata" in result:
                metadata = result["metadata"]
                if metadata.get("title"):
                    print(f"Название: {metadata['title']}")
                if metadata.get("author"):
                    print(f"Автор: {metadata['author']}")
            
            if "pages_data" in result:
                total_text_length = sum(len(page.get("text", "")) for page in result["pages_data"])
                total_images = sum(page.get("images_count", 0) for page in result["pages_data"])
                print(f"Общий объем текста: {total_text_length} символов")
                print(f"Всего изображений: {total_images}")
            
        except Exception as e:
            print(f"Ошибка при обработке {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("Обработка завершена")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
