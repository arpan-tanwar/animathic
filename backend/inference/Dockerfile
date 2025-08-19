FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-distutils python3-pip \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

WORKDIR /app
COPY serve_manim_lora.py /app/serve_manim_lora.py
# Copy adapter into image (replace with your adapter dir path)
COPY models/qwen-manim-lora /app/models/qwen-manim-lora

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
       torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 \
    && python -m pip install --no-cache-dir triton==2.3.1 \
    && python -m pip install --no-cache-dir fastapi uvicorn \
       transformers==4.42.4 peft==0.12.0 bitsandbytes==0.43.1 accelerate==0.32.0 sentencepiece \
       google-cloud-storage

ENV MODEL_BASE=Qwen/Qwen2.5-1.5B-Instruct
ENV ADAPTER_PATH=/app/models/qwen-manim-lora
ENV PORT=8080

EXPOSE 8080
CMD ["python", "-m", "uvicorn", "serve_manim_lora:app", "--host", "0.0.0.0", "--port", "8080"]


