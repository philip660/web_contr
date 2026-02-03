# Python 3.10 cho ARMv7 (Raspberry Pi 3B)
FROM arm32v7/python:3.10-slim

WORKDIR /app

# Cài tool build cho RPi.GPIO
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Update pip
RUN pip install --upgrade pip

# Cài thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

CMD ["python", "app.py"]
