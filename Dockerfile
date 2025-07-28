FROM python:3.10-slim

# Set env to ensure consistent behavior
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages: poppler (for pdf2image) and Tesseract + language packs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-hin \
        tesseract-ocr-deu \
        tesseract-ocr-fra \
        tesseract-ocr-spa \
        tesseract-ocr-ita \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code
COPY src /app/src
COPY input /app/input
COPY output /app/output
WORKDIR /app

# Run your extractor
CMD ["python", "src/extractor.py"]
