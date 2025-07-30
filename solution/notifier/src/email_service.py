import resend
import logging
from jinja2 import Template
from config import Config

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails usando Resend"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        
        # Configurar Resend API Key
        resend.api_key = self.config.RESEND_API_KEY
        
    def send_processing_complete_email(self, data):
        """Envía un email con los resultados del procesamiento"""
        try:
            recipient_email = data['email']
            processing_results = data['processing_results']
            
            # Generar contenido del email
            subject = self._generate_subject(processing_results)
            html_body = self._generate_html_body(data)
            text_body = self._generate_text_body(data)
            
            # Enviar email
            success = self._send_email(
                to_email=recipient_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                logger.info(f"Email enviado exitosamente a {recipient_email} para file_id: {data['file_id']}")
            else:
                logger.error(f"Error enviando email a {recipient_email} para file_id: {data['file_id']}")
                
        except Exception as e:
            logger.error(f"Error en send_processing_complete_email: {e}")
            
    def _generate_subject(self, processing_results):
        """Genera el asunto del email basado en los resultados"""
        status = processing_results.get('status', 'UNKNOWN')
        success = processing_results.get('success', False)
        file_id = processing_results.get('file_id', 'N/A')
        
        if success and status == 'PROCESSED':
            return f"✅ Procesamiento Completado - Archivo #{file_id}"
        else:
            return f"⚠️ Procesamiento con Errores - Archivo #{file_id}"
    
    def _generate_html_body(self, data):
        """Genera el cuerpo HTML del email"""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .content { background-color: #ffffff; padding: 20px; border: 1px solid #dee2e6; border-radius: 5px; }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .error { color: #dc3545; }
        .stats { display: flex; gap: 20px; margin: 15px 0; }
        .stat-item { text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }
        .footer { margin-top: 20px; font-size: 12px; color: #6c757d; }
    </style>
</head>
<body>
    <div class="header">
        <h2>{{ app_name }}</h2>
        <p>Reporte de Procesamiento de Web Scraping</p>
    </div>
    
    <div class="content">
        <h3>Detalles del Procesamiento</h3>
        
        <p><strong>ID del Archivo:</strong> {{ file_id }}</p>
        <p><strong>Estado:</strong> 
            <span class="{% if success %}success{% else %}error{% endif %}">
                {{ status }}
            </span>
        </p>
        <p><strong>Fecha de Procesamiento:</strong> {{ timestamp }}</p>
        
        <div class="stats">
            <div class="stat-item">
                <strong>{{ total_urls }}</strong><br>
                URLs Totales
            </div>
            <div class="stat-item">
                <strong class="success">{{ processed }}</strong><br>
                Procesadas
            </div>
            <div class="stat-item">
                <strong class="error">{{ failed }}</strong><br>
                Fallidas
            </div>
        </div>
        
        {% if success %}
            <p class="success">✅ El procesamiento se completó exitosamente.</p>
        {% else %}
            <p class="warning">⚠️ El procesamiento se completó con algunos errores.</p>
        {% endif %}
        
        <h4>Resumen de Resultados:</h4>
        <ul>
            <li>Total de URLs procesadas: {{ processed }} de {{ total_urls }}</li>
            <li>Tasa de éxito: {{ success_rate }}%</li>
            {% if failed > 0 %}
            <li class="error">URLs que fallaron: {{ failed }}</li>
            {% endif %}
        </ul>
    </div>
    
    <div class="footer">
        <p>Este email fue generado automáticamente por el sistema de Web Scraping.</p>
        <p>Fecha de envío: {{ current_time }}</p>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        # Calcular estadísticas adicionales
        processing_results = data['processing_results']
        total_urls = processing_results.get('total_urls', 0)
        processed = processing_results.get('processed', 0)
        success_rate = round((processed / total_urls * 100), 2) if total_urls > 0 else 0
        
        from datetime import datetime
        
        return template.render(
            app_name=self.config.APP_NAME,
            file_id=data['file_id'],
            success=processing_results.get('success', False),
            status=processing_results.get('status', 'UNKNOWN'),
            timestamp=data['timestamp'],
            total_urls=total_urls,
            processed=processed,
            failed=processing_results.get('failed', 0),
            success_rate=success_rate,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _generate_text_body(self, data):
        """Genera el cuerpo de texto plano del email"""
        processing_results = data['processing_results']
        total_urls = processing_results.get('total_urls', 0)
        processed = processing_results.get('processed', 0)
        failed = processing_results.get('failed', 0)
        success_rate = round((processed / total_urls * 100), 2) if total_urls > 0 else 0
        
        status_emoji = "✅" if processing_results.get('success', False) else "⚠️"
        
        return f"""
{self.config.APP_NAME}
Reporte de Procesamiento de Web Scraping

{status_emoji} DETALLES DEL PROCESAMIENTO {status_emoji}

ID del Archivo: {data['file_id']}
Estado: {processing_results.get('status', 'UNKNOWN')}
Fecha de Procesamiento: {data['timestamp']}

ESTADÍSTICAS:
- URLs Totales: {total_urls}
- URLs Procesadas: {processed}
- URLs Fallidas: {failed}
- Tasa de éxito: {success_rate}%

RESUMEN:
El procesamiento {'se completó exitosamente' if processing_results.get('success', False) else 'se completó con algunos errores'}.

---
Este email fue generado automáticamente por el sistema de Web Scraping.
        """.strip()
    
    def _send_email(self, to_email, subject, html_body, text_body):
        """Envía el email usando Resend"""
        try:
            logger.info(f"Preparando envío de email a: {to_email}")
            logger.info(f"FROM_EMAIL configurado: {self.config.FROM_EMAIL}")
            logger.info(f"FROM_NAME configurado: {self.config.FROM_NAME}")
            logger.info(f"API Key presente: {'Sí' if self.config.RESEND_API_KEY else 'No'}")
            
            # Verificar que la API key esté configurada
            if not self.config.RESEND_API_KEY:
                logger.error("RESEND_API_KEY no está configurada")
                return False
            
            # Enviar email con Resend - versión completa con HTML
            email_data = {
                "from": f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": html_body,
                "text": text_body
            }
            
            logger.info(f"Enviando email con contenido HTML y texto completo")
            logger.info(f"Destinatario: {to_email}")
            logger.info(f"Asunto: {subject}")
            
            r = resend.Emails.send(email_data)
            
            logger.info(f"Respuesta de Resend: {r}")
            logger.info(f"Email enviado exitosamente con Resend. ID: {r.get('id', 'N/A')}")
            return True
            
        except resend.exceptions.ResendError as e:
            logger.error(f"Error específico de Resend: {e}")
            logger.error(f"Código de error: {getattr(e, 'code', 'N/A')}")
            logger.error(f"Mensaje de error: {getattr(e, 'message', 'N/A')}")
            logger.error(f"Tipo de error: {getattr(e, 'error_type', 'N/A')}")
            return False
        except Exception as e:
            logger.error(f"Error enviando email con Resend: {e}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Detalles del error: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False
