FROM python:3.11-slim

WORKDIR /app

# Sistem paketleri
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Logs dizini
RUN mkdir -p logs

# Default command
CMD ["python", "-m", "orchestrator.main"]
