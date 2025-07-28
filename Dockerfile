FROM python:3.10-slim

# ***Setting environment to ensure consistent behavior and avois any conflict***
ENV DEBIAN_FRONTEND=noninteractive


# ***Installing system packages that are required in our solution***
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

# ***Installing all the python dependencies present into requirements.txt***
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# ***Copying the source code for execution***
COPY src /app/src
COPY input /app/input
COPY output /app/output
WORKDIR /app

# ***Runing the extractor file that holds the main logic***
CMD ["python", "src/extractor.py"]
