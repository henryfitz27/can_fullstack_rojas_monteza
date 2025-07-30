from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from .apps.scraper import scrape_url
from .settings import get_db, engine, Base, CORS_ORIGINS
from .models import Link, File
from .tasks import process_file_task
import logging
from typing import List, Optional
from datetime import datetime


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Web Scraper API",
    description="API para realizar web scraping con BeautifulSoup4 y almacenamiento en PostgreSQL",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Orígenes permitidos desde variables de entorno
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Modelo para la petición POST del endpoint /process
class ProcessRequest(BaseModel):
    file_id: int
    email: str


@app.get("/")
async def read_root():
    return {
        "message": "Web Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process": "Procesa un archivo de URLs usando Celery (requiere file_id)",
            "GET /task-status/{task_id}": "Consulta el estado de una tarea de procesamiento"
        }
    }

@app.post("/process")
async def process_file(request: ProcessRequest, db: Session = Depends(get_db)):
    """
    Endpoint para procesar un archivo de URLs usando Celery
    
    Args:
        request (ProcessRequest): Objeto que contiene el file_id a procesar
        db (Session): Sesión de base de datos
        
    Returns:
        Dict: Información sobre la tarea iniciada
    """
    try:
        logger.info(f"Iniciando procesamiento del archivo con ID: {request.file_id}")
        
        # Verificar que el archivo existe
        file_record = db.query(File).filter(File.id == request.file_id).first()
        if not file_record:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el archivo con ID: {request.file_id}"
            )
        
        # Verificar que el archivo no esté ya siendo procesado
        if file_record.status == "PROCESSING":
            raise HTTPException(
                status_code=400,
                detail=f"El archivo con ID {request.file_id} ya está siendo procesado"
            )
        
        # Verificar que el archivo exista en el sistema de archivos
        import os
        if not os.path.exists(file_record.file_path):
            raise HTTPException(
                status_code=404,
                detail=f"El archivo no existe en la ruta especificada: {file_record.file_path}"
            )
        
        # Iniciar la tarea de Celery
        task = process_file_task.delay(request.file_id, request.email)
        
        logger.info(f"Tarea de Celery iniciada con ID: {task.id} para archivo: {request.file_id} - Email: {request.email}")
        
        return {
            "message": "Procesamiento iniciado",
            "file_id": request.file_id,
            "task_id": task.id,
            "status": "QUEUED",
            "file_name": file_record.file_name,
            "file_path": file_record.file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en el endpoint /process: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Endpoint para consultar el estado de una tarea de Celery
    
    Args:
        task_id (str): ID de la tarea de Celery
        
    Returns:
        Dict: Estado actual de la tarea
    """
    try:
        from celery.result import AsyncResult
        from tasks import app as celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Tarea en cola o no encontrada'
            }
        elif result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'current': result.info.get('current', 0),
                'total': result.info.get('total', 1),
                'progress': result.info.get('progress', 0),
                'processed': result.info.get('processed', 0),
                'failed': result.info.get('failed', 0),
                'status': f"Procesando... {result.info.get('progress', 0)}%"
            }
        elif result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'result': result.result,
                'status': 'Completado exitosamente'
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': result.state,
                'error': str(result.info),
                'status': 'Error en el procesamiento'
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error al consultar estado de tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar el estado de la tarea: {str(e)}"
        )