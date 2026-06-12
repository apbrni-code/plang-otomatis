FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Install dependensi sistem yang mungkin dibutuhkan oleh EasyOCR/OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements.txt
COPY requirements.txt .

# Install dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode proyek ke dalam container
COPY . .

# Ekspose port 8000 (port bawaan uvicorn)
EXPOSE 8000

# Perintah yang dijalankan saat container dihidupkan
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
