from celery import Celery
from sqlalchemy.orm import Session
from datetime import datetime
import os
import logging
import redis
import json
from typing import List

from .settings import get_db, SessionLocal
from .models import File, Link
from .apps.scraper import WebScraper

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Celery con Redis
# Usar diferentes URLs según el entorno (Docker vs local)
import os
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '9050')
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Para Docker, usar el nombre del servicio configurado en variables de entorno
if os.getenv('DOCKER_ENV'):
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

app = Celery(
    'scraper_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['src.tasks']
)

# Configuración adicional de Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

def publish_processing_complete(file_id: int, email: str, results: dict):
    """
    Publica un mensaje en Redis cuando se completa el procesamiento
    
    Args:
        file_id (int): ID del archivo procesado
        email (str): Email para notificación
        results (dict): Resultados del procesamiento
    """
    try:
        # Conectar a Redis
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            db=0,
            decode_responses=True
        )
        
        # Preparar el mensaje
        message = {
            "file_id": file_id,
            "email": email,
            "processing_results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publicar en el canal "processing_complete"
        channel = "processing_complete"
        redis_client.publish(channel, json.dumps(message))
        
        logger.info(f"Mensaje publicado en Redis - Canal: {channel}, File ID: {file_id}, Email: {email}")
        
    except Exception as e:
        logger.error(f"Error al publicar en Redis: {str(e)}")

def read_urls_from_file(file_path: str) -> List[str]:
    """
    Lee las URLs de un archivo de texto o CSV
    """
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                url = line.strip()
                if url and url.startswith('http'):  # Validación básica de URL
                    urls.append(url)
        logger.info(f"Se encontraron {len(urls)} URLs en el archivo {file_path}")
        return urls
    except Exception as e:
        logger.error(f"Error al leer el archivo {file_path}: {str(e)}")
        raise

@app.task(bind=True)
def process_file_task(self, file_id: int, email: str):
    """
    Tarea principal que procesa un archivo completo de URLs
    
    Args:
        file_id (int): ID del archivo en la base de datos
        email (str): Email para notificación de finalización
        
    Returns:
        dict: Resultado del procesamiento
    """
    db = SessionLocal()
    try:
        logger.info(f"Iniciando procesamiento del archivo con ID: {file_id}")
        
        # Buscar el archivo en la base de datos
        file_record = db.query(File).filter(File.id == file_id).first()
        if not file_record:
            error_msg = f"No se encontró el archivo con ID: {file_id}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Actualizar el estado a "PROCESSING"
        file_record.status = "PROCESSING"
        db.commit()
        logger.info(f"Estado del archivo {file_id} actualizado a PROCESSING")
        
        # Leer las URLs del archivo
        try:
            urls = read_urls_from_file(file_record.file_path)
        except Exception as e:
            file_record.status = "ERROR"
            db.commit()
            error_msg = f"Error al leer el archivo: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        if not urls:
            file_record.status = "ERROR"
            db.commit()
            error_msg = "No se encontraron URLs válidas en el archivo"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Actualizar el total de links en el archivo
        file_record.total_links = len(urls)
        db.commit()
        
        # Procesar cada URL
        scraper = WebScraper()
        processed_count = 0
        failed_count = 0
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"Procesando URL {i}/{len(urls)}: {url}")
                
                # Realizar el scraping
                result = scraper.scrape_website(url)
                
                # Procesar la fecha si existe
                post_date = None
                if result.get('date'):
                    try:
                        date_str = result.get('date')
                        # Manejar diferentes formatos de fecha
                        if 'T' in date_str:
                            if date_str.endswith('Z'):
                                date_str = date_str.replace('Z', '+00:00')
                            post_date = datetime.fromisoformat(date_str)
                        else:
                            # Si no tiene formato ISO, intentar parsearlo como string
                            from dateutil import parser
                            post_date = parser.parse(date_str)
                    except Exception as date_error:
                        logger.warning(f"Error al parsear fecha '{result.get('date')}': {date_error}")
                        post_date = None
                
                # Crear nuevo registro en la tabla links
                link_record = Link(
                    file_id=file_id,
                    url=url,
                    title=result.get('title'),
                    post_date=post_date,
                    content=result.get('content'),
                    page_exists=result.get('page_exists', False),
                    success=result.get('success', False),
                    error_description=result.get('error') if not result.get('success') else None,
                    processed_date=datetime.utcnow()
                )
                
                db.add(link_record)
                
                if result.get('success'):
                    processed_count += 1
                    logger.info(f"URL procesada exitosamente: {url}")
                else:
                    failed_count += 1
                    logger.warning(f"Error al procesar URL {url}: {result.get('error')}")
                
                # Actualizar progreso cada 10 URLs o en la última
                if i % 10 == 0 or i == len(urls):
                    file_record.total_processed = processed_count
                    file_record.total_failed = failed_count
                    db.commit()
                    
                    # Actualizar progreso de la tarea
                    progress = int((i / len(urls)) * 100)
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i,
                            'total': len(urls),
                            'progress': progress,
                            'processed': processed_count,
                            'failed': failed_count
                        }
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error inesperado al procesar URL {url}: {str(e)}")
                
                # Crear registro de error
                link_record = Link(
                    file_id=file_id,
                    url=url,
                    title=None,
                    post_date=None,
                    content=None,
                    page_exists=False,
                    success=False,
                    error_description=f"Error en el procesamiento: {str(e)}",
                    processed_date=datetime.utcnow()
                )
                db.add(link_record)
                
                file_record.total_failed = failed_count
                db.commit()
        
        # Actualizar estado final del archivo
        file_record.status = "PROCESSED"
        file_record.total_processed = processed_count
        file_record.total_failed = failed_count
        db.commit()
        
        result_summary = {
            "success": True,
            "file_id": file_id,
            "total_urls": len(urls),
            "processed": processed_count,
            "failed": failed_count,
            "status": "PROCESSED"
        }

        # Publicar en Redis que el procesamiento ha terminado
        publish_processing_complete(file_id, email, result_summary)
        
        logger.info(f"Procesamiento completado para archivo {file_id}: {result_summary}")
        return result_summary
        
    except Exception as e:
        logger.error(f"Error crítico en el procesamiento del archivo {file_id}: {str(e)}")
        
        # Actualizar estado a ERROR en caso de falla crítica
        try:
            file_record = db.query(File).filter(File.id == file_id).first()
            if file_record:
                file_record.status = "ERROR"
                db.commit()
        except:
            pass
            
        return {"success": False, "error": str(e)}
        
    finally:
        db.close()

@app.task
def process_single_url_task(file_id: int, url: str):
    """
    Tarea para procesar una sola URL (puede ser útil para reprocesamiento)
    
    Args:
        file_id (int): ID del archivo asociado
        url (str): URL a procesar
        
    Returns:
        dict: Resultado del procesamiento
    """
    db = SessionLocal()
    try:
        logger.info(f"Procesando URL individual: {url}")
        
        scraper = WebScraper()
        result = scraper.scrape_website(url)
        
        # Procesar la fecha si existe
        post_date = None
        if result.get('date'):
            try:
                date_str = result.get('date')
                # Manejar diferentes formatos de fecha
                if 'T' in date_str:
                    if date_str.endswith('Z'):
                        date_str = date_str.replace('Z', '+00:00')
                    post_date = datetime.fromisoformat(date_str)
                else:
                    # Si no tiene formato ISO, intentar parsearlo como string
                    from dateutil import parser
                    post_date = parser.parse(date_str)
            except Exception as date_error:
                logger.warning(f"Error al parsear fecha '{result.get('date')}': {date_error}")
                post_date = None
        
        # Crear nuevo registro en la tabla links
        link_record = Link(
            file_id=file_id,
            url=url,
            title=result.get('title'),
            post_date=post_date,
            content=result.get('content'),
            page_exists=result.get('page_exists', False),
            success=result.get('success', False),
            error_description=result.get('error') if not result.get('success') else None,
            processed_date=datetime.utcnow()
        )
        
        db.add(link_record)
        db.commit()
        
        return {
            "success": True,
            "url": url,
            "link_id": link_record.id,
            "scraping_success": result.get('success', False)
        }
        
    except Exception as e:
        logger.error(f"Error al procesar URL {url}: {str(e)}")
        return {"success": False, "url": url, "error": str(e)}
        
    finally:
        db.close()
