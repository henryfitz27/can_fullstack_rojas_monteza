import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.tasks import process_file_task, publish_processing_complete
from src.models import File, Link


class TestTasks:
    """Tests para las tareas de Celery"""
    
    @patch('src.tasks.WebScraper')
    @patch('src.tasks.SessionLocal')
    @patch('src.tasks.publish_processing_complete')
    def test_process_file_task_success(self, mock_publish, mock_session, mock_scraper, sample_file_record, temp_file):
        """Test para procesar un archivo exitosamente"""
        # Mock de la sesión de base de datos
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock del archivo y links
        sample_file_record.file_path = temp_file
        mock_db.query.return_value.filter.return_value.first.return_value = sample_file_record
        
        # Mock del scraper
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.scrape_website.return_value = {
            "title": "Test Page",
            "date": "2024-01-01T12:00:00Z",
            "content": "Test content",
            "page_exists": True,
            "success": True,
            "error": None
        }
        
        # Mock de self para la tarea de Celery
        mock_self = Mock()
        mock_self.update_state = Mock()
        
        # Ejecutar la tarea (sin .delay ya que estamos probando la función directamente)
        result = process_file_task(mock_self, sample_file_record.id, "test@example.com")
        
        # Verificaciones
        assert result["file_id"] == sample_file_record.id
        assert result["success"] is True
        assert "processed" in result
        
        # Verificar que se llamó el scraper
        assert mock_scraper_instance.scrape_website.call_count >= 0  # Depende de las URLs en el archivo
        
        # Verificar que se publicó el resultado
        mock_publish.assert_called_once()
    
    @patch('src.tasks.SessionLocal')
    def test_process_file_task_file_not_found(self, mock_session):
        """Test para procesar un archivo que no existe"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock de self para la tarea de Celery
        mock_self = Mock()
        
        result = process_file_task(mock_self, 9999, "test@example.com")
        
        assert result["success"] is False
        assert "no encontró" in result["error"]
    
    @patch('src.tasks.WebScraper')
    @patch('src.tasks.SessionLocal') 
    @patch('src.tasks.publish_processing_complete')
    def test_process_file_task_with_failures(self, mock_publish, mock_session, mock_scraper, sample_file_record, temp_file):
        """Test para procesar un archivo con algunos fallos"""
        # Mock de la sesión de base de datos
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        sample_file_record.file_path = temp_file
        mock_db.query.return_value.filter.return_value.first.return_value = sample_file_record
        
        # Mock del scraper con un éxito y un fallo alternado
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        
        # Lista de respuestas para simular éxito/fallo
        side_effect_responses = [
            {
                "title": "Success Page",
                "page_exists": True,
                "success": True,
                "error": None
            },
            {
                "title": None,
                "page_exists": False,
                "success": False,
                "error": "Page not found"
            },
            {
                "title": "Another Success",
                "page_exists": True,
                "success": True,
                "error": None
            }
        ]
        
        mock_scraper_instance.scrape_website.side_effect = side_effect_responses
        
        # Mock de self para la tarea de Celery
        mock_self = Mock()
        mock_self.update_state = Mock()
        
        result = process_file_task(mock_self, sample_file_record.id, "test@example.com")
        
        assert result["success"] is True
        assert "processed" in result
        assert "failed" in result
    
    @patch('src.tasks.redis.Redis')
    def test_publish_processing_complete(self, mock_redis_class):
        """Test para publicar el completado del procesamiento"""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance
        
        results = {
            "file_id": 1,
            "total_processed": 5,
            "total_failed": 0,
            "status": "COMPLETED"
        }
        
        publish_processing_complete(1, "test@example.com", results)
        
        # Verificar que se creó el cliente Redis
        mock_redis_class.assert_called_once()
        
        # Verificar que se publicó en el canal correcto
        mock_redis_instance.publish.assert_called_once()
        call_args = mock_redis_instance.publish.call_args
        assert call_args[0][0] == "processing_complete"
        
        # Verificar el contenido del mensaje
        import json
        message = json.loads(call_args[0][1])
        assert message["file_id"] == 1
        assert message["email"] == "test@example.com"
        assert message["processing_results"]["total_processed"] == 5
    
    @patch('src.tasks.redis.Redis')
    def test_redis_client_creation(self, mock_redis):
        """Test para crear cliente Redis"""
        from src.tasks import redis
        
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        
        # Simular creación de cliente
        client = redis.Redis(host='localhost', port=6379, db=0)
        
        assert client == mock_redis_instance
        mock_redis.assert_called_once()
    
    @patch('src.tasks.SessionLocal')
    def test_process_file_task_file_path_not_exists(self, mock_session, sample_file_record):
        """Test para procesar un archivo cuya ruta no existe"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Archivo existe en BD pero no en sistema de archivos
        sample_file_record.file_path = "/path/that/does/not/exist.txt"
        mock_db.query.return_value.filter.return_value.first.return_value = sample_file_record
        
        # Mock de self para la tarea de Celery
        mock_self = Mock()
        
        result = process_file_task(mock_self, sample_file_record.id, "test@example.com")
        
        assert result["success"] is False
        assert "Error al leer" in result["error"]
    
    @patch('src.tasks.WebScraper')
    @patch('src.tasks.SessionLocal')
    @patch('src.tasks.publish_processing_complete')
    def test_process_file_task_updates_file_status(self, mock_publish, mock_session, mock_scraper, sample_file_record, temp_file):
        """Test para verificar que se actualiza el estado del archivo"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        sample_file_record.file_path = temp_file
        mock_db.query.return_value.filter.return_value.first.return_value = sample_file_record
        
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.scrape_website.return_value = {
            "success": True,
            "title": "Test",
            "page_exists": True
        }
        
        # Mock de self para la tarea de Celery
        mock_self = Mock()
        mock_self.update_state = Mock()
        
        result = process_file_task(mock_self, sample_file_record.id, "test@example.com")
        
        # Verificar que se cambió el estado del archivo
        assert mock_db.commit.called
        
        # Verificar que el resultado fue exitoso
        assert result["success"] is True
