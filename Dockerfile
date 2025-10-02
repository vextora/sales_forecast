# 1. Base image yang lebih baru
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Set working directory
WORKDIR /app

# 3. Update OS & install minimal build tools
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y --no-install-recommends gcc g++ libpq-dev && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements dulu
COPY requirements.txt .

# 5. Install Python dependencies
# Install Python dependencies with visible progress
RUN pip install --progress-bar=on --no-cache-dir -r requirements.txt

# 6. Copy kode aplikasi
COPY . /app

# 7. Default command (bisa diganti saat docker run)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]