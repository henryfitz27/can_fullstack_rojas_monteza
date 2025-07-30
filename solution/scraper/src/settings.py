import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configuración de la base de datos PostgreSQL
# Variables de entorno desde docker-compose o .env
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123456789")
POSTGRES_DB = os.getenv("POSTGRES_DB", "links_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Para desarrollo local, usar el puerto expuesto si no es Docker
if not os.getenv('DOCKER_ENV') and POSTGRES_HOST == "localhost":
    # Para desarrollo local, usar el puerto expuesto
    POSTGRES_PORT = "9040"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Configuración CORS
# Permitir orígenes específicos desde variables de entorno
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
# Limpiar espacios en blanco de cada origen
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS]

# Log de la configuración para debugging
logger.info(f"Configuración de base de datos:")
logger.info(f"  - Host: {POSTGRES_HOST}")
logger.info(f"  - Puerto: {POSTGRES_PORT}")
logger.info(f"  - Base de datos: {POSTGRES_DB}")
logger.info(f"  - Usuario: {POSTGRES_USER}")
logger.info(f"  - Entorno Docker: {bool(os.getenv('DOCKER_ENV'))}")
logger.info(f"Configuración CORS:")
logger.info(f"  - Orígenes permitidos: {CORS_ORIGINS}")

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear la clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la clase base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()