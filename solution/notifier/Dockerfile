# Usar imagen base de Python 3.11 slim
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Establecer variables de entorno
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Comando por defecto
CMD ["python", "src/main.py"]

# Metadata
LABEL maintainer="tu-email@ejemplo.com"
LABEL description="Servicio de notificaciones por email para Web Scraping"
LABEL version="1.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}, db=${REDIS_DB}, password='${REDIS_PASSWORD}'); r.ping()" || exit 1
