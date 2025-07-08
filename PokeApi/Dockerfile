FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including awscli
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    unzip \
    groff \
    less \
    awscli \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONPATH=/app

CMD ["python", "-u", "app/main.py"]
