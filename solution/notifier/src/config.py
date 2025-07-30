import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)

class Config:
    """Configuración del servicio usando variables de entorno"""
    
    # Configuración de Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # Configuración de Resend
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    
    # Configuración del remitente
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')
    FROM_NAME = os.getenv('FROM_NAME', 'Sistema de Web Scraping')
    
    # Configuración de la aplicación
    APP_NAME = os.getenv('APP_NAME', 'Web Scraping Notifier')
    
    def __init__(self):
        """Inicializar configuración y mostrar valores cargados"""
        logger.info("=== CONFIGURACIÓN CARGADA ===")
        logger.info(f"REDIS_HOST: {self.REDIS_HOST}")
        logger.info(f"REDIS_PORT: {self.REDIS_PORT}")
        logger.info(f"REDIS_DB: {self.REDIS_DB}")
        logger.info(f"RESEND_API_KEY: {'***' + (self.RESEND_API_KEY[-4:] if self.RESEND_API_KEY and len(self.RESEND_API_KEY) > 4 else 'NONE')}")
        logger.info(f"FROM_EMAIL: {self.FROM_EMAIL}")
        logger.info(f"FROM_NAME: {self.FROM_NAME}")
        logger.info(f"APP_NAME: {self.APP_NAME}")
        logger.info("============================")
    
    @classmethod
    def validate(cls):
        """Valida que las variables de entorno requeridas estén configuradas"""
        required_vars = [
            'RESEND_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
                
        if missing_vars:
            raise ValueError(f"Variables de entorno requeridas no configuradas: {', '.join(missing_vars)}")
        
        return True
