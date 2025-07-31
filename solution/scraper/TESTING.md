# Guía de Testing para el Proyecto Scraper

## Estructura de Tests

El proyecto incluye tests unitarios para los componentes principales:

### Archivos de Test

- `tests/test_models.py` - Tests para los modelos SQLAlchemy (File, Link)
- `tests/test_scraper.py` - Tests para la funcionalidad de web scraping
- `tests/test_main.py` - Tests para los endpoints de la API FastAPI
- `tests/test_tasks.py` - Tests para las tareas de Celery
- `tests/test_settings.py` - Tests para la configuración del proyecto
- `tests/conftest.py` - Fixtures y configuración compartida

# Instalar dependencias de testing
pip install -r requirements-test.txt

# Ejecutar tests principales
pytest tests/test_models.py tests/test_scraper.py tests/test_settings.py -v

