# Servicio de Notificaciones por Email

Este servicio se encarga de escuchar notificaciones de Redis y enviar emails con los resultados del procesamiento de Web Scraping.

## Estructura del Proyecto

```
notifier/
├── src/
│   ├── main.py              # Punto de entrada principal
│   ├── config.py            # Configuración y variables de entorno
│   └── email_service.py     # Servicio de envío de emails
├── requirements.txt         # Dependencias de Python
├── Dockerfile              # Imagen de Docker
├── .env.example            # Ejemplo de variables de entorno
└── README.md               # Este archivo
```

## Configuración

### Variables de Entorno Requeridas

Copia `.env.example` a `.env` y configura las siguientes variables:

```bash
# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Resend (servicio de email)
RESEND_API_KEY=re_FJmkbp1C_HWWaXUvEBTQ7G1VxSjtAT2YG

# Remitente
FROM_EMAIL=onboarding@resend.dev
FROM_NAME=Sistema de Web Scraping

# Aplicación
APP_NAME=Web Scraping Notifier
```

### Configuración de Resend

Para usar Resend como servicio de email:

1. Registrate en [resend.com](https://resend.com)
2. Crea una API Key en tu dashboard
3. Usa esa API Key en `RESEND_API_KEY`
4. Configura tu dominio verificado en `FROM_EMAIL` (o usa el dominio de prueba `onboarding@resend.dev`)

## Estructura del Mensaje de Redis

El servicio escucha mensajes en el canal `processing_complete` con esta estructura:

```json
{
  "file_id": 123,
  "email": "usuario@ejemplo.com",
  "processing_results": {
    "success": true,
    "file_id": 123,
    "total_urls": 100,
    "processed": 95,
    "failed": 5,
    "status": "PROCESSED"
  },
  "timestamp": "2025-07-30T10:30:45.123456"
}
```

## Desarrollo Local

### Con Python Virtual Environment

```bash
# Crear virtual environment
python -m venv venv

# Activar (Windows)
venv\Scripts\activate
# Activar (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar el servicio
python src/main.py
```

### Con Docker

```bash
# Construir la imagen
docker build -t notifier-service .

# Ejecutar el contenedor
docker run --env-file .env notifier-service
```

## Uso en Docker Compose

Ejemplo de configuración en `docker-compose.yml`:

```yaml
version: '3.8'

services:
  notifier:
    build: ./notifier
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
      - RESEND_API_KEY=${RESEND_API_KEY}
      - FROM_EMAIL=${FROM_EMAIL}
      - FROM_NAME=Sistema de Web Scraping
      - APP_NAME=Web Scraping Notifier
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

## Características

- ✅ Suscripción a canal Redis `processing_complete`
- ✅ Envío de emails HTML y texto plano
- ✅ Plantillas de email personalizables
- ✅ Validación de configuración
- ✅ Logging detallado
- ✅ Health check en Docker
- ✅ Usuario no-root en contenedor
- ✅ Manejo de errores robusto

## Logs

El servicio genera logs detallados con información sobre:

- Conexión a Redis
- Mensajes recibidos
- Emails enviados
- Errores y excepciones

Los logs se muestran en formato:
```
2025-07-30 10:30:45 - INFO - Mensaje recibido para file_id: 123
2025-07-30 10:30:46 - INFO - Email enviado exitosamente a usuario@ejemplo.com para file_id: 123
```

## Problemas Comunes

### Error de conexión a Redis
- Verificar que Redis esté ejecutándose
- Verificar la configuración de `REDIS_HOST` y `REDIS_PORT`
- Verificar credenciales si Redis requiere autenticación

### Error enviando emails
- Verificar configuración de Resend API Key
- Verificar que el dominio en `FROM_EMAIL` esté verificado en Resend
- Para pruebas puedes usar `onboarding@resend.dev` como `FROM_EMAIL`

### Mensajes no procesados
- Verificar que los mensajes tengan la estructura JSON correcta
- Verificar logs para errores de parsing
- Verificar que el canal Redis sea exactamente `processing_complete`
