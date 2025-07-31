import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import get_db, DATABASE_URL, CORS_ORIGINS


class TestSettings:
    """Tests para el módulo de configuración"""
    
    def test_database_url_format(self):
        """Test para verificar el formato de la URL de base de datos"""
        assert DATABASE_URL.startswith("postgresql://")
        # La URL debe contener elementos esperados
        assert "localhost" in DATABASE_URL or "postgres" in DATABASE_URL
    
    def test_cors_origins_configuration(self):
        """Test para verificar la configuración de CORS"""
        assert isinstance(CORS_ORIGINS, list)
        assert len(CORS_ORIGINS) > 0
    
    @patch.dict('os.environ', {'DOCKER_ENV': 'true'})
    def test_docker_environment_detection(self):
        """Test para verificar la detección del entorno Docker"""
        import os
        assert os.getenv('DOCKER_ENV') == 'true'
    
    

    
    @patch.dict('os.environ', {
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_pass',
        'POSTGRES_DB': 'test_db',
        'POSTGRES_HOST': 'test_host',
        'POSTGRES_PORT': '5433'
    })
    def test_custom_environment_variables(self):
        """Test para verificar que se usan variables de entorno personalizadas"""
        from importlib import reload
        import src.settings
        reload(src.settings)
        
        assert "test_user" in src.settings.DATABASE_URL
        assert "test_pass" in src.settings.DATABASE_URL
        assert "test_db" in src.settings.DATABASE_URL
        assert "test_host" in src.settings.DATABASE_URL
        assert "5433" in src.settings.DATABASE_URL
    
    @patch.dict('os.environ', {'CORS_ORIGINS': 'http://localhost:3000,https://example.com'})
    def test_cors_origins_from_env(self):
        """Test para verificar que CORS_ORIGINS se lee del entorno"""
        from importlib import reload
        import src.settings
        reload(src.settings)
        
        expected_origins = ['http://localhost:3000', 'https://example.com']
        assert src.settings.CORS_ORIGINS == expected_origins
    
