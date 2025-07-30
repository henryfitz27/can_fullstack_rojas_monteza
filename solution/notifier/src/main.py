import redis
import json
import logging
import os
import sys
from email_service import EmailService
from config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedisSubscriber:
    def __init__(self):
        self.config = Config()
        self.redis_client = redis.Redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            db=self.config.REDIS_DB,
            password=self.config.REDIS_PASSWORD,
            decode_responses=True
        )
        self.email_service = EmailService()
        
    def start_listening(self):
        """Inicia la escucha de mensajes en el canal processing_complete"""
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe('processing_complete')
            
            logger.info("Iniciando escucha en canal 'processing_complete'...")
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        self.process_message(message['data'])
                    except Exception as e:
                        logger.error(f"Error procesando mensaje: {e}")
                        
        except Exception as e:
            logger.error(f"Error conectando a Redis: {e}")
            sys.exit(1)
            
    def process_message(self, message_data):
        """Procesa un mensaje recibido del canal Redis"""
        try:
            # Parsear el JSON del mensaje
            data = json.loads(message_data)
            
            logger.info(f"Mensaje recibido para file_id: {data.get('file_id')}")
            
            # Validar estructura del mensaje
            required_fields = ['file_id', 'email', 'processing_results', 'timestamp']
            if not all(field in data for field in required_fields):
                logger.error("Mensaje no tiene todos los campos requeridos")
                return
                
            # Enviar email
            self.email_service.send_processing_complete_email(data)
            
        except json.JSONDecodeError:
            logger.error("Error decodificando JSON del mensaje")
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")

def main():
    """Función principal"""
    logger.info("Iniciando servicio de notificaciones por email...")
    
    subscriber = RedisSubscriber()
    
    try:
        subscriber.start_listening()
    except KeyboardInterrupt:
        logger.info("Servicio detenido por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
