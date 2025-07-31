import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import requests

from src.apps.scraper import WebScraper


class TestWebScraper:
    """Tests para la clase WebScraper"""
        
    @patch('src.apps.scraper.requests.Session.get')
    def test_scrape_website_success(self, mock_get):
        """Test para un scraping exitoso"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <time datetime="2024-01-01T12:00:00Z">Enero 1, 2024</time>
                <p>Esta es una prueba</p>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        scraper = WebScraper()
        result = scraper.scrape_website("https://example.com/test")
        
        assert result['success'] is True
        assert result['url'] == "https://example.com/test"
        assert result['status_code'] == 200
        assert result['title'] == "Test Page"
        assert result['page_exists'] is True
        assert result['error'] is None
        assert 'content' in result
        assert 'meta_description' in result
        
        mock_get.assert_called_once_with("https://example.com/test", timeout=30)
    
    
    @patch('src.apps.scraper.requests.Session.get')
    def test_scrape_website_page_not_found(self, mock_get):
        """Test para detectar páginas que no existen"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = """
        <html>
            <head><title>Error</title></head>
            <body>
                <h1>Recurso no encontrado</h1>
                <p>La pagina que buscas no existe.</p>
            </body>
        </html>
        """.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        scraper = WebScraper()
        result = scraper.scrape_website("https://example.com/test")
        
        assert result['success'] is False
        assert result['page_exists'] is False
        assert "Recurso no encontrado" in result['error']
    
    def test_get_title_with_title_tag(self):
        """Test para extraer título cuando existe tag title"""
        from bs4 import BeautifulSoup
        
        html = "<html><head><title>  Test Title  </title></head></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        scraper = WebScraper()
        title = scraper._get_title(soup)
        
        assert title == "Test Title"
    
    def test_get_title_without_title_tag(self):
        """Test para extraer título cuando no existe tag title"""
        from bs4 import BeautifulSoup
        
        html = "<html><head></head><body><h1>Header</h1></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        scraper = WebScraper()
        title = scraper._get_title(soup)
        
        assert title is None
    
    def test_get_date_with_time_tag(self):
        """Test para extraer fecha cuando existe tag time con datetime"""
        from bs4 import BeautifulSoup
        
        html = '<html><body><time datetime="2024-01-01T12:00:00Z">Jan 1, 2024</time></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        scraper = WebScraper()
        date = scraper._get_date(soup)
        
        assert date == "2024-01-01T12:00:00Z"
    
    def test_get_date_without_time_tag(self):
        """Test para extraer fecha cuando no existe tag time"""
        from bs4 import BeautifulSoup
        
        html = "<html><body><p>Some content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        scraper = WebScraper()
        date = scraper._get_date(soup)
        
        assert date is None
    
    def test_get_meta_description(self):
        """Test para extraer meta description"""
        from bs4 import BeautifulSoup
        
        html = '<html><head><meta name="description" content="Test description"></head></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        scraper = WebScraper()
        description = scraper._get_meta_description(soup)
        
        assert description == "Test description"
    
    def test_get_content_extraction(self):
        """Test para extraer contenido del body"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <div class="article-content">
                    <h1>Title</h1>
                    <p>First paragraph</p>
                    <p>Second paragraph</p>
                </div>
                <script>console.log('test');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        scraper = WebScraper()
        content = scraper._get_content(soup)
        
        assert content == "First paragraph"  # La función retorna el primer párrafo
    
    def test_get_content_no_article_div(self):
        """Test para extraer contenido cuando no existe article-content"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <h1>Title</h1>
                <p>First paragraph</p>
                <p>Second paragraph</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        scraper = WebScraper()
        content = scraper._get_content(soup)
        
        assert content is None  # Debería retornar None si no hay div article-content
