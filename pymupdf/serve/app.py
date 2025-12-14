"""
FastAPI сервис для парсинга PDF документов с помощью PyMuPDF
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF (импортируется как fitz)
import json
from typing import Optional, Dict, Any
from pathlib import Path

app = FastAPI(
    title="PyMuPDF Document Parser",
    description="REST API для извлечения текста, метаданных и изображений из PDF документов",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "PyMuPDF Document Parser",
        "version": "1.0.0",
        "endpoints": {
            "/extract_text": "Извлечение текста из PDF",
            "/extract_metadata": "Извлечение метаданных",
            "/extract_images": "Извлечение изображений",
            "/extract_all": "Извлечение всего содержимого"
        }
    }


@app.get("/health")
async def health():
    """Проверка состояния сервиса"""
    return {"status": "healthy"}


@app.post("/extract_text")
async def extract_text(file: UploadFile = File(...)):
    """
    Извлечение текста из PDF документа
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Поддерживаются только PDF файлы")
    
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        
        result = {
            "filename": file.filename,
            "pages": len(doc),
            "text": []
        }
        
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            result["text"].append({
                "page": page_num,
                "content": text
            })
        
        doc.close()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


@app.post("/extract_metadata")
async def extract_metadata(file: UploadFile = File(...)):
    """
    Извлечение метаданных из PDF документа
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Поддерживаются только PDF файлы")
    
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        
        metadata = doc.metadata
        result = {
            "filename": file.filename,
            "pages": len(doc),
            "metadata": {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "format": metadata.get("format", ""),
                "encryption": metadata.get("encryption", "")
            }
        }
        
        doc.close()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


@app.post("/extract_images")
async def extract_images(file: UploadFile = File(...)):
    """
    Извлечение изображений из PDF документа
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Поддерживаются только PDF файлы")
    
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        
        result = {
            "filename": file.filename,
            "pages": len(doc),
            "images": []
        }
        
        for page_num, page in enumerate(doc, 1):
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                result["images"].append({
                    "page": page_num,
                    "index": img_index,
                    "xref": xref,
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "colorspace": base_image["colorspace"],
                    "bpc": base_image["bpc"],
                    "size": len(base_image["image"])
                })
        
        doc.close()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


@app.post("/extract_all")
async def extract_all(file: UploadFile = File(...)):
    """
    Извлечение всего содержимого из PDF: текст, метаданные и информация об изображениях
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Поддерживаются только PDF файлы")
    
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        
        # Метаданные
        metadata = doc.metadata
        metadata_dict = {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "format": metadata.get("format", ""),
            "encryption": metadata.get("encryption", "")
        }
        
        # Текст и изображения по страницам
        pages_data = []
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            image_list = page.get_images()
            
            images_info = []
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                images_info.append({
                    "index": img_index,
                    "xref": xref,
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "colorspace": base_image["colorspace"],
                    "bpc": base_image["bpc"],
                    "size": len(base_image["image"])
                })
            
            pages_data.append({
                "page": page_num,
                "text": text,
                "images_count": len(image_list),
                "images": images_info
            })
        
        result = {
            "filename": file.filename,
            "pages": len(doc),
            "metadata": metadata_dict,
            "pages_data": pages_data
        }
        
        doc.close()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
