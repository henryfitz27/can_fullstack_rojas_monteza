import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.models import File, Link


class TestModels:
    """Tests para los modelos de SQLAlchemy"""
    
    def test_link_model_creation(self, test_db, sample_file_record):
        """Test para crear un modelo Link"""
        link = Link(
            file_id=sample_file_record.id,
            url="https://example.com/test",
            title="Test Title",
            page_exists=True,
            success=False
        )
        
        test_db.add(link)
        test_db.commit()
        test_db.refresh(link)
        
        assert link.id is not None
        assert link.file_id == sample_file_record.id
        assert link.url == "https://example.com/test"
        assert link.title == "Test Title"
        assert link.page_exists is True
        assert link.success is False
    
