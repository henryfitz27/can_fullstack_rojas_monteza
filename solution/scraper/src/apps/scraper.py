import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """
    Clase para realizar web scraping utilizando BeautifulSoup4
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        # Headers básicos para simular un navegador
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Función principal para realizar scraping de una página web
        
        Args:
            url (str): URL de la página web a scrapear
            
        Returns:
            Dict[str, Any]: Diccionario con los datos extraídos y metadatos
        """
        try:
            logger.info(f"Iniciando scraping de: {url}")
            
            # Realizar la petición HTTP
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parsear el HTML con BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Verificar si la página existe (no contiene "Recurso no encontrado")
            page_exists, error_message = self._check_page_exists(soup)
            if not page_exists:
                logger.error(f"La página {url} no existe: {error_message}")
                return self._create_error_response(url, error_message)
            
            # Estructura básica de datos a retornar
            scraped_data = {
                "url": url,
                "status_code": response.status_code,
                "title": self._get_title(soup),
                "date": self._get_date(soup),
                "content": self._get_content(soup),
                "meta_description": self._get_meta_description(soup),
                "content_length": len(response.content),
                "html_content": str(soup),  # HTML completo para análisis posterior
                "page_exists": True,  # Agregamos este campo para confirmar que la página existe
                "success": True,
                "error": None
            }
            
            logger.info(f"Scraping completado exitosamente para: {url}")
            return scraped_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al acceder a {url}: {str(e)}")
            return self._create_error_response(url, f"Error de red: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error inesperado al procesar {url}: {str(e)}")
            return self._create_error_response(url, f"Error inesperado: {str(e)}")
    
    def _get_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el título de la página"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else None
    
    def _get_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae la fecha de la página buscando elementos <time> con atributo datetime
        
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup del HTML parseado
            
        Returns:
            Optional[str]: Fecha encontrada en formato datetime, o None si no se encuentra
        """
        # Buscar el primer elemento <time> que tenga el atributo datetime
        time_tag = soup.find('time', attrs={'datetime': True})
        
        if time_tag and time_tag.get('datetime'):
            datetime_value = time_tag['datetime'].strip()
            logger.info(f"Fecha encontrada: {datetime_value}")
            return datetime_value
        
        # Si no se encuentra, retornar None
        logger.warning("No se encontró ningún elemento <time> con atributo datetime")
        return None
    
    def _get_content(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extrae el contenido del primer <p> que se encuentra después de <div class="article-content">
        
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup del HTML parseado
            
        Returns:
            Optional[str]: Contenido del primer párrafo encontrado, o None si no se encuentra
        """
        # Buscar el div con clase "article-content"
        article_content_div = soup.find('div', class_='article-content')
        
        if not article_content_div:
            logger.warning("No se encontró el div con clase 'article-content'")
            return None
        
        # Buscar el primer elemento <p> dentro del div article-content
        first_paragraph = article_content_div.find('p')
        
        if first_paragraph:
            content = first_paragraph.get_text(strip=True)
            logger.info(f"Contenido extraído: {content[:100]}...")  # Log de los primeros 100 caracteres
            return content
        else:
            logger.warning("No se encontró ningún párrafo <p> dentro del div 'article-content'")
            return None
    
    def _get_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la meta descripción de la página"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content') if meta_desc else None
    
    def _check_page_exists(self, soup: BeautifulSoup) -> tuple[bool, Optional[str]]:
        """
        Verifica si la página existe buscando el texto 'Recurso no encontrado'
        
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup del HTML parseado
            
        Returns:
            tuple[bool, Optional[str]]: (página_existe, mensaje_error)
                - True si la página existe (no se encontró el texto de error)
                - False si no existe (se encontró "Recurso no encontrado")
                - mensaje_error será None si existe, o descripción del error si no existe
        """
        # Extraer todo el texto de la página para buscar el mensaje de error
        page_text = soup.get_text().strip()
        
        # Buscar el texto de error (case insensitive)
        error_text = "Recurso no encontrado"
        if error_text.lower() in page_text.lower():
            logger.warning(f"Página no encontrada - se detectó el texto: '{error_text}'")
            return False, f"La página no existe - se encontró el mensaje: '{error_text}'"
        
        # Si no se encuentra el texto de error, la página existe
        return True, None
    
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extrae todo el texto visible de la página"""
        # Remover scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(strip=True, separator=' ')
    
    def _create_error_response(self, url: str, error_message: str) -> Dict[str, Any]:
        """Crea una respuesta de error estandarizada"""
        return {
            "url": url,
            "status_code": None,
            "title": None,
            "date": None,
            "content": None,
            "meta_description": None,
            "content_length": 0,
            "html_content": None,
            "page_exists": False,  # En caso de error, asumimos que la página no existe o no es válida
            "success": False,
            "error": error_message
        }

# Función de conveniencia para usar directamente
def scrape_url(url: str) -> Dict[str, Any]:
    """
    Función de conveniencia para realizar scraping de una URL
    
    Args:
        url (str): URL a scrapear
        
    Returns:
        Dict[str, Any]: Datos extraídos de la página
    """
    scraper = WebScraper()
    return scraper.scrape_website(url)
