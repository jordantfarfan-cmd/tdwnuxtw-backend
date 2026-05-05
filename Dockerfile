FROM python:3.9-slim

# Instalar dependencias de sistema para Playwright y FFmpeg
RUN apt-get update && apt-get install -y ffmpeg libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

WORKDIR /app

# Crear carpeta de descargas con permisos totales
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright playwright-stealth
RUN playwright install chromium
RUN playwright install-deps chromium

COPY api.py .
COPY temp_cookies.txt .

# IMPORTANTE: Para Render y Google Cloud, usar la variable de entorno PORT
CMD sh -c "uvicorn api:app --host 0.0.0.0 --port ${PORT:-10000}"
