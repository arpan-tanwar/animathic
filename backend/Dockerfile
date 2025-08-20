# Minimal Cloud Run image (no manim)
FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2 and Manim (cairo, pango, ffmpeg, latex minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 build-essential \
    ffmpeg \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpango1.0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 