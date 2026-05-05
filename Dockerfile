FROM python:3.9-slim

# Instalar dependencias adicionales de sistema para Playwright y FFmpeg
RUN apt-get update && apt-get install -y ffmpeg libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# Establecer la carpeta de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright playwright-stealth
RUN playwright install chromium
RUN playwright install-deps chromium

# Copiar el código del backend y las cookies
COPY api.py .
COPY temp_cookies.txt .

# Comando para encender el servidor API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
