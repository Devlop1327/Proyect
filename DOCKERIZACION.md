# 🐳 Guía Definitiva de Dockerización - Sistema PQRS (Reflex)

Esta guía contiene la información puntual, clara y paso a paso para dockerizar y desplegar la aplicación del Sistema PQRS construida con **Reflex (Python + Next.js)**.

---

## 📑 Índice
1. [Arquitectura y Puertos de la Aplicación](#1-arquitectura-y-puertos-de-la-aplicación)
2. [Estructura de Archivos Necesarios](#2-estructura-de-archivos-necesarios)
3. [Creación de Archivos de Configuración](#3-creación-de-archivos-de-configuración)
   - `.dockerignore`
   - `Dockerfile`
   - `docker-compose.yml`
4. [Paso a Paso para Compilar y Ejecutar](#4-paso-a-paso-para-compilar-y-ejecutar)
5. [Comandos de Mantenimiento y Verificación](#5-comandos-de-mantenimiento-y-verificación)
6. [Persistencia de Datos y Archivos](#6-persistencia-de-datos-y-archivos)
7. [Solución de Problemas Frecuentes](#7-solución-de-problemas-frecuentes)

---

## 1. Arquitectura y Puertos de la Aplicación

Reflex funciona internamente con dos capas en el mismo contenedor o coordinadas:
- **Frontend (Next.js):** Puerto `3000` (Interfaz de usuario para los navegadores).
- **Backend (FastAPI / WebSockets):** Puerto `8000` (API REST, gestión de eventos reactivos y base de datos).

Para entornos Docker, ambos puertos deben exponerse y mapearse.

---

## 2. Estructura de Archivos Necesarios

En la raíz del proyecto (`D:\PQ\Proyect`), se agregan/verifican los siguientes 3 archivos:

```text
Proyect/
│
├── Dockerfile              # Instrucciones de compilación y empaquetado de la imagen
├── docker-compose.yml      # Orquestador simplificado con volúmenes y puertos
├── .dockerignore           # Excluye cachés, entornos locales y archivos pesados
├── requirements.txt        # Dependencias de Python
├── rxconfig.py             # Configuración del framework Reflex
└── ... (código fuente)
```

---

## 3. Creación de Archivos de Configuración

### 📄 Archivo 1: `.dockerignore`
Evita que se copien entornos locales de Windows, node_modules o temporales innecesarios al contenedor:

```text
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.web/
node_modules/
.git/
.gitignore
.env
*.log
```

---

### 📄 Archivo 2: `Dockerfile`
Utiliza una imagen ligera de Python y descarga Node.js (necesario por Reflex para compilar el frontend):

```dockerfile
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
```

---

### 📄 Archivo 3: `docker-compose.yml`
Permite levantar la aplicación completa con un solo comando y mantener los datos (base de datos SQLite y archivos adjuntos) persistentes en el disco de tu máquina.

```yaml
version: '3.8'

services:
  pqrs-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sistema_pqrs_app
    restart: unless-stopped
    ports:
      - "3000:3000"   # Frontend
      - "8000:8000"   # Backend API
    environment:
      - API_URL=http://localhost:8000
      - DATABASE_URL=sqlite:////app/reflex.db
    volumes:
      # Persistencia de la base de datos y archivos subidos
      - ./reflex.db:/app/reflex.db
      - ./uploaded_files:/app/uploaded_files
      - ./.web/public/uploads:/app/.web/public/uploads
```

---

## 4. Paso a Paso para Compilar y Ejecutar

### Paso 1: Abrir la terminal en la raíz del proyecto
Asegúrate de estar en el directorio principal:
```bash
cd D:\PQ\Proyect
```

### Paso 2: Construir la imagen de Docker
Descarga las dependencias y empaqueta la aplicación:
```bash
docker compose build
```

### Paso 3: Iniciar el contenedor
Levanta el servicio en segundo plano:
```bash
docker compose up -d
```

### Paso 4: Abrir la aplicación en el navegador
- **Portal Ciudadano / Login:** [http://localhost:3000](http://localhost:3000)
- **API / Documentación Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Comandos de Mantenimiento y Verificación

| Acción | Comando |
|---|---|
| **Ver logs en tiempo real** | `docker compose logs -f` |
| **Detener la aplicación** | `docker compose down` |
| **Reiniciar la aplicación** | `docker compose restart` |
| **Ver estado del contenedor** | `docker ps` |
| **Entrar a la terminal del contenedor** | `docker exec -it sistema_pqrs_app bash` |

---

## 6. Persistencia de Datos y Archivos

Gracias a la sección `volumes` del archivo `docker-compose.yml`:
1. **Base de Datos SQLite (`reflex.db`):** Todas las solicitudes creadas, historiales y usuarios creados se conservan en tu máquina aunque apagues o borres el contenedor.
2. **Archivos Adjuntos (`uploaded_files/`):** Todos los documentos y evidencias adjuntadas por los ciudadanos se mantendrán guardados en tu carpeta local.

---

## 7. Solución de Problemas Frecuentes

- **Problema: Puerto 3000 u 8000 ocupado.**
  - *Causa:* Tienes una instancia local de Reflex ejecutándose en tu computadora.
  - *Solución:* Detén el proceso local de Reflex en tu terminal antes de ejecutar `docker compose up -d`.
- **Problema: Cambios en el código no se reflejan.**
  - *Solución:* Vuelve a compilar la imagen ejecutando `docker compose build --no-cache` y luego `docker compose up -d`.

