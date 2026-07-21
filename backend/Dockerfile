FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install standard and GPU dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    slowapi \
    python-multipart \
    faster-whisper \
    nvidia-cublas-cu12 \
    nvidia-cudnn-cu12

# Copy the custom markitdown engine and install it
COPY backend/packages/markitdown /app/packages/markitdown
RUN pip install --no-cache-dir -e '/app/packages/markitdown[all]'

# Copy the OCR plugin and install it alongside OpenAI bindings
COPY backend/packages/markitdown-ocr /app/packages/markitdown-ocr
RUN pip install --no-cache-dir -e '/app/packages/markitdown-ocr[llm]'

COPY backend /app/backend

# Inject CUDA libraries so faster-whisper can find them natively
ENV LD_LIBRARY_PATH=/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

EXPOSE 8001

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
