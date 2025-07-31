import pytest
import os
import tempfile
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.settings import Base, get_db
from src.main import app
from src.models import File, Link

# Configuración de base de datos de pruebas en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Fixture que crea una base de datos SQLite en memoria para las pruebas"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    
    # Habilitar foreign keys en SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Fixture que proporciona un cliente de pruebas para FastAPI"""
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock de Redis para las pruebas"""
    with patch('src.tasks.redis') as mock:
        yield mock


@pytest.fixture
def sample_file_record(test_db):
    """Fixture que crea un registro de archivo de ejemplo"""
    file_record = File(
        id=1,
        total_links=3,
        file_path="/tmp/test_file.txt",
        file_name="test_file.txt",
        total_processed=0,
        total_failed=0,
        status="PENDING",
        uploaded_at=datetime.now(),
        user_id=1
    )
    test_db.add(file_record)
    test_db.commit()
    test_db.refresh(file_record)
    return file_record


@pytest.fixture
def sample_links(test_db, sample_file_record):
    """Fixture que crea registros de links de ejemplo"""
    links = [
        Link(
            file_id=sample_file_record.id,
            url="https://example.com/page1",
            title="Test Page 1",
            page_exists=True,
            success=False
        ),
        Link(
            file_id=sample_file_record.id,
            url="https://example.com/page2",
            title="Test Page 2",
            page_exists=True,
            success=False
        ),
        Link(
            file_id=sample_file_record.id,
            url="https://example.com/page3",
            title="Test Page 3",
            page_exists=True,
            success=False
        )
    ]
    
    for link in links:
        test_db.add(link)
    test_db.commit()
    
    for link in links:
        test_db.refresh(link)
    
    return links


@pytest.fixture
def temp_file():
    """Fixture que crea un archivo temporal para las pruebas"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("https://example.com/page1\n")
        f.write("https://example.com/page2\n")
        f.write("https://example.com/page3\n")
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def mock_scraper():
    """Mock del WebScraper para las pruebas"""
    with patch('src.apps.scraper.WebScraper') as mock:
        scraper_instance = Mock()
        scraper_instance.scrape_website.return_value = {
            "url": "https://example.com/test",
            "status_code": 200,
            "title": "Test Page",
            "date": "2024-01-01T12:00:00Z",
            "content": "Test content",
            "meta_description": "Test description",
            "content_length": 1000,
            "html_content": "<html><body>Test</body></html>",
            "page_exists": True,
            "success": True,
            "error": None
        }
        mock.return_value = scraper_instance
        yield scraper_instance
