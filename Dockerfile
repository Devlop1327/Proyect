# 1. Imagen base oficial de Python
FROM python:3.12-slim

# 2. Evitar buffering de logs y bytecode
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Instalar herramientas del sistema y Node.js (requerido por Reflex)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Directorio de trabajo en el contenedor
WORKDIR /app

# 5. Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copiar el código fuente del proyecto
COPY . .

# 7. Inicializar y compilar Reflex en modo producción
RUN reflex init
RUN reflex export --frontend-only || true

# 8. Exponer puertos de Frontend (3000) y Backend (8000)
EXPOSE 3000
EXPOSE 8000

# 9. Comando de arranque de la aplicación
CMD ["reflex", "run", "--env", "prod"]

