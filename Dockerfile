FROM python:3.10-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-mar \
    tesseract-ocr-jpn \
    tesseract-ocr-hin && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirement.txt /app/

RUN pip install --no-cache-dir -r requirement.txt

COPY ./app /app/app

COPY ./models /app/models

COPY ./run.py /app/

CMD ["python", "run.py"]
