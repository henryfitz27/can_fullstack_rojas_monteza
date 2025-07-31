import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException

from src.main import app


class TestMainAPI:
    """Tests para los endpoints de la API principal"""
    
    def test_process_file_success(self, client, sample_file_record, temp_file):
        """Test para procesar un archivo exitosamente"""
        # Actualizar el archivo con la ruta temporal real
        sample_file_record.file_path = temp_file
        
        with patch('src.main.process_file_task') as mock_task:
            # Mock de la tarea de Celery
            mock_task.delay.return_value = Mock(id="test-task-123")
            
            response = client.post("/process", json={
                "file_id": sample_file_record.id,
                "email": "test@example.com"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Procesamiento iniciado"
            assert data["file_id"] == sample_file_record.id
            assert data["task_id"] == "test-task-123"
            assert data["status"] == "QUEUED"
            
            # Verificar que se llamó la tarea
            mock_task.delay.assert_called_once_with(
                sample_file_record.id,
                "test@example.com"
            )
    
    def test_process_file_not_found(self, client):
        """Test para procesar un archivo que no existe"""
        response = client.post("/process", json={
            "file_id": 9999,
            "email": "test@example.com"
        })
        
        assert response.status_code == 404
        data = response.json()
        assert "No se encontró el archivo" in data["detail"]
    
    def test_process_file_already_processing(self, client, sample_file_record, temp_file):
        """Test para procesar un archivo que ya está siendo procesado"""
        # Configurar el archivo como en procesamiento
        sample_file_record.status = "PROCESSING"
        sample_file_record.file_path = temp_file
        
        response = client.post("/process", json={
            "file_id": sample_file_record.id,
            "email": "test@example.com"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "ya está siendo procesado" in data["detail"]
    
    def test_process_file_path_not_exists(self, client, sample_file_record):
        """Test para procesar un archivo cuya ruta no existe"""
        # El archivo en la DB tiene una ruta que no existe
        sample_file_record.file_path = "/path/that/does/not/exist.txt"
        
        response = client.post("/process", json={
            "file_id": sample_file_record.id,
            "email": "test@example.com"
        })
        
        assert response.status_code == 404
        data = response.json()
        assert "El archivo no existe en la ruta especificada" in data["detail"]
    
    def test_process_file_invalid_request_data(self, client):
        """Test para request con datos inválidos"""
        response = client.post("/process", json={
            "file_id": "invalid",  # Debe ser entero
            "email": "test@example.com"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_process_file_missing_email(self, client):
        """Test para request sin email"""
        response = client.post("/process", json={
            "file_id": 1
            # falta email
        })
        
        assert response.status_code == 422  # Validation error
    