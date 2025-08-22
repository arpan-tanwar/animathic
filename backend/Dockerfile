# Minimal Cloud Run image (no manim)
FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2 and Manim (cairo, pango, ffmpeg, latex minimal)
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    libpq5 build-essential \
    ffmpeg \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpango1.0-dev \
    pkg-config \
    libexpat1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

# Install gunicorn for production
RUN pip install gunicorn

# Create production directories
RUN mkdir -p /var/log/animathic /tmp/animathic

# Copy and make startup script executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Use production startup with dynamic port binding
CMD ["/app/start.sh"] 