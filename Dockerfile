# ==========================================================
# 🏛️ LexMonitor Yucatán — Dockerfile Multi-Stage para Render
# ==========================================================

# Etapa 1: Compilación del Frontend (React + esbuild)
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci || npm install
COPY src/ ./src/
COPY public/ ./public/
RUN npm run build

# Etapa 2: Runtime del Servidor Python
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Merida \
    PORT=5000

# Instalar dependencias del sistema para psycopg2 y zona horaria
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar backend y archivos del proyecto
COPY backend/ ./backend/
COPY database.py .
COPY server.py .

# Copiar assets estáticos compilados en la etapa 1
COPY --from=frontend-builder /app/public/ ./public/

# Exponer puerto (Render asigna automáticamente la variable $PORT)
EXPOSE 5000

# Iniciar servidor
CMD ["python", "server.py"]
