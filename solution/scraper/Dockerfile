FROM python:3.10-slim

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar solo el código fuente necesario
COPY src/ ./src/

# Exponer el puerto
EXPOSE 8000

# Variables de entorno por defecto (pueden ser sobrescritas)
ENV DOCKER_ENV=true
ENV PYTHONPATH=/app

# Comando por defecto (con --reload para desarrollo)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]